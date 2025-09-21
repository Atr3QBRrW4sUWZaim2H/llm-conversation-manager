---
title: Update to Nomic Embed
source: https://chatgpt.com/c/67a6e17b-3fe8-8003-9183-c5a8c0ac1f01
---

# Update to Nomic Embed

#### You:
<time datetime="2025-02-08T04:54:04.963Z" title="2/8/2025, 1:54:04 PM">13:54</time>

update this script  to use the nomic-embed-text:latest embedding model on ollama server http://192.168.1.200:11434. also, the script should fail if it does not find a valid config file


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
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_1536.yml")
with open(CONFIG_PATH, "r") as f:
	config = yaml.safe_load(f)

# Extract relevant fields from the YAML config
MODEL_NAME     = config.get("embedding_model", "nomic-embed-text:latest")
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

#### ChatGPT:
<time datetime="2025-02-08T04:54:45.038Z" title="2/8/2025, 1:54:45 PM">13:54</time>

Below is an example of how you might modify the script to:

1. **Fail** if it does not find a valid config file (i.e., `CONFIG_PATH` doesn't exist or can't be read).
2. **Use** the `nomic-embed-text:latest` model on an Ollama server at `http://192.168.1.200:11434`.
3. **Remove** any direct use of `SentenceTransformer`/local embeddings and call Ollama instead.

> **Note**: This script assumes Ollama’s embedding endpoint is something like `POST /embeddings` (or similar) that accepts JSON payloads with `"model"` and `"prompt"` fields and returns a JSON response containing an `"embedding"` array. Adjust the URL/path and payload/response structure to match your actual Ollama setup.

---

```python
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
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_1536.yml")

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
OLLAMA_BASE_URL = "http://192.168.1.200:11434"

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
```

### Key Changes / Notes

1. **Fail if config not found**
   - We explicitly check `os.path.isfile(CONFIG_PATH)` and `try/except` around reading the YAML. If it fails, the script exits with error status.

2. **Removed local `SentenceTransformer`**
   - The script no longer imports nor loads a local `SentenceTransformer`. Instead, it calls Ollama via `aiohttp` for each text.

3. **Use Ollama for embeddings**
   - `embed_text_ollama()` sends a `POST` request to `http://192.168.1.200:11434/embeddings` (adjust if your Ollama server uses a different path), passing in `"model"`, `"prompt"`, and any `OLLAMA_OPTIONS` from the YAML.
   - Assumes Ollama returns a JSON with `{"embedding": [ ... ]}`, which we then return as a list of floats.

4. **Batch embedding**
   - `compute_batch_embeddings()` spins up parallel tasks (capped by `asyncio.Semaphore(8)`) to avoid flooding the Ollama server. You can tweak that concurrency or the batch size.

Adjust the URL endpoint (`/embeddings`) or payload fields to match your actual Ollama server’s API. Otherwise, this should give you the desired behavior of embedding via Ollama and failing if the config file is missing or invalid.


#### You:
<time datetime="2025-02-08T05:17:18.719Z" title="2/8/2025, 2:17:18 PM">14:17</time>

(langchain) ashwin@ubuntu-server:~/crawl4ai$ ./run_compute.sh
[Info] Using Ollama server at: http://192.168.1.200:11434
[Info] Model name: nomic-embed-text:latest
[Info] Starting to embed missing data in column 'embedding_1536'...
Traceback (most recent call last):
  File "/home/ashwin/crawl4ai/src/compute.py", line 186, in <module>
    asyncio.run(main())
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/ashwin/crawl4ai/src/compute.py", line 164, in main
    batch_embs = await compute_batch_embeddings(chunk_texts)
  File "/home/ashwin/crawl4ai/src/compute.py", line 128, in compute_batch_embeddings
    await asyncio.gather(*tasks)
  File "/home/ashwin/crawl4ai/src/compute.py", line 125, in embed_one
    results[i] = await embed_text_ollama(session, t)
  File "/home/ashwin/crawl4ai/src/compute.py", line 105, in embed_text_ollama
    raise RuntimeError(f"Ollama request failed [{resp.status}]: {body}")
