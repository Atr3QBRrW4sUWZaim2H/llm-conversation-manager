---
title: Code Cleanup and Optimization
source: https://chatgpt.com/c/67930ef5-b074-8003-984e-0bc575e6c623
---

# Code Cleanup and Optimization

#### You:
<time datetime="2025-01-24T03:54:30.092Z" title="1/24/2025, 12:54:30 PM">12:54</time>

remove any unnecessary parts of this code. list what you remove
```
#!/usr/bin/env python3
import os
import re
import sys
import json
import yaml
import asyncio
import asyncpg
import httpx
import nltk
from nltk import sent_tokenize, word_tokenize
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
nltk.download("punkt")  # Ensure sentence tokenizer is available

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
	config = yaml.safe_load(f)

SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

pool: Optional[asyncpg.Pool] = None

# We'll limit concurrent Ollama requests to avoid overloading
SEM = asyncio.Semaphore(5)

# ------------------------------------------------------------
# 2. DataClass for Chunk
# ------------------------------------------------------------
@dataclass
class TextChunk:
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
	Calls an Ollama endpoint to get a short 'title' and 'summary' in JSON form.
	Adjust the model name, prompt, or parsing logic as needed.
	"""
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
		# Limit concurrency with a semaphore
		async with SEM:
			async with httpx.AsyncClient(timeout=300.0) as client:
				resp = await client.post(
					"http://localhost:11434/api/generate",
					json={
						"model": "llama3.2:1b",  # or whichever model Ollama provides
						"prompt": prompt_text,
						"stream": False,
						"format": "json"
					}
				)
				resp.raise_for_status()
				data = resp.json()
				raw_response = data.get("response", "").strip()

				# Attempt to parse JSON
				try:
					parsed = json.loads(raw_response)
					title = parsed.get("title", "").strip()
					summary = parsed.get("summary", "").strip()
				except json.JSONDecodeError:
					# If the model didn't return valid JSON, store fallback
					title = "Untitled"
					summary = raw_response

				return (title, summary)

	except Exception as e:
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
	Splits text into chunks.
	- Code blocks (```...```) become single chunks.
	- Normal text is chunked by sentences with overlap.
	"""
	segments = re.split(r"```(.*?)```", text, flags=re.DOTALL)

	chunks: List[str] = []
	for i, segment in enumerate(segments):
		if i % 2 == 1:  # code block
			code_content = segment.strip()
			code_content = unify_triple_quotes(code_content)
			if code_content:
				chunks.append(code_content)
		else:  # normal text
			normal_text = segment.strip()
			if not normal_text:
				continue
			normal_text = unify_triple_quotes(normal_text)

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
	Splits text into sentences, grouping them into ~target_size chars each,
	using sentence_overlap to repeat the last few sentences of the previous chunk.
	"""
	sentences = sent_tokenize(text)
	results: List[str] = []
	current_block: List[str] = []
	current_length = 0

	for sent in sentences:
		sent_len = len(sent)
		if current_length + sent_len > target_size and current_block:
			block_str = " ".join(current_block).strip()
			results.append(block_str)

			overlap_slice = current_block[-sentence_overlap:] if sentence_overlap > 0 else []
			current_block = list(overlap_slice)
			current_length = sum(len(s) for s in overlap_slice)

		current_block.append(sent)
		current_length += sent_len

	if current_block:
		block_str = " ".join(current_block).strip()
		results.append(block_str)

	return [r for r in results if r.strip()]

def unify_triple_quotes(text: str) -> str:
	"""
	Replaces sequences of 3 or more double quotes with exactly three.
	"""
	import re
	return re.sub(r'"{3,}', '"""', text)



# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_with_cleaned_markdown() -> List[asyncpg.Record]:
	"""
	Returns rows from `crawl4ai_pages` that have a non-empty `cleaned_markdown`.
	You might add a WHERE clause if you only want to process each page once.
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
	Inserts one chunk into `crawl4ai_chunks` with:
	  - chunk_size (int)
	  - word_count (int)
	  - chunk_title (text)
	  - chunk_summary (text)
	Make sure the table has those columns.
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
	For a single chunk:
	  1) Generate title & summary from Ollama.
	  2) Insert chunk + metadata into DB.
	"""
	(title, summary) = await generate_title_and_summary(chunk.content)
	await insert_chunk(chunk, title, summary)

# ------------------------------------------------------------
# 7. Main Chunking Script
# ------------------------------------------------------------
async def main():
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
		page_id  = record["id"]
		page_url = record["page_url"]
		cleaned_md = record["cleaned_markdown"]

		# 1) Chunk the text
		final_chunks = chunk_text_with_code_blocks(
			cleaned_md,
			target_size=800,
			sentence_overlap=2
		)
		if not final_chunks:
			continue

		# 2) Create tasks for concurrency
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

		# 3) Run tasks concurrently
		await asyncio.gather(*tasks)
		total_chunk_count += len(final_chunks)

		print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(final_chunks)}")

	print(f"[Info] Finished chunking + metadata. Inserted {total_chunk_count} total chunks.")
	await pool.close()


if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T03:55:43.728Z" title="1/24/2025, 12:55:43 PM">12:55</time>

Below is a cleaned-up version of the script, followed by a list of everything removed. The functionality remains the same—only unused imports and truly unused code segments are removed.

---

## Cleaned-Up Code

````python
#!/usr/bin/env python3
import re
import json
import yaml
import asyncio
import asyncpg
import httpx
import nltk
from nltk import sent_tokenize, word_tokenize
from typing import List, Tuple, Optional
from dataclasses import dataclass

nltk.download("punkt")  # Ensure sentence tokenizer is available

# ------------------------------------------------------------
# 1. Configuration (Static Supabase credentials)
# ------------------------------------------------------------
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

pool: Optional[asyncpg.Pool] = None

# We'll limit concurrent Ollama requests to avoid overloading
SEM = asyncio.Semaphore(5)

# ------------------------------------------------------------
# 2. DataClass for Chunk
# ------------------------------------------------------------
@dataclass
class TextChunk:
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
    Calls an Ollama endpoint to get a short 'title' and 'summary' in JSON form.
    """
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
        # Limit concurrency with a semaphore
        async with SEM:
            async with httpx.AsyncClient(timeout=300.0) as client:
                resp = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:1b",
                        "prompt": prompt_text,
                        "stream": False,
                        "format": "json"
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                raw_response = data.get("response", "").strip()

                # Attempt to parse JSON
                try:
                    parsed = json.loads(raw_response)
                    title = parsed.get("title", "").strip()
                    summary = parsed.get("summary", "").strip()
                except json.JSONDecodeError:
                    # If the model didn't return valid JSON, store fallback
                    title = "Untitled"
                    summary = raw_response

                return (title, summary)

    except Exception as e:
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
    Splits text into chunks.
    - Code blocks (```...```) become single chunks.
    - Normal text is chunked by sentences with overlap.
    """
    segments = re.split(r"```(.*?)```", text, flags=re.DOTALL)

    chunks: List[str] = []
    for i, segment in enumerate(segments):
        if i % 2 == 1:  # code block
            code_content = segment.strip()
            code_content = unify_triple_quotes(code_content)
            if code_content:
                chunks.append(code_content)
        else:  # normal text
            normal_text = segment.strip()
            if not normal_text:
                continue
            normal_text = unify_triple_quotes(normal_text)

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
    Splits text into sentences, grouping them into ~target_size chars each,
    using sentence_overlap to repeat the last few sentences of the previous chunk.
    """
    sentences = sent_tokenize(text)
    results: List[str] = []
    current_block: List[str] = []
    current_length = 0

    for sent in sentences:
        sent_len = len(sent)
        if current_length + sent_len > target_size and current_block:
            block_str = " ".join(current_block).strip()
            results.append(block_str)

            overlap_slice = current_block[-sentence_overlap:] if sentence_overlap > 0 else []
            current_block = list(overlap_slice)
            current_length = sum(len(s) for s in overlap_slice)

        current_block.append(sent)
        current_length += sent_len

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
    Returns rows from `crawl4ai_pages` that have a non-empty `cleaned_markdown`.
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
    Inserts one chunk into `crawl4ai_chunks`.
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
    For a single chunk:
      1) Generate title & summary from Ollama.
      2) Insert chunk + metadata into DB.
    """
    (title, summary) = await generate_title_and_summary(chunk.content)
    await insert_chunk(chunk, title, summary)

# ------------------------------------------------------------
# 7. Main Chunking Script
# ------------------------------------------------------------
async def main():
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
        page_id  = record["id"]
        page_url = record["page_url"]
        cleaned_md = record["cleaned_markdown"]

        # 1) Chunk the text
        final_chunks = chunk_text_with_code_blocks(
            cleaned_md,
            target_size=800,
            sentence_overlap=2
        )
        if not final_chunks:
            continue

        # 2) Create tasks for concurrency
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

        # 3) Run tasks concurrently
        await asyncio.gather(*tasks)
        total_chunk_count += len(final_chunks)

        print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(final_chunks)}")

    print(f"[Info] Finished chunking + metadata. Inserted {total_chunk_count} total chunks.")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
````

---

## Removed Items

1. **Unused Imports**
   - `import os`
   - `import sys`
   - `from datetime import datetime, timezone`
   - `from typing import Dict, Any`
   - `from urllib.parse import urlparse`

2. **Unused dotenv**

   - `from dotenv import load_dotenv`
   - `load_dotenv()`

   (Because the script uses hardcoded Supabase credentials and never calls `os.getenv`.)

3. **Unused YAML Configuration Loading**
   ```python
   with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
       config = yaml.safe_load(f)
   ```
   (The `config` variable was never used after loading.)

Everything else in the script is either used for functionality or supports the main logic.


#### You:
<time datetime="2025-01-24T03:57:16.876Z" title="1/24/2025, 12:57:16 PM">12:57</time>

review the new code above and add in exhaustive comments

#### ChatGPT:
<time datetime="2025-01-24T03:57:28.988Z" title="1/24/2025, 12:57:28 PM">12:57</time>

Below is the “cleaned-up” script **with comprehensive, line-by-line commentary** explaining what each part does. The additional comments will help you understand how the script orchestrates database connections, text chunking, and concurrent calls to Ollama for summary generation.

---

```python
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
        # If any error occurs (network, JSON parsing, etc.), return

