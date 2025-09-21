---
title: Homebrew Installation Setup
source: https://chatgpt.com/c/6785cc44-bee8-8003-93e4-24fd200578c7
---

# Homebrew Installation Setup

#### You:
<time datetime="2025-01-14T02:31:23.454Z" title="1/14/2025, 11:31:23 AM">11:31</time>

ashwin@Macbook-Air-M3 scripts % brew install firefoxpwa
zsh: command not found: brew
ashwin@Macbook-Air-M3 scripts % cd ~
ashwin@Macbook-Air-M3 ~ % cd /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
cd: too many arguments
ashwin@Macbook-Air-M3 ~ % /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
==> Checking for `sudo` access (which may request your password)...
Password:
==> This script will install:
/opt/homebrew/bin/brew
/opt/homebrew/share/doc/homebrew
/opt/homebrew/share/man/man1/brew.1
/opt/homebrew/share/zsh/site-functions/_brew
/opt/homebrew/etc/bash_completion.d/brew
/opt/homebrew

Press RETURN/ENTER to continue or any other key to abort:
==> /usr/bin/sudo /usr/sbin/chown -R ashwin:admin /opt/homebrew
==> Downloading and installing Homebrew...
remote: Enumerating objects: 1407, done.
remote: Counting objects: 100% (556/556), done.
remote: Compressing objects: 100% (83/83), done.
remote: Total 1407 (delta 519), reused 473 (delta 473), pack-reused 851 (from 4)
==> Updating Homebrew...
Updated 2 taps (homebrew/core and homebrew/cask).
Warning: /opt/homebrew/bin is not in your PATH.
  Instructions on how to configure your shell for Homebrew
  can be found in the 'Next steps' section below.
==> Installation successful!

==> Homebrew has enabled anonymous aggregate formulae and cask analytics.
Read the analytics documentation (and how to opt-out) here:
  https://docs.brew.sh/Analytics
No analytics data has been sent yet (nor will any be during this install run).

==> Homebrew is run entirely by unpaid volunteers. Please consider donating:
  https://github.com/Homebrew/brew#donations

==> Next steps:
- Run these commands in your terminal to add Homebrew to your PATH:
    echo >> /Users/ashwin/.zprofile
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/ashwin/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
- Run brew help to get started
- Further documentation:
    https://docs.brew.sh

ashwin@Macbook-Air-M3 ~ % echo >> /Users/ashwin/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/ashwin/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
ashwin@Macbook-Air-M3 ~ % brew install firefoxpwa
==> Downloading https://ghcr.io/v2/homebrew/core/firefoxpwa/manifests/2.13.2
############################################################################################################################################################### 100.0%
==> Fetching firefoxpwa
==> Downloading https://ghcr.io/v2/homebrew/core/firefoxpwa/blobs/sha256:fd891b5a51d292a0eac3b2dc885bf6fa5f75a7c802bf1a5b1c2091f751054d47
############################################################################################################################################################### 100.0%
==> Pouring firefoxpwa--2.13.2.arm64_sequoia.bottle.tar.gz
==> Caveats
To use the browser extension, manually link the app manifest with:
  sudo mkdir -p "/Library/Application Support/Mozilla/NativeMessagingHosts"
  sudo ln -sf "/opt/homebrew/opt/firefoxpwa/share/firefoxpwa.json" "/Library/Application Support/Mozilla/NativeMessagingHosts/firefoxpwa.json"

zsh completions have been installed to:
  /opt/homebrew/share/zsh/site-functions
==> Summary
🍺  /opt/homebrew/Cellar/firefoxpwa/2.13.2: 55 files, 17.3MB
==> Running `brew cleanup firefoxpwa`...
Disable this behaviour by setting HOMEBREW_NO_INSTALL_CLEANUP.
Hide these hints with HOMEBREW_NO_ENV_HINTS (see `man brew`).
ashwin@Macbook-Air-M3 ~ % 

