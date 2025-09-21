---
title: Token-Based Chunking Implementation
source: https://chatgpt.com/c/67b0b0e4-2630-8003-bade-ad750ab61d8c
---

# Token-Based Chunking Implementation

#### You:
<time datetime="2025-02-15T15:21:08.240Z" title="2/16/2025, 12:21:08 AM">00:21</time>

Use Token-Based Chunking (Instead of Raw Character Counts)

    Current Approach: You’re splitting text by ~800 characters (target_size=800) and allowing overlap of 2 sentences.
    Potential Issue: LLMs work in tokens, and a chunk measured only by characters may not map nicely to the embedding model’s token limit. A chunk that is 800 characters of mostly short words might be well under 512 tokens, while 800 characters of dense code or text might exceed 512 tokens.
    Improvement: Use a token-based approach (e.g., use the tiktoken library if you’re embedding with OpenAI or a compatible tokenizer) or at least approximate tokens using word_tokenize more rigorously. For instance:

# Pseudocode
MAX_TOKENS = 512
# chunk by tokens rather than len(sentence)

This ensures each chunk is within your embedding model’s maximum comfortable size (and it also avoids splitting a single chunk into pieces that are too large for certain LLM contexts).

what questions do you have for me before implementing this change?
----
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
      - Code blocks (

...

) become single chunks.
      - Normal text is split by sentences, respecting a target size.
    """
    segments = re.split(r"

(.*?)

", text, flags=re.DOTALL)

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

#### ChatGPT:
<time datetime="2025-02-15T15:21:17.714Z" title="2/16/2025, 12:21:17 AM">00:21</time>

Here are a few questions and clarifications I’d want to confirm before implementing a token-based approach:

1. **Which Tokenizer Are We Using?**
   - Will we be using [OpenAI’s `tiktoken`](https://github.com/openai/tiktoken) (which is often recommended for GPT-based embeddings) or a different tokenizer?
   - If we’re strictly on Python’s `nltk` right now, do we want to pull in the `tiktoken` dependency or do you prefer an approximate token calculation using `word_tokenize` (or some other library like `spacy`)?

2. **Embeddings Model & Token Limit**
   - Which model do you plan to use for embeddings? For instance, if you plan to use `text-embedding-ada-002` from OpenAI, the recommended chunk size might be up to 512 tokens or 800 tokens. Different embedding models have different maximum context lengths.
   - Knowing the maximum safe token limit is important so we can pick a conservative `MAX_TOKENS` threshold (e.g., 512 tokens or 768 tokens).

3. **Overlap in Terms of Tokens**
   - Currently, there’s a sentence overlap of 2. When moving to a token-based approach, do we still want to maintain an overlap in terms of entire sentences, or do we want an overlap in terms of tokens (e.g., always keep the last 20–30 tokens from one chunk in the next)?
   - If sentences are very short or very long, token-based overlap may behave differently than the current “2-sentence” overlap. Do you prefer to preserve the existing “2-sentence overlap,” or adapt to a consistent “N tokens overlap”?

4. **Handling Code Blocks**
   - We currently treat code blocks as single, atomic chunks. Should we consider splitting large code blocks if they exceed the `MAX_TOKENS` limit? Or do we want to keep them whole (risking that some code blocks may exceed the token limit and thus cause issues in the embedding request)?

5. **Edge Cases**
   - Some pages might have extremely long paragraphs or single sentences that could exceed the `MAX_TOKENS` threshold (especially if you have user-generated or unstructured text). Do we want to forcibly split those (even if it breaks in the middle of a sentence/code block)?
   - How do we handle short documents that are far below the token limit? It may not be a big deal, but just clarifying the approach.

6. **Performance Considerations**
   - Are there any performance constraints or concurrency limits we should keep in mind when adding token-based splitting (like the cost of tokenizing each sentence or chunk)?
   - If using `tiktoken`, are we comfortable making it an optional or a required library dependency?

7. **Documentation and Logging**
   - Would you like verbose logging on how many tokens each chunk has?
   - Any need to store the token count in the database (similar to how we store word\_count) so we can later filter by token size or check how large a chunk is?

8. **Migration vs. Fresh Table**
   - If we’re inserting new rows in `crawl4ai_chunks`, is it okay if we end up with different chunk boundaries or different chunk counts for the same documents after switching from character-based to token-based?
   - Or do we want to do a wholesale cleanup of the existing rows and regenerate everything from scratch?

These details will help shape the final approach and ensure the new token-based chunking integrates smoothly with your existing pipeline, especially regarding model constraints, performance, and data consistency. Let me know your preferences, and I can proceed accordingly!


#### You:
<time datetime="2025-02-15T15:22:32.063Z" title="2/16/2025, 12:22:32 AM">00:22</time>

i also want to make the following updates. maybe we should review all of the goals first, and then think of the questions to clarify:
```
1. Use Token-Based Chunking (Instead of Raw Character Counts)

    Current Approach: You’re splitting text by ~800 characters (target_size=800) and allowing overlap of 2 sentences.
    Potential Issue: LLMs work in tokens, and a chunk measured only by characters may not map nicely to the embedding model’s token limit. A chunk that is 800 characters of mostly short words might be well under 512 tokens, while 800 characters of dense code or text might exceed 512 tokens.
    Improvement: Use a token-based approach (e.g., use the tiktoken library if you’re embedding with OpenAI or a compatible tokenizer) or at least approximate tokens using word_tokenize more rigorously. For instance:

    # Pseudocode
    MAX_TOKENS = 512
    # chunk by tokens rather than len(sentence)

    This ensures each chunk is within your embedding model’s maximum comfortable size (and it also avoids splitting a single chunk into pieces that are too large for certain LLM contexts).

2. Preserve Headings and Section Titles in Metadata

    Why: If your text has section headers (like ## Title in Markdown), you can store these headers in chunk metadata. RAG models often leverage headings to figure out the chunk’s topic.
    How:
        As you parse the markdown, keep track of the most recent heading (e.g., #, ##, ###).
        Store that heading (or a small path of headings) in the chunk’s metadata.
        Insert that metadata into your DB’s columns (like chunk_title or a dedicated JSON field).

That way, when your RAG pipeline retrieves the chunk, the LLM sees not only the chunk text but also an identifying heading or title.
3. Consider Splitting Large Code Blocks Too

    Current Approach: You treat each entire code block (```...```) as a single chunk.
    Potential Problem: If the code block is extremely large (e.g., hundreds of lines of code), it might exceed your chunk size (or token limit) and degrade retrieval.
    Improvement:
        If a code block is bigger than, say, ~500 tokens, you can split that code block into multiple smaller blocks (with or without overlap).
        Alternatively, keep your code-block-lumps but set an upper limit.

This prevents the scenario where a single huge code chunk is truncated or becomes unwieldy in embeddings or at retrieval time.
4. Store Additional Context in the Chunk Metadata

You’re already capturing page_id, page_url, content, chunk_size, and word_count. Consider adding:

    parent_heading or section_title (if applicable).
    created_at, modified_at timestamps if relevant.
    summaries or a short “gist” of the chunk if you have the ability to generate them (though that can be an additional cost).

Having more metadata helps you filter or rank chunks better during retrieval and can give the LLM better context.
5. Adjust Overlap Dynamically

    Current Approach: You overlap 2 sentences (sentence_overlap=2) between consecutive chunks.
    Potential Refinement: Use a dynamic overlap that depends on average sentence length or total chunk length. For instance, if a chunk has 5 short sentences, you might overlap 1 or 2. If it has long sentences, you might overlap more to maintain continuity.
    Why: This can help the model see continuity across chunks if the text is very narrative or flows across paragraphs. Of course, you don’t want so much overlap that it wastes tokens and leads to repeated information in multiple chunks. A typical rule-of-thumb is 10–15% overlap by tokens.

6. Summaries (Optional)

One advanced approach is to generate a short summary of each chunk (e.g., a sentence or two) and store it in the database as chunk_summary. Then, at retrieval time, the LLM sees both the chunk text and the short summary. This can help the LLM quickly determine if the chunk is relevant. Summaries are especially helpful if your text is very verbose.

    But do note, generating high-quality summaries for each chunk can be expensive if you have thousands of pages. You might do it offline once or set up a pipeline that only generates summaries for top chunks.

7. Clean Markdown Artifacts More Thoroughly

You do some cleaning with unify_triple_quotes, but real Markdown often has headings, bullet points, code blocks, etc. Depending on your data, you might:

    Remove or transform raw Markdown links ([text](url)) into a more plain-text form.
    Standardize bullet points and newlines.
    Remove HTML tags if any remain.

A more thorough pass ensures your final chunks read smoothly for the LLM at retrieval time.
8. Add Logging or Stats to Evaluate Chunk Quality

After chunking, it can be helpful to log or measure:

    Average chunk size (characters / tokens).
    Number of chunks that are primarily code vs. text.
    Max chunk size or if any chunk is suspiciously large (like 5000 chars).

This data helps you fine-tune your parameters (target_size, sentence_overlap, etc.).
9. Parallel or Batch Insert (Performance Optimization)

You already use asyncio.gather to insert chunks concurrently. That’s good. If your dataset is extremely large, consider batch inserts or certain pooling strategies so you don’t overwhelm the database. But for moderate volume, your approach should be fine.
10. Check for Repetitive or Duplicate Chunks

Depending on your source material, you could occasionally end up with repeated text (like repeated disclaimers or boilerplate). You might:

    De-duplicate exact text chunks in your DB.
    Or store them but mark them as “boilerplate” to be either filtered out or lower-ranked in retrieval.

#### ChatGPT:
<time datetime="2025-02-15T15:23:13.571Z" title="2/16/2025, 12:23:13 AM">00:23</time>

Below is a consolidated view of your **10 goals**, along with some high-level commentary and the **key questions**/clarifications we should sort out before we start coding. Once we get clarity on these points, we can outline a concrete plan to implement the changes.

---

## 1. Use Token-Based Chunking (Instead of Raw Character Counts)

**Goal:**

- Move away from `target_size=800` **characters** to a token-based approach, e.g., `MAX_TOKENS=512` (or whatever limit is appropriate).

**Key Points to Clarify:**

1. **Tokenizer Choice**
   - Will we use [OpenAI’s `tiktoken`](https://github.com/openai/tiktoken) (ideal for GPT-based embeddings) or remain with `nltk` approximations (`word_tokenize`)?
   - If we use `tiktoken`, are we okay introducing it as a new dependency?

2. **Exact Max Token Threshold**
   - Which embedding model are you using? For `text-embedding-ada-002`, 512–800 tokens per chunk might be typical.
   - Do you have a preferred exact token limit (512, 768, 1000, etc.)?

3. **Overlap**
   - Currently you overlap 2 sentences. Do you prefer to keep the overlap in terms of sentences (e.g., still 2 sentences), or switch to a token-based overlap (e.g., the last 30 tokens)?

4. **Handling Edge Cases**
   - What if a single sentence (or code block) itself exceeds the max token limit? Should we split within that sentence/code block or skip it?

---

## 2. Preserve Headings and Section Titles in Metadata

**Goal:**

- Keep track of the nearest heading (e.g., `#`, `##`, `###`) to provide better context in retrieval.

**Key Points to Clarify:**

1. **Method of Extraction**
   - Use a simple regex for Markdown headings (`^(#{1,6})\s+(.*)`) or use a library like `markdown-it`/`mistune` to parse more robustly?
2. **Storage**
   - Where in the DB do we store this heading info?
     - A new column like `chunk_heading`?
     - A JSON/BLOB column that can store hierarchical headings (in case of nested sections)?
3. **Updates to Existing Table**
   - Are we okay altering `crawl4ai_chunks` to add a `heading` column, or do we want to store it in an existing column like `title`?

---

## 3. Consider Splitting Large Code Blocks

**Goal:**

- Avoid having a single chunk that’s an entire huge code block if it exceeds your token limit (because that chunk becomes too large to embed or retrieve effectively).

**Key Points to Clarify:**

1. **Threshold**
   - Is 500 tokens per chunk okay for code blocks, or do you want to align it with the same limit as text (e.g., 512 tokens or your chosen max)?
2. **Overlap in Code**
   - Do you need an overlap for code chunks (e.g., to keep context for large code segments)? Or just straightforward splits?
3. **Preservation of Fences**
   - When splitting, do you want to keep \`\`\` fences around each sub-chunk, or do you just store the raw code text?

---

## 4. Store Additional Context in the Chunk Metadata

**Goal:**

- Include more fields in the `crawl4ai_chunks` table (e.g., `parent_heading`, `created_at`, `modified_at`, short summaries, etc.).

**Key Points to Clarify:**

1. **Which Fields?**
   - Exactly which new metadata fields do we want to add? (e.g. `heading`, `created_at`, `modified_at`, `source_type`, etc.)
2. **Schema Changes**
   - Are we creating new columns or a JSON column (e.g. `metadata`) to store this extra context in a flexible way?

---

## 5. Adjust Overlap Dynamically

**Goal:**

- Instead of a fixed overlap (2 sentences), use a dynamic approach (like 10%–15% token overlap).

**Key Points to Clarify:**

1. **Overlap Strategy**
   - Overlap by fraction of tokens?
   - Overlap by fraction of sentences?
   - Overlap by a fixed number of tokens?
2. **Implementation Complexity vs. Benefit**
   - A dynamic overlap can be more complex. Are we okay with the added logic (and possibly more chunking time)?

---

## 6. Summaries (Optional)

**Goal:**

- Generate a short summary (or gist) of each chunk and store it, so the LLM can quickly see if the chunk is relevant.

**Key Points to Clarify:**

1. **When to Summarize**
   - Do you want to do this offline (e.g., a separate script that runs after chunking), or inline during the chunking pipeline?
   - Summaries can be costly if you have a huge dataset.
2. **Model & Format**
   - Which model or method do we use to generate summaries? (E.g., GPT-3.5 or GPT-4, or a local model?)
3. **Storage**
   - Will we add a new column `chunk_summary` or store it in a JSON metadata field?

---

## 7. Clean Markdown Artifacts More Thoroughly

**Goal:**

- Improve the text cleanliness by removing or transforming:
  - Markdown links: `[text](url)`
  - Extra HTML tags
  - Bullet points or other formatting issues

**Key Points to Clarify:**

1. **Preferred Format**
   - Should `[text](url)` become just `text (url)` or just `text`?
   - Do we want to keep bullet points or convert them into e.g., `- bullet text` for clarity?
2. **HTML Sanitization**
   - Should we strip all HTML tags or convert them to something else (like newlines)?
3. **Regex vs. Markdown Parser**
   - Are we okay with a straightforward regex approach or do we want a more robust parse?

---

## 8. Add Logging or Stats to Evaluate Chunk Quality

**Goal:**

- Log or store stats about the chunking process (average chunk size, maximum chunk size, etc.) so we can refine parameters over time.

**Key Points to Clarify:**

1. **Which Stats to Capture?**
   - Average tokens per chunk, distribution (min/max), total code vs. text chunks, etc.
2. **Storage / Logging**
   - Just print logs to console, or store in a table/CSV for future analysis?
3. **Frequency**
   - Do we want real-time logging after each page is processed, or a final summary at the end?

---

## 9. Parallel or Batch Insert (Performance Optimization)

**Goal:**

- Potentially group inserts into batches if there are performance issues with large datasets.

**Key Points to Clarify:**

1. **Expected Data Volume**
   - Are we talking about tens of thousands of chunks or millions? This affects whether we truly need more sophisticated batching.
2. **Database Constraints**
   - Does Postgres have any constraints on batch insert sizes we should be mindful of?
3. **Priority**
   - Is this more of a “nice to have” if we see performance issues, or do we want it from the start?

---

## 10. Check for Repetitive or Duplicate Chunks

**Goal:**

- Avoid storing large blocks of repeated disclaimers or identical text over and over, or at least label them so we can filter them out.

**Key Points to Clarify:**

1. **Approach**
   - Do we want to *not store duplicates at all* (i.e., skip them), or store them but mark them?
2. **How to Detect Duplicates**
   - Compare chunk text hash? Compare partial text?
   - Some text might be almost the same but not identical (e.g., “© 2023” vs. “© 2024”).
3. **Storage & Retrieval**
   - If duplicates are stored, do we handle them specially at retrieval (like assigning them a lower rank)?

---

### Additional Overarching Questions

- **Migration vs. Fresh Table**
  - Are we planning to regenerate *all* chunks from scratch with the new approach, or do we want a migration strategy that modifies only the chunking logic going forward?

- **Data Consistency / Re-Chunking**
  - If we re-chunk existing documents, we’ll end up with *different* chunk boundaries. That means old embeddings might mismatch. Do we need to re-embed everything, or can we keep old embeddings for old chunks?

- **Time Constraints / Priorities**
  - Which of these goals (1 through 10) are the most pressing? Do you want them all in one big refactor, or do we roll them out step by step?

---

## Next Steps

1. **Confirm Priorities**
   - Which of the 10 items do you consider “must-have” vs. “nice-to-have” in the short term?

2. **Answer Key Clarifications**
   - For each relevant item above, let’s finalize approach (e.g., “Use `tiktoken` at 512 tokens,” “store heading in `chunk_heading` column,” etc.).

3. **Create an Implementation Plan**
   - Based on the clarifications, we’ll propose a phased or all-in-one approach.
   - Possibly do a smaller prototype (e.g., token-based chunking with heading extraction) before adding advanced features (dynamic overlap, chunk summaries, etc.).

4. **Code & Test**
   - Implement in a branch, test on a small dataset, confirm correctness, then scale up.

Let me know your thoughts on these questions and how you’d like to proceed with prioritizing and tackling each of the 10 goals!


#### You:
<time datetime="2025-02-15T15:26:26.393Z" title="2/16/2025, 12:26:26 AM">00:26</time>

Below is a **high-level plan** you can use to proceed with these 10 goals. The plan assumes you want to tackle them incrementally, rather than attempting all changes in one pass. For each item, I’ve consolidated the key questions into specific next steps. Once you confirm each step’s details, you can move on to implementation. 

---

# High-Level Plan for the 10 Goals

## 1. Use Token-Based Chunking

### Key Decisions
1. **Tokenizer**: Decide whether to use:
   - `tiktoken` (common for GPT-based embeddings), or
   - Another library (such as a local tokenizer matching your embedding model).

2. **Max Token Threshold**: Pick a default. For example:
   - `MAX_TOKENS = 512`, or some other limit based on your embedding model.

3. **Overlap**: Decide if overlap is still in *sentences* or now in *tokens* (e.g., 10–15% overlap).

4. **Handling Large Single Sentences**: If a single sentence/code block is bigger than your token limit, how do you handle partial splits?

### Next Steps
- **Add the tokenizer** (e.g., `pip install tiktoken`), or verify the approach if using another library.  
- **Implement** a new function `chunk_by_tokens()` that measures token length instead of character length.  
- **Replace** or augment the existing `chunk_by_sentence_overlap` logic if you want token-based overlap.  

---

## 2. Preserve Headings & Section Titles

### Key Decisions
1. **Extraction Method**: Simple regex or a markdown parser library (like `mistune`, `markdown-it-py`, etc.).  
2. **Storage**: 
   - New column `chunk_heading` in `crawl4ai_chunks`, or 
   - A JSON metadata column, e.g. `metadata->>'heading'`.  
3. **Location**: How do you attach headings to text? 
   - Keep track of the last heading seen while traversing the document, store it in each chunk that falls under that heading.

### Next Steps
- **Parse headings** from your `cleaned_markdown` before chunking.  
- **Track** the heading as you chunk the text, assigning the nearest heading to each chunk.  
- **Store** the heading in the new/existing column or metadata JSON.

---

## 3. Splitting Large Code Blocks

### Key Decisions
1. **Split Threshold**: Use the same max tokens as text, or a different threshold for code?  
2. **Code Overlap**: Do you need overlap for code blocks, or just a direct chop?  
3. **Fences**: Keep triple backticks in each sub-chunk or strip them?

### Next Steps
- **Update** your `chunk_text_with_code_blocks` to detect when a code block is too large in tokens, and then split it into multiple sub-chunks accordingly.  
- **Decide** on overlap for code or no overlap.  

---

## 4. Store Additional Context (Metadata)

### Key Decisions
1. **Which Fields?**: (heading, created_at, etc.)  
2. **Schema Changes**: 
   - Create additional columns in `crawl4ai_chunks`, or 
   - Migrate to a single `metadata JSONB` column for flexible storage.  

### Next Steps
- **Modify** your table schema if needed (e.g., `ALTER TABLE crawl4ai_chunks ADD COLUMN heading text;`).  
- **In your chunk insertion** code, populate these new fields with the relevant data.  

---

## 5. Adjust Overlap Dynamically

### Key Decisions
1. **Overlap Metric**: 
   - A fraction of chunk size (e.g., 10–15% of tokens)? 
   - A fixed number of tokens? 
2. **Implementation**:
   - More complex than a fixed overlap—worth it?

### Next Steps
- **Implement** a function that, once a chunk hits `MAX_TOKENS`, adds a partial overlap back into the next chunk.  
- **Tune** the overlap ratio to see if it improves retrieval performance.  

---

## 6. Chunk Summaries (Optional)

### Key Decisions
1. **Summarization Model**: e.g., GPT-3.5 or GPT-4.  
2. **Workflow**: Summarize inline during chunking or in a separate pass after chunk insertion?  
3. **Cost/Time**: Are you comfortable with the token costs for large datasets?

### Next Steps
- **Prototype** a separate summarization step for each chunk (might be an offline or separate script).  
- **Add** a `chunk_summary` column or store in `metadata`.  

---

## 7. Thorough Markdown Cleaning

### Key Decisions
1. **Approach**: 
   - Simple regex replacements for `[link](url)`, bullet points, etc.  
   - Or parse with a markdown library for deeper transformations.  
2. **HTML Handling**: Are HTML tags present? If so, how to handle them?

### Next Steps
- **Extend** your existing cleaning step in `chunk_text_with_code_blocks` to handle additional transformations (links, bullet points, HTML).  
- **Test** on real data to ensure formatting is sensible for the LLM.

---

## 8. Logging or Stats on Chunk Quality

### Key Decisions
1. **Which Stats**: e.g., average tokens per chunk, distribution of chunk sizes, number of code vs. text chunks, etc.  
2. **Storage**: Print logs or store in DB?

### Next Steps
- **Add** a stats collector in your chunking script that logs the final distribution of chunk sizes.  
- Possibly **print** or store these stats after processing each page.

---

## 9. Parallel/Batch Inserts (Performance)

### Key Decisions
1. **Data Volume**: Are you dealing with tens of thousands or millions of chunks?  
2. **Implementation**: 
   - Use Postgres COPY or batch inserts? 
   - Already using `asyncio.gather`; might be sufficient for moderate scale.

### Next Steps
- **Evaluate** performance with your typical dataset size. If the concurrency is insufficient, consider batching or using `copy_expert` in psycopg or a similar approach with `asyncpg`.

---

## 10. De-Duplicate or Label Repetitive Chunks

### Key Decisions
1. **Strategy**: 
   - Skip duplicates entirely or store them but label them?  
   - Full text hash or partial similarity check? 
2. **Storage**: 
   - Mark duplicates in a boolean column `is_duplicate` or store a `hash` and check collisions?

### Next Steps
- **Implement** a check before insertion: 
  - Calculate hash of chunk text (e.g., `SHA-256`), 
  - Query if that hash exists. 
  - Skip insertion or mark it as duplicate.  

---

# Overarching Questions & Recommendations

1. **Migration vs. Fresh Table**  
   - If you plan to re-chunk and re-embed everything, a fresh start may be simpler. You can build a new table (`crawl4ai_chunks_v2`), chunk all pages with new logic, then rename tables.  

2. **Data Consistency**  
   - If you change chunk boundaries, you’ll need to re-embed your new chunks. Otherwise, the old embeddings won’t align with the new chunk text.

3. **Phased Implementation**  
   - A typical approach is to do **token-based chunking + heading extraction** first (goals #1 and #2). Then see if you also need advanced features like code splitting (#3), dynamic overlap (#5), or summarization (#6).

4. **Time & Cost**  
   - Summaries (#6) can be done offline if cost is a concern. De-duplication (#10) might be helpful if you have a lot of repeated boilerplate.

---

# Proposed Workflow

1. **Answer the Clarifications**  
   - For each item, decide on the final approach (token limit, overlap style, heading storage, etc.).  

2. **Implement Core**  
   - Switch chunking to token-based (#1).  
   - Extract headings (#2) and store them in a new column or metadata JSON.  
   - (Optionally) handle large code blocks (#3).  
   - (Optional) Enhance your markdown cleaning (#7).  

3. **Test & Validate**  
   - Run on a subset of your data.  
   - Check logs/stats (#8) to see average chunk size, code vs. text breakdown, and confirm correctness.  

4. **Expand**  
   - If chunking performance is slow, implement batch inserts (#9).  
   - If you see lots of duplicates, add a duplicate-check step (#10).  
   - If you want advanced dynamic overlap (#5), integrate it.  

5. **(Optional) Summaries**  
   - If you need chunk summaries (#6), do it in a separate pass or inline. Decide on the model, cost, and approach.

6. **Re-Embed**  
   - Once you finalize chunk boundaries, re-embed the new chunks so your RAG system is consistent.

---

## Conclusion

That’s the overall plan to evolve your chunking approach and data pipeline:

1. **Nail down** the specifics (token limit, heading extraction, code splitting, metadata structure).  
2. **Implement** and test each feature in small steps.  
3. **Refine** based on actual results and performance.  

Feel free to pick and choose which tasks are critical to your immediate needs and which can wait. Good luck with the refactoring, and let me know if you have any further questions about these next steps!

#### ChatGPT:
<time datetime="2025-02-15T15:26:56.154Z" title="2/16/2025, 12:26:56 AM">00:26</time>

Below is a **high-level plan** you can use to proceed with implementing the 10 goals you listed. This plan assumes an **incremental approach**, so you can tackle them step by step, rather than attempting all changes in one pass. I’ve included key decisions, next steps, and suggestions for each goal. Feel free to adjust based on your priorities, data volume, and the specific embedding or retrieval workflow you’re using (e.g., if you’re building a Retrieval-Augmented Generation \[RAG] pipeline).

---

# High-Level Plan for the 10 Goals

## 1. Use Token-Based Chunking

### Key Decisions

1. **Tokenizer**
   - Are you comfortable adding a new dependency like [OpenAI’s `tiktoken`](https://github.com/openai/tiktoken)?
   - Alternatively, do you want to keep an approximate token approach using `word_tokenize` from `nltk` or another library that more closely matches your chosen embedding model?

2. **Max Token Threshold**
   - Typical values are between 512–800 tokens per chunk for `text-embedding-ada-002`.
   - Decide on a final limit, e.g., `MAX_TOKENS = 512` or `MAX_TOKENS = 768`.

3. **Overlap**
   - Decide whether you want an overlap in **sentences** (like you have now) or in **tokens** (e.g., 30 tokens overlap).
   - Some people do a 10–15% overlap by tokens to preserve context in RAG workflows.

4. **Handling Large Single Sentences**
   - If a sentence itself exceeds `MAX_TOKENS`, do you break it mid-sentence or skip it? Typically best to **split** (despite the awkwardness) so you don’t lose data.

### Next Steps

- **Add the tokenizer** (e.g., `pip install tiktoken`) and a function `count_tokens(text: str) -> int`.
- **Implement** a `chunk_by_tokens()` function that measures token length instead of character length, creating new chunks whenever you exceed `MAX_TOKENS`.
- **Replace** or augment the existing `chunk_by_sentence_overlap` logic to do token-based chunking with optional overlap.

---

## 2. Preserve Headings & Section Titles

### Key Decisions

1. **Extraction Method**
   - A regex for Markdown headings (like `^(#{1,6})\s+(.*)`) might be enough.
   - Or use a markdown parser library (e.g., `mistune`, `markdown-it-py`) for more robust heading detection.

2. **Storage**
   - In your `crawl4ai_chunks` table, add a new column `heading` or store it in a JSON column (e.g., `metadata ->> 'heading'`).
   - For deeply nested docs, you might store a “heading path” if you want the entire hierarchy.

3. **Association With Chunks**
   - As you parse the document, keep track of the **most recent heading** encountered.
   - For all subsequent sentences until the next heading, assign that heading to each chunk’s metadata.

### Next Steps

- **Parse** headings up front while scanning the text (or as part of your existing chunking pipeline).
- **Include** the heading info in each chunk’s data structure (e.g., `TextChunk.heading`).
- **Insert** it into your DB column (new or existing).

---

## 3. Splitting Large Code Blocks

### Key Decisions

1. **Token Threshold**
   - Use the same `MAX_TOKENS` as text or define a separate threshold for code (e.g., 800 tokens if code often has fewer semantic tokens)?
   - Some code is very verbose, so it might exceed your token limit quickly.

2. **Overlap**
   - If you have extremely large code blocks, do you want to overlap some lines or tokens to preserve context?

3. **Fences**
   - When you split a code block, do you keep triple backticks (\`\`\`) at the start/end of each sub-chunk?

### Next Steps

- **Update** `chunk_text_with_code_blocks` to measure code blocks in tokens. If a block exceeds the threshold, split it into multiple sub-chunks.
- **Decide** whether to add a small overlap or not. Usually, code might not need overlapping in the same way text does, but that depends on your usage scenario.

---

## 4. Store Additional Context (Metadata)

### Key Decisions

1. **Which Fields**
   - You mentioned headings, but also consider `created_at`, `modified_at`, or even `source_type` (docs, blog, code, etc.).
   - Summaries can also go here if you generate them later.

2. **Schema Changes**
   - Decide if you’d like multiple new columns or one `metadata JSONB` column for flexibility.

### Next Steps

- **Extend** your DB schema, e.g. `ALTER TABLE crawl4ai_chunks ADD COLUMN heading TEXT;` (or `metadata JSONB`).
- **Populate** those fields during chunk creation or as a post-processing step.

---

## 5. Adjust Overlap Dynamically

### Key Decisions

1. **Overlap Metric**
   - If a chunk is 512 tokens, you might overlap 50 tokens (about 10%) into the next chunk.
   - Alternatively, keep a simpler approach: a fixed number of tokens overlap, e.g., 30 tokens.

2. **Implementation Complexity**
   - Dynamic overlap is more flexible but adds more logic. Decide if it’s worth it versus a simpler approach.

### Next Steps

- **Implement** a function that calculates how many tokens to overlap in each chunk.
- **Iterate** to find a sweet spot that balances context continuity vs. token efficiency.

---

## 6. Chunk Summaries (Optional)

### Key Decisions

1. **Summarization Model**
   - Use GPT-3.5, GPT-4, or a local model for summarization.
   - Note the **cost** if you have a large volume of chunks.

2. **Timing**
   - Summarize inline during chunk creation or as an offline batch process?

3. **Storage**
   - New column `chunk_summary` or a JSON field `metadata->>'summary'`.

### Next Steps

- **Prototype** a separate script that iterates over chunks and calls a summarization endpoint.
- **Insert** summaries back into the DB.
- Possibly **use** these summaries at query time to help the LLM quickly gauge relevance.

---

## 7. Thorough Markdown Cleaning

### Key Decisions

1. **Links**
   - `[text](url)` → `text (url)` or just `text`.

2. **Bullet Points & HTML**
   - Do you keep them as `- bullet` or convert to plain text?
   - Strip HTML tags vs. convert them to something else (like newlines).

3. **Implementation**
   - Regex-based approach vs. a real markdown parser (like `mistune`) that can generate plain text.

### Next Steps

- **Extend** your existing cleaning logic to handle links, bullet points, HTML.
- **Test** on real input to ensure the output text is coherent for an LLM.

---

## 8. Logging or Stats on Chunk Quality

### Key Decisions

1. **Which Stats**
   - Average tokens per chunk, min/max chunk size, how many code vs. text chunks, etc.

2. **Storage**
   - Print them to the console/log file or store them in a DB/table for historical comparison.

### Next Steps

- **Add** code to gather chunk stats during or after chunk creation.
- **Review** the logs to see if you need to adjust your token limit or overlap.

---

## 9. Parallel/Batch Inserts (Performance)

### Key Decisions

1. **Data Volume**
   - If you have tens or hundreds of thousands of chunks, your current `asyncio.gather` approach might be fine.
   - If you’re in the millions, you might need a more efficient insert approach (bulk copy).

2. **Implementation**
   - `asyncio.gather` can be enough. If it’s too slow, consider `copy_expert` in `psycopg2` or a similar approach in `asyncpg`.

### Next Steps

- **Evaluate** how many chunks you generate.
- If you see performance issues, **implement** batch inserts or a specialized approach (like Postgres COPY).

---

## 10. De-Duplicate or Label Repetitive Chunks

### Key Decisions

1. **Skip vs. Mark**
   - If a chunk is a near-duplicate, do you skip insertion entirely or store but flag it with `is_duplicate`?
   - Some disclaimers might be 90% the same but not fully identical, so do you check exact duplicates or partial duplicates?

2. **Implementation**
   - Easiest is to hash chunk text (e.g., SHA-256) and check if it’s in the DB.
   - More complex if you want to detect near-duplicates with a similarity threshold.

### Next Steps

- **Implement** a hashing step (`hashlib.sha256(chunk_text).hexdigest()`).
- **Check** for existing hash in DB; if found, skip insertion or mark `is_duplicate = TRUE`.
- **Consider** whether near-duplicates are prevalent enough to handle partial matching.

---

# Overarching Strategy

1. **Migration vs. Fresh Table**
   - If you re-chunk all content, you might want to re-embed everything. Often it’s simpler to build a new table (`crawl4ai_chunks_v2`) rather than trying to partially update an existing table.

2. **Phased Implementation**
   - Start with **token-based chunking** + **heading extraction** (goals #1 and #2).
   - Decide if large code block splitting (goal #3) and dynamic overlap (goal #5) are needed immediately or can wait.
   - Summaries (goal #6) and de-duplication (goal #10) are nice enhancements if your budget/time allows.

3. **Evaluate & Refine**
   - After you test the new chunks, check the distribution of token sizes, ensure performance is good, and confirm that headings/metadata show up as expected in retrieval.
   - Only then consider deeper expansions like advanced dynamic overlap, summarization, or code block splitting if you see real-world benefits.

4. **Re-Embedding**
   - Once the new chunking strategy is stable, re-embed them so your retrieval flow aligns with the updated chunk boundaries. Otherwise, old embeddings won’t match the new chunk text.

---

## Final Thoughts

- **Token-based chunking** is crucial for a robust RAG pipeline, ensuring you don’t exceed model limits.
- **Metadata like headings** greatly improves retrieval, as the LLM can interpret chunk context more accurately.
- **Summaries** are powerful if you can afford them—especially for large or complex text.
- **Performance** can be managed with async inserts or batching, and you can always scale up if your dataset grows.
- **De-duplication** avoids clutter. If your corpus has lots of boilerplate, it’s worth implementing.

With these incremental steps, you’ll be able to refine your entire chunking pipeline, improve the quality of your stored chunks, and ultimately enhance retrieval results for your LLM or RAG use cases. Good luck, and feel free to follow up if you run into any specific implementation questions!


#### You:
<time datetime="2025-02-15T15:27:16.603Z" title="2/16/2025, 12:27:16 AM">00:27</time>

do you have enough information to generate the code? if so, generate the new code

#### ChatGPT:
<time datetime="2025-02-15T15:28:26.552Z" title="2/16/2025, 12:28:26 AM">00:28</time>

Below is an **example** of how you could modify your script to implement many of the improvements discussed, including:

- **Token-based chunking** (using the [tiktoken](https://github.com/openai/tiktoken) library).
- **Preserving headings** and attaching them to each chunk.
- **Splitting large code blocks** if they exceed a token threshold.
- **Storing additional metadata** (like `heading`) in your database.
- **(Optional) Overlap** in tokens rather than sentences.
- **(Optional) Basic logging** to track average chunk size, etc.

> **Note**
>
> 1. You’ll need to install `tiktoken`:\
>    \`\`\`bash
>    pip install tiktoken
>    \`\`\`
> 2. This code uses an **additional** column `heading` (of type `TEXT`) in the `crawl4ai_chunks` table. If you haven’t added that column yet, run something like:
>    \`\`\`sql
>    ALTER TABLE crawl4ai\_chunks ADD COLUMN heading TEXT;
>    \`\`\`
>    Or you could store `heading` in a JSON field—adjust as you prefer.
> 3. Feel free to adjust **token limits**, **overlap**, and other logic to your needs.

---

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

# Make sure you've installed tiktoken: pip install tiktoken
import tiktoken

nltk.download("punkt")  # Ensure the sentence tokenizer is available

# ------------------------------------------------------------
# 1. Configuration
# ------------------------------------------------------------
SUPABASE_USER     = "supabase_admin"
SUPABASE_PASSWORD = "supabase"
SUPABASE_HOST     = "192.168.1.200"
SUPABASE_PORT     = 5432
SUPABASE_DB       = "supabase"

# Adjust these as needed
MAX_TOKENS = 512            # The max tokens per chunk
TOKEN_OVERLAP = 30          # How many tokens to overlap between chunks (optional)
MODEL_NAME = "gpt-3.5-turbo"  # For tiktoken encoding
MIN_CODE_CHUNK_TOKENS = 50  # If splitting large code blocks, how big is each sub-chunk?

pool: Optional[asyncpg.Pool] = None

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
      - content:       The chunk text (either code or normal text).
      - chunk_size:    The length of the chunk in characters.
      - word_count:    Approx. number of words/tokens in the chunk.
      - heading:       The nearest heading/title in the source markdown, if any.
    """
    page_id: int
    page_url: str
    chunk_number: int
    content: str
    chunk_size: int
    word_count: int
    heading: Optional[str] = None

