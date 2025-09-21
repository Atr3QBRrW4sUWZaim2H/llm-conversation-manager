---
title: Refactor to use .env
source: https://chatgpt.com/c/679331a7-26b4-8003-b2fa-ca9a5df1140e
---

# Refactor to use .env

#### You:
<time datetime="2025-01-24T06:22:32.024Z" title="1/24/2025, 3:22:32 PM">15:22</time>

refactor this script to use a .env file now that I'm done testing it:
```
#!/usr/bin/env python3
"""
Script Purpose:
---------------
1. Read a config file containing a sitemap URL and other settings.
2. Fetch the sitemap to obtain URLs and optional 'lastmod' timestamps.
3. Use an async crawler (AsyncWebCrawler) to retrieve raw Markdown from each URL.
4. Store or update this raw Markdown in a Postgres DB (table: crawl4ai_pages),
   leaving the 'cleaned_markdown' column NULL (i.e., not cleaning at this step).
5. Leverage async concurrency to speed up the crawling process.
"""

import yaml                  # For reading the YAML config.
import asyncio               # For asynchronous tasks (crawling and DB access).
import asyncpg               # Async Postgres driver.
import requests              # To fetch the sitemap.xml over HTTP.
import dateutil.parser       # To parse last_modified dates (in ISO 8601, etc.).
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# Local module for crawling, includes the classes used to run asynchronous browser-based crawls.
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
	# Load the YAML file that contains various config data.
	config = yaml.safe_load(f)

# We read the sitemap URL from the config. Adjust the key name if your YAML uses a different key.
SITEMAP_URL = config.get("sitemap_url")

# Hard-coded Supabase (PostgreSQL) credentials. You might want to use environment variables
# in production, but for now, they're inline for demonstration.
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# We'll keep a global asyncpg connection pool. We'll create it once in main() and close it later.
pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Upsert Raw Markdown (Without Cleaning)
# ------------------------------------------------------------
async def upsert_raw_page(page_url: str, raw_markdown: str, last_modified: Optional[str]):
	"""
	Inserts or updates a record in `crawl4ai_pages` with *raw* markdown.

	Table schema (simplified):
	CREATE TABLE crawl4ai_pages (
		page_url        TEXT PRIMARY KEY,
		raw_markdown    TEXT,
		cleaned_markdown TEXT,
		created_at      TIMESTAMP WITHOUT TIME ZONE,
		last_modified   TIMESTAMP WITHOUT TIME ZONE
	);

	Note:
	  - If the page_url already exists, we replace its raw_markdown,
		reset cleaned_markdown to NULL (to force re-cleaning), and update last_modified.
	  - We store the "created_at" as the time of insertion or upsert.

	:param page_url: The page’s URL.
	:param raw_markdown: The unprocessed markdown text retrieved from the crawler.
	:param last_modified: Optional string from the sitemap’s <lastmod> tag, e.g. '2023-01-05T12:34:56Z'.
	"""
	try:
		# Convert sitemap's last_modified (if any) to a UTC datetime for insertion.
		if last_modified:
			dt = dateutil.parser.parse(last_modified)
			dt_utc = dt.astimezone(timezone.utc)
			last_modified_dt = dt_utc.replace(tzinfo=None)
		else:
			last_modified_dt = None

		# For insertion, we’ll also record a 'created_at'.
		created_at_dt = datetime.now(timezone.utc).replace(tzinfo=None)

		# Acquire a DB connection from the global pool and run our UPSERT query.
		async with pool.acquire() as conn:
			await conn.execute(
				"""
				INSERT INTO crawl4ai_pages(page_url, raw_markdown, cleaned_markdown, created_at, last_modified)
				VALUES ($1, $2, NULL, $3, $4)
				ON CONFLICT (page_url) DO UPDATE
				  SET raw_markdown    = EXCLUDED.raw_markdown,
					  cleaned_markdown = NULL,
					  created_at      = EXCLUDED.created_at,
					  last_modified   = EXCLUDED.last_modified
				""",
				page_url,
				raw_markdown,
				created_at_dt,
				last_modified_dt
			)
		print(f"[DB] Upserted raw markdown for: {page_url}")

	except Exception as e:
		print(f"[DB Error] Inserting/updating page in crawl4ai_pages: {e}")

# ------------------------------------------------------------
# 3. Crawler Logic
# ------------------------------------------------------------
async def crawl_parallel(urls_with_lastmod: List[Tuple[str, Optional[str]]], max_concurrent: int = 5):
	"""
	Concurrently crawl a list of URLs, storing their raw Markdown in the DB.

	:param urls_with_lastmod: A list of (url, lastmod) tuples from the sitemap.
	:param max_concurrent: Max number of concurrent crawling tasks.
	"""
	# Configure our headless browser.
	browser_config = BrowserConfig(
		headless=True,
		verbose=False,
		extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
	)
	# Bypass cache to ensure fresh content (you could also set up caching if desired).
	crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

	# Instantiate our async crawler, then start it (e.g. launch the browser).
	crawler = AsyncWebCrawler(config=browser_config)
	await crawler.start()

	try:
		# Semaphore enforces we never have more than `max_concurrent` tasks in flight.
		semaphore = asyncio.Semaphore(max_concurrent)

		async def process_url(url: str, lastmod: Optional[str]):
			"""
			Nested function to handle a single URL. Tries up to 2 attempts in case of transient failures.
			"""
			for attempt in range(2):
				try:
					# Make sure only `max_concurrent` tasks run at once.
					async with semaphore:
						# The crawler returns a result object containing success status, errors, and markdown.
						result = await crawler.arun(
							url=url,
							config=crawl_config,
							session_id="session_docs_crawl4ai"
						)

					if result.success:
						print(f"[Attempt {attempt+1}] Crawled: {url}")
						# Retrieve raw markdown from the result and store it in the DB.
						raw_md = result.markdown_v2.raw_markdown
						await upsert_raw_page(url, raw_md, lastmod)
						return  # Success: end the loop early.
					else:
						print(f"[Attempt {attempt+1}] Failed for {url}: {result.error_message}")

				except Exception as e:
					print(f"Exception on attempt {attempt+1} for {url}: {e}")

			print(f"Gave up on {url} after 2 attempts.")

		# Create an async Task for each URL and run them concurrently.
		tasks = [process_url(u, lm) for (u, lm) in urls_with_lastmod]
		await asyncio.gather(*tasks)

	finally:
		# Ensure the crawler browser is closed no matter what happens.
		await crawler.close()

# ------------------------------------------------------------
# 4. Sitemap Parser
# ------------------------------------------------------------
def get_urls_from_sitemap(sitemap_url: str) -> List[Tuple[str, Optional[str]]]:
	"""
	Fetch the sitemap XML and extract (loc, lastmod) for each <url> entry.

	:param sitemap_url: A string containing the full sitemap.xml URL.
	:return: A list of (loc, lastmod) tuples.
	"""
	try:
		# Issue a GET request to retrieve the sitemap.
		resp = requests.get(sitemap_url)
		resp.raise_for_status()

		# We import ElementTree here, so the script runs even if no sitemap is loaded (optional).
		from xml.etree import ElementTree

		# Parse the XML into a structured tree.
		root = ElementTree.fromstring(resp.content)
		# Typical sitemaps use this namespace for <urlset> and <url> elements.
		namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

		results = []
		# For each <url> in the sitemap:
		for url_elem in root.findall('ns:url', namespace):
			loc_node = url_elem.find('ns:loc', namespace)
			lastmod_node = url_elem.find('ns:lastmod', namespace)

			loc = loc_node.text if loc_node is not None else None
			lastmod = lastmod_node.text if lastmod_node is not None else None

			# If there's a valid 'loc' (URL), add it to our results list, optionally storing lastmod.
			if loc:
				results.append((loc, lastmod))

		return results

	except Exception as e:
		print(f"Error fetching sitemap: {e}")
		return []

# ------------------------------------------------------------
# 5. Main Entrypoint
# ------------------------------------------------------------
async def main():
	"""
	1. Create an asyncpg connection pool to talk to PostgreSQL/Supabase.
	2. Parse the sitemap URL from config, fetch it, extract (url, lastmod) pairs.
	3. Crawl each URL in parallel, storing the raw Markdown into `crawl4ai_pages`.
	4. Close the DB pool at the end.
	"""
	global pool
	pool = await asyncpg.create_pool(
		user=SUPABASE_USER,
		password=SUPABASE_PASSWORD,
		host=SUPABASE_HOST,
		port=SUPABASE_PORT,
		database=SUPABASE_DB,
		min_size=1,
		max_size=5
	)

	# Fetch URLs from the sitemap. If none found, there's nothing to crawl.
	urls_with_lastmod = get_urls_from_sitemap(SITEMAP_URL)
	if not urls_with_lastmod:
		print("[Error] No URLs found in sitemap.")
		return

	print(f"[Info] Found {len(urls_with_lastmod)} URLs to crawl...")

	# Crawl all found URLs in parallel, respecting max concurrency.
	await crawl_parallel(urls_with_lastmod)

	# Finally, close the connection pool.
	await pool.close()

# Standard Python pattern for running the async main method.
if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T06:23:26.304Z" title="1/24/2025, 3:23:26 PM">15:23</time>

Below is a refactored version of your script that loads the Postgres credentials from a **.env** file using the **python-dotenv** package. In production, you’d typically place sensitive information (like DB credentials) into environment variables rather than hard-coding them directly.

> **Note**: Make sure you’ve installed `python-dotenv` via `pip install python-dotenv`, and create a **.env** file in the same directory as this script with your credentials (see the sample at the end).

---

```python
#!/usr/bin/env python3
"""
Script Purpose:
---------------
1. Read a config file containing a sitemap URL and other settings.
2. Fetch the sitemap to obtain URLs and optional 'lastmod' timestamps.
3. Use an async crawler (AsyncWebCrawler) to retrieve raw Markdown from each URL.
4. Store or update this raw Markdown in a Postgres DB (table: crawl4ai_pages),
   leaving the 'cleaned_markdown' column NULL (i.e., not cleaning at this step).
5. Leverage async concurrency to speed up the crawling process.
"""