#### ChatGPT:
<time datetime="2025-01-14T02:31:57.593Z" title="1/14/2025, 11:31:57 AM">11:31</time>

It looks like you’ve successfully installed **FirefoxPWA** via Homebrew. Here’s what to do next and how to get started using it:

---

## 1. Add the FirefoxPWA Native Messaging Host Manifest (Optional, but Recommended)

This step is only necessary if you want to integrate the **browser extension** (so that PWAs installed through FirefoxPWA show up as distinct apps).

**Terminal commands:**

```bash
sudo mkdir -p "/Library/Application Support/Mozilla/NativeMessagingHosts"
sudo ln -sf "/opt/homebrew/opt/firefoxpwa/share/firefoxpwa.json" "/Library/Application Support/Mozilla/NativeMessagingHosts/firefoxpwa.json"
```

What this does:

- `mkdir -p` ensures that the folder `/Library/Application Support/Mozilla/NativeMessagingHosts` exists.
- `ln -sf` creates (or updates) a symbolic link so that Firefox can find the **FirefoxPWA** native messaging file `firefoxpwa.json`.

If you do **not** want to use the extension, you can skip this. However, linking the manifest makes it possible for FirefoxPWA to manage apps more seamlessly.

---

## 2. Make Sure Homebrew is in Your PATH

Homebrew’s “Next steps” message suggests adding the following lines to your `~/.zprofile` (you’ve likely already done this, but just double-check):

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

If you open a new terminal and type `which firefoxpwa`, it should point to `/opt/homebrew/bin/firefoxpwa` (or similar). If it doesn’t, close and reopen your terminal or source your `~/.zprofile`:

```bash
source ~/.zprofile
```

---

## 3. Using FirefoxPWA

Once installed, **FirefoxPWA** provides commands that let you install, open, list, or remove PWAs (Progressive Web Apps). Common commands include:

1. **Install a site as a PWA**

   ```bash
   firefoxpwa install <URL> [--name "Custom App Name"] [--icon /path/to/icon.png]
   ```

   **Example:**

   ```bash
   firefoxpwa install https://twitter.com --name "Twitter" --icon ~/Downloads/twitter-icon.png
   ```

   - This will create a self-contained PWA in your Applications folder (or wherever you specify).
   - You can optionally provide a custom name and icon; otherwise, FirefoxPWA will try to use the site’s metadata.

2. **Open a previously installed PWA**

   ```bash
   firefoxpwa open <URL or App Name>
   ```

   - For instance, if you installed Twitter as shown above, you could do:

     ```bash
     firefoxpwa open Twitter
     ```

     or

     ```bash
     firefoxpwa open https://twitter.com
     ```

3. **List installed PWAs**

   ```bash
   firefoxpwa list
   ```

   - This shows all PWAs you’ve installed with FirefoxPWA, along with their installation paths.

4. **Uninstall a PWA**

   ```bash
   firefoxpwa uninstall <URL or App Name>
   ```

   - Cleans up the generated app, icon, etc.

---

## 4. Updating and Uninstalling FirefoxPWA

- **Update** FirefoxPWA to the latest version:

  ```bash
  brew update
  brew upgrade firefoxpwa
  ```

- **Uninstall** FirefoxPWA:

  ```bash
  brew uninstall firefoxpwa
  ```

  If you no longer want the linked manifest for the browser extension, you can remove it:

  ```bash
  sudo rm "/Library/Application Support/Mozilla/NativeMessagingHosts/firefoxpwa.json"
  ```

---

## 5. Further Documentation

- **FirefoxPWA GitHub repository**:\
  <https://github.com/MrAlex94/FireFoxPWA>\
  Contains more detailed usage instructions, troubleshooting tips, and development notes.

- **Homebrew documentation**:\
  <https://docs.brew.sh>\
  Helpful if you’re new to Homebrew and want to learn more about installing or managing packages on macOS.

---

### That’s it!

With FirefoxPWA installed, you can now create and manage “true” web app experiences in Firefox. Enjoy your new PWAs!
