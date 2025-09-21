---
title: SQL to CSV Conversion
source: https://chatgpt.com/c/678d58af-1530-8003-a19e-716792a294a1
---

# SQL to CSV Conversion

#### You:
<time datetime="2025-01-19T20:53:30.275Z" title="1/20/2025, 5:53:30 AM">05:53</time>

i need a python script to convert a txt file into a csv.

here is a sample of the text file. the text file is very large
column headers: ("id", "title", "source", "create_time", "datemodified", "data", "cost", "model_id", "model_name", "num_messages", "chat_title", "preview", "synced_at")
example data in text file:  

(359, 'Exploring the PAS Framework in Copywriting', 'ru0iyThu6R', '2024-05-16 20:18:38.958', '2024-05-16 20:19:02.78', '{"content": {"model": "gpt-4-turbo", "chatID": "ru0iyThu6R", "messages": [{"role": "user", "uuid": "6386f545-3be9-4138-8070-2d5ddb3bfc1e", "content": "what is the PAS copywriting framework? give me examples of some effective PAS copy]", "createdAt": "2024-05-16T20:18:38.912Z"}, {"role": "assistant", "uuid": "808f70bd-ac51-4f0f-b100-84860ee053d1", "model": "gpt-4-turbo", "usage": {"total_tokens": 735, "prompt_tokens": 78, "completion_tokens": 657}, "content": "The PAS framework stands for Problem-Agitation-Solution. It''s a powerful technique used in copywriting to capture the attention of the audience, stir their emotions, and then offer a solution. Here’s how it typically works:1. **Problem**: Identify a problem that your target audience faces. This empathizes with the reader''s situation and captures their attention because it’s relevant to their needs or pain points.   2. **Agitation**: Amplify the problem. This doesn’t just restate the problem but digs deeper into the implications of the problem, increasing the reader''s emotional investment.3. **Solution**: Present your product or service as the solution to the problem. This should be a natural and compelling resolution that feels satisfying in the context of the agitation.### Examples of PAS CopywritingHere are a few examples applying the PAS framework across different products and services:#### Example 1: Skincare Product- **Problem**: Does your acne flare up at the worst possible times?- **Agitation**: Imagine being on a date or heading into a crucial job interview, only to have a breakout that’s impossible to ignore. Not only does it hurt, it also shatters your confidence when you need it the most.- **Solution**: Introducing ClearSkin Pro, a dermatologist-approved acne treatment that not only tackles acne at its source but also boosts your skin''s health to prevent future breakouts. Start your day confident and clear!#### Example 2: Time Management App- **Problem**: Feel like there are never enough hours in the day?- **Agitation**: You’re rushing from task to task, barely keeping up, yet everything still piles up. Stress builds, deadlines loom larger, and your personal life? What personal life?- **Solution**: TimeMaster, the app designed to reclaim your schedule. Our smart planning features prioritize your day so you can breathe easier, achieve more, and reclaim your time for what truly matters.#### Example 3: Home Security System- **Problem**: Worried about the safety of your home when you''re away?- **Agitation**: Every noise or unexpected alert during the night sends a shockwave of anxiety through your mind. Could it be an intruder? Are your loved ones safe?- **Solution**: SafeGuard Home Security offers cutting-edge technology that watches over your home 24/7, sends instant alerts to your smartphone, and contacts authorities at suspicious signs. Sleep soundly knowing SafeGuard is on watch.These examples follow the PAS structure, effectively leading the reader through a coherent and engaging message that escalates a problem and offers a concise solution.", "createdAt": "2024-05-16T20:19:02.705Z"}], "syncedAt": "2025-01-14T00:49:12.991Z", "chatTitle": "Exploring the PAS Framework in Copywriting", "createdAt": "2024-05-16T20:18:38.958Z", "deletedAt": null, "modelInfo": {"id": "gpt-4-turbo", "title": "GPT-4 Turbo"}, "updatedAt": "2024-05-16T20:19:02.780Z", "chatParams": {"topK": null, "topP": null, "maxTokens": null, "streaming": true, "outputTone": "", "outputStyle": "", "temperature": null, "contextLimit": 0, "outputFormat": "", "systemMessage": "You are a helpful AI assistant. Today is {local_date}, local time is {local_time}.If you need to display math symbols and expressions, put them in double dollar signs \"$$\" (example: $$ x - 1 $$)", "outputLanguage": "", "presencePenalty": null, "frequencyPenalty": null, "showOutputSettings": ""}, "tokenUsage": {"recordedAt": "2024-05-16T20:19:02.720Z", "totalTokens": 735, "totalCostUSD": 0.02049, "messageTokens": 735, "enhancedTokens": 0, "messageCostUSD": 0.02049, "enhancedCostUSD": 0}, "linkedPlugins": [{"id": "get_web_search_results", "emoji": "🔍", "title": "Web Search"}, {"id": "image_generation_via_dalle_3", "emoji": "✨", "title": "DALL-E 3"}, {"id": "search_images_via_google", "emoji": "🌅", "title": "Image Search"}, {"id": "read_web_page_content", "emoji": "📃", "title": "Web Page Reader"}, {"id": "get_calculation_result", "emoji": "🧮", "title": "Simple Calculator"}, {"id": "execute_javascript", "emoji": "⌨️", "title": "JavaScript Interpreter"}, {"id": "render_html", "emoji": "🖥️", "title": "Render HTML"}]}}', 0.02049, 'gpt-4-turbo', 'GPT-4 Turbo', 2, 'Exploring the PAS Framework in Copywriting', '', '2025-01-14 00:49:12.991'),(344, 'Deploying a GitHub Repository on Docker Desktop', 'vnVf6zIhic', '2024-05-10 00:33:03.859', '2024-05-10 00:33:26.584', '{"content": {"model": "gpt-4-turbo", "chatID": "vnVf6zIhic", "messages": [{"role": "user", "uuid": "6ef92366-8a5c-4462-9710-daeb7f603e0d", "content": "https://github.com/TypingMind/plugins-server how do I deploy this on my docker desktop?", "createdAt": "2024-05-10T00:33:03.839Z"}, {"role": "assistant", "uuid": "4f13d3c9-9884-4416-acc8-199955988267", "model": "gpt-4-turbo", "usage": {"total_tokens": 671, "prompt_tokens": 79, "completion_tokens": 592}, "content": "To deploy the repository found at \"https://github.com/TypingMind/plugins-server\" on your Docker Desktop, you can follow these steps:### Step 1: Install Docker DesktopEnsure that Docker Desktop is installed on your machine. You can download it from [Docker Hub](https://www.docker.com/products/docker-desktop) if you haven''t already.### Step 2: Clone the RepositoryOpen a terminal or command prompt on your machine and clone the repository using Git. If Git is not installed, install it from [Git SCM](https://git-scm.com/downloads).```bashgit clone https://github.com/TypingMind/plugins-server.gitcd plugins-server```### Step 3: Build the Docker ImageAssuming the repository has a Dockerfile, you can build a Docker image. Navigate to the directory containing the Dockerfile and run:```bashdocker build -t plugins-server .```This command builds a Docker image and tags it as `plugins-server`. If there are specific build arguments or a different tag is needed, adjust the command accordingly.### Step 4: Run the Docker ContainerOnce the image is built, you can run it in a container:```bashdocker run -d -p 8000:8000 plugins-server```This command runs the `plugins-server` image in a detached mode (`-d`), which means the container runs in the background. The `-p` flag publishes a container''s port(s) to the host. Here, `8000:8000` means that port 8000 of the container will be exposed on port 8000 of your localhost.### Step 5: Verify the DeploymentCheck that the container is running:```bashdocker ps```And try accessing it via the browser or using curl:```bashcurl http://localhost:8000```### Step 6: View Logs and Manage the ContainerTo view logs from your Docker container:```bashdocker logs [container_id]```Replace `[container_id]` with the actual ID of your container. You can find the container ID by looking at the output of `docker ps`.To stop your container:```bashdocker stop [container_id]```And to remove it:```bashdocker rm [container_id]```Use these commands to manage your Docker deployment. Before starting this process, ensure that the repository contains all necessary Docker-related files like `Dockerfile` and possibly `docker-compose.yml` if there are multiple services to run. If any specific instructions are given in the repository''s README, they should be followed as well.", "createdAt": "2024-05-10T00:33:26.502Z"}], "syncedAt": "2025-01-14T00:49:12.991Z", "chatTitle": "Deploying a GitHub Repository on Docker Desktop", "createdAt": "2024-05-10T00:33:03.859Z", "deletedAt": null, "modelInfo": {"id": "gpt-4-turbo", "title": "GPT-4 Turbo"}, "updatedAt": "2024-05-10T00:33:26.584Z", "chatParams": {"topK": null, "topP": null, "maxTokens": null, "streaming": true, "outputTone": "", "outputStyle": "", "temperature": null, "contextLimit": 0, "outputFormat": "", "systemMessage": "You are a helpful AI assistant. Today is {local_date}, local time is {local_time}.If you need to display math symbols and expressions, put them in double dollar signs \"$$\" (example: $$ x - 1 $$)", "outputLanguage": "", "presencePenalty": null, "frequencyPenalty": null, "showOutputSettings": ""}, "tokenUsage": {"recordedAt": "2024-05-10T00:33:26.508Z", "totalTokens": 671, "totalCostUSD": 0.018549999999999997, "messageTokens": 671, "enhancedTokens": 0, "messageCostUSD": 0.018549999999999997, "enhancedCostUSD": 0}, "linkedPlugins": [{"id": "get_web_search_results", "emoji": "🔍", "title": "Web Search"}, {"id": "image_generation_via_dalle_3", "emoji": "✨", "title": "DALL-E 3"}, {"id": "search_images_via_google", "emoji": "🌅", "title": "Image Search"}, {"id": "read_web_page_content", "emoji": "📃", "title": "Web Page Reader"}, {"id": "get_calculation_result", "emoji": "🧮", "title": "Simple Calculator"}, {"id": "execute_javascript", "emoji": "⌨️", "title": "JavaScript Interpreter"}, {"id": "render_html", "emoji": "🖥️", "title": "Render HTML"}]}}', 0.018549999999999997, 'gpt-4-turbo', 'GPT-4 Turbo', 2, 'Deploying a GitHub Repository on Docker Desktop', '', '2025-01-14 00:49:12.991'),