import os
import yaml                 # For reading the YAML config.
import asyncio              # For asynchronous tasks (crawling and DB access).
import asyncpg              # Async Postgres driver.
import requests             # To fetch the sitemap.xml over HTTP.
import dateutil.parser      # To parse last_modified dates (in ISO 8601, etc.).
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# Local module for crawling, includes the classes used to run asynchronous browser-based crawls.
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ------------------------------------------------------------
# 1. Load Environment Variables + Local Config
# ------------------------------------------------------------
# This will load environment variables from the .env file in your project directory.
load_dotenv()

with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
    # Load the YAML file that contains various config data.
    config = yaml.safe_load(f)

SITEMAP_URL = config.get("sitemap_url")

# DB credentials from environment variables; you can define them in your .env file.
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# We'll keep a global asyncpg connection pool. We'll create it once in main() and close it later.
pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Upsert Raw Markdown (Without Cleaning)
# ------------------------------------------------------------
async def upsert_raw_page(page_url: str, raw_markdown: str, last_modified: Optional[str]):
    """
    Inserts or updates a record in `crawl4ai_pages` with *raw* markdown.

    Table schema (simplified):
    CREATE TABLE crawl4ai_pages (
        page_url         TEXT PRIMARY KEY,
        raw_markdown     TEXT,
        cleaned_markdown TEXT,
        created_at       TIMESTAMP WITHOUT TIME ZONE,
        last_modified    TIMESTAMP WITHOUT TIME ZONE
    );

    Note:
      - If the page_url already exists, we replace its raw_markdown,
        reset cleaned_markdown to NULL (to force re-cleaning), and update last_modified.
      - We store the "created_at" as the time of insertion or upsert.

    :param page_url: The page’s URL.
    :param raw_markdown: The unprocessed markdown text retrieved from the crawler.
    :param last_modified: Optional string from the sitemap’s <lastmod> tag, e.g. '2023-01-05T12:34:56Z'.
    """
    try:
        # Convert sitemap's last_modified (if any) to a UTC datetime for insertion.
        if last_modified:
            dt = dateutil.parser.parse(last_modified)
            dt_utc = dt.astimezone(timezone.utc)
            last_modified_dt = dt_utc.replace(tzinfo=None)
        else:
            last_modified_dt = None

        # For insertion, we’ll also record a 'created_at'.
        created_at_dt = datetime.now(timezone.utc).replace(tzinfo=None)

        # Acquire a DB connection from the global pool and run our UPSERT query.
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO crawl4ai_pages(page_url, raw_markdown, cleaned_markdown, created_at, last_modified)
                VALUES ($1, $2, NULL, $3, $4)
                ON CONFLICT (page_url) DO UPDATE
                  SET raw_markdown    = EXCLUDED.raw_markdown,
                      cleaned_markdown = NULL,
                      created_at      = EXCLUDED.created_at,
                      last_modified   = EXCLUDED.last_modified
                """,
                page_url,
                raw_markdown,
                created_at_dt,
                last_modified_dt
            )
        print(f"[DB] Upserted raw markdown for: {page_url}")

    except Exception as e:
        print(f"[DB Error] Inserting/updating page in crawl4ai_pages: {e}")

# ------------------------------------------------------------
# 3. Crawler Logic
# ------------------------------------------------------------
async def crawl_parallel(urls_with_lastmod: List[Tuple[str, Optional[str]]], max_concurrent: int = 5):
    """
    Concurrently crawl a list of URLs, storing their raw Markdown in the DB.

    :param urls_with_lastmod: A list of (url, lastmod) tuples from the sitemap.
    :param max_concurrent: Max number of concurrent crawling tasks.
    """
    # Configure our headless browser.
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )
    # Bypass cache to ensure fresh content (you could also set up caching if desired).
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Instantiate our async crawler, then start it (e.g. launch the browser).
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Semaphore enforces we never have more than `max_concurrent` tasks in flight.
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_url(url: str, lastmod: Optional[str]):
            """
            Nested function to handle a single URL. Tries up to 2 attempts in case of transient failures.
            """
            for attempt in range(2):
                try:
                    # Make sure only `max_concurrent` tasks run at once.
                    async with semaphore:
                        # The crawler returns a result object containing success status, errors, and markdown.
                        result = await crawler.arun(
                            url=url,
                            config=crawl_config,
                            session_id="session_docs_crawl4ai"
                        )

                    if result.success:
                        print(f"[Attempt {attempt+1}] Crawled: {url}")
                        # Retrieve raw markdown from the result and store it in the DB.
                        raw_md = result.markdown_v2.raw_markdown
                        await upsert_raw_page(url, raw_md, lastmod)
                        return  # Success: end the loop early.
                    else:
                        print(f"[Attempt {attempt+1}] Failed for {url}: {result.error_message}")

                except Exception as e:
                    print(f"Exception on attempt {attempt+1} for {url}: {e}")

            print(f"Gave up on {url} after 2 attempts.")

        # Create an async Task for each URL and run them concurrently.
        tasks = [process_url(u, lm) for (u, lm) in urls_with_lastmod]
        await asyncio.gather(*tasks)

    finally:
        # Ensure the crawler browser is closed no matter what happens.
        await crawler.close()

# ------------------------------------------------------------
# 4. Sitemap Parser
# ------------------------------------------------------------
def get_urls_from_sitemap(sitemap_url: str) -> List[Tuple[str, Optional[str]]]:
    """
    Fetch the sitemap XML and extract (loc, lastmod) for each <url> entry.

    :param sitemap_url: A string containing the full sitemap.xml URL.
    :return: A list of (loc, lastmod) tuples.
    """
    try:
        # Issue a GET request to retrieve the sitemap.
        resp = requests.get(sitemap_url)
        resp.raise_for_status()

        # We import ElementTree here, so the script runs even if no sitemap is loaded (optional).
        from xml.etree import ElementTree

        # Parse the XML into a structured tree.
        root = ElementTree.fromstring(resp.content)
        # Typical sitemaps use this namespace for <urlset> and <url> elements.
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        results = []
        # For each <url> in the sitemap:
        for url_elem in root.findall('ns:url', namespace):
            loc_node = url_elem.find('ns:loc', namespace)
            lastmod_node = url_elem.find('ns:lastmod', namespace)

            loc = loc_node.text if loc_node is not None else None
            lastmod = lastmod_node.text if lastmod_node is not None else None

            # If there's a valid 'loc' (URL), add it to our results list, optionally storing lastmod.
            if loc:
                results.append((loc, lastmod))

        return results

    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

# ------------------------------------------------------------
# 5. Main Entrypoint
# ------------------------------------------------------------
async def main():
    """
    1. Create an asyncpg connection pool to talk to PostgreSQL/Supabase.
    2. Parse the sitemap URL from config, fetch it, extract (url, lastmod) pairs.
    3. Crawl each URL in parallel, storing the raw Markdown into `crawl4ai_pages`.
    4. Close the DB pool at the end.
    """
    global pool
    pool = await asyncpg.create_pool(
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        database=SUPABASE_DB,
        min_size=1,
        max_size=5
    )

    # Fetch URLs from the sitemap. If none found, there's nothing to crawl.
    urls_with_lastmod = get_urls_from_sitemap(SITEMAP_URL)
    if not urls_with_lastmod:
        print("[Error] No URLs found in sitemap.")
        return

    print(f"[Info] Found {len(urls_with_lastmod)} URLs to crawl...")

    # Crawl all found URLs in parallel, respecting max concurrency.
    await crawl_parallel(urls_with_lastmod)

    # Finally, close the connection pool.
    await pool.close()

# Standard Python pattern for running the async main method.
if __name__ == "__main__":
    asyncio.run(main())
```

---

## Sample `.env` File

Create a file named `.env` in your project’s root directory with contents like:

```bash
# Postgres/Supabase Credentials
SUPABASE_USER=supabase_admin
SUPABASE_PASSWORD=supabase
SUPABASE_HOST=192.168.1.200
SUPABASE_PORT=5432
SUPABASE_DB=supabase
```

This way, your sensitive credentials are no longer hard-coded, and you can easily switch credentials for different environments (development, staging, production) by changing the `.env` file.


#### You:
<time datetime="2025-01-24T06:24:37.656Z" title="1/24/2025, 3:24:37 PM">15:24</time>

do  the same for this script
```
#!/usr/bin/env python3
"""
Script Purpose:
---------------
1. Retrieve pages from the database (Supabase/PostgreSQL) where
   'raw_markdown' is present but 'cleaned_markdown' is empty.
2. Perform a multi-stage cleaning process to remove "boilerplate" text:
   - Use a global skip pattern list applying to all domains.
   - Retrieve and apply domain-specific skip patterns from a 'domain_cleaning_rules' table.
   - Identify lines that appear in a high percentage of pages for the same domain
	 and skip them (frequency-based boilerplate).