# ------------------------------------------------------------
# 3. Token Counting
# ------------------------------------------------------------
# Use tiktoken to count tokens based on the model you plan to use for embeddings or GPT queries.
encoding = tiktoken.encoding_for_model(MODEL_NAME)

def count_tokens(text: str) -> int:
    """Return the number of tokens in `text` according to tiktoken."""
    # If you have a specific embedding model, you may want to use encoding_for_model("text-embedding-ada-002") instead
    return len(encoding.encode(text))

# ------------------------------------------------------------
# 4. Heading Extraction
# ------------------------------------------------------------
def extract_headings(text: str) -> List[tuple]:
    """
    Scans the markdown text and returns a list of tuples (start_index, heading_level, heading_text).
    Example: 
      [ (15, 2, "Some Section Title"), (120, 3, "Subsection"), ... ]
    This tells us that at character 15 in the text, there's a ## heading "Some Section Title".
    """
    pattern = r"^(#{1,6})\s+(.*)$"
    matches = []
    current_index = 0

    # We'll do a manual line-by-line approach
    lines = text.split("\n")
    char_pos = 0
    for line in lines:
        line_stripped = line.strip()
        match = re.match(pattern, line_stripped)
        if match:
            hashes = match.group(1)
            heading_text = match.group(2).strip()
            heading_level = len(hashes)
            # Record the position of this heading in the overall text
            matches.append((char_pos, heading_level, heading_text))
        # Move char_pos by line length + 1 (for newline)
        char_pos += len(line) + 1

    return matches