#### ChatGPT:
<time datetime="2025-01-19T20:54:32.856Z" title="1/20/2025, 5:54:32 AM">05:54</time>

Below is a simple Python script that demonstrates how to convert each parenthesized row in your `.txt` file into a corresponding CSV row. It uses Python’s built-in `ast.literal_eval` to safely parse each line (which is essentially a SQL/tuple-like string) into a Python tuple, then writes that tuple to CSV.

> **Important**:
>
> 1. This approach assumes **one row per line** in the `.txt` file.
> 2. Because the text includes doubled single quotes (`''`) for apostrophes (typical in SQL dumps), the script replaces those with standard single quotes (`'`) so that `ast.literal_eval` can parse them properly.
> 3. If your data has other quoting anomalies, you may need additional cleanup or more sophisticated parsing.

---

### Sample Python Script

```python
import csv
import ast

INPUT_FILE = "input.txt"   # Change this to your actual .txt file path
OUTPUT_FILE = "output.csv"

# Define your column headers in the correct order:
HEADERS = [
    "id",
    "title",
    "source",
    "create_time",
    "datemodified",
    "data",
    "cost",
    "model_id",
    "model_name",
    "num_messages",
    "chat_title",
    "preview",
    "synced_at"
]

def txt_to_csv(input_path, output_path):
    """
    Reads lines from a text file where each line represents a tuple of values.
    Parses each tuple and writes to a CSV file using HEADERS as column names.
    """
    with open(input_path, "r", encoding="utf-8") as txt_file, \
         open(output_path, "w", encoding="utf-8", newline="") as csv_file:
        
        writer = csv.writer(csv_file)
        # Write the column headers first
        writer.writerow(HEADERS)
        
        for line in txt_file:
            line = line.strip()
            
            # Skip empty lines if any
            if not line:
                continue
            
            # Remove trailing comma if it exists at the end of the line
            if line.endswith(","):
                line = line[:-1]
            
            # Remove leading "(" and trailing ")" if present
            # and re-wrap in parentheses so it looks like a Python tuple
            if line.startswith("(") and line.endswith(")"):
                line = line[1:-1]
            line = "(" + line + ")"
            
            # Replace doubled single quotes ('') with a single quote (')
            # so that ast.literal_eval can parse it
            line = line.replace("''", "'")
            
            try:
                # Safely parse the string into a Python tuple
                row_tuple = ast.literal_eval(line)
                
                # Make sure the row length matches the headers
                if len(row_tuple) != len(HEADERS):
                    print(f"Warning: Row has {len(row_tuple)} columns but expected {len(HEADERS)}. Skipping.")
                    continue
                
                # Write the parsed row to CSV
                writer.writerow(row_tuple)
            
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing line. Skipping.\nLine Content: {line}\nError: {e}")
                continue

if __name__ == "__main__":
    txt_to_csv(INPUT_FILE, OUTPUT_FILE)
    print(f"Conversion complete. CSV saved as: {OUTPUT_FILE}")
```