```


#### You:
<time datetime="2025-01-24T03:58:07.035Z" title="1/24/2025, 12:58:07 PM">12:58</time>

ashwin@ubuntu-server:~/crawl4ai$ ./run_chunk.sh
  File "/home/ashwin/crawl4ai/src/chunk.py", line 259
    return re.sub(r'"{3,}', '"""', text)
                                ^
SyntaxError: unterminated string liter

#### ChatGPT:
<time datetime="2025-01-24T03:58:27.272Z" title="1/24/2025, 12:58:27 PM">12:58</time>

From the error message, Python thinks the string literal is never closed around the line:

```python
return re.sub(r'"{3,}', '"""', text)
```

In a normal Python environment, **this line is valid** as it uses single quotes (`'...'`) on the outside and includes three double quotes inside. However, two common issues can cause a syntax error like yours:

1. **Unintended “Smart Quotes”**\
   If any of the quotes are curved or typographic (“ ”) instead of straight quotes (" "), Python’s parser will fail. This can happen when copy-pasting from certain editors or browsers.

2. **Invisible Characters or Formatting**\
   Hidden characters (e.g., non-ASCII whitespace) near the quote can break parsing. DOS line endings or stray backticks can also cause problems.

---

## How to Fix

### 1. Check All Quotes Are ASCII

Make sure the line precisely matches:

```python
return re.sub(r'"{3,}', '"""', text)
```

- The **outer** quotes are **single** straight quotes: `' '`
- The **inner** quotes are **double** straight quotes: `"`
- There are exactly three double quotes inside `'"""'`

### 2. Try Escaped Quotes

If your environment continues to complain, you can replace the triple quotes with escaped double quotes:

```python
return re.sub(r'"{3,}', r'\"\"\"', text)
```

This ensures everything is interpreted plainly, without confusion over nested quotes. The replacement string `r'\"\"\"'` is equivalent to `'"""'`, but the backslashes make it very explicit.

### 3. Check Surrounding Code

Confirm there’s no mismatch with preceding or trailing triple-quoted docstrings. For example, a docstring or comment that never closed properly can cause Python to interpret the next triple quotes as part of the string. The function should look like:

```python
def unify_triple_quotes(text: str) -> str:
    """
    Replaces sequences of 3 or more double quotes with exactly three.
    """
    return re.sub(r'"{3,}', '"""', text)
```

No extra indentation, no stray backticks, no missing or extra triple quotes.

### 4. Examine File Encoding

Sometimes copying and pasting from certain sources might insert Unicode BOMs or use different line endings:

- Run `cat -v chunk.py` (on Linux/Mac) to see if there are hidden characters.
- Use a proper code editor to confirm the file encoding is UTF-8 without a BOM.

---

## Final Confirmed Snippet

Below is a self-contained snippet for the function, which should not produce a syntax error:

```python
import re

def unify_triple_quotes(text: str) -> str:
    """
    Replaces sequences of 3 or more double quotes with exactly three.
    """
    # We replace any occurrence of 3 or more consecutive double quotes (""")
    # with exactly three double quotes, to normalize code blocks or quotes.
    return re.sub(r'"{3,}', '"""', text)
```