def find_current_heading(position: int, headings: List[tuple]) -> Optional[str]:
    """
    Given a character `position` and a sorted list of headings (by start_index),
    returns the text of the latest heading that appears before `position`.
    """
    current = None
    for (start_idx, level, heading_text) in headings:
        if start_idx <= position:
            current = heading_text
        else:
            break
    return current

# ------------------------------------------------------------
# 5. Main Chunking Logic (Token-Based)
# ------------------------------------------------------------
def split_code_block_by_tokens(code_text: str) -> List[str]:
    """
    If a code block is too large (over MAX_TOKENS), split it into multiple sub-chunks.
    We do no overlap here by default, but you can add overlap if needed.
    """
    tokens = encoding.encode(code_text)
    if len(tokens) <= MAX_TOKENS:
        # No need to split
        return [code_text]

    # Split into multiple lumps
    sub_chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + MAX_TOKENS, len(tokens))
        sub_token_ids = tokens[start:end]
        sub_text = encoding.decode(sub_token_ids)
        sub_chunks.append(sub_text)
        start = end

    return sub_chunks

def chunk_by_tokens(text: str, heading: Optional[str] = None) -> List[str]:
    """
    Splits a given text into multiple token-based chunks, with optional token overlap.
    """
    # Encode the entire text into tokens
    token_ids = encoding.encode(text)
    if len(token_ids) <= MAX_TOKENS:
        return [text]

    chunks = []
    start = 0
    while start < len(token_ids):
        end = min(start + MAX_TOKENS, len(token_ids))
        sub_tokens = token_ids[start:end]
        chunk_text = encoding.decode(sub_tokens)
        chunks.append(chunk_text)
        # Overlap logic: move start by (MAX_TOKENS - TOKEN_OVERLAP), so we overlap the last N tokens
        start += (MAX_TOKENS - TOKEN_OVERLAP)

    return chunks