### How This Works

1. **Read line by line**: Assumes each row of your data is on its own line.
2. **Strip trailing comma**: Removes any extra comma at the end of the line (common in SQL dump formatting).
3. **Rebuild into a Python tuple**:
   - Strips the leading `(` and trailing `)`, then re-wraps the line in parentheses.
   - Replaces doubled single quotes (`''`) with single quotes (`'`) to make it valid for Python parsing.
4. **`ast.literal_eval`**: Safely evaluates the string, turning it into a Python tuple.
5. **Check the tuple length**: Ensures we have exactly 13 elements (matching your 13 columns).
6. **Write to CSV**: Uses Python’s `csv.writer` to output rows.

### Usage

1. **Update file paths**: Change `INPUT_FILE` and `OUTPUT_FILE` near the top of the script to match your actual file names.
2. **Run the script**:
   ```bash
   python convert_to_csv.py
   ```
3. Check the newly generated `output.csv`.

That’s it! You should end up with a valid CSV file where each row corresponds to the tuple data in your text file.


#### You:
<time datetime="2025-01-19T20:57:14.220Z" title="1/20/2025, 5:57:14 AM">05:57</time>

title": "JavaScript Interpreter"}]}}', 7.1962, 'claude-3-5-sonnet-20240620', 'Claude 3.5 Sonnet', 86, 'Docker Compose for Time Machine Server with VLAN', 'create a docker compose file to run this timemachine server, including a vlan)
Error: invalid non-printable character U+2060 (<unknown>, line 1)
Error parsing line. Skipping.
Line Content: (docker)
Error: malformed node or string on line 1: <ast.Name object at 0x10086bc90>
Error parsing line. Skipping.
Line Content: (Hub)
Error: malformed node or string on line 1: <ast.Name object at 0x10079eb10>
Error parsing line. Skipping.
Line Content: (​)
Error: invalid non-printable character U+200B (<unknown>, line 1)
Error parsing line. Skipping.
Line Content: (​)
Error: invalid non-printable character U+200B (<unknown>, line 1)
Error parsing line. Skipping.
Line Content: (Explore)
Error: malformed node or string on line 1: <ast.Name object at 0x10086bc90>
Error parsing line. Skipping.
Line Content: (mbentley/timemachine)
Error: malformed node or string on line 1: <ast.BinOp object at 0x10079f250>
Error parsing line. Skipping.
Line Content: (mbentley/timemachine)
Error: malformed node or string on line 1: <ast.BinOp object at 0x10079eb10>
Traceback (most recent call last):
  File "/Users/ashwin/Desktop/split.py", line 74, in <module>
    txt_to_csv(INPUT_FILE, OUTPUT_FILE)
  File "/Users/ashwin/Desktop/split.py", line 62, in txt_to_csv
    if len(row_tuple) != len(HEADERS):
       ^^^^^^^^^^^^^^