3. Store the cleaned Markdown back into the database.
4. Use async/await to leverage concurrency for database I/O operations.
"""

import re                # Regular expressions used for removing tags/patterns.
import asyncio           # Async I/O for concurrency.
import asyncpg           # PostgreSQL driver for asynchronous queries.
from urllib.parse import urlparse  # Extract domain from URLs.
from typing import List, Dict, Optional, Tuple, Set  # Type hints for clarity.
from collections import Counter   # Helps count line occurrences for frequency-based cleaning.

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
# Hard-coded credentials for a local Supabase instance.
# In production, you might use environment variables or a config file instead.
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# FREQUENCY_THRESHOLD dictates how commonly a line must appear across sampled pages
# to be considered boilerplate. For example, 0.60 means "appearing in 60% or more pages."
FREQUENCY_THRESHOLD = 0.60

# We'll keep a global variable 'pool' for the asyncpg connection pool.
pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Domain Skip Patterns
# ------------------------------------------------------------
async def get_domain_skip_patterns(domain: str) -> List[str]:
	"""
	Look up an array of 'skip_patterns' for a specific domain from the 'domain_cleaning_rules' table.
	Each pattern is typically a substring that should cause a line to be removed if matched.

	Table Schema (simplified):
	CREATE TABLE domain_cleaning_rules (
	  domain TEXT PRIMARY KEY,
	  skip_patterns TEXT[]
	);

	:param domain: The domain to fetch skip patterns for (e.g. 'docs.example.com').
	:return: A list of skip pattern strings for that domain.
	"""
	# Acquire a connection from the pool to execute the query.
	async with pool.acquire() as conn:
		record = await conn.fetchrow(
			"""
			SELECT skip_patterns
			FROM domain_cleaning_rules
			WHERE domain = $1
			""",
			domain
		)

	# If a record with skip_patterns is found, return them; otherwise return an empty list.
	if record and record["skip_patterns"]:
		skip_patterns = record["skip_patterns"]
		print(f"[INFO] Found {len(skip_patterns)} skip patterns for domain: {domain}")
		return skip_patterns
	else:
		print(f"[INFO] No skip patterns found for domain: {domain}")
		return []

# ------------------------------------------------------------
# 3. Frequency-Based (Cross-Page) Boilerplate Detection
# ------------------------------------------------------------
async def fetch_raw_markdown_for_domain(domain: str, sample_size: int = 20) -> List[str]:
	"""
	Fetch a sample of 'raw_markdown' from pages of the given domain to analyze
	which lines appear too frequently across different pages.

	:param domain: Domain name (like 'docs.example.com').
	:param sample_size: Number of pages to sample for frequency analysis.
	:return: A list of raw markdown strings from the database.
	"""
	async with pool.acquire() as conn:
		rows = await conn.fetch(
			"""
			SELECT raw_markdown
			FROM crawl4ai_pages
			WHERE page_url ILIKE $1
			  AND raw_markdown IS NOT NULL
			  AND raw_markdown <> ''
			ORDER BY created_at DESC
			LIMIT $2
			""",
			f"%{domain}%",
			sample_size
		)
	# Convert each record to just the raw_markdown text.
	return [r["raw_markdown"] for r in rows]


def get_frequent_lines(domain_raw_markdowns: List[str]) -> Set[str]:
	"""
	Detect lines that appear in at least FREQUENCY_THRESHOLD fraction of the pages.

	Steps:
	  1. Convert each page’s content into a unique set of lines (so one line
		 can't be double-counted if it repeats multiple times in the same page).
	  2. Count how many pages each line appears in.
	  3. If line_count >= (FREQUENCY_THRESHOLD * total_pages), it is deemed "frequent."

	:param domain_raw_markdowns: List of raw markdown (each item is a single page's text).
	:return: Set of lines that are "frequent" enough to be considered boilerplate.
	"""
	if not domain_raw_markdowns:
		return set()

	total_pages = len(domain_raw_markdowns)
	line_counter: Counter[str] = Counter()

	# Count occurrences of each line across all pages.
	for md in domain_raw_markdowns:
		# Convert each page into a set of lines to avoid double-counting within the same page.
		lines = set(md.splitlines())
		for ln in lines:
			line_stripped = ln.strip().lower()
			if line_stripped:
				line_counter[line_stripped] += 1

	# Build a set of lines that appear frequently enough.
	frequent_lines = {
		ln for ln, count in line_counter.items()
		if count >= FREQUENCY_THRESHOLD * total_pages
	}
	return frequent_lines

# ------------------------------------------------------------
# 4. Master Cleaning Function
# ------------------------------------------------------------
def remove_boilerplate_markdown(
	raw_md: str,
	global_skip_patterns: List[str],
	domain_skip_patterns: List[str],
	frequent_lines: Set[str]
) -> str:
	"""
	Clean a single page’s raw_markdown by removing:
	  - Lines matching global skip patterns
	  - Lines matching domain-specific skip patterns
	  - Lines that appear in "frequent_lines" across pages of that domain

	:param raw_md: The original raw markdown text from the database.
	:param global_skip_patterns: A list of patterns to skip for all domains.
	:param domain_skip_patterns: A list of domain-specific patterns.
	:param frequent_lines: A set of lines considered "boilerplate" by frequency analysis.
	:return: Cleaned markdown string with unwanted lines removed.
	"""
	lines = raw_md.splitlines()
	cleaned_lines = []

	# Merge domain-specific and global skip patterns into one set for quick membership checks.
	# Patterns are lowercased, and we do "substring" checks for each line.
	all_skip = set([p.lower() for p in (global_skip_patterns + domain_skip_patterns)])

	for line in lines:
		# Remove any HTML-like tags (including <docs> placeholders, etc.)
		line_no_tags = re.sub(r"<[^>]*>", "", line)
		line_no_tags = re.sub(r"</docs[^>]*>", "", line_no_tags, flags=re.IGNORECASE)

		# Lowercased version for skip checks.
		line_stripped_lc = line_no_tags.strip().lower()

		# 1) Skip if any skip pattern is a substring of the line.
		if any(p in line_stripped_lc for p in all_skip):
			continue

		# 2) Skip if the line is in the domain’s frequent boilerplate lines.
		if line_stripped_lc in frequent_lines:
			continue

		# 3) Skip completely empty lines.
		if not line_no_tags.strip():
			continue

		# If none of the filters match, keep the line.
		cleaned_lines.append(line_no_tags.strip())

	# Rejoin the remaining lines with newline separators.
	return "\n".join(cleaned_lines)

# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_to_clean() -> List[asyncpg.Record]:
	"""
	Find all pages that have 'raw_markdown' but do NOT have 'cleaned_markdown' yet.
	This is the set of pages we'll run our cleaning routine on.

	:return: List of database rows, each containing (id, page_url, raw_markdown).
	"""
	async with pool.acquire() as conn:
		rows = await conn.fetch(
			"""
			SELECT id, page_url, raw_markdown
			FROM crawl4ai_pages
			WHERE raw_markdown IS NOT NULL
			  AND raw_markdown <> ''
			  AND (cleaned_markdown IS NULL OR cleaned_markdown = '')
			ORDER BY id ASC
			"""
		)
	return rows

async def update_cleaned_markdown(page_id: int, cleaned_markdown: str):
	"""
	Update the 'cleaned_markdown' field for a specific page in the database.

	:param page_id: The ID of the page to update.
	:param cleaned_markdown: The cleaned markdown string to store.
	"""
	async with pool.acquire() as conn:
		await conn.execute(
			"""
			UPDATE crawl4ai_pages
			SET cleaned_markdown = $1
			WHERE id = $2
			""",
			cleaned_markdown,
			page_id
		)

# ------------------------------------------------------------
# 6. Main Cleaning Loop
# ------------------------------------------------------------
GLOBAL_SKIP_PATTERNS = [
	"github-icon-light.svg",
	"icons/swift-icon.svg",
	"icons/kotlin-icon.svg",
	"icons/svelte-icon.svg",
	"search docs...",
	"main menu",
	"k",
	"kkgeebnipy7le",
	# etc...
]

async def main():
	"""
	1. Create a connection pool to the database.
	2. Fetch pages needing cleaning.
	3. Group pages by domain to avoid repeated queries for each domain.
	4. For each domain, fetch skip patterns and run frequency analysis.
	5. Clean each page’s raw_markdown, then update the cleaned_markdown in the DB.
	6. Close the connection pool.
	"""
	global pool
	pool = await asyncpg.create_pool(
		user=SUPABASE_USER,
		password=SUPABASE_PASSWORD,
		host=SUPABASE_HOST,
		port=SUPABASE_PORT,
		database=SUPABASE_DB,
		min_size=1,
		max_size=5
	)

	pages = await fetch_pages_to_clean()
	if not pages:
		print("[Info] No pages found that need cleaning.")
		await pool.close()
		return

	print(f"[Info] Found {len(pages)} pages to clean...")

	# Group pages by domain for more efficient skip-pattern and frequency lookups.
	domain_map: Dict[str, List[asyncpg.Record]] = {}
	for record in pages:
		page_url = record["page_url"]
		# Extract the domain from the URL and ensure it's lowercased.
		domain = urlparse(page_url).netloc.lower()
		domain_map.setdefault(domain, []).append(record)

	# Precompute domain skip patterns and frequent lines for each domain.
	domain_skip_data: Dict[str, Tuple[List[str], Set[str]]] = {}
	for domain in domain_map:
		# Domain-specific patterns from the DB.
		domain_skip_patterns = await get_domain_skip_patterns(domain)

		# Sample raw_markdown from this domain to detect frequent lines.
		domain_samples = await fetch_raw_markdown_for_domain(domain, sample_size=20)
		freq_lines = get_frequent_lines(domain_samples)

		# Store them together so we only compute once per domain.
		domain_skip_data[domain] = (domain_skip_patterns, freq_lines)

	# Now clean each page based on the above data.
	cleaned_count = 0
	for record in pages:
		page_id = record["id"]
		page_url = record["page_url"]
		raw_md  = record["raw_markdown"]

		# Look up domain-specific data for this page’s domain.
		domain = urlparse(page_url).netloc.lower()
		domain_skip_patterns, freq_lines = domain_skip_data.get(domain, ([], set()))

		# Run our cleaning function to remove boilerplate lines.
		cleaned_md = remove_boilerplate_markdown(
			raw_md,
			GLOBAL_SKIP_PATTERNS,
			domain_skip_patterns,
			freq_lines
		)

		# Update the database with the cleaned text.
		await update_cleaned_markdown(page_id, cleaned_md)
		cleaned_count += 1

		print(f"[Cleaned] page_id={page_id}, domain={domain}, url={page_url}")

	print(f"[Info] Cleaning complete. {cleaned_count} pages updated.")
	await pool.close()

if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T06:25:40.411Z" title="1/24/2025, 3:25:40 PM">15:25</time>

Below is the script refactored to read Supabase/PostgreSQL credentials from a **.env** file using **python-dotenv**. Make sure you install `python-dotenv` (e.g., `pip install python-dotenv`) and create a `.env` file (sample at the bottom) in the same directory as this script.

---

```python
#!/usr/bin/env python3
"""
Script Purpose:
---------------
1. Retrieve pages from the database (Supabase/PostgreSQL) where
   'raw_markdown' is present but 'cleaned_markdown' is empty.
2. Perform a multi-stage cleaning process to remove "boilerplate" text:
   - Use a global skip pattern list applying to all domains.
   - Retrieve and apply domain-specific skip patterns from a 'domain_cleaning_rules' table.
   - Identify lines that appear in a high percentage of pages for the same domain
     and skip them (frequency-based boilerplate).
3. Store the cleaned Markdown back into the database.
4. Use async/await to leverage concurrency for database I/O operations.
"""

import os
import re
import asyncio
import asyncpg
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter

# ------------------------------------------------------------
# 1. Environment Variables + Global Configuration
# ------------------------------------------------------------
# Load environment variables from .env file
load_dotenv()

# DB credentials from environment variables
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# FREQUENCY_THRESHOLD dictates how commonly a line must appear across sampled pages
# to be considered boilerplate. For example, 0.60 means "appearing in 60% or more pages."
FREQUENCY_THRESHOLD = 0.60

# We'll keep a global variable 'pool' for the asyncpg connection pool.
pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Domain Skip Patterns
# ------------------------------------------------------------
async def get_domain_skip_patterns(domain: str) -> List[str]:
    """
    Look up an array of 'skip_patterns' for a specific domain from the 'domain_cleaning_rules' table.
    Each pattern is typically a substring that should cause a line to be removed if matched.

    Table Schema (simplified):
    CREATE TABLE domain_cleaning_rules (
      domain TEXT PRIMARY KEY,
      skip_patterns TEXT[]
    );

    :param domain: The domain to fetch skip patterns for (e.g. 'docs.example.com').
    :return: A list of skip pattern strings for that domain.
    """
    async with pool.acquire() as conn:
        record = await conn.fetchrow(
            """
            SELECT skip_patterns
            FROM domain_cleaning_rules
            WHERE domain = $1
            """,
            domain
        )

    # If a record with skip_patterns is found, return them; otherwise return an empty list.
    if record and record["skip_patterns"]:
        skip_patterns = record["skip_patterns"]
        print(f"[INFO] Found {len(skip_patterns)} skip patterns for domain: {domain}")
        return skip_patterns
    else:
        print(f"[INFO] No skip patterns found for domain: {domain}")
        return []

# ------------------------------------------------------------
# 3. Frequency-Based (Cross-Page) Boilerplate Detection
# ------------------------------------------------------------
async def fetch_raw_markdown_for_domain(domain: str, sample_size: int = 20) -> List[str]:
    """
    Fetch a sample of 'raw_markdown' from pages of the given domain to analyze
    which lines appear too frequently across different pages.

    :param domain: Domain name (like 'docs.example.com').
    :param sample_size: Number of pages to sample for frequency analysis.
    :return: A list of raw markdown strings from the database.
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT raw_markdown
            FROM crawl4ai_pages
            WHERE page_url ILIKE $1
              AND raw_markdown IS NOT NULL
              AND raw_markdown <> ''
            ORDER BY created_at DESC
            LIMIT $2
            """,
            f"%{domain}%",
            sample_size
        )
    return [r["raw_markdown"] for r in rows]


def get_frequent_lines(domain_raw_markdowns: List[str]) -> Set[str]:
    """
    Detect lines that appear in at least FREQUENCY_THRESHOLD fraction of the pages.

    Steps:
      1. Convert each page’s content into a unique set of lines (so one line
         can't be double-counted if it repeats multiple times in the same page).
      2. Count how many pages each line appears in.
      3. If line_count >= (FREQUENCY_THRESHOLD * total_pages), it is deemed "frequent."

    :param domain_raw_markdowns: List of raw markdown (each item is a single page's text).
    :return: Set of lines that are "frequent" enough to be considered boilerplate.
    """
    if not domain_raw_markdowns:
        return set()

    total_pages = len(domain_raw_markdowns)
    line_counter: Counter[str] = Counter()

    for md in domain_raw_markdowns:
        # Convert each page into a set of lines to avoid double-counting within that page.
        lines = set(md.splitlines())
        for ln in lines:
            line_stripped = ln.strip().lower()
            if line_stripped:
                line_counter[line_stripped] += 1

    # Build a set of lines that appear frequently enough.
    frequent_lines = {
        ln for ln, count in line_counter.items()
        if count >= FREQUENCY_THRESHOLD * total_pages
    }
    return frequent_lines

# ------------------------------------------------------------
# 4. Master Cleaning Function
# ------------------------------------------------------------
def remove_boilerplate_markdown(
    raw_md: str,
    global_skip_patterns: List[str],
    domain_skip_patterns: List[str],
    frequent_lines: Set[str]
) -> str:
    """
    Clean a single page’s raw_markdown by removing:
      - Lines matching global skip patterns
      - Lines matching domain-specific skip patterns
      - Lines that appear in "frequent_lines" across pages of that domain

    :param raw_md: The original raw markdown text from the database.
    :param global_skip_patterns: A list of patterns to skip for all domains.
    :param domain_skip_patterns: A list of domain-specific patterns.
    :param frequent_lines: A set of lines considered "boilerplate" by frequency analysis.
    :return: Cleaned markdown string with unwanted lines removed.
    """
    lines = raw_md.splitlines()
    cleaned_lines = []

    # Merge domain-specific and global skip patterns into one set for quick membership checks.
    # Patterns are lowercased, and we do "substring" checks for each line.
    all_skip = set([p.lower() for p in (global_skip_patterns + domain_skip_patterns)])

    for line in lines:
        # Remove any HTML-like tags (including <docs> placeholders, etc.)
        line_no_tags = re.sub(r"<[^>]*>", "", line)
        line_no_tags = re.sub(r"</docs[^>]*>", "", line_no_tags, flags=re.IGNORECASE)

        # Lowercased version for skip checks.
        line_stripped_lc = line_no_tags.strip().lower()

        # 1) Skip if any skip pattern is a substring of the line.
        if any(p in line_stripped_lc for p in all_skip):
            continue

        # 2) Skip if the line is in the domain’s frequent boilerplate lines.
        if line_stripped_lc in frequent_lines:
            continue

        # 3) Skip completely empty lines.
        if not line_no_tags.strip():
            continue

        # If none of the filters match, keep the line.
        cleaned_lines.append(line_no_tags.strip())

    return "\n".join(cleaned_lines)

# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_to_clean() -> List[asyncpg.Record]:
    """
    Find all pages that have 'raw_markdown' but do NOT have 'cleaned_markdown' yet.

    :return: List of database rows, each containing (id, page_url, raw_markdown).
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, page_url, raw_markdown
            FROM crawl4ai_pages
            WHERE raw_markdown IS NOT NULL
              AND raw_markdown <> ''
              AND (cleaned_markdown IS NULL OR cleaned_markdown = '')
            ORDER BY id ASC
            """
        )
    return rows

async def update_cleaned_markdown(page_id: int, cleaned_markdown: str):
    """
    Update the 'cleaned_markdown' field for a specific page in the database.

    :param page_id: The ID of the page to update.
    :param cleaned_markdown: The cleaned markdown string to store.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE crawl4ai_pages
            SET cleaned_markdown = $1
            WHERE id = $2
            """,
            cleaned_markdown,
            page_id
        )

# ------------------------------------------------------------
# 6. Main Cleaning Loop
# ------------------------------------------------------------
GLOBAL_SKIP_PATTERNS = [
    "github-icon-light.svg",
    "icons/swift-icon.svg",
    "icons/kotlin-icon.svg",
    "icons/svelte-icon.svg",
    "search docs...",
    "main menu",
    "k",
    "kkgeebnipy7le",
    # etc...
]

async def main():
    """
    1. Create a connection pool to the database.
    2. Fetch pages needing cleaning.
    3. Group pages by domain to avoid repeated queries for each domain.
    4. For each domain, fetch skip patterns and run frequency analysis.
    5. Clean each page’s raw_markdown, then update the cleaned_markdown in the DB.
    6. Close the connection pool.
    """
    global pool
    pool = await asyncpg.create_pool(
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        database=SUPABASE_DB,
        min_size=1,
        max_size=5
    )

    pages = await fetch_pages_to_clean()
    if not pages:
        print("[Info] No pages found that need cleaning.")
        await pool.close()
        return

    print(f"[Info] Found {len(pages)} pages to clean...")

    # Group pages by domain for more efficient skip-pattern and frequency lookups.
    domain_map: Dict[str, List[asyncpg.Record]] = {}
    for record in pages:
        page_url = record["page_url"]
        domain = urlparse(page_url).netloc.lower()
        domain_map.setdefault(domain, []).append(record)

    # Precompute domain skip patterns and frequent lines for each domain.
    domain_skip_data: Dict[str, Tuple[List[str], Set[str]]] = {}
    for domain in domain_map:
        domain_skip_patterns = await get_domain_skip_patterns(domain)
        domain_samples = await fetch_raw_markdown_for_domain(domain, sample_size=20)
        freq_lines = get_frequent_lines(domain_samples)
        domain_skip_data[domain] = (domain_skip_patterns, freq_lines)

    # Now clean each page based on the above data.
    cleaned_count = 0
    for record in pages:
        page_id = record["id"]
        page_url = record["page_url"]
        raw_md  = record["raw_markdown"]

        domain = urlparse(page_url).netloc.lower()
        domain_skip_patterns, freq_lines = domain_skip_data.get(domain, ([], set()))

        cleaned_md = remove_boilerplate_markdown(
            raw_md,
            GLOBAL_SKIP_PATTERNS,
            domain_skip_patterns,
            freq_lines
        )
        await update_cleaned_markdown(page_id, cleaned_md)
        cleaned_count += 1

        print(f"[Cleaned] page_id={page_id}, domain={domain}, url={page_url}")

    print(f"[Info] Cleaning complete. {cleaned_count} pages updated.")
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Sample `.env` File

In the same directory as this script, create a file called `.env` containing:

```bash
# Supabase/PostgreSQL Credentials
SUPABASE_USER=supabase_admin
SUPABASE_PASSWORD=supabase
SUPABASE_HOST=192.168.1.200
SUPABASE_PORT=5432
SUPABASE_DB=supabase
```

> This structure keeps your credentials out of version control and allows you to use different DB settings for different environments (development, staging, production) simply by changing your `.env` file.


#### You:
<time datetime="2025-01-24T06:26:13.216Z" title="1/24/2025, 3:26:13 PM">15:26</time>

do the same for this script
```
#!/usr/bin/env python3
"""
This script:
1. Connects to a PostgreSQL database (specifically a Supabase instance).
2. Fetches pages from a table `crawl4ai_pages` that contain cleaned Markdown text.
3. Splits (chunks) the text into manageable segments:
   - Single chunks for code blocks delineated by triple backticks.
   - Multi-sentence chunks for normal text with some overlap between chunks.
4. Sends each chunk to an Ollama API endpoint to generate a title and summary.
5. Inserts each chunk with metadata, title, and summary into a `crawl4ai_chunks` table.
6. Uses concurrency (async/await) to parallelize the requests to Ollama.
"""

import re
import json
import yaml  # Used for reading YAML files if needed in future, left for demonstration
import asyncio
import asyncpg
import httpx
import nltk
from nltk import sent_tokenize, word_tokenize
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Download the "punkt" tokenizer for sentence splitting (only needs to be done once).
nltk.download("punkt")

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
# These credentials are hardcoded for a local Supabase instance.
# In production, you would normally load these from environment variables or a config file.
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# We will keep a single asyncpg connection pool globally, for reuse in queries.
pool: Optional[asyncpg.Pool] = None

# Limit the concurrency of Ollama requests to avoid sending too many requests at once.
SEM = asyncio.Semaphore(5)

# ------------------------------------------------------------
# 2. DataClass for Chunk
# ------------------------------------------------------------
@dataclass
class TextChunk:
	"""
	Represents a discrete text chunk:
	- page_id:    The ID of the original page from the database.
	- page_url:   The URL of the page (for reference).
	- chunk_number: The sequence number of the chunk in that page.
	- content:    Actual chunk text (either code or normal sentences).
	- chunk_size: Number of characters in the chunk.
	- word_count: Number of tokens/words in the chunk (used for analysis).
	"""
	page_id: int
	page_url: str
	chunk_number: int
	content: str
	chunk_size: int
	word_count: int

# ------------------------------------------------------------
# 3. Ollama-based Title & Summary
# ------------------------------------------------------------
async def generate_title_and_summary(chunk_text: str) -> Tuple[str, str]:
	"""
	Contacts the Ollama API endpoint to generate a short title and summary.
	The endpoint is expected to return strictly valid JSON of the form:
	{
	  "title": "...",
	  "summary": "..."
	}

	If the chunk is primarily code (>70%), the script instructs the API to respond with
	"title": "No Title" and "summary": "Mainly code block".

	Returns:
		(title, summary): A tuple of strings containing the chunk's title and summary.

	If an exception occurs or invalid JSON is returned,
	default fallback values ("Untitled", "Error Summary") will be used.
	"""
	# Prompt template with instructions for the Ollama model
	prompt_text = f"""
You are an assistant that extracts a short 'title' and 'summary' from the text below.
Return strictly valid JSON in this format:

{{
  "title": "...",
  "summary": "..."
}}

Rules:
1. If more than 70% of the chunk is code or unparseable text, respond with:
   "title": "No Title"
   "summary": "Mainly code block"
2. Otherwise, create a short descriptive title and summary from the text.
3. If you find no direct heading or name, generate a short descriptive title from the content (max 50 characters).
4. Keep the summary under 200 characters, focusing on the main idea.
5. Output exactly two keys: "title" and "summary". No extra keys or line breaks.

Text:
{chunk_text}
""".strip()

	try:
		# Use the concurrency semaphore to limit requests simultaneously.
		async with SEM:
			# Make an HTTP POST request to the Ollama API.
			async with httpx.AsyncClient(timeout=300.0) as client:
				resp = await client.post(
					"http://localhost:11434/api/generate",
					json={
						"model": "llama3.2:1b",  # Example model name; adjust as needed.
						"prompt": prompt_text,
						"stream": False,
						"format": "json"
					}
				)
				# Raise an exception if status code is not 2xx.
				resp.raise_for_status()

				# The API is expected to return JSON containing a key "response".
				data = resp.json()
				raw_response = data.get("response", "").strip()

				# Attempt to parse the Ollama response as JSON.
				try:
					parsed = json.loads(raw_response)
					title = parsed.get("title", "").strip()
					summary = parsed.get("summary", "").strip()
				except json.JSONDecodeError:
					# If the model returns malformed JSON, store fallback.
					title = "Untitled"
					summary = raw_response

				return (title, summary)

	except Exception as e:
		# If any error occurs (network, JSON parsing, etc.), return fallback.
		print(f"[ERROR] Ollama request failed: {e}")
		return ("Error Title", "Error Summary")

# ------------------------------------------------------------
# 4. Chunking Logic
# ------------------------------------------------------------
def chunk_text_with_code_blocks(
	text: str,
	target_size: int = 800,
	sentence_overlap: int = 2
) -> List[str]:
	"""
	Splits text into chunks, ensuring code blocks remain intact:
	- Uses a regex split on backticks (```...```) to separate code from normal text.
	- Code blocks become single chunks.
	- Normal text is further split into multi-sentence chunks with overlap.

	Args:
		text (str): The input text to be chunked, possibly containing code blocks.
		target_size (int): Approximate target chunk size in characters.
		sentence_overlap (int): Number of sentences to overlap between consecutive chunks.

	Returns:
		List[str]: A list of chunked text segments (strings).
	"""
	# Split the text using a capturing group around backticks so we keep code blocks separate.
	segments = re.split(r"```(.*?)```", text, flags=re.DOTALL)

	chunks: List[str] = []
	for i, segment in enumerate(segments):
		if i % 2 == 1:
			# Odd-indexed segments are code blocks (due to how capturing groups work).
			code_content = segment.strip()
			# Normalize triple quotes for consistency in the DB or further processing.
			code_content = unify_triple_quotes(code_content)
			if code_content:
				chunks.append(code_content)
		else:
			# Even-indexed segments are normal text (outside code blocks).
			normal_text = segment.strip()
			if not normal_text:
				continue
			# Normalize triple quotes again.
			normal_text = unify_triple_quotes(normal_text)

			# Further split normal text into chunks by sentences.
			sentence_chunks = chunk_by_sentence_overlap(
				normal_text, target_size=target_size, sentence_overlap=sentence_overlap
			)
			# Extend the main list of chunks.
			chunks.extend(sentence_chunks)

	return chunks

def chunk_by_sentence_overlap(
	text: str,
	target_size: int,
	sentence_overlap: int
) -> List[str]:
	"""
	Splits a string into sentence-based chunks, each up to ~target_size characters.
	Overlaps a specified number of sentences (sentence_overlap) between consecutive chunks
	to preserve some context.

	Args:
		text (str): The string to be chunked.
		target_size (int): Max number of characters in each chunk.
		sentence_overlap (int): Number of sentences repeated from the previous chunk.

	Returns:
		List[str]: A list of text chunks respecting the target size and overlap.
	"""
	# Use NLTK to break the text into individual sentences.
	sentences = sent_tokenize(text)
	results: List[str] = []
	current_block: List[str] = []
	current_length = 0

	for sent in sentences:
		sent_len = len(sent)

		# If adding this sentence exceeds the chunk size, finalize the current chunk.
		if current_length + sent_len > target_size and current_block:
			block_str = " ".join(current_block).strip()
			results.append(block_str)

			# Overlap the last 'sentence_overlap' sentences to start the next chunk.
			overlap_slice = current_block[-sentence_overlap:] if sentence_overlap > 0 else []
			current_block = list(overlap_slice)
			current_length = sum(len(s) for s in overlap_slice)

		# Add the sentence to the current block.
		current_block.append(sent)
		current_length += sent_len

	# Add any leftover block after the loop ends.
	if current_block:
		block_str = " ".join(current_block).strip()
		results.append(block_str)

	# Return only non-empty chunks.
	return [r for r in results if r.strip()]

def unify_triple_quotes(text: str) -> str:
	"""
	Replaces sequences of 3 or more double quotes with exactly three.
	"""
	return re.sub(r'"{3,}', '"""', text)


# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_with_cleaned_markdown() -> List[asyncpg.Record]:
	"""
	Fetches rows from the `crawl4ai_pages` table where `cleaned_markdown` is not empty.
	The data is assumed to be pre-processed text from the original crawled page content.

	Returns:
		A list of asyncpg.Record objects, each containing:
		  - id (int)
		  - page_url (str)
		  - cleaned_markdown (str)
	"""
	async with pool.acquire() as conn:
		return await conn.fetch(
			"""
			SELECT id, page_url, cleaned_markdown
			FROM crawl4ai_pages
			WHERE cleaned_markdown IS NOT NULL
			  AND cleaned_markdown <> ''
			ORDER BY id ASC
			"""
		)

async def insert_chunk(chunk: TextChunk, chunk_title: str, chunk_summary: str):
	"""
	Inserts a single chunk and its metadata into the `crawl4ai_chunks` table.

	Args:
		chunk (TextChunk): A dataclass instance containing chunk-related info.
		chunk_title (str): The generated chunk title from Ollama.
		chunk_summary (str): The generated chunk summary from Ollama.

	Assumes the `crawl4ai_chunks` table has columns:
		page_id, page_url, chunk_number, content,
		chunk_size, word_count, chunk_title, chunk_summary.
	"""
	async with pool.acquire() as conn:
		await conn.execute(
			"""
			INSERT INTO crawl4ai_chunks
				(page_id, page_url, chunk_number, content,
				 chunk_size, word_count,
				 chunk_title, chunk_summary)
			VALUES
				($1, $2, $3, $4,
				 $5, $6,
				 $7, $8)
			""",
			chunk.page_id,
			chunk.page_url,
			chunk.chunk_number,
			chunk.content,
			chunk.chunk_size,
			chunk.word_count,
			chunk_title,
			chunk_summary
		)

# ------------------------------------------------------------
# 6. Orchestration
# ------------------------------------------------------------
async def handle_chunk(chunk: TextChunk) -> None:
	"""
	Orchestrates the processing for a single chunk:
	  1) Generates a title & summary using Ollama (async call).
	  2) Inserts the chunk (with the newly generated title & summary) into the DB.

	Args:
		chunk (TextChunk): The text chunk to process.
	"""
	(title, summary) = await generate_title_and_summary(chunk.content)
	await insert_chunk(chunk, title, summary)

# ------------------------------------------------------------
# 7. Main Chunking Script
# ------------------------------------------------------------
async def main():
	"""
	Main entry-point function:
	- Creates an asyncpg connection pool.
	- Fetches pages that have cleaned markdown.
	- For each page, chunks the text, then asynchronously processes each chunk.
	- Prints progress logs along the way.
	- Closes the connection pool at the end.
	"""
	# Make the global 'pool' variable available locally.
	global pool

	# Create a database connection pool with defined min & max connections.
	pool = await asyncpg.create_pool(
		user=SUPABASE_USER,
		password=SUPABASE_PASSWORD,
		host=SUPABASE_HOST,
		port=SUPABASE_PORT,
		database=SUPABASE_DB,
		min_size=1,
		max_size=5
	)

	# Fetch all pages with non-empty cleaned_markdown field.
	pages = await fetch_pages_with_cleaned_markdown()
	if not pages:
		print("[Info] No pages found with cleaned_markdown.")
		await pool.close()
		return

	print(f"[Info] Found {len(pages)} pages to chunk...")

	total_chunk_count = 0

	# Iterate through each page record.
	for record in pages:
		page_id  = record["id"]
		page_url = record["page_url"]
		cleaned_md = record["cleaned_markdown"]

		# 1) Chunk the text by code blocks and sentences.
		final_chunks = chunk_text_with_code_blocks(
			cleaned_md,
			target_size=800,
			sentence_overlap=2
		)
		if not final_chunks:
			continue

		# 2) Prepare tasks for concurrency—one task per chunk.
		tasks = []
		for i, ctext in enumerate(final_chunks):
			chunk_size = len(ctext)
			word_count = len(word_tokenize(ctext))

			chunk_obj = TextChunk(
				page_id=page_id,
				page_url=page_url,
				chunk_number=i,
				content=ctext,
				chunk_size=chunk_size,
				word_count=word_count
			)
			# Each chunk's handling (title/summary generation + DB insert) is an async task.
			tasks.append(handle_chunk(chunk_obj))

		# 3) Run all tasks for the current page in parallel.
		await asyncio.gather(*tasks)
		total_chunk_count += len(final_chunks)

		print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(final_chunks)}")

	print(f"[Info] Finished chunking + metadata. Inserted {total_chunk_count} total chunks.")
	await pool.close()


if __name__ == "__main__":
	# Run the main coroutine in the event loop.
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T06:27:13.405Z" title="1/24/2025, 3:27:13 PM">15:27</time>

Below is your script refactored to load the Postgres credentials from a **.env** file instead of hardcoding them. Make sure you install `python-dotenv` (e.g. `pip install python-dotenv`) and create a `.env` file (sample provided at the bottom) in the same directory as this script.

---

````python
#!/usr/bin/env python3
"""
This script:
1. Connects to a PostgreSQL database (specifically a Supabase instance).
2. Fetches pages from a table `crawl4ai_pages` that contain cleaned Markdown text.
3. Splits (chunks) the text into manageable segments:
   - Single chunks for code blocks delineated by triple backticks.
   - Multi-sentence chunks for normal text with some overlap between chunks.
4. Sends each chunk to an Ollama API endpoint to generate a title and summary.
5. Inserts each chunk with metadata, title, and summary into a `crawl4ai_chunks` table.
6. Uses concurrency (async/await) to parallelize the requests to Ollama.
"""

import os
import re
import json
import asyncio
import asyncpg
import httpx
import nltk
from dataclasses import dataclass
from dotenv import load_dotenv
from nltk import sent_tokenize, word_tokenize
from typing import List, Tuple, Optional

# Download the "punkt" tokenizer for sentence splitting (only needs to be done once).
nltk.download("punkt")

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# We will keep a single asyncpg connection pool globally, for reuse in queries.
pool: Optional[asyncpg.Pool] = None

# Limit the concurrency of Ollama requests to avoid sending too many requests at once.
SEM = asyncio.Semaphore(5)

# ------------------------------------------------------------
# 2. DataClass for Chunk
# ------------------------------------------------------------
@dataclass
class TextChunk:
    """
    Represents a discrete text chunk:
    - page_id:      The ID of the original page from the database.
    - page_url:     The URL of the page (for reference).
    - chunk_number: The sequence number of the chunk in that page.
    - content:      Actual chunk text (either code or normal sentences).
    - chunk_size:   Number of characters in the chunk.
    - word_count:   Number of tokens/words in the chunk (used for analysis).
    """
    page_id: int
    page_url: str
    chunk_number: int
    content: str
    chunk_size: int
    word_count: int

# ------------------------------------------------------------
# 3. Ollama-based Title & Summary
# ------------------------------------------------------------
async def generate_title_and_summary(chunk_text: str) -> Tuple[str, str]:
    """
    Contacts the Ollama API endpoint to generate a short title and summary.
    The endpoint is expected to return strictly valid JSON of the form:
    {
      "title": "...",
      "summary": "..."
    }

    If the chunk is primarily code (>70%), the script instructs the API to respond with
    "title": "No Title" and "summary": "Mainly code block".

    Returns:
        (title, summary): A tuple of strings containing the chunk's title and summary.

    If an exception occurs or invalid JSON is returned,
    default fallback values ("Error Title", "Error Summary") will be used.
    """
    # Prompt template with instructions for the Ollama model
    prompt_text = f"""
You are an assistant that extracts a short 'title' and 'summary' from the text below.
Return strictly valid JSON in this format:

{{
  "title": "...",
  "summary": "..."
}}

Rules:
1. If more than 70% of the chunk is code or unparseable text, respond with:
   "title": "No Title"
   "summary": "Mainly code block"
2. Otherwise, create a short descriptive title and summary from the text.
3. If you find no direct heading or name, generate a short descriptive title from the content (max 50 characters).
4. Keep the summary under 200 characters, focusing on the main idea.
5. Output exactly two keys: "title" and "summary". No extra keys or line breaks.

Text:
{chunk_text}
""".strip()

    try:
        # Use the concurrency semaphore to limit requests simultaneously.
        async with SEM:
            async with httpx.AsyncClient(timeout=300.0) as client:
                resp = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:1b",  # Example model name; adjust as needed.
                        "prompt": prompt_text,
                        "stream": False,
                        "format": "json"
                    }
                )
                resp.raise_for_status()

                # The API is expected to return JSON containing a key "response".
                data = resp.json()
                raw_response = data.get("response", "").strip()

                try:
                    parsed = json.loads(raw_response)
                    title = parsed.get("title", "").strip()
                    summary = parsed.get("summary", "").strip()
                except json.JSONDecodeError:
                    # If the model returns malformed JSON, store fallback.
                    title = "Untitled"
                    summary = raw_response

                return (title, summary)

    except Exception as e:
        # If any error occurs (network, JSON parsing, etc.), return fallback.
        print(f"[ERROR] Ollama request failed: {e}")
        return ("Error Title", "Error Summary")

# ------------------------------------------------------------
# 4. Chunking Logic
# ------------------------------------------------------------
def chunk_text_with_code_blocks(
    text: str,
    target_size: int = 800,
    sentence_overlap: int = 2
) -> List[str]:
    """
    Splits text into chunks, ensuring code blocks remain intact:
    - Uses a regex split on backticks (```...```) to separate code from normal text.
    - Code blocks become single chunks.
    - Normal text is further split into multi-sentence chunks with overlap.

    Args:
        text (str): The input text to be chunked, possibly containing code blocks.
        target_size (int): Approximate target chunk size in characters.
        sentence_overlap (int): Number of sentences to overlap between consecutive chunks.

    Returns:
        List[str]: A list of chunked text segments (strings).
    """
    segments = re.split(r"```(.*?)```", text, flags=re.DOTALL)

    chunks: List[str] = []
    for i, segment in enumerate(segments):
        if i % 2 == 1:
            # Odd-indexed segments are code blocks (captured by the group).
            code_content = segment.strip()
            code_content = unify_triple_quotes(code_content)
            if code_content:
                chunks.append(code_content)
        else:
            # Even-indexed segments are normal text (outside code blocks).
            normal_text = segment.strip()
            if not normal_text:
                continue
            normal_text = unify_triple_quotes(normal_text)

            # Further split normal text into chunks by sentences.
            sentence_chunks = chunk_by_sentence_overlap(
                normal_text, target_size=target_size, sentence_overlap=sentence_overlap
            )
            chunks.extend(sentence_chunks)

    return chunks

def chunk_by_sentence_overlap(
    text: str,
    target_size: int,
    sentence_overlap: int
) -> List[str]:
    """
    Splits a string into sentence-based chunks, each up to ~target_size characters.
    Overlaps a specified number of sentences (sentence_overlap) between consecutive chunks
    to preserve some context.

    Args:
        text (str): The string to be chunked.
        target_size (int): Max number of characters in each chunk.
        sentence_overlap (int): Number of sentences repeated from the previous chunk.

    Returns:
        List[str]: A list of text chunks respecting the target size and overlap.
    """
    sentences = sent_tokenize(text)
    results: List[str] = []
    current_block: List[str] = []
    current_length = 0

    for sent in sentences:
        sent_len = len(sent)
        # If adding this sentence exceeds the chunk size, finalize current chunk.
        if current_length + sent_len > target_size and current_block:
            block_str = " ".join(current_block).strip()
            results.append(block_str)

            # Overlap the last 'sentence_overlap' sentences to start the next chunk.
            overlap_slice = current_block[-sentence_overlap:] if sentence_overlap > 0 else []
            current_block = list(overlap_slice)
            current_length = sum(len(s) for s in overlap_slice)

        current_block.append(sent)
        current_length += sent_len

    # Add any leftover block.
    if current_block:
        block_str = " ".join(current_block).strip()
        results.append(block_str)

    return [r for r in results if r.strip()]

def unify_triple_quotes(text: str) -> str:
    """
    Replaces sequences of 3 or more double quotes with exactly three.
    """
    return re.sub(r'"{3,}', '"""', text)

# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_with_cleaned_markdown() -> List[asyncpg.Record]:
    """
    Fetches rows from the `crawl4ai_pages` table where `cleaned_markdown` is not empty.
    Returns a list of asyncpg.Record objects, each with:
      - id (int)
      - page_url (str)
      - cleaned_markdown (str)
    """
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT id, page_url, cleaned_markdown
            FROM crawl4ai_pages
            WHERE cleaned_markdown IS NOT NULL
              AND cleaned_markdown <> ''
            ORDER BY id ASC
            """
        )

async def insert_chunk(chunk: TextChunk, chunk_title: str, chunk_summary: str):
    """
    Inserts a single chunk and its metadata into the `crawl4ai_chunks` table.

    Args:
        chunk (TextChunk): A dataclass instance containing chunk-related info.
        chunk_title (str): Title returned by Ollama.
        chunk_summary (str): Summary returned by Ollama.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO crawl4ai_chunks
                (page_id, page_url, chunk_number, content,
                 chunk_size, word_count,
                 chunk_title, chunk_summary)
            VALUES
                ($1, $2, $3, $4,
                 $5, $6,
                 $7, $8)
            """,
            chunk.page_id,
            chunk.page_url,
            chunk.chunk_number,
            chunk.content,
            chunk.chunk_size,
            chunk.word_count,
            chunk_title,
            chunk_summary
        )

# ------------------------------------------------------------
# 6. Orchestration
# ------------------------------------------------------------
async def handle_chunk(chunk: TextChunk) -> None:
    """
    Orchestrates the processing for a single chunk:
      1) Generates a title & summary using Ollama (async call).
      2) Inserts the chunk (with the newly generated title & summary) into the DB.
    """
    (title, summary) = await generate_title_and_summary(chunk.content)
    await insert_chunk(chunk, title, summary)

# ------------------------------------------------------------
# 7. Main Chunking Script
# ------------------------------------------------------------
async def main():
    """
    Main entry-point function:
    - Creates an asyncpg connection pool.
    - Fetches pages that have cleaned markdown.
    - For each page, chunks the text, then asynchronously processes each chunk.
    - Prints progress logs along the way.
    - Closes the connection pool at the end.
    """
    global pool
    pool = await asyncpg.create_pool(
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        database=SUPABASE_DB,
        min_size=1,
        max_size=5
    )

    pages = await fetch_pages_with_cleaned_markdown()
    if not pages:
        print("[Info] No pages found with cleaned_markdown.")
        await pool.close()
        return

    print(f"[Info] Found {len(pages)} pages to chunk...")

    total_chunk_count = 0

    for record in pages:
        page_id = record["id"]
        page_url = record["page_url"]
        cleaned_md = record["cleaned_markdown"]

        # 1) Chunk the text by code blocks and sentences.
        final_chunks = chunk_text_with_code_blocks(
            cleaned_md,
            target_size=800,
            sentence_overlap=2
        )
        if not final_chunks:
            continue

        # 2) Prepare tasks for concurrency—one task per chunk.
        tasks = []
        for i, ctext in enumerate(final_chunks):
            chunk_size = len(ctext)
            word_count = len(word_tokenize(ctext))

            chunk_obj = TextChunk(
                page_id=page_id,
                page_url=page_url,
                chunk_number=i,
                content=ctext,
                chunk_size=chunk_size,
                word_count=word_count
            )
            tasks.append(handle_chunk(chunk_obj))

        # 3) Run all tasks for the current page in parallel.
        await asyncio.gather(*tasks)
        total_chunk_count += len(final_chunks)

        print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(final_chunks)}")

    print(f"[Info] Finished chunking + metadata. Inserted {total_chunk_count} total chunks.")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
````

---

## Sample `.env` File

In the same directory as this script, create a file called `.env` containing:

```bash
# Supabase/PostgreSQL Credentials
SUPABASE_USER=supabase_admin
SUPABASE_PASSWORD=supabase
SUPABASE_HOST=192.168.1.200
SUPABASE_PORT=5432
SUPABASE_DB=supabase
```

> This approach ensures you keep sensitive credentials out of your source code and can easily change them by modifying the `.env` file.


#### You:
<time datetime="2025-01-24T06:28:00.561Z" title="1/24/2025, 3:28:00 PM">15:28</time>

do the same for this script
```
#!/usr/bin/env python3
import os
import sys
import json
import yaml
import asyncio
import asyncpg
import torch
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# --------------------------------------------------------------------
# 1. Read Configuration
# --------------------------------------------------------------------
# Suppose we read a YAML file `configs/embedding_config.yml` with keys like:
#   embedding_model: "nvidia/NV-Embed-v2"
#   embedding_column: "embedding"
#   ollama_options:
#     temperature: 0.8
#     repeat_penalty: 1.2
#     ...
#
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_768d.yml")
with open(CONFIG_PATH, "r") as f:
	config = yaml.safe_load(f)

# Extract relevant fields
MODEL_NAME      = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
COLUMN_NAME     = config.get("embedding_column", "embedding")
OLLAMA_OPTIONS  = config.get("ollama_options", {})  # optional, if needed

# DB config (could also be loaded from the same config or from .env)
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# --------------------------------------------------------------------
# 2. Global Variables
# --------------------------------------------------------------------
pool: Optional[asyncpg.Pool] = None
embedding_model: Optional[SentenceTransformer] = None

# --------------------------------------------------------------------
# 3. Fetch Rows Lacking This Particular Embedding Column
# --------------------------------------------------------------------
async def fetch_chunks_missing_embedding(batch_size: int = 50) -> List[asyncpg.Record]:
	"""
	Grab a batch of chunk rows where `COLUMN_NAME` is NULL.
	i.e. if config says 'embedding_column: embedding_4096',
	we'll do `WHERE embedding_4096 IS NULL`.
	"""
	query = f"""
		SELECT id, content
		FROM crawl4ai_chunks
		WHERE {COLUMN_NAME} IS NULL
		ORDER BY id
		LIMIT $1
	"""
	async with pool.acquire() as conn:
		rows = await conn.fetch(query, batch_size)
	return rows

# --------------------------------------------------------------------
# 4. Updating the Single Embedding Column
# --------------------------------------------------------------------
async def update_chunk_embedding(chunk_id: int, embedding: List[float]):
	"""
	Convert embedding -> '[x1,x2,...]' and store it in the config-specified column.
	"""
	vector_str = "[" + ",".join(str(v) for v in embedding) + "]"
	query = f"""
		UPDATE crawl4ai_chunks
		SET {COLUMN_NAME} = $1::vector
		WHERE id = $2
	"""
	async with pool.acquire() as conn:
		await conn.execute(query, vector_str, chunk_id)

# --------------------------------------------------------------------
# 5. Compute Embeddings for a Batch
# --------------------------------------------------------------------
def compute_batch_embeddings(texts: List[str]) -> List[List[float]]:
	"""
	Encodes a batch of texts at once for performance, returning a list of float vectors.
	"""
	device = "cuda" if torch.cuda.is_available() else "cpu"
	embeddings = embedding_model.encode(
		texts,
		show_progress_bar=False,
		device=device,
		batch_size=8  # can be tuned
	)
	# Convert to Python lists
	return [vec.tolist() for vec in embeddings]

# --------------------------------------------------------------------
# 6. Main Loop
# --------------------------------------------------------------------
async def main():
	global pool, embedding_model

	print("[Info] Loading embedding model:", MODEL_NAME)
	embedding_model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
	if torch.cuda.is_available():
		embedding_model.to(torch.device("cuda"))

	# Connect to DB
	pool = await asyncpg.create_pool(
		user=SUPABASE_USER,
		password=SUPABASE_PASSWORD,
		host=SUPABASE_HOST,
		port=SUPABASE_PORT,
		database=SUPABASE_DB,
		min_size=1,
		max_size=5
	)

	print(f"[Info] Starting to embed missing data in column '{COLUMN_NAME}'...")

	while True:
		rows = await fetch_chunks_missing_embedding(batch_size=50)
		if not rows:
			print("[Info] No more chunks to embed. Exiting.")
			break

		chunk_ids   = [r["id"]      for r in rows]
		chunk_texts = [r["content"] for r in rows]

		# Compute embeddings
		batch_embs = compute_batch_embeddings(chunk_texts)
		assert len(batch_embs) == len(rows), "Mismatch in row vs. embedding counts"

		# Parallel DB updates
		tasks = []
		for i, row in enumerate(rows):
			chunk_id = row["id"]
			emb      = batch_embs[i]
			tasks.append(update_chunk_embedding(chunk_id, emb))

		await asyncio.gather(*tasks)
		for i, row in enumerate(rows):
			print(f"[Embedded] chunk_id={row['id']} => dimension: {len(batch_embs[i])}")

	await pool.close()
	print("[Info] All done. Good bye!")

# --------------------------------------------------------------------
# 7. Entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T06:28:35.579Z" title="1/24/2025, 3:28:35 PM">15:28</time>

Below is your script refactored to pull the database credentials and optional config path from environment variables using **python-dotenv**. The key difference is that now you rely on environment variables (with optional defaults) rather than hardcoding.

Make sure you’ve installed `python-dotenv` (e.g. `pip install python-dotenv`) and create a `.env` file (sample provided at the bottom). The script already includes `load_dotenv()`, so it will automatically read environment variables from your `.env` file at runtime.

---

```python
#!/usr/bin/env python3
import os
import sys
import json
import yaml
import asyncio
import asyncpg
import torch
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables from .env
load_dotenv()

# --------------------------------------------------------------------
# 1. Read Configuration
# --------------------------------------------------------------------
# EMBED_CONFIG_PATH can be specified in your .env:
#   EMBED_CONFIG_PATH=/path/to/embedding_config.yml
# or else defaults to a certain local path if not found.
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_768d.yml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Extract relevant fields from the YAML config
MODEL_NAME     = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
COLUMN_NAME    = config.get("embedding_column", "embedding")
OLLAMA_OPTIONS = config.get("ollama_options", {})  # optional, if needed

# DB config from environment variables (fallbacks provided for convenience)
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# --------------------------------------------------------------------
# 2. Global Variables
# --------------------------------------------------------------------
pool: Optional[asyncpg.Pool] = None
embedding_model: Optional[SentenceTransformer] = None

# --------------------------------------------------------------------
# 3. Fetch Rows Lacking This Particular Embedding Column
# --------------------------------------------------------------------
async def fetch_chunks_missing_embedding(batch_size: int = 50) -> List[asyncpg.Record]:
    """
    Grab a batch of chunk rows where `COLUMN_NAME` is NULL.
    i.e. if config says 'embedding_column: embedding_4096',
    we'll do `WHERE embedding_4096 IS NULL`.
    """
    query = f"""
        SELECT id, content
        FROM crawl4ai_chunks
        WHERE {COLUMN_NAME} IS NULL
        ORDER BY id
        LIMIT $1
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, batch_size)
    return rows