def unify_triple_quotes(text: str) -> str:
    """Replaces sequences of 3 or more double quotes with exactly three."""
    return re.sub(r'"{3,}', '"""', text)

def chunk_page_content(text: str) -> List[tuple]:
    """
    1. Extract code blocks (```...``` or ~~~...~~~).
    2. Extract headings in the overall text.
    3. Create chunks either from code blocks (split further if needed) 
       or from normal text, using token-based splitting.
    4. Return a list of tuples: (chunk_text, heading, start_char_index, is_code).
    """
    # Extract headings from entire text first
    headings_info = extract_headings(text)

    # Regex to split code blocks: group1 captures fence (``` or ~~~), group2 captures code content.
    pattern = r"(```|~~~)(.*?)(\1)"
    segments = re.split(pattern, text, flags=re.DOTALL)

    results = []
    current_char_idx = 0

    # segments will alternate between normal text and captured groups if the pattern matches
    # A typical segmentation might look like:
    #   [ normal_text, '```', code_content, '```', normal_text, ... ]
    # We'll process it chunk by chunk.
    idx = 0
    while idx < len(segments):
        segment = segments[idx]

        # If this segment is a code fence marker (``` or ~~~),
        # the next index (idx+1) should be the code content,
        # and the next after that (idx+2) is the fence again.
        # So we'll handle them in sets of three.
        if segment in ["```", "~~~"] and (idx + 1) < len(segments):
            code_content = segments[idx + 1]
            # The next one should be the matching fence, segments[idx + 2] -> ignore
            fence_length = len(segment) + len(code_content) + len(segment)
            # Attempt to unify triple quotes within the code
            code_content = unify_triple_quotes(code_content.strip())
            # Find heading relevant at the current_char_idx
            current_heading = find_current_heading(current_char_idx, headings_info)
            
            # Possibly split large code blocks by tokens
            code_blocks = split_code_block_by_tokens(code_content)
            for cb in code_blocks:
                results.append((cb, current_heading, current_char_idx, True))
            
            # Advance current_char_idx
            current_char_idx += fence_length
            idx += 3  # jump over code fence, code content, closing fence
        else:
            # Normal text
            normal_text = segment
            if normal_text.strip():
                # Possibly unify triple quotes
                normal_text = unify_triple_quotes(normal_text)
                # We'll chunk by tokens
                # But we also want to keep track of which heading is active
                current_heading = find_current_heading(current_char_idx, headings_info)
                text_chunks = chunk_by_tokens(normal_text, heading=current_heading)
                
                for chunk_txt in text_chunks:
                    results.append((chunk_txt, current_heading, current_char_idx, False))
                
            current_char_idx += len(segment)
            idx += 1

    return results