TypeError: object of type 'int' h

#### ChatGPT:
<time datetime="2025-01-19T20:57:48.051Z" title="1/20/2025, 5:57:48 AM">05:57</time>

Below is an updated version of the script that gracefully handles (and skips) any lines that don’t match your expected SQL-like tuple format (including single-token lines like `(docker)` or lines containing invisible characters). Specifically, it does the following:

1. **Removes zero-width spaces** (common invisible characters like `U+200B`, `U+200C`, etc.).
2. **Skips lines** if they can’t be parsed as a Python tuple.
3. **Skips lines** if they parse into something other than a tuple (e.g., a single integer or a single string).
4. **Skips lines** if the tuple size does not match your headers.

> **Note**: If you actually want to capture single-item lines like `(docker)` or `(mbentley/timemachine)`, you’ll need to decide what column(s) they should map to and adjust accordingly. This script simply skips them because they are not valid 13-column rows.

---

```python
import csv
import ast
import re

INPUT_FILE = "input.txt"   # Change this to your .txt file path
OUTPUT_FILE = "output.csv"

# Define your column headers in the correct order:
HEADERS = [
    "id",
    "title",
    "source",
    "create_time",
    "datemodified",
    "data",
    "cost",
    "model_id",
    "model_name",
    "num_messages",
    "chat_title",
    "preview",
    "synced_at"
]

def txt_to_csv(input_path, output_path):
    """
    Reads lines from a text file where each line represents a tuple of values.
    Safely parses each tuple and writes to a CSV file using HEADERS as column names.
    Skips lines that are not valid tuples or do not match the expected length.
    """
    with open(input_path, "r", encoding="utf-8") as txt_file, \
         open(output_path, "w", encoding="utf-8", newline="") as csv_file:
        
        writer = csv.writer(csv_file)
        # Write the column headers
        writer.writerow(HEADERS)
        
        for line in txt_file:
            line = line.strip()
            if not line:
                continue

            # 1. Remove zero-width or other invisible Unicode characters.
            #    This handles errors like invalid non-printable character U+200B, etc.
            line = re.sub(r'[\u200B-\u200F\uFEFF]', '', line)

            # 2. Optional: If the line ends with a comma, remove it.
            if line.endswith(","):
                line = line[:-1]
            
            # 3. Ensure the line has parentheses around it.
            #    If it's already in the format "( ... )", we do minimal changes.
            if not line.startswith("("):
                line = "(" + line
            if not line.endswith(")"):
                line += ")"
            
            # 4. Replace doubled single quotes with single quotes for valid Python syntax
            line = line.replace("''", "'")
            
            try:
                # 5. Attempt to parse the string into a Python object (tuple, etc.)
                row_tuple = ast.literal_eval(line)
                
                # 6. If it isn’t actually a tuple (e.g. single int, single string), skip
                if not isinstance(row_tuple, tuple):
                    print(f"Skipping (not a tuple): {line}")
                    continue
                
                # 7. Verify the tuple length matches the headers
                if len(row_tuple) != len(HEADERS):
                    print(f"Skipping (wrong # columns): {line}")
                    continue
                
                # 8. Write to CSV
                writer.writerow(row_tuple)
            
            except (SyntaxError, ValueError) as e:
                # If parsing fails, we skip the line
                print(f"Error parsing line. Skipping.\nLine Content: {line}\nError: {e}")
                continue

if __name__ == "__main__":
    txt_to_csv(INPUT_FILE, OUTPUT_FILE)
    print(f"Conversion complete. CSV saved as: {OUTPUT_FILE}")
```