# --------------------------------------------------------------------
# 4. Updating the Single Embedding Column
# --------------------------------------------------------------------
async def update_chunk_embedding(chunk_id: int, embedding: List[float]):
    """
    Convert embedding -> '[x1,x2,...]' and store it in the config-specified column.
    """
    vector_str = "[" + ",".join(str(v) for v in embedding) + "]"
    query = f"""
        UPDATE crawl4ai_chunks
        SET {COLUMN_NAME} = $1::vector
        WHERE id = $2
    """
    async with pool.acquire() as conn:
        await conn.execute(query, vector_str, chunk_id)

# --------------------------------------------------------------------
# 5. Compute Embeddings for a Batch
# --------------------------------------------------------------------
def compute_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Encodes a batch of texts at once for performance, returning a list of float vectors.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=False,
        device=device,
        batch_size=8  # can be tuned
    )
    # Convert to Python lists
    return [vec.tolist() for vec in embeddings]

# --------------------------------------------------------------------
# 6. Main Loop
# --------------------------------------------------------------------
async def main():
    global pool, embedding_model

    print("[Info] Loading embedding model:", MODEL_NAME)
    embedding_model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    if torch.cuda.is_available():
        embedding_model.to(torch.device("cuda"))

    # Connect to DB
    pool = await asyncpg.create_pool(
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        host=SUPABASE_HOST,
        port=SUPABASE_PORT,
        database=SUPABASE_DB,
        min_size=1,
        max_size=5
    )

    print(f"[Info] Starting to embed missing data in column '{COLUMN_NAME}'...")

    while True:
        rows = await fetch_chunks_missing_embedding(batch_size=50)
        if not rows:
            print("[Info] No more chunks to embed. Exiting.")
            break

        chunk_ids   = [r["id"]      for r in rows]
        chunk_texts = [r["content"] for r in rows]

        # Compute embeddings
        batch_embs = compute_batch_embeddings(chunk_texts)
        assert len(batch_embs) == len(rows), "Mismatch in row vs. embedding counts"

        # Parallel DB updates
        tasks = []
        for i, row in enumerate(rows):
            chunk_id = row["id"]
            emb = batch_embs[i]
            tasks.append(update_chunk_embedding(chunk_id, emb))

        await asyncio.gather(*tasks)
        for i, row in enumerate(rows):
            print(f"[Embedded] chunk_id={row['id']} => dimension: {len(batch_embs[i])}")

    await pool.close()
    print("[Info] All done. Good bye!")