# ------------------------------------------------------------
# 6. Database Access
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
    Inserts one chunk into `crawl4ai_chunks`, including the new `heading`.
    Make sure your table has the appropriate columns:
      - page_id, page_url, chunk_number, content, chunk_size, word_count, heading
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO crawl4ai_chunks
                (page_id, page_url, chunk_number,
                 content, chunk_size, word_count, heading)
            VALUES
                ($1, $2, $3,
                 $4, $5, $6, $7)
            """,
            chunk.page_id,
            chunk.page_url,
            chunk.chunk_number,
            chunk.content,
            chunk.chunk_size,
            chunk.word_count,
            chunk.heading
        )

# ------------------------------------------------------------
# 7. Orchestration
# ------------------------------------------------------------
async def process_chunk(chunk: TextChunk) -> None:
    """
    Insert chunk data into the DB.
    """
    await insert_chunk(chunk)

# ------------------------------------------------------------
# 8. Main Script
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

        # 1) Chunk the page content using token-based approach
        chunked_segments = chunk_page_content(cleaned_md)

        # 2) Create and insert each chunk
        tasks = []
        for i, (chunk_text, heading_text, start_char_idx, is_code) in enumerate(chunked_segments):
            # We'll define chunk size in characters, but also store a 'word_count' or 'token_count'
            chunk_size = len(chunk_text)
            token_count = count_tokens(chunk_text)

            chunk_obj = TextChunk(
                page_id=page_id,
                page_url=page_url,
                chunk_number=i,
                content=chunk_text,
                chunk_size=chunk_size,
                word_count=token_count,
                heading=heading_text
            )
            tasks.append(process_chunk(chunk_obj))

        # 3) Run insert tasks concurrently
        await asyncio.gather(*tasks)
        total_chunk_count += len(chunked_segments)

        print(f"[Chunked] page_id={page_id}, url={page_url}, total_chunks={len(chunked_segments)}")

    print(f"[Info] Finished chunking. Inserted {total_chunk_count} total chunks.")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
````

---

## Explanation of Key Changes

1. **Token Counting (Tiktoken)**
   - We import `tiktoken` and define `count_tokens(text: str)` using an encoding derived from `tiktoken.encoding_for_model(MODEL_NAME)`.
   - This lets us split text accurately by token count rather than characters.

2. **Code Splitting**
   - In `split_code_block_by_tokens(code_text)`, if a code block is too large (over `MAX_TOKENS`), it’s split into sub-chunks.
   - This avoids having a single massive code block chunk that could exceed your embedding or retrieval token limits.

3. **Headings**
   - The function `extract_headings(text)` locates headings (`#`, `##`, etc.) in the raw markdown, storing their character positions.
   - `find_current_heading(position, headings)` returns the last heading that began *before* a given character index. This is used to tag each chunk with the nearest heading.

4. **Token-Based Chunking**
   - `chunk_by_tokens(text)` encodes the text into tokens and slices them into segments of up to `MAX_TOKENS` each.
   - An optional `TOKEN_OVERLAP` is subtracted from the start position for the next chunk, so you can overlap text if desired (helps maintain context across chunk boundaries).

5. **Metadata**
   - We extended the `TextChunk` dataclass with a `heading` field. We also store the token count in `word_count` (formerly used for `len(word_tokenize)`, now replaced with the real token count).
   - The example SQL insertion includes the `heading` column.

6. **Logging**
   - Each page’s chunk count is printed: `[Chunked] page_id=..., total_chunks=...`.
   - You could also log average tokens per chunk, min/max chunk size, etc., if you want more detailed stats.

---

### Additional Notes

- If you want **dynamic overlap** (e.g., 10% overlap rather than a fixed 30 tokens), you can compute it by fraction:
  ```python
  overlap_size = int(MAX_TOKENS * 0.1)  # e.g., 10%
  start += (MAX_TOKENS - overlap_size)
  ```
- If you prefer to keep your **existing sentence-based overlap** in addition to token-limiting, you could combine the approaches. But typically, once you switch to token-based chunking, you do your overlap in tokens rather than sentences.
- The **heading extraction** is a simple regex approach. If your markdown is more complex, or if you want bullet points / other structures, consider a robust parser like `mistune`, `markdown-it-py`, or `mdformat` libraries.
- **De-duplication**, **summaries**, and other advanced features (like storing `chunk_summary`) can be layered in similarly, either by adding columns or a JSON field to store extra metadata.

This skeleton should give you a solid starting point for token-based chunking, heading preservation, code splitting, and better metadata storage in your RAG or any retrieval pipeline. Adjust the details (token limit, overlap, headings, etc.) to your exact requirements.
