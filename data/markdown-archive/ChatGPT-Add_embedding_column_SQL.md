---
title: Add embedding column SQL
source: https://chatgpt.com/c/679309b1-7970-8003-97f7-bd5c46f76ec5
---

# Add embedding column SQL

#### You:
<time datetime="2025-01-24T03:32:02.195Z" title="1/24/2025, 12:32:02 PM">12:32</time>

CREATE COLUMN embedding_384 IN TABLE crawl4ai_chunks;

#### ChatGPT:
<time datetime="2025-01-24T03:32:18.813Z" title="1/24/2025, 12:32:18 PM">12:32</time>

Below is an example of how you might add a new column called `embedding_384` to an existing table named `crawl4ai_chunks` so that you can store vector embeddings. I’ll assume you’re using PostgreSQL along with the [pgvector extension](https://github.com/pgvector/pgvector), which supports vector-based columns for storing and querying embeddings.

---

### 1. Make sure the `vector` extension is enabled

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

- This extension provides the `vector` data type, which is ideal for storing fixed-length embeddings.
- If you’re on a managed PostgreSQL service, you may need to ensure your service supports installing extensions or that pgvector is already available.

---

### 2. Add the new column to your table

```sql
ALTER TABLE crawl4ai_chunks
ADD COLUMN embedding_384 vector(384);
```

- Here, `vector(384)` specifies a 384-dimensional vector, which is suitable for storing embeddings from models like BERT or certain GPT embeddings that output a 384-dimensional representation.
- Feel free to adjust the dimensionality if your model outputs embeddings of a different size.

---

### 3. (Optional) Populate your new column

Once the column is created, you can start inserting or updating your embeddings. For example:

```sql
UPDATE crawl4ai_chunks
SET embedding_384 = '[0.123, 0.456, -0.789, ...]'::vector
WHERE id = 1;
```

- This syntax assumes you’ll provide a comma-separated array of floats in brackets, then cast it to the `vector` type.
- You can also set the column during an `INSERT`.

---

### 4. (Optional) Explore vector search

With pgvector installed, you can perform similarity searches using operators like `<->` (Euclidean distance), `<#>` (dot product), or `<=>` (cosine distance). For example:

```sql
SELECT id
FROM crawl4ai_chunks
ORDER BY embedding_384 <-> '[0.111, 0.222, -0.333, ...]'::vector
LIMIT 5;
```

- This query returns the top 5 rows most similar (by Euclidean distance) to the specified vector.
- You can create an **index** on the vector column to speed up similarity searches:

```sql
CREATE INDEX ON crawl4ai_chunks USING ivfflat (embedding_384 vector_l2_ops) WITH (lists = 100);
```

- Adjust the `lists` parameter based on the size of your data and performance needs.

---

### Why store embeddings in a database?

Since you mentioned you’re dealing with AI data pipelines, storing embeddings in a database like PostgreSQL with the pgvector extension can be quite powerful:

1. **Centralized**: You keep both the text (or any associated metadata) and its embeddings in the same system.
2. **Scalable**: PostgreSQL can handle large datasets and can be tuned for fast I/O.
3. **Querying**: You can do standard SQL queries plus vector similarity queries in the same environment.
4. **Security & Compliance**: PostgreSQL gives you a well-established security model and transaction guarantees.

---

### Key Concepts to Expand Your Knowledge

- **Embeddings**: Numerical representations of data (text, images, etc.) so that semantic similarity can be computed.
- **Vector Search**: Performing approximate or exact nearest-neighbor searches in a vector space to find similar items (like related chunks of text).
- **Dimensionality**: Many modern language model embeddings range from 384 dimensions (like some MiniLM models) up to 1536 or even 4096 for larger GPT-based embeddings.
- **Indexing**: Using methods like `ivfflat` or `hnsw` for efficient similarity search over millions (or billions) of vectors.

---

**Putting it all together**, the minimal SQL to create your new column is:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE crawl4ai_chunks
ADD COLUMN embedding_384 vector(384);
```

From there, you can start inserting your 384-dimensional embeddings and leverage vector-based queries. This approach integrates nicely into AI-driven pipelines where you might want to store, retrieve, and search large volumes of text with semantic similarity.


#### You:
<time datetime="2025-01-24T03:35:03.237Z" title="1/24/2025, 12:35:03 PM">12:35</time>

this is what's set up in the database today. what needs to be added?

idx_chunks_embedding	IVFFLAT	false	embedding	"(lists='1000')"	"(lists='1000')"	NULL
crawl4ai_chunks_pkey	BTREE	true	id			NULL

#### ChatGPT:
<time datetime="2025-01-24T03:35:20.328Z" title="1/24/2025, 12:35:20 PM">12:35</time>

It looks like you already have:

1. A primary key index on `id` (using BTREE).
2. An IVFFLAT index (`idx_chunks_embedding`) on some existing column named `embedding` with `lists='1000'`.

If your goal is to store 384-dimensional embeddings *in addition* to whatever is currently in the `embedding` column, then you need:

1. A new `vector(384)` column — for example, `embedding_384`.
2. (Optionally) an IVFFLAT index on that new column, similar to your existing `idx_chunks_embedding`.

Below are the SQL statements you would typically run:

```sql
-- 1. Create the new column if you haven't already
ALTER TABLE crawl4ai_chunks
ADD COLUMN embedding_384 vector(384);

-- 2. (Optional) Create an IVFFLAT index on the new column
CREATE INDEX idx_chunks_embedding_384
  ON crawl4ai_chunks
  USING ivfflat (embedding_384 vector_l2_ops) 
  WITH (lists = 1000);
```

### Why Add `embedding_384`?

- If your embedding model now outputs 384 dimensions (e.g., switching from a 768-d model to a 384-d model), you’ll want a column that matches the new dimensionality.
- Keeping the old `embedding` column and the new `embedding_384` side by side lets you test or transition gradually without losing data from the old pipeline.

### Recap of Steps

1. **Enable the `vector` extension** (if you haven't done so yet):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. **Add the column** to store your 384-dimensional embeddings:
   ```sql
   ALTER TABLE crawl4ai_chunks
   ADD COLUMN embedding_384 vector(384);
   ```
3. **(Optional) Index the new column** for fast similarity search:
   ```sql
   CREATE INDEX idx_chunks_embedding_384
     ON crawl4ai_chunks
     USING ivfflat (embedding_384 vector_l2_ops) 
     WITH (lists = 1000);
   ```
4. **Populate** the `embedding_384` column via `UPDATE` or on `INSERT` as you generate new embeddings.

That’s all you need to add to support storing and querying 384-dimensional embeddings alongside your existing `embedding` column and index.


#### You:
<time datetime="2025-01-24T03:37:39.679Z" title="1/24/2025, 12:37:39 PM">12:37</time>

CREATE INDEX idx_chunks_embedding_4096
  ON crawl4ai_chunks
  USING ivfflat (embedding_4096 vector_l2_ops) 
  WITH (lists = 1000);

Query 1 ERROR at Line 1: : ERROR:  column cannot have more than 2000 dimensions for ivfflat index

#### ChatGPT:
<time datetime="2025-01-24T03:38:04.684Z" title="1/24/2025, 12:38:04 PM">12:38</time>

It looks like your version (or build) of the pgvector extension enforces a maximum dimension of 2000 when creating an IVFFLAT index. Hence, you’re getting the error:

> `ERROR: column cannot have more than 2000 dimensions for ivfflat index`

### Why the limitation?

By default, pgvector sets a hard-coded limit on the vector dimension when creating IVFFLAT indexes—often 1024 or 2000 depending on the version. Any attempt to index a column that exceeds this limit will fail.

### Options to handle 4096-dim embeddings

1. **Reduce dimensionality**
   - **Dimensionality Reduction**: You can apply PCA, random projection, or other techniques (e.g. [UMAP](https://umap-learn.readthedocs.io/), [Faiss’s random projection or PCA](https://github.com/facebookresearch/faiss)) to compress from 4096 down to, say, 768 or 1024. This is a common approach when dealing with high-dimensional embeddings, especially if you want to do real-time similarity search.
   - **Use a Smaller Embedding Model**: If you have the flexibility to use a different model that outputs fewer dimensions (for example, 1536-d or 768-d embeddings from OpenAI or Hugging Face), you can avoid exceeding the pgvector limit.

2. **Split your embedding across multiple columns**
   - If you really need to store all 4096 dimensions, you could break them into two separate columns, each <= 2000 dimensions. This is somewhat cumbersome because you’d then have to run two separate vector searches (or build your own logic to handle them). Not the nicest approach, but a workaround.

3. **Recompile pgvector with a higher limit**
   - If you have full control over your environment and can install from source, you can increase the maximum dimension in the pgvector source and recompile. In pgvector’s [`extension.c`](https://github.com/pgvector/pgvector/blob/main/extension.c) (or a similarly named file), there is a constant that sets the max dimension. You can increase it to 4096, rebuild, and reinstall.
   - Keep in mind that very high dimensional indexes can use more memory and slow down queries or indexing. Make sure to test performance carefully.

4. **Don’t index your embedding (store only)**
   - You could store the 4096-dim vector in a `vector(4096)` column without creating an IVFFLAT index. Then you could do a brute-force similarity search (`ORDER BY embedding_4096 <-> '...'::vector`) in smaller datasets. However, this is not scalable for large data because the queries will be slow without an index.

5. **Use a specialized Vector Database**
   - If your workflow heavily relies on high-dimensional vectors (4096+), you might consider a dedicated vector database (e.g. Pinecone, Milvus, Weaviate, or Qdrant). You can still store metadata in PostgreSQL and keep the vector data in a separate system optimized for large vector dimensions.

### Most common solution in practice

Because 4096 is quite large for typical vector similarity indexes, many teams choose to:

1. **Use a smaller embedding** or
2. **Apply PCA to reduce from 4096 to a more manageable size (like 768 or 1024)**

PCA can preserve most of the variance in the data while drastically cutting down dimensionality, leading to smaller indexes and faster queries.

---

#### Example Workflow for PCA Reduction

1. **Extract your 4096-d embeddings** from your model.
2. **Train a PCA model** (e.g., [scikit-learn PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)) on a representative sample.
3. **Choose a target dimension** (768, 1024, or even 1536) that fits your hardware and performance constraints.
4. **Transform all embeddings** with PCA before saving them into `embedding_768` or `embedding_1024` in PostgreSQL.
5. **Create an IVFFLAT index** on that reduced vector column.

---

### Summary

- You’re hitting a dimension limit in pgvector’s IVFFLAT index (2000).
- To proceed with 4096-dimensional vectors, either **reduce** their dimensionality, **split** them, **recompile** pgvector, or move to a specialized vector search engine.

Among these, **dimensionality reduction** is the path most often taken in production scenarios where you want to keep using PostgreSQL + pgvector for vector search. If you truly need all 4096 dimensions, then recompiling or switching to a dedicated vector DB might be better.


#### You:
<time datetime="2025-01-24T03:42:36.322Z" title="1/24/2025, 12:42:36 PM">12:42</time>

model_name: "sentence-transformers/all-mpnet-base-v2"
embedding_column: "embedding_768"

ollama_options:
  temperature: 0.7
  repeat_penalty: 1.2


ashwin@ubuntu-server:~/crawl4ai$ ./run_compute.sh 
[Info] Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
[Info] Starting to embed missing data in column 'embedding_768'...
Traceback (most recent call last):
  File "/home/ashwin/crawl4ai/src/compute.py", line 156, in <module>
    asyncio.run(main())
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/asyncio/runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/asyncio/base_events.py", line 649, in run_until_complete
    return future.result()
  File "/home/ashwin/crawl4ai/src/compute.py", line 145, in main
    await asyncio.gather(*tasks)
  File "/home/ashwin/crawl4ai/src/compute.py", line 82, in update_chunk_embedding
    await conn.execute(query, vector_str, chunk_id)
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/site-packages/asyncpg/connection.py", line 352, in execute
    _, status, _ = await self._execute(
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/site-packages/asyncpg/connection.py", line 1864, in _execute
    result, _ = await self.__execute(
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/site-packages/asyncpg/connection.py", line 1961, in __execute
    result, stmt = await self._do_execute(
  File "/home/ashwin/miniconda3/envs/crawl4ai/lib/python3.10/site-packages/asyncpg/connection.py", line 2024, in _do_execute
    result = await executor(stmt, None)
  File "asyncpg/protocol/protocol.pyx", line 206, in bind_execute
asyncpg.exceptions.DataError: expected 768 dimensions, not 384
ashwin@ubuntu-server:~/crawl4ai$ 


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
<time datetime="2025-01-24T03:43:00.436Z" title="1/24/2025, 12:43:00 PM">12:43</time>

The root cause is that the model you’re loading (`all-MiniLM-L6-v2`) produces **384-dimensional** embeddings, but your database column (`embedding_768`) is declared as `vector(768)`. PostgreSQL (via pgvector) is expecting 768 floating-point values, yet you’re only passing in 384.

Hence the error:

```
asyncpg.exceptions.DataError: expected 768 dimensions, not 384
```

---

## Why This Happens

1. **Mismatch between config key and code**

   - Your code uses `config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")`.
   - Your config file (posted snippet) uses a key named `model_name: "sentence-transformers/all-mpnet-base-v2"`.

   Because the code looks for `embedding_model` (not `model_name`), it falls back to `"sentence-transformers/all-MiniLM-L6-v2"`—a 384-dim model.

2. **Database column is `vector(768)`**
   - The column name is `embedding_768`, implying `vector(768)`.
   - If you feed it a model outputting 384 dims, the query fails.

---

## How to Fix It

### Option 1: Actually use a 768-dimensional model

If you **want** a 768-dimensional embedding column:

1. **Change your YAML key** from:
   ```yaml
   model_name: "sentence-transformers/all-mpnet-base-v2"
   ```
   to
   ```yaml
   embedding_model: "sentence-transformers/all-mpnet-base-v2"
   ```
2. Ensure your code picks up `"sentence-transformers/all-mpnet-base-v2"`:
   ```python
   MODEL_NAME = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
   # ...
   embedding_model = SentenceTransformer(MODEL_NAME)
   ```
3. Confirm in logs that it’s loading the correct model:
   ```
   [Info] Loading embedding model: sentence-transformers/all-mpnet-base-v2
   ```
4. Now you’ll get 768 values and can insert them into `embedding_768`.

> *Note:* `all-mpnet-base-v2` is known to produce 768-d embeddings, which will match a `vector(768)` column perfectly.

### Option 2: Switch your column to 384 dimensions

If you **want** to keep using `"all-MiniLM-L6-v2"` (384-dim model):

1. **Make sure your code references the correct YAML key** (as above), or just rely on the default.
2. **Drop or rename your existing column** if it’s not yet in use, then create a new 384-dim column:
   ```sql
   ALTER TABLE crawl4ai_chunks
   ADD COLUMN embedding_384 vector(384);
   ```
3. Update the config:
   ```yaml
   embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
   embedding_column: "embedding_384"
   ```
4. Update your code references to read from that new column.

> Then the code will store 384 values into `embedding_384 vector(384)`—no dimension mismatch.

---

## In Summary

1. **Check which model you actually want**.
2. **Match the column dimension** (`vector(768)` or `vector(384)`) to the model output dimension.
3. **Align** the YAML key used for the model name (`embedding_model` vs. `model_name`) with what the code expects.

Once the model output and database column dimension line up, the error will disappear.