RuntimeError: Ollama request failed [404]: 404 page not found
(langchain) ashwin@ubuntu-server:~/crawl4ai$ 
```#!/usr/bin/env python3
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
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_1536d.yml")

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
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.1.200:11434")

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
<time datetime="2025-02-08T05:18:05.251Z" title="2/8/2025, 2:18:05 PM">14:18</time>

It looks like the Ollama server you’re using returns a `404` on `POST /embeddings`. That typically means your Ollama build **doesn’t** have a dedicated `/embeddings` endpoint, or it’s using a different route altogether.

### How Ollama Embeddings Usually Work

Depending on your Ollama version and configuration, embeddings are often obtained by sending a `POST` request to the **`/api/generate`** endpoint with `"embedding": true`. In that scenario:

- **Route**: `POST /api/generate`
- **Body**: JSON containing `"model"`, `"prompt"`, `"embedding": true`, and possibly other options.
- **Response**: JSON that includes an `"embedding"` field.

Some Ollama builds (especially newer/experimental ones) do have a dedicated `POST /api/embeddings` endpoint. But if you see a 404, you most likely need to use the `generate` endpoint with `"embedding": true` instead.

Below is an **updated** script that uses:

1. **`POST /api/generate`**
2. Passes `"embedding": true` in the JSON body.
3. Checks for `"embedding"` in the returned JSON.

Make sure your Ollama server is running in a way that supports this usage. Also note that certain versions of Ollama may return embeddings as a streaming response. The snippet below requests a **non-stream** response by including `"stream": false`, so you can simply call `resp.json()`.

---

```python
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
CONFIG_PATH = os.getenv("EMBED_CONFIG_PATH", "/home/ashwin/crawl4ai/src/configs/embedding_config_1536d.yml")

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
# e.g.  "http://192.168.1.200:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.1.200:11434")

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
    Given a single text, call the Ollama server to get its embedding
    using the 'nomic-embed-text:latest' model (or whatever is in MODEL_NAME).
    
    This version calls /api/generate with "embedding": true so you don’t get a 404.
    """
    # Ollama's "generate" endpoint, with embedding = true
    url = f"{OLLAMA_BASE_URL}/api/generate"

    # If your Ollama version doesn't need certain fields, remove them.
    # If you want to override them from config, store them in OLLAMA_OPTIONS.
    payload = {
        "model": MODEL_NAME,
        "prompt": text,
        "embedding": True,
        # Typically to get a "clean" embedding we do:
        "temperature": 0,
        "stream": False,         # request a single JSON response
        "top_k": 40,
        "top_p": 1,
        # Merge in any additional Ollama options from config:
        **OLLAMA_OPTIONS
    }

    async with session.post(url, json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Ollama request failed [{resp.status}]: {body}")
        data = await resp.json()

    # For embedding calls, Ollama typically returns something like:
    # { "embedding": [...], "model": "xxx", "created": "...", ...}
    if "embedding" not in data:
        raise RuntimeError("Ollama response did not contain 'embedding' field.")
    
    return data["embedding"]

async def compute_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embeds a batch of texts by calling Ollama for each text (in parallel).
    """
    results: List[List[float]] = [None] * len(texts)

    # We'll limit concurrency to avoid flooding the server
    sem = asyncio.Semaphore(8)

    async with aiohttp.ClientSession() as session:
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
```

---

### Tips & Next Steps

1. **Confirm Your Ollama Version**\
   Make sure you’re running an Ollama version that supports embeddings. If `POST /api/generate` still fails, verify your Ollama server logs or update to a newer release that includes embedding support.

2. **Check Streaming vs Non-Streaming**
   - Some Ollama builds default to streaming responses. We set `"stream": false` in the payload to get a single JSON chunk.
   - If your version doesn’t support `"stream": false`, remove that field and parse the streamed JSON carefully.

3. **Adjust Payload Options**\
   If you find unwanted text generation or timeouts, try setting parameters like `"temperature": 0`, or other penalty/decoding settings, so you only get the embedding.

Using the `generate` endpoint with `"embedding": true` is the key to avoid the `404 page not found` error in Ollama versions that don’t have a separate `/embeddings` route.


#### You:
<time datetime="2025-02-08T05:24:13.687Z" title="2/8/2025, 2:24:13 PM">14:24</time>

asyncpg.exceptions.DataError: expected 1536 dimensions, not 768

#### ChatGPT:
<time datetime="2025-02-08T05:24:27.437Z" title="2/8/2025, 2:24:27 PM">14:24</time>

This error means that your PostgreSQL column is defined as `VECTOR(1536)` while your model is returning embeddings of size 768. In other words, there’s a **dimension mismatch**: the database expects a 1536-dimensional vector, but your model returns a 768-dimensional vector.

To fix the error, you must ensure that **the number of dimensions in your embeddings** and **the PostgreSQL vector column definition** match. You have three main options:

---

## Option 1: Use a Model That Produces 1536-D Vectors

If your database schema is set up for 1536 dimensions and you **want to keep it that way**, you need a model that produces **1536-dimensional embeddings**. For instance:

- **OpenAI’s `text-embedding-ada-002`** returns 1536-dimensional embeddings.
- Some local models also produce 1536-dimensional embeddings, but you have to confirm their specs.

If you are calling Ollama, verify which model you’re running inside Ollama. Most embedding-capable models have a fixed dimensionality.

**Steps**:

1. In your YAML config, set:
   ```yaml
   embedding_model: text-embedding-ada-002
   ```
   (Or another 1536-dim model available via Ollama—be sure to check dimension specs.)

2. On the Ollama side, ensure that model is indeed 1536-dimensional. If it’s returning 768, you’ll get the same error.

3. Run the script again.

---

## Option 2: Change the Postgres Column to 768 Dimensions

If you **want to keep using** the model that yields 768-dim embeddings, then you need to alter your database column to store 768-dimensional vectors.

For example, if the column is `embedding_1536 vector(1536)`, you can run something like:

```sql
ALTER TABLE crawl4ai_chunks
  ALTER COLUMN embedding_1536 TYPE vector(768);
```

(You may also rename the column if desired.) After that, Postgres will accept 768-dimensional embeddings without error.

---

## Option 3: Create a New Column With the Correct Dimension

Sometimes you may want to keep the old 1536 column but also store new 768-d embeddings in a different column. In that case, you can create a **new** column with the correct dimension and update your script to target that column. For instance:

1. In Postgres:
   ```sql
   ALTER TABLE crawl4ai_chunks
   ADD COLUMN embedding_768 vector(768);
   ```
2. In your YAML config (or script), set `embedding_column: embedding_768`.
3. The script will now store 768-dimensional embeddings in `embedding_768`.

---

## Summary

- **Check the embedding dimension** returned by your model (768 vs 1536).
- **Match** that dimension in Postgres (`vector(768)` or `vector(1536)`).
- Adjust either the **model** (to match DB) or the **DB column** (to match the model).

Once both sides align on the same number of embedding dimensions, the error will disappear.
