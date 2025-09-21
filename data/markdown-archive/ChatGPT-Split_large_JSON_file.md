---
title: Split large JSON file
source: https://chatgpt.com/c/677dea94-21b4-8003-bd22-5c7784e4cbf4
---

# Split large JSON file

#### You:
<time datetime="2025-01-08T03:01:40.377Z" title="1/8/2025, 12:01:40 PM">12:01</time>

I have a large json file (20mb). Is there a way to split it into smaller parts without reading it into memory? When I try to open it my computer freezes

#### ChatGPT:
<time datetime="2025-01-08T03:01:50.878Z" title="1/8/2025, 12:01:50 PM">12:01</time>

Yes, you can split a large JSON file into smaller parts without loading the entire file into memory. This approach is especially useful for handling large files that might cause your computer to freeze when opened normally. Below are several methods you can use, depending on your comfort with command-line tools or scripting.

---

### **Method 1: Using `jq` (Command-Line JSON Processor)**

[`jq`](https://stedolan.github.io/jq/) is a lightweight and flexible command-line JSON processor that's perfect for manipulating JSON data without loading it entirely into memory.

#### **Steps:**

1. **Install `jq`:**
   - **Windows:** You can download the executable from the [jq downloads page](https://stedolan.github.io/jq/download/).
   - **macOS:** Use Homebrew:
     ```bash
     brew install jq
     ```
   - **Linux:** Use your distribution’s package manager, e.g.,
     ```bash
     sudo apt-get install jq
     ```

2. **Determine the Structure of Your JSON File:**
   - **Array of Objects:** If your JSON file is structured as an array (`[ {...}, {...}, ... ]`), you can split it into smaller arrays.
   - **JSON Lines (NDJSON):** If each line is a separate JSON object, splitting is more straightforward.

3. **Split the JSON File:**

   - **For a JSON Array:**
     Suppose your JSON file (`large.json`) is an array of objects. You can split it into multiple smaller arrays, each containing a specific number of objects.

     ```bash
     jq -c '.[]' large.json | split -l 1000 - "part_"
     ```

     - This command does the following:
       - `jq -c '.[]' large.json`: Streams each element of the array as a compact JSON object.
       - `split -l 1000 - "part_"`: Splits the stream into files with 1000 JSON objects each, named `part_aa`, `part_ab`, etc.

     - **Post-Processing:** You might want to wrap each split file back into a JSON array:

       ```bash
       for file in part_*; do
           echo "[" > "${file}.json"
           paste -sd, "$file" >> "${file}.json"
           echo "]" >> "${file}.json"
           rm "$file"
       done
       ```

   - **For JSON Lines (NDJSON):**
     If each line is a separate JSON object, splitting is easier.

     ```bash
     split -l 1000 large.json part_
     ```

     - Each `part_` file will contain 1000 JSON objects. You can rename them with a `.json` extension if needed.

---

### **Method 2: Using a Python Script with Streaming**

If you prefer using Python, especially when dealing with more complex JSON structures, you can utilize streaming to process the file without loading it entirely into memory.

#### **Prerequisites:**

- **Python Installed:** Ensure you have Python 3.x installed.
- **Install `ijson`:** A streaming JSON parser for Python.

  ```bash
  pip install ijson
  ```

#### **Script to Split JSON Array into Smaller Files:**

```python
import ijson
import json

def split_json_array(input_file, output_prefix, chunk_size):
    with open(input_file, 'r', encoding='utf-8') as f:
        objects = ijson.items(f, 'item')  # Adjust the prefix if your JSON structure is different
        chunk = []
        file_count = 1
        for obj in objects:
            chunk.append(obj)
            if len(chunk) >= chunk_size:
                with open(f"{output_prefix}_{file_count}.json", 'w', encoding='utf-8') as out:
                    json.dump(chunk, out, ensure_ascii=False, indent=2)
                print(f"Created {output_prefix}_{file_count}.json with {chunk_size} items.")
                chunk = []
                file_count += 1
        # Write remaining objects
        if chunk:
            with open(f"{output_prefix}_{file_count}.json", 'w', encoding='utf-8') as out:
                json.dump(chunk, out, ensure_ascii=False, indent=2)
            print(f"Created {output_prefix}_{file_count}.json with {len(chunk)} items.")

if __name__ == "__main__":
    input_json = 'large.json'         # Path to your large JSON file
    output_prefix = 'split_part'      # Prefix for output files
    chunk_size = 1000                 # Number of items per split file

    split_json_array(input_json, output_prefix, chunk_size)
```

#### **How It Works:**

1. **Streaming Parsing:** The `ijson` library parses the JSON file incrementally, extracting one item at a time from the top-level array.
2. **Chunking:** It collects a specified number of items (`chunk_size`) and writes them to a new JSON file.
3. **Output Files:** Each split file is named with the provided prefix and a sequential number, e.g., `split_part_1.json`, `split_part_2.json`, etc.

#### **Usage:**

1. Save the script to a file, e.g., `split_json.py`.
2. Run the script:

   ```bash
   python split_json.py
   ```

   Ensure that `large.json` is in the same directory or provide the correct path.

---

### **Method 3: Using Specialized Tools**

There are tools specifically designed to handle large JSON files. One such tool is [`json-splitter`](https://github.com/codemix/json-splitter), which can split JSON files based on specified criteria.

#### **Steps:**

1. **Install `json-splitter`:**

   ```bash
   npm install -g json-splitter
   ```

   *(Requires Node.js and npm installed.)*

2. **Use `json-splitter` to Split the File:**

   ```bash
   json-splitter -i large.json -o split_part_ -c 1000
   ```

   - `-i`: Input file.
   - `-o`: Output file prefix.
   - `-c`: Number of items per split file.

---

### **Additional Tips:**

- **Backup Your Data:** Always keep a backup of your original JSON file before performing split operations.

- **Validate Split Files:** After splitting, you can use `jq` or other JSON validators to ensure each split file is valid JSON.

  ```bash
  jq empty split_part_1.json
  ```

- **Adjust `chunk_size`:** Depending on your needs and system capabilities, you can adjust the number of items per split file.

---

By using these methods, you can efficiently split your large JSON file into smaller, more manageable parts without overwhelming your computer's memory. Choose the method that best fits your environment and comfort level.