If you still see `SyntaxError: unterminated string literal`, carefully re-check for any hidden or special characters in the file. Once you have purely ASCII quotes and a well-formed docstring, Python will accept it without error.


#### You:
<time datetime="2025-01-24T04:00:21.531Z" title="1/24/2025, 1:00:21 PM">13:00</time>

do the same 2 things for this script. remove unnecessary lines and add exhaustive comments:
```
#!/usr/bin/env python3
import os
import re
import sys
import json
import yaml
import asyncio
import asyncpg
import dateutil.parser
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set
from urllib.parse import urlparse
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
	config = yaml.safe_load(f)

SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# For demonstration, set your "high frequency" threshold:
# e.g., if 60% or more pages in a domain contain the same line, treat as boilerplate
FREQUENCY_THRESHOLD = 0.60

pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Domain Skip Patterns
# ------------------------------------------------------------
# ------------------------------------------------------------
# 2. Domain Skip Patterns
# ------------------------------------------------------------
async def get_domain_skip_patterns(domain: str) -> List[str]:
	"""
	Fetch domain-specific skip patterns from the 'domain_cleaning_rules' table.
	Prints a confirmation message if patterns were found or not.

	CREATE TABLE IF NOT EXISTS domain_cleaning_rules (
		domain TEXT PRIMARY KEY,
		skip_patterns TEXT[]
	);

	Example row:
	   domain = 'docs.crawl4ai.com'
	   skip_patterns = ARRAY[
		 'search docs...',
		 'main menu',
		 'follow us on social'
	   ]
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
	Fetch a small sample of 'raw_markdown' rows for pages in the same domain.
	This helps us identify lines that appear too frequently across pages.
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
	Return a set of lines that appear in >= FREQUENCY_THRESHOLD fraction of pages (for that domain).
	Example approach:
	  1. For each page, keep a unique set of lines (avoid double-counting duplicates within the same page).
	  2. Count how many pages each line appears in.
	  3. If line_count >= FREQUENCY_THRESHOLD * total_pages, it's "frequent".
	"""
	if not domain_raw_markdowns:
		return set()

	total_pages = len(domain_raw_markdowns)
	line_counter: Counter[str] = Counter()

	# For each page, parse lines (unique set per page to avoid overcounting)
	for md in domain_raw_markdowns:
		lines = set(md.splitlines())
		for ln in lines:
			# standardize for counting
			line_stripped = ln.strip().lower()
			if line_stripped:
				line_counter[line_stripped] += 1

	# Identify lines that appear in >= threshold fraction of pages
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
	Remove or replace lines that are considered 'boilerplate' or irrelevant,
	using a combination of:
	  - Global skip patterns
	  - Domain-specific skip patterns
	  - Frequency-based lines (common to many pages in the domain)
	"""
	lines = raw_md.splitlines()
	cleaned_lines = []

	# Merge skip patterns: global + domain-level
	# We'll treat them all as lowercased exact or substring matches
	# for simplicity. You could also store regex patterns if needed.
	all_skip = set([p.lower() for p in global_skip_patterns + domain_skip_patterns])

	for line in lines:
		# Remove leftover HTML-like tags from markdown
		line_no_tags = re.sub(r"<[^>]*>", "", line)
		# further cleaning for e.g. leftover doc tags
		line_no_tags = re.sub(r"</docs[^>]*>", "", line_no_tags, flags=re.IGNORECASE)

		# Standardize for checks
		line_stripped_lc = line_no_tags.strip().lower()

		# 1) Skip if this line is in the combined skip sets
		if any(p in line_stripped_lc for p in all_skip):
			continue

		# 2) Skip if it’s in frequent_lines for the domain
		if line_stripped_lc in frequent_lines:
			continue

		# 3) Remove empty lines
		if not line_no_tags.strip():
			continue

		cleaned_lines.append(line_no_tags.strip())

	cleaned_text = "\n".join(cleaned_lines)
	return cleaned_text

# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_to_clean() -> List[asyncpg.Record]:
	"""
	Retrieves rows from `crawl4ai_pages` that have a raw_markdown but no cleaned_markdown.
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

# A global skip pattern list you might want to apply to *all* domains
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

	# STEP 1: Gather domain-based patterns in parallel
	# We'll group pages by domain to reduce queries
	domain_map: Dict[str, List[asyncpg.Record]] = {}
	for record in pages:
		page_url  = record["page_url"]
		domain    = urlparse(page_url).netloc.lower()
		domain_map.setdefault(domain, []).append(record)

	# Pre-fetch skip patterns & frequent lines for each domain
	domain_skip_data: Dict[str, Tuple[List[str], Set[str]]] = {}

	for domain in domain_map.keys():
		domain_skip_patterns = await get_domain_skip_patterns(domain)
		# Grab a small sample of raw markdown from the DB for freq analysis
		domain_samples = await fetch_raw_markdown_for_domain(domain, sample_size=20)
		freq_lines = get_frequent_lines(domain_samples)

		domain_skip_data[domain] = (domain_skip_patterns, freq_lines)

	# STEP 2: Clean each page
	cleaned_count = 0
	for record in pages:
		page_id   = record["id"]
		page_url  = record["page_url"]
		raw_md    = record["raw_markdown"]

		domain = urlparse(page_url).netloc.lower()
		domain_skip_patterns, freq_lines = domain_skip_data.get(domain, ([], set()))

		cleaned_md = remove_boilerplate_markdown(
			raw_md,
			GLOBAL_SKIP_PATTERNS,
			domain_skip_patterns,
			freq_lines
		)

		# Update DB
		await update_cleaned_markdown(page_id, cleaned_md)
		cleaned_count += 1
		print(f"[Cleaned] page_id={page_id}, domain={domain}, url={page_url}")

	print(f"[Info] Cleaning complete. {cleaned_count} pages updated.")

	await pool.close()

if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T04:02:05.684Z" title="1/24/2025, 1:02:05 PM">13:02</time>

Below is a **cleaned-up** version of the script—removing unused imports and unreferenced code—followed by a fully **commented** version that explains each part in detail.

---

## 1. Cleaned-Up Script

```python
#!/usr/bin/env python3
import re
import asyncio
import asyncpg
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# Threshold for marking lines as "frequent boilerplate" across pages of the same domain.
FREQUENCY_THRESHOLD = 0.60

# Global connection pool reference
pool: Optional[asyncpg.Pool] = None