### What Changed / How It Helps

1. **Zero-width space removal**\
   The `re.sub(r'[\u200B-\u200F\uFEFF]', '', line)` call strips out common invisible Unicode characters that can break parsing.

2. **Type-checking**\
   After calling `ast.literal_eval`, we verify `isinstance(row_tuple, tuple)` so that any single-item parentheses (like `(docker)`) or `(123)` (which Python interprets as just `123`) get skipped rather than breaking the script.

3. **Length Check**\
   We confirm each valid tuple has exactly the number of elements matching your `HEADERS` list. Otherwise, the script prints a warning and skips the line.

4. **Graceful Skips**\
   Instead of crashing with a `TypeError`, any line that fails to parse or doesn’t match the expected format is just skipped, and the script continues processing the next line.

---

**If you need those single-word lines** to be captured, you’ll have to decide how to store them (e.g., do they map to a single column, with the rest empty?), then adjust your logic accordingly. As written, this script strictly expects 13 fields in each tuple.


#### You:
<time datetime="2025-01-19T20:58:32.654Z" title="1/20/2025, 5:58:32 AM">05:58</time>

"content_type": "text"}, "end_turn": null, "metadata": {"parent_id": "aaa27233-8975-42a9-9d9d-e461e91b7669", "model_slug": "o1", "request_id": "902219eabb3fa379-SEA", "timestamp_": "absolute", "initial_text": "Thinking", "message_type": null, "finished_text": "Thought about safari options in September for 23 seconds", "default_model_slug": "o1"}, "recipient": "all", "create_time": 1736904728.094438, "update_time": null}, "children": ["211d4083-43c8-4cdf-8fbf-4310af6c7a5f"]}}, "gizmo_id": null, "safe_urls": [], "gizmo_type": null, "is_starred": null, "plugin_ids": null, "create_time": 1736904471.857801, "is_archived": false, "update_time": 1736905919.136158, "async_status": null, "current_node": "7eaadabf-4fe6-4d42-b4dd-1184a0619e41", "conversation_id": "67870f17-449c-8003-9274-1c924f28a900", "disabled_tool_ids": [], "default_model_slug": "o1", "moderation_results": [], "conversation_origin": null, "conversation_template_id": null}}', 0.0, ', ', 0, 'Great Migration Quiet Options', ', NULL);)
Error: invalid decimal literal (<unknown>, line 1)
Error parsing line. Skipping.
Line Content: (INSERT INTO "public"."conversations" ("id", "title", "source", "create_time", "datemodified", "data", "cost", "model_id", "model_name", "num_messages", "chat_title", "preview", "synced_at") VALUES)
Error: invalid syntax. Perhaps you forgot a comma? (<unknown>, line 1)
Error parsing line. Skipping.
Line Content: (1323, 'NAA D

#### ChatGPT:
<time datetime="2025-01-19T20:58:56.355Z" title="1/20/2025, 5:58:56 AM">05:58</time>

Below is a revised version of the script that **skips SQL statements** (like `INSERT INTO ... VALUES`), **skips partial lines** that don’t conform to a tuple, and **handles invisible characters** (e.g., zero-width spaces). By default, any line that fails to parse or doesn’t match the expected 13-column format is skipped rather than causing the script to crash.

```python
import csv
import ast
import re

INPUT_FILE = "input.txt"   # Update with your actual file path
OUTPUT_FILE = "output.csv"

# Define your column headers in the correct order:
HEADERS = [
    "id",
    "title",
    "source",
    "create_time",
    "datemodified",
    "data",
    "cost",
    "model_id",
    "model_name",
    "num_messages",
    "chat_title",
    "preview",
    "synced_at"
]

def txt_to_csv(input_path, output_path):
    """
    Reads lines from a text file where each line is expected to be a tuple of values,
    e.g. (1, 'title', 'source', ...).
    
    Skips:
      - lines containing SQL statements (INSERT/VALUES/etc.),
      - lines that can’t be parsed by `ast.literal_eval`,
      - lines that don't parse to a Python tuple of the correct length,
      - lines that contain zero-width or otherwise invisible Unicode characters (which are removed).
    """
    with open(input_path, "r", encoding="utf-8") as txt_file, \
         open(output_path, "w", encoding="utf-8", newline="") as csv_file:
        
        writer = csv.writer(csv_file)
        # Write header row in the CSV
        writer.writerow(HEADERS)
        
        for raw_line in txt_file:
            line = raw_line.strip()
            
            # Skip empty lines
            if not line:
                continue

            # -- 1. Skip obvious SQL lines (e.g. "INSERT INTO", "VALUES")
            #       or any lines that contain keywords from a typical SQL dump
            if ("INSERT INTO" in line.upper() or "VALUES" in line.upper()):
                print(f"Skipping SQL line: {line}")
                continue

            # -- 2. Remove zero-width spaces (which can break parsing)
            #       Covers common invisible chars like U+200B to U+200F and U+FEFF.
            line = re.sub(r'[\u200B-\u200F\uFEFF]', '', line)

            # -- 3. Sometimes lines end with a comma. Remove trailing comma if present.
            if line.endswith(","):
                line = line[:-1]

            # -- 4. Ensure we have parentheses around the content
            if not line.startswith("("):
                line = "(" + line
            if not line.endswith(")"):
                line += ")"

            # -- 5. Replace doubled single quotes with single quotes
            #       so ast.literal_eval can handle them
            line = line.replace("''", "'")

            try:
                # -- 6. Try parsing as a Python tuple
                parsed = ast.literal_eval(line)
                
                # Ensure parsed is actually a tuple
                if not isinstance(parsed, tuple):
                    print(f"Skipping (not a tuple): {line}")
                    continue
                
                # Ensure the tuple has the exact number of columns
                if len(parsed) != len(HEADERS):
                    print(f"Skipping (wrong # of columns): {line}")
                    continue

                # Finally, write to CSV
                writer.writerow(parsed)

            except (SyntaxError, ValueError) as e:
                # If there's a parsing error, we skip the line
                print(f"Error parsing line. Skipping.\nLine Content: {line}\nError: {e}")
                continue

if __name__ == "__main__":
    txt_to_csv(INPUT_FILE, OUTPUT_FILE)
    print(f"Conversion complete. CSV saved as: {OUTPUT_FILE}")
```

### How this helps

1. **Skipping SQL boilerplate**\
   Any line containing typical SQL statements (e.g., `INSERT INTO`, `VALUES`) is immediately ignored. This prevents the parser from attempting to interpret SQL keywords and syntax as a Python tuple.

2. **Stripping zero-width spaces**\
   Removes characters like `U+200B` or `U+FEFF` that can otherwise cause parsing errors.

3. **Graceful error handling**
   - **`ast.literal_eval`** is wrapped in a `try/except` block. Any line that fails to parse (like partial/incomplete lines) is skipped.
   - We also verify the parsed object is indeed a **tuple** and has **exactly 13 columns** (matching your `HEADERS`). Anything else is skipped.

4. **Prints diagnostic messages**\
   So you know which lines were skipped and why.

---

If you **do** need some of those skipped lines, you’ll have to decide how they map to your columns (e.g., fill missing columns with `NULL` or empty strings) and adjust the script accordingly. Otherwise, this script will robustly skip invalid lines and produce a clean CSV of only well-formed 13-column tuples.
