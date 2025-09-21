---
title: Search for Roon files
source: https://chatgpt.com/c/67ae1998-384c-8003-9c3d-3955c1117de1
---

# Search for Roon files

#### You:
<time datetime="2025-02-13T16:11:04.512Z" title="2/14/2025, 1:11:04 AM">01:11</time>

➜  ~ ls   
addon_configs  addons         backup         config         homeassistant  media          share          ssl

search these directories for any mention of 'roon'

#### ChatGPT:
<time datetime="2025-02-13T16:11:17.555Z" title="2/14/2025, 1:11:17 AM">01:11</time>

Here’s a quick way to search those directories recursively for any file containing the string “roon.” In a typical Linux shell, you can run:

```bash
grep -ir "roon" addon_configs addons backup config homeassistant media share ssl
```

**Explanation of the options:**

- **-i** makes the search case-insensitive (so it will catch “Roon,” “roon,” etc.).
- **-r** instructs `grep` to search recursively through all subdirectories.
- The directories listed at the end are the ones you want to search.

Any matches will be printed to your console along with the path to the file and (by default) the matching line(s). This is often the most straightforward way to hunt down specific keywords across multiple folders in a Home Assistant environment.

If you want to see line numbers in the results, just add the **-n** option:

```bash
grep -irn "roon" addon_configs addons backup config homeassistant media share ssl
```

This will help you locate and review any mention of “roon” quickly.