# ------------------------------------------------------------
# 2. Domain Skip Patterns
# ------------------------------------------------------------
async def get_domain_skip_patterns(domain: str) -> List[str]:
    """
    Fetch domain-specific skip patterns from the 'domain_cleaning_rules' table.
    Returns a list of strings to skip for the given domain.
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
    Fetch up to `sample_size` raw_markdown entries for the given domain.
    This sample is used to detect lines that appear too frequently across pages.
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
    Return a set of lines that appear in >= FREQUENCY_THRESHOLD fraction of pages.
    Each page's lines are de-duplicated before counting to avoid skewed frequencies.
    """
    if not domain_raw_markdowns:
        return set()

    total_pages = len(domain_raw_markdowns)
    line_counter: Counter[str] = Counter()

    # Count each unique line across all pages
    for md in domain_raw_markdowns:
        lines = set(md.splitlines())
        for ln in lines:
            line_stripped = ln.strip().lower()
            if line_stripped:
                line_counter[line_stripped] += 1

    # Lines that show up in >= threshold fraction of pages
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
    Remove lines considered boilerplate, using:
      1. Global skip patterns
      2. Domain-specific skip patterns
      3. Lines that appear too frequently across pages (frequent_lines)
    """
    lines = raw_md.splitlines()
    cleaned_lines = []

    all_skip = set([p.lower() for p in global_skip_patterns + domain_skip_patterns])

    for line in lines:
        # Remove HTML-like tags
        line_no_tags = re.sub(r"<[^>]*>", "", line)
        line_no_tags = re.sub(r"</docs[^>]*>", "", line_no_tags, flags=re.IGNORECASE)

        # Prepare for pattern checks
        line_stripped_lc = line_no_tags.strip().lower()

        # 1) Skip if line matches any global or domain skip patterns
        if any(p in line_stripped_lc for p in all_skip):
            continue

        # 2) Skip if line is frequent enough to be considered boilerplate
        if line_stripped_lc in frequent_lines:
            continue

        # 3) Skip completely empty lines
        if not line_no_tags.strip():
            continue

        cleaned_lines.append(line_no_tags.strip())

    return "\n".join(cleaned_lines)

# ------------------------------------------------------------
# 5. Database Access
# ------------------------------------------------------------
async def fetch_pages_to_clean() -> List[asyncpg.Record]:
    """
    Return pages that have raw_markdown but lack cleaned_markdown.
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
    Update the cleaned_markdown field of a specific page row.
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
    global pool
    # Create a connection pool to Supabase / PostgreSQL.
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

    # Group pages by their domain to batch domain-specific operations.
    domain_map: Dict[str, List[asyncpg.Record]] = {}
    for record in pages:
        page_url = record["page_url"]
        domain = urlparse(page_url).netloc.lower()
        domain_map.setdefault(domain, []).append(record)

    # Precompute skip patterns and frequent lines for each domain.
    domain_skip_data: Dict[str, Tuple[List[str], Set[str]]] = {}
    for domain in domain_map:
        domain_skip_patterns = await get_domain_skip_patterns(domain)
        domain_samples = await fetch_raw_markdown_for_domain(domain, sample_size=20)
        freq_lines = get_frequent_lines(domain_samples)
        domain_skip_data[domain] = (domain_skip_patterns, freq_lines)

    # Clean each page and update database.
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

## 2. Exhaustive Comments Version

Below is the same script with **line-by-line commentary** to help you understand each part of the code base and the reasoning behind it:

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
```

---

### What Was Removed?

1. **Unused Imports**
   - `import os`
   - `import sys`
   - `import json`
   - `import yaml` (since the loaded `config` was never used in the script)
   - `import dateutil.parser`
   - `from datetime import datetime, timezone`
   - `from dotenv import load_dotenv`

2. **Unused `.env` Loading and YAML Config**
   ```python
   load_dotenv()
   with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
       config = yaml.safe_load(f)
   ```
   (Neither `load_dotenv` nor `config` was used later.)

3. **Unused Type Hint (`Any`)**
   - Removed `Any` from `from typing import List, Dict, Any, Optional, Tuple, Set`
     since no function used `Any`.

Everything else remains necessary for the script’s functionality and clarity.


#### You:
<time datetime="2025-01-24T04:02:46.103Z" title="1/24/2025, 1:02:46 PM">13:02</time>

excellent. do the same with this script:
```
#!/usr/bin/env python3
import os
import sys
import json
import yaml
import asyncio
import asyncpg
import requests
import dateutil.parser
from datetime import datetime, timezone
from xml.etree import ElementTree
from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from dotenv import load_dotenv

# Import your local module or library for crawling
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

load_dotenv()

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
	config = yaml.safe_load(f)

SITEMAP_URL = config.get("sitemap_url")

SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

pool: Optional[asyncpg.Pool] = None  # Global DB connection pool

