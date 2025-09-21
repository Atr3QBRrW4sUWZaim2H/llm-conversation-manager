---
title: Alt-tab for web apps
source: https://chatgpt.com/c/678011f2-770c-8003-bfaf-d533949dbafe
---

# Alt-tab for web apps

#### You:
<time datetime="2025-01-09T18:14:10.688Z" title="1/10/2025, 3:14:10 AM">03:14</time>

I use a bunch of web apps within chrome tabs and I often have trouble finding them again. I would like to be able to alt-tab to these web apps just like I would with an installed program on my osx system. What are my options?

#### ChatGPT:
<time datetime="2025-01-09T18:15:15.675Z" title="1/10/2025, 3:15:15 AM">03:15</time>

On macOS, Chrome tabs generally don’t show up as separate “apps” in your Command+Tab (or Alt+Tab) switcher. However, there are a few ways to turn a web-based tool into something that looks and behaves more like a standalone app—complete with its own icon and its own space in your application switcher. Here are some approaches:

---

## 1. Use Chrome’s Built-In “Create Shortcut” (a.k.a. “Open as Window”)

Chrome has a native feature to create application-like windows for sites you frequently use:

1. **Open the website** (or web app) in Chrome.
2. Click the three-dot menu > **More Tools** > **Create Shortcut...**
3. **Name** the shortcut and **enable “Open as window”** (this is crucial).
4. The shortcut should now show up in your **Applications** folder (on macOS) and can be pinned to your Dock or launched like any other app.

By opening in a separate window, it should also show up as its own icon when you press **Command+Tab**.

> **Note**: If the site still does not appear in the Command+Tab switcher, you may need to manually drag it from the Applications folder into the Dock. Once it’s in your Dock and opened as a separate window, it typically gets its own entry in the app switcher.

---

## 2. Use Third-Party Site-Specific Browser Tools

If you want a more robust or polished “app-like” experience, there are dedicated tools (sometimes called “site-specific browsers” or SSBs) that wrap a website with its own app window, icon, and menu bar:

- **Fluid** (macOS only):
  - Create a site-specific browser by providing a URL and choosing an icon.
  - Your new “web app” will appear in your Applications folder and in Command+Tab.
  - <https://fluidapp.com/>

- **Coherence** (macOS only):
  - Similar idea, but integrates with Chrome. It can install Chrome extensions (like LastPass) in the generated app.
  - <https://www.bzgapps.com/coherence>

- **Epichrome** (macOS only):
  - Creates Chrome-based SSBs. You can pick which Chrome extensions to include, customize icons, etc.
  - <https://github.com/dmarmor/epichrome>

All of these basically provide an “.app” file for your chosen web service.

---

## 3. Use an “Electron” Wrapper Tool (e.g., Nativefier)

For power users and developers, [Nativefier](https://github.com/nativefier/nativefier) is a command-line tool that takes a URL and spits out a desktop application for macOS, Windows, or Linux. The app runs in an Electron shell but looks and behaves like a desktop app. This may be overkill for many users, but it’s great if you want a lot of control.

---

### Practical Tips

- Once you’ve created these app shortcuts, **pin them to your Dock** for quick access, and they’ll remain distinct from any Chrome window.
- If you like keyboard shortcuts, you can also assign your newly created apps a **hotkey** or use third-party launcher tools (e.g. Alfred, Raycast) to open them.
- Keep an eye on **Chrome profiles** (if you create multiple site-specific shortcuts with different Google accounts, for instance). Each can open in its own “profile” context if you set it that way.

---

#### In summary:

- If you just need a quick solution, **Chrome’s “Create Shortcut”** (with “Open as window” checked) is enough to get standalone windows that show up in Command+Tab.
- If you need more features or better isolation, check out **Fluid**, **Coherence**, or **Epichrome** to create a fully separate “app” using Chrome’s engine.
- For maximum customization or cross-platform packaging, try **Nativefier**.

Either way, using site-specific browsers or Chrome’s built-in shortcut feature will help keep each web app separate in your Command+Tab list, making it easier to switch among them without losing your place.


#### You:
<time datetime="2025-01-09T18:16:32.240Z" title="1/10/2025, 3:16:32 AM">03:16</time>

Great. I used https://github.com/nativefier/nativefier

#### ChatGPT:
<time datetime="2025-01-09T18:17:21.149Z" title="1/10/2025, 3:17:21 AM">03:17</time>

Nice choice! Nativefier is a great option if you want maximum flexibility, or if you’re already comfortable working in a command-line environment. Here are a few tips and tricks you might find useful when using Nativefier:

---

## 1. Set a Custom App Name and Icon

- **Name**: Use the `--name "MyApp"` option to set a custom name for your app.
- **Icon**: Use the `--icon /path/to/icon.png` (or `.icns` on macOS) to give your app a unique icon.

For example:

```bash
nativefier "https://example.com" \
  --name "MyExampleApp" \
  --icon /path/to/icon.icns
```

> **Note**: The icon format can differ by platform (PNG for Windows/Linux, ICNS for macOS).

---

## 2. Hide the Menu Bar and Address Bar

- Use `--hide-window-frame` to remove the title bar (if you want a frameless window).
- Use `--disable-context-menu` to prevent right-click context menus in the app.

Example:

```bash
nativefier "https://example.com" \
  --hide-window-frame \
  --disable-context-menu
```

---

## 3. Tweak the Window Size and Behavior

- **Initial Size**: `--width 1280 --height 800`
- **Resizable** or **Not**: `--resizable false`

Example:

```bash
nativefier "https://example.com" \
  --width 1200 --height 800 \
  --resizable false
```

---

## 4. Use a Custom User Agent or Chromium Flags

If you need the site to think you’re using a particular browser (or have certain flags enabled):

- **User agent**: `--user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."`
- **Chromium flags**: `--inject "path/to/script.js"` or `--browserwindow-options "{ \"enableRemoteModule\": false }"`

Example:

```bash
nativefier "https://example.com" \
  --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/..." \
  --browserwindow-options '{ "autoHideMenuBar": true }'
```

---

## 5. Keep or Separate Cookies/Local Storage

By default, Nativefier stores cookies and local data in your generated app’s `AppData` (Windows), `~/.config` (Linux), or Library (macOS) folder. If you want a fresh session each time, or to share session data among different apps, you can tweak how profiles and data directories are handled with additional flags. Check the [Nativefier docs](https://github.com/nativefier/nativefier) for details.

---

## 6. Place the Final App in Your Applications Folder (macOS)

Once Nativefier builds your `.app`, it’s good practice to move it to your **Applications** folder. That way it’ll show up properly in Spotlight and in the **Command+Tab** app switcher (after it’s launched).

1. Drag the generated `.app` into `Applications`.
2. Launch it normally from Applications (or pin it to your Dock).

---

## 7. Build for Multiple Platforms (If Needed)

If you need versions for Windows or Linux, you can specify `--platform`:

```bash
nativefier "https://example.com" \
  --platform "darwin"  # or "win32", "linux"
```

> This requires you to have the appropriate Electron build tools and dependencies available on your system.

---

### That’s It!

With these extra tips, you can tailor your Nativefier-created apps to look and work exactly the way you want. If you run into any oddities (like certain keyboard shortcuts or websites refusing to load in an embedded browser), check the Nativefier GitHub issues page—odds are someone else has run into the same scenario and found a solution.

Enjoy your newly minted, standalone web apps!