# --------------------------------------------------------------------
# 7. Entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
```

---

## Sample `.env` File

Below is an example `.env` you could place in the same directory. Adjust the values as needed for your environment:

```bash
# Optional path override for the embedding config YAML
EMBED_CONFIG_PATH=/home/ashwin/crawl4ai/src/configs/embedding_config_768d.yml

# Postgres/Supabase Credentials
SUPABASE_USER=supabase_admin
SUPABASE_PASSWORD=supabase
SUPABASE_HOST=192.168.1.200
SUPABASE_PORT=5432
SUPABASE_DB=supabase
```

With this setup, your script will read all these values when it runs, keeping sensitive details out of source code.


#### You:
<time datetime="2025-01-24T06:29:29.281Z" title="1/24/2025, 3:29:29 PM">15:29</time>

it looks like the values for the username and password are still in the script. is this expected?
```
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")


#### ChatGPT:
<time datetime="2025-01-24T06:29:47.960Z" title="1/24/2025, 3:29:47 PM">15:29</time>

By default, Python’s `os.getenv(key, default_value)` allows you to specify a fallback in case the environment variable isn’t set. In the snippet:

```python
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")
```

the `"supabase_admin"` and `"supabase"` etc. are just **defaults**—they’re not meant to be real credentials. If no environment variable is found (e.g., if `SUPABASE_USER` is not set in your `.env` or system environment), then Python will fall back to `"supabase_admin"`.

### Is this expected?

- **Yes**, it’s common to keep default placeholders (like `"root"`, `"localhost"`, or `"test"`) so that if someone runs the script without a `.env` file, it won’t crash. It will still attempt a connection with those “dummy” credentials.
- **If you want to be stricter** (e.g., you require credentials and never want a fallback in code), you can remove the default values altogether and raise an error if the environment variables aren’t set. For example:

  ```python
  SUPABASE_USER = os.getenv("SUPABASE_USER")
  if not SUPABASE_USER:
      raise ValueError("SUPABASE_USER environment variable is not set.")

  SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
  if not SUPABASE_PASSWORD:
      raise ValueError("SUPABASE_PASSWORD environment variable is not set.")

  ...
  ```

  In this version, your script will refuse to run unless those environment variables are explicitly defined. This ensures you never inadvertently commit or use a placeholder credential in production.

### TL;DR

The fallback values are there for convenience (so the script “works” in a local environment if environment variables are missing). If you don’t want any credentials in your code at all, simply remove those default values and force the script to rely entirely on environment variables.