# ------------------------------------------------------------
# 2. Upsert Raw Markdown (Without Cleaning)
# ------------------------------------------------------------
async def upsert_raw_page(
	page_url: str,
	raw_markdown: str,
	last_modified: Optional[str]
):
	"""
	Inserts or updates a record in `crawl4ai_pages` with *raw* markdown.
	We'll leave `cleaned_markdown` as NULL here—this script is only for raw collection.
	"""
	try:
		if last_modified:
			dt = dateutil.parser.parse(last_modified)
			dt_utc = dt.astimezone(timezone.utc)
			last_modified_dt = dt_utc.replace(tzinfo=None)
		else:
			last_modified_dt = None

		created_at_dt = datetime.now(timezone.utc).replace(tzinfo=None)

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
	Crawl each URL in parallel and store only raw Markdown in the DB.
	"""
	browser_config = BrowserConfig(
		headless=True,
		verbose=False,
		extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
	)
	crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

	crawler = AsyncWebCrawler(config=browser_config)
	await crawler.start()

	try:
		semaphore = asyncio.Semaphore(max_concurrent)

		async def process_url(url: str, lastmod: Optional[str]):
			for attempt in range(2):
				try:
					async with semaphore:
						result = await crawler.arun(
							url=url,
							config=crawl_config,
							session_id="session_docs_crawl4ai"
						)

					if result.success:
						print(f"[Attempt {attempt+1}] Crawled: {url}")
						raw_md = result.markdown_v2.raw_markdown
						await upsert_raw_page(url, raw_md, lastmod)
						return  # done
					else:
						print(f"[Attempt {attempt+1}] Failed for {url}: {result.error_message}")

				except Exception as e:
					print(f"Exception on attempt {attempt+1} for {url}: {e}")

			print(f"Gave up on {url} after 2 attempts.")

		tasks = [process_url(u, lm) for (u, lm) in urls_with_lastmod]
		await asyncio.gather(*tasks)
	finally:
		await crawler.close()

# ------------------------------------------------------------
# 4. Sitemap Parser
# ------------------------------------------------------------
def get_urls_from_sitemap(sitemap_url: str) -> List[Tuple[str, Optional[str]]]:
	"""
	Fetches a sitemap.xml and returns a list of (loc, lastmod) tuples.
	"""
	try:
		resp = requests.get(sitemap_url)
		resp.raise_for_status()

		root = ElementTree.fromstring(resp.content)
		namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

		results = []
		for url_elem in root.findall('ns:url', namespace):
			loc_node = url_elem.find('ns:loc', namespace)
			lastmod_node = url_elem.find('ns:lastmod', namespace)

			loc = loc_node.text if loc_node is not None else None
			lastmod = lastmod_node.text if lastmod_node is not None else None
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

	urls_with_lastmod = get_urls_from_sitemap(SITEMAP_URL)
	if not urls_with_lastmod:
		print("[Error] No URLs found in sitemap.")
		return

	print(f"[Info] Found {len(urls_with_lastmod)} URLs to crawl...")
	await crawl_parallel(urls_with_lastmod)

	await pool.close()

if __name__ == "__main__":
	asyncio.run(main())

#### ChatGPT:
<time datetime="2025-01-24T04:03:47.127Z" title="1/24/2025, 1:03:47 PM">13:03</time>

Below is a **cleaned-up** version of the script—removing unused imports and unreferenced code—followed by a **fully commented** version that explains each part in detail.

---

## 1. Cleaned-Up Script

```python
#!/usr/bin/env python3
import yaml
import asyncio
import asyncpg
import requests
import dateutil.parser
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# Import your local module or library for crawling
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
with open("/home/ashwin/crawl4ai/src/configs/docs_crawl4ai.yml", "r") as f:
    config = yaml.safe_load(f)

SITEMAP_URL = config.get("sitemap_url")

SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

pool: Optional[asyncpg.Pool] = None  # Global DB connection pool

# ------------------------------------------------------------
# 2. Upsert Raw Markdown (Without Cleaning)
# ------------------------------------------------------------
async def upsert_raw_page(page_url: str, raw_markdown: str, last_modified: Optional[str]):
    """
    Inserts or updates a record in `crawl4ai_pages` with *raw* markdown.
    We'll leave `cleaned_markdown` as NULL here—this script is only for raw collection.
    """
    try:
        if last_modified:
            dt = dateutil.parser.parse(last_modified)
            dt_utc = dt.astimezone(timezone.utc)
            last_modified_dt = dt_utc.replace(tzinfo=None)
        else:
            last_modified_dt = None

        created_at_dt = datetime.now(timezone.utc).replace(tzinfo=None)

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
    Crawl each URL in parallel and store only raw Markdown in the DB.
    """
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_url(url: str, lastmod: Optional[str]):
            # We'll attempt crawling each URL up to two times.
            for attempt in range(2):
                try:
                    async with semaphore:
                        result = await crawler.arun(
                            url=url,
                            config=crawl_config,
                            session_id="session_docs_crawl4ai"
                        )

                    if result.success:
                        print(f"[Attempt {attempt+1}] Crawled: {url}")
                        raw_md = result.markdown_v2.raw_markdown
                        await upsert_raw_page(url, raw_md, lastmod)
                        return
                    else:
                        print(f"[Attempt {attempt+1}] Failed for {url}: {result.error_message}")

                except Exception as e:
                    print(f"Exception on attempt {attempt+1} for {url}: {e}")

            print(f"Gave up on {url} after 2 attempts.")

        tasks = [process_url(u, lm) for (u, lm) in urls_with_lastmod]
        await asyncio.gather(*tasks)
    finally:
        await crawler.close()

# ------------------------------------------------------------
# 4. Sitemap Parser
# ------------------------------------------------------------
def get_urls_from_sitemap(sitemap_url: str) -> List[Tuple[str, Optional[str]]]:
    """
    Fetches a sitemap.xml and returns a list of (loc, lastmod) tuples.
    """
    try:
        resp = requests.get(sitemap_url)
        resp.raise_for_status()
        from xml.etree import ElementTree

        root = ElementTree.fromstring(resp.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        results = []
        for url_elem in root.findall('ns:url', namespace):
            loc_node = url_elem.find('ns:loc', namespace)
            lastmod_node = url_elem.find('ns:lastmod', namespace)

            loc = loc_node.text if loc_node is not None else None
            lastmod = lastmod_node.text if lastmod_node is not None else None
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

    urls_with_lastmod = get_urls_from_sitemap(SITEMAP_URL)
    if not urls_with_lastmod:
        print("[Error] No URLs found in sitemap.")
        return

    print(f"[Info] Found {len(urls_with_lastmod)} URLs to crawl...")
    await crawl_parallel(urls_with_lastmod)

    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### What Was Removed?

1. **Unused Imports**
   - `import os`
   - `import sys`
   - `import json`
   - `from dataclasses import dataclass`
   - `from urllib.parse import urlparse` (never used here)
   - `from dotenv import load_dotenv` (since no env vars are actually read)
   - `dateutil.parser` **is** used, so we keep that.
   - `xml.etree.ElementTree` is imported **inside** `get_urls_from_sitemap` now,
     so we removed the global `import ElementTree`.

2. **Unused `.env` Loading**
   ```python
   load_dotenv()
   ```
   (Not needed if we aren’t reading environment variables.)

Everything else is relevant to reading the YAML config, parsing the sitemap, crawling pages, and upserting data into the database.

---

## 2. Exhaustive Comments Version

Below is the same script **with line-by-line commentary** explaining each part. Note that the **functionality is the same**; we just added detailed docstrings and inline comments.

```python
#!/usr/bin/env python3
"""
Script Purpose:
---------------
1. Read a config file (docs_crawl4ai.yml) containing a sitemap URL.
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
```

---

### Summary of Key Changes

1. **Unused Imports Removed**
   - **`os`, `sys`, `json`, `from dataclasses import dataclass`, `from urllib.parse import urlparse`, `from dotenv import load_dotenv`**\
     (No environment variable usage, no code referencing them.)

2. **Shifted `import xml.etree.ElementTree`**
   - Moved to inside `get_urls_from_sitemap` so it only loads if the sitemap is actually fetched.

3. **YAML Config**
   - `yaml` is necessary because we read `docs_crawl4ai.yml` to get the `SITEMAP_URL`.

4. **Retained**
   - `dateutil.parser` for parsing `<lastmod>` strings.
   - `requests` for fetching the sitemap.
   - `asyncio` and `asyncpg` for concurrency and DB I/O.
   - `datetime`, `timezone` for converting `last_modified` into UTC datetimes.
   - `crawl4ai` library for the actual asynchronous crawling.

Everything else is part of the script’s required functionality.


#### You:
<time datetime="2025-02-09T02:27:26.095Z" title="2/9/2025, 11:27:26 AM">11:27</time>

remove the step that generates a title from ollama. i will do that in another step that does all the callouts to ollama. focus on text chunking in this script

#### ChatGPT:
<time datetime="2025-02-09T02:27:49.535Z" title="2/9/2025, 11:27:49 AM">11:27</time>

Below is the **modified script** focused purely on text chunking and database insertion **without generating a title or summary via Ollama**. Any references to Ollama, title, and summary have been removed. Afterward, you'll find a **list of everything removed**.

---

## Cleaned-Up Script (Text Chunking Only)

````python
#!/usr/bin/env python3
import re
import json
import yaml
import asyncio
import asyncpg
import nltk
from nltk import sent_tokenize, word_tokenize
from typing import List, Optional
from dataclasses import dataclass

nltk.download("punkt")  # Ensure the sentence tokenizer is available

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

pool: Optional[asyncpg.Pool] = None

# We'll keep concurrency aspects if needed, but we no longer call Ollama.
# If you'd like concurrency for chunk processing, you can still implement it.

# ------------------------------------------------------------
# 2. DataClass for Chunk
# ------------------------------------------------------------
@dataclass
class TextChunk:
    """
    Represents a discrete text chunk:
    - page_id:       The ID of the original page from the database.
    - page_url:      The URL of the page (for reference).
    - chunk_number:  The index of the chunk in that page.
    - content:       The chunk text (either code or normal sentences).
    - chunk_size:    The length of the chunk in characters.
    - word_count:    The number of tokens/words in the chunk.
    """
    page_id: int
    page_url: str
    chunk_number: int
    content: str
    chunk_size: int
    word_count: int

# ------------------------------------------------------------
# 3. Chunking Logic
# ------------------------------------------------------------
def chunk_text_with_code_blocks(
    text: str,
    target_size: int = 800,
    sentence_overlap: int = 2
) -> List[str]:
    """
    Splits text into chunks:
      - Code blocks (```...```) become single chunks.
      - Normal text is split by sentences, respecting a target size.
    """
    segments = re.split(r"```(.*?)```", text, flags=re.DOTALL)

    chunks: List[str] = []
    for i, segment in enumerate(segments):
        if i % 2 == 1:  # code block
            code_content = segment.strip()
            code_content = unify_triple_quotes(code_content)
            if code_content:
                chunks.append(code_content)
        else:  # normal text
            normal_text = segment.strip()
            if not normal_text:
                continue
            normal_text = unify_triple_quotes(normal_text)

            sentence_chunks = chunk_by_sentence_overlap(
                normal_text,
                target_size=target_size,
                sentence_overlap=sentence_overlap
            )
            chunks.extend(sentence_chunks)

    return chunks

def chunk_by_sentence_overlap(
    text: str,
    target_size: int,
    sentence_overlap: int
) -> List[str]:
    """
    Split text into chunks ~ target_size characters each.
    Overlap the last N sentences of one chunk into the next (sentence_overlap).
    """
    sentences = sent_tokenize(text)
    results: List[str] = []
    current_block: List[str] = []
    current_length = 0

    for sent in sentences:
        sent_len = len(sent)
        if current_length + sent_len > target_size and current_block:
            block_str = " ".join(current_block).strip()
            results.append(block_str)

            overlap_slice = current_block[-sentence_overlap:] if sentence_overlap > 0 else []
            current_block = list(overlap_slice)
            current_length = sum(len(s) for s in overlap_slice)

        current_block.append(sent)
        current_length += sent_len

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
# 4. Database Access
# ------------------------------------------------------------
async def fetch_pages_with_cleaned_markdown() -> List[asyncpg.Record]:
    """
    Returns rows from `crawl4ai_pages` that have a non-empty `cleaned_markdown`.
    Adjust the query if you only want to process certain pages.
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

async def insert_chunk(chunk: TextChunk):
    """
    Inserts one chunk into `crawl4ai_chunks`, ignoring title/summary for now.
    Make sure your table has appropriate columns for content, size, word_count, etc.
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO crawl4ai_chunks
                (page_id, page_url, chunk_number,
                 content, chunk_size, word_count)
            VALUES
                ($1, $2, $3,
                 $4, $5, $6)
            """,
            chunk.page_id,
            chunk.page_url,
            chunk.chunk_number,
            chunk.content,
            chunk.chunk_size,
            chunk.word_count
        )

# ------------------------------------------------------------
# 5. Orchestration
# ------------------------------------------------------------
async def process_chunk(chunk: TextChunk) -> None:
    """
    Only inserts chunk data into the DB. No title/summary generation here.
    """
    await insert_chunk(chunk)

# ------------------------------------------------------------
# 6. Main Chunking Script
# ------------------------------------------------------------
async def main():
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
        page_id  = record["id"]
        page_url = record["page_url"]
        cleaned_md = record["cleaned_markdown"]

        # 1) Chunk the text
        final_chunks = chunk_text_with_code_blocks(
            cleaned_md,
            target_size=800,
            sentence_overlap=2
        )
        if not final_chunks:
            continue

        # 2) Process each chunk (insert into DB)
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
            tasks.append(process_chunk(chunk_obj))

        # 3) Run tasks concurrently or sequentially
        await asyncio.gather(*tasks)
        total_chunk_count += len(final_chunks)

        print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(final_chunks)}")

    print(f"[Info] Finished chunking. Inserted {total_chunk_count} total chunks.")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
````

---

## Removed Items

1. **Entire Ollama Title & Summary Step**
   - The function `generate_title_and_summary` was removed.
   - Any references to creating or storing `"title"` and `"summary"` were removed (including columns in the `INSERT` query).

2. **`handle_chunk` / `generate_title_and_summary`**
   - Replaced `handle_chunk` with a simpler `process_chunk` that just inserts the chunk.
   - No calls to Ollama or JSON parsing logic remain.

3. **Unused Columns**
   - Removed `chunk_title`, `chunk_summary` from the `crawl4ai_chunks` insertion.
   - The database insertion now only includes `page_id, page_url, chunk_number, content, chunk_size, word_count`.

This script now focuses **exclusively on chunking text and inserting chunks**. Any additional steps for generating a title, summary, or other metadata should happen in a separate script.


#### You:
<time datetime="2025-02-09T02:33:50.180Z" title="2/9/2025, 11:33:50 AM">11:33</time>

update this script to generate the chunk summary and title as well as the embeddings

#!/usr/bin/env python3
import os
import sys
import yaml
import asyncio
import asyncpg
import aiohttp
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --------------------------------------------------------------------
# 1. Read Configuration (FAIL if not found)
# --------------------------------------------------------------------
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_768d.yml")

# Check config file existence
if not os.path.isfile(CONFIG_PATH):
    print(f"[Error] Config file not found at {CONFIG_PATH}")
    sys.exit(1)

try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"[Error] Failed to read config file at {CONFIG_PATH}: {e}")
    sys.exit(1)

# Extract relevant fields from the YAML config
MODEL_NAME     = config.get("embedding_model", "nomic-embed-text:latest")
COLUMN_NAME    = config.get("embedding_column", "embedding")
OLLAMA_OPTIONS = config.get("ollama_options", {})  # additional key/value pairs for Ollama

# DB config from environment variables (fallbacks provided for convenience)
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# Ollama server base URL
OLLAMA_BASE_URL = "http://192.168.1.200:11434/api"

# --------------------------------------------------------------------
# 2. Global Variables
# --------------------------------------------------------------------
pool: Optional[asyncpg.Pool] = None

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
# 5. Compute Embeddings via Ollama
# --------------------------------------------------------------------
async def embed_text_ollama(session: aiohttp.ClientSession, text: str) -> List[float]:
    """
    Given a single text, call the Ollama server to get its embedding using the
    'nomic-embed-text:latest' model (or whatever is in MODEL_NAME).
    """
    url = f"{OLLAMA_BASE_URL}/embeddings"
    payload = {
        "model": MODEL_NAME,
        "prompt": text,
        # Merge in any extra Ollama options from config:
        **OLLAMA_OPTIONS
    }
    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Ollama request failed [{resp.status}]: {body}")
        data = await resp.json()

    # Expecting something like {"embedding": [...]}
    if "embedding" not in data:
        raise RuntimeError("Ollama response did not contain 'embedding' field.")

    return data["embedding"]

async def compute_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embeds a batch of texts by calling Ollama for each text (in parallel).
    """
    results: List[List[float]] = [None] * len(texts)
    async with aiohttp.ClientSession() as session:
        # We'll limit concurrency to avoid flooding the server
        sem = asyncio.Semaphore(8)
        
        async def embed_one(i: int, t: str):
            async with sem:
                results[i] = await embed_text_ollama(session, t)

        tasks = [embed_one(i, text) for i, text in enumerate(texts)]
        await asyncio.gather(*tasks)

    return results

# --------------------------------------------------------------------
# 6. Main Loop
# --------------------------------------------------------------------
async def main():
    global pool

    print("[Info] Using Ollama server at:", OLLAMA_BASE_URL)
    print("[Info] Model name:", MODEL_NAME)

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

        # Compute embeddings (in parallel) via Ollama
        batch_embs = await compute_batch_embeddings(chunk_texts)
        assert len(batch_embs) == len(rows), "Mismatch in row vs. embedding counts"

        # Update DB in parallel
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

#### ChatGPT:
<time datetime="2025-02-09T02:34:51.606Z" title="2/9/2025, 11:34:51 AM">11:34</time>

Below is an updated script that **generates a chunk summary, a chunk title, and embeddings** for any chunks missing that data. It uses:

1. **Ollama** (the `/generate` endpoint) to produce the title and summary.
2. **Ollama** (the `/embeddings` endpoint) to produce embeddings.
3. A single **database update** (`UPDATE crawl4ai_chunks`) to set all three fields at once.

Wherever possible, the logic mirrors the original embedding script, but modified to also handle title/summary generation. The script processes chunks in batches, calling Ollama in parallel.

---

## Updated Script

```python
#!/usr/bin/env python3
import os
import sys
import yaml
import asyncio
import asyncpg
import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --------------------------------------------------------------------
# 1. Read Configuration (FAIL if not found)
# --------------------------------------------------------------------
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_768d.yml")

# Check config file existence
if not os.path.isfile(CONFIG_PATH):
    print(f"[Error] Config file not found at {CONFIG_PATH}")
    sys.exit(1)

try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"[Error] Failed to read config file at {CONFIG_PATH}: {e}")
    sys.exit(1)

# Extract relevant fields from the YAML config
MODEL_NAME     = config.get("embedding_model", "nomic-embed-text:latest")
COLUMN_NAME    = config.get("embedding_column", "embedding")
OLLAMA_OPTIONS = config.get("ollama_options", {})  # additional key/value pairs for Ollama

# DB config from environment variables (fallbacks provided for convenience)
SUPABASE_USER     = os.getenv("SUPABASE_USER", "supabase_admin")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "supabase")
SUPABASE_HOST     = os.getenv("SUPABASE_HOST", "192.168.1.200")
SUPABASE_PORT     = int(os.getenv("SUPABASE_PORT", "5432"))
SUPABASE_DB       = os.getenv("SUPABASE_DB", "supabase")

# Ollama server base URL
OLLAMA_BASE_URL = "http://192.168.1.200:11434/api"

# --------------------------------------------------------------------
# 2. Global Variables
# --------------------------------------------------------------------
pool: Optional[asyncpg.Pool] = None

# --------------------------------------------------------------------
# 3. Fetch Rows Missing Title, Summary, or Embedding
# --------------------------------------------------------------------
async def fetch_chunks_missing_data(batch_size: int = 50) -> List[asyncpg.Record]:
    """
    Grab a batch of chunk rows that need any of the following:
      - chunk_title IS NULL
      - chunk_summary IS NULL
      - embedding column IS NULL (e.g. 'embedding' or 'embedding_768')
    
    We unify into one pass, so each row can be updated once with all new data.
    """
    query = f"""
        SELECT id, content, chunk_title, chunk_summary
        FROM crawl4ai_chunks
        WHERE (chunk_title IS NULL
               OR chunk_summary IS NULL
               OR {COLUMN_NAME} IS NULL)
        ORDER BY id
        LIMIT $1
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, batch_size)
    return rows

# --------------------------------------------------------------------
# 4. Updating Title, Summary, and Embedding
# --------------------------------------------------------------------
async def update_chunk_data(
    chunk_id: int,
    title: str,
    summary: str,
    embedding: List[float]
):
    """
    Single query to update title, summary, and embedding vector. 
    The config-specified column is updated with a vector type.
    """
    vector_str = "[" + ",".join(str(v) for v in embedding) + "]"
    query = f"""
        UPDATE crawl4ai_chunks
        SET chunk_title = $1,
            chunk_summary = $2,
            {COLUMN_NAME} = $3::vector
        WHERE id = $4
    """
    async with pool.acquire() as conn:
        await conn.execute(query, title, summary, vector_str, chunk_id)

# --------------------------------------------------------------------
# 5. Generate Title and Summary via Ollama
# --------------------------------------------------------------------
async def generate_title_and_summary(session: aiohttp.ClientSession, text: str) -> Tuple[str, str]:
    """
    Calls the Ollama `/generate` endpoint to produce a short title and summary.

    If your Ollama server's prompt or model differs, adjust accordingly.
    The example prompt instructs the model to return strictly JSON with
    "title" and "summary" fields.
    """
    url = f"{OLLAMA_BASE_URL}/generate"
    # Example system instructions for the model:
    prompt_text = f"""
You are an assistant that extracts a short 'title' and 'summary' from the text below.
Return strictly valid JSON in this format:

{{
  "title": "...",
  "summary": "..."
}}

Rules:
1. If more than 70% of the chunk is code, respond with:
   "title": "No Title"
   "summary": "Mainly code block"
2. Otherwise, create a short descriptive title and summary from the text.
3. If no direct heading is found, generate a short descriptive title (max 50 characters).
4. Keep the summary under 200 characters.
5. Output exactly two keys: "title" and "summary". No extra keys or line breaks.

Text:
{text}
""".strip()

    payload = {
        "model": OLLAMA_OPTIONS.get("summary_model", "llama2:7b"),  # or your chosen model
        "prompt": prompt_text,
        "stream": False,
        "format": "json",
        # Additional Ollama options if needed:
        **OLLAMA_OPTIONS
    }

    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Ollama summary request failed [{resp.status}]: {body}")
        data = await resp.json()

    # The 'response' field should contain the raw JSON string from the model
    raw_response = data.get("response", "").strip()

    # Attempt to parse the model's JSON
    import json
    try:
        parsed = json.loads(raw_response)
        title = parsed.get("title", "Untitled").strip()
        summary = parsed.get("summary", "No summary").strip()
    except json.JSONDecodeError:
        # If invalid JSON, fallback
        title = "Untitled"
        summary = raw_response

    return (title, summary)

# --------------------------------------------------------------------
# 6. Compute Embeddings via Ollama
# --------------------------------------------------------------------
async def embed_text_ollama(session: aiohttp.ClientSession, text: str) -> List[float]:
    """
    Given text, call the Ollama server's /embeddings endpoint to get a vector.
    """
    url = f"{OLLAMA_BASE_URL}/embeddings"
    payload = {
        "model": MODEL_NAME,
        "prompt": text,
        # Merge in any extra Ollama options from config:
        **OLLAMA_OPTIONS
    }
    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Ollama embed request failed [{resp.status}]: {body}")
        data = await resp.json()

    # Expecting something like {"embedding": [...]} in the response
    if "embedding" not in data:
        raise RuntimeError("Ollama response did not contain 'embedding' field.")

    return data["embedding"]

# --------------------------------------------------------------------
# 7. Process Batches: Title, Summary, and Embedding
# --------------------------------------------------------------------
async def process_chunks(rows: List[asyncpg.Record]):
    """
    For each chunk row, generate a summary/title and embedding, then update the DB.
    We do everything concurrently to speed up calls to Ollama.
    """
    # We'll store results of tasks here.
    # Each index i in `rows` will correspond to tasks for that chunk.
    results_title_summaries: List[Tuple[str, str]] = [("", "")] * len(rows)
    results_embeddings: List[List[float]]          = [[]]       * len(rows)

    # Concurrency limit
    sem = asyncio.Semaphore(8)

    async with aiohttp.ClientSession() as session:
        # Define an inner function that gets title/summary, embedding, and updates DB for a single chunk.
        async def handle_one(i: int, r: asyncpg.Record):
            async with sem:
                text = r["content"]
                # 1) Title + Summary
                title, summary = await generate_title_and_summary(session, text)
                # 2) Embedding
                emb = await embed_text_ollama(session, text)
                # 3) Update DB
                await update_chunk_data(r["id"], title, summary, emb)
                # Save results (optional, for debugging)
                results_title_summaries[i] = (title, summary)
                results_embeddings[i] = emb

        tasks = [handle_one(i, row) for i, row in enumerate(rows)]
        await asyncio.gather(*tasks)

    # Optional: print or log a summary
    for i, row in enumerate(rows):
        cid = row["id"]
        t, s = results_title_summaries[i]
        e = results_embeddings[i]
        print(f"[Processed] chunk_id={cid}, title='{t}', summary='{s[:60]}...', embedding_dim={len(e)}")

# --------------------------------------------------------------------
# 8. Main Loop
# --------------------------------------------------------------------
async def main():
    global pool

    print("[Info] Using Ollama server at:", OLLAMA_BASE_URL)
    print("[Info] Embedding model name:", MODEL_NAME)
    print(f"[Info] We'll also store the results in column '{COLUMN_NAME}'")

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

    print(f"[Info] Generating summary, title, and embeddings...")

    while True:
        # Fetch a batch that needs any of chunk_title, chunk_summary, or embedding
        rows = await fetch_chunks_missing_data(batch_size=50)
        if not rows:
            print("[Info] No more chunks to process. Exiting.")
            break

        # Process them concurrently
        await process_chunks(rows)

    await pool.close()
    print("[Info] All done. Good bye!")

# --------------------------------------------------------------------
# 9. Entrypoint
# --------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
```

---

## How It Works

1. **Configuration Loading**
   - Reads `embedding_config_768d.yml` for `MODEL_NAME`, `COLUMN_NAME`, and any `OLLAMA_OPTIONS`.
   - Grabs database credentials from environment variables or uses defaults.

2. **Fetching Rows**
   - `fetch_chunks_missing_data` selects chunks where either `chunk_title` IS NULL, `chunk_summary` IS NULL, **or** the embedding column is NULL. It returns a small batch of 50 chunks at a time.

3. **Generating Title & Summary**
   - `generate_title_and_summary` calls the `/generate` endpoint with a specific prompt. It expects strictly JSON from Ollama: `{"title": "...", "summary": "..."}`.

4. **Embedding**
   - `embed_text_ollama` calls the `/embeddings` endpoint to get a vector of floats for the chunk’s text.

5. **Concurrency**
   - All calls to Ollama happen in parallel, limited by a `Semaphore(8)`. This prevents flooding Ollama with too many simultaneous requests.

6. **Database Update**
   - `update_chunk_data` sets `chunk_title`, `chunk_summary`, and your chosen embedding column (cast to `vector`).

7. **Looping**
   - The script keeps fetching 50 chunks at a time until there are none left that need any fields.

---

### Adjusting or Customizing

- **`COLUMN_NAME`**\
  If your DB column is `embedding_768`, ensure your table is created accordingly, e.g. `ALTER TABLE crawl4ai_chunks ADD COLUMN embedding_768 vector(768);`.
- **Prompt**\
  Update the `prompt_text` in `generate_title_and_summary` to reflect how you want Ollama to produce titles and summaries.
- **Models**\
  By default, this script uses `MODEL_NAME` for embeddings, and `OLLAMA_OPTIONS["summary_model"]` for summary/title. You can unify them or adapt them as needed.
- **Batch Size & Concurrency**\
  The script processes 50 chunks per loop, each with up to 8 concurrent requests. Adjust if you have a more capable machine or a large backlog.

This script now **generates chunk summaries, titles, and embeddings** in a single pass, storing them all in `crawl4ai_chunks`.
