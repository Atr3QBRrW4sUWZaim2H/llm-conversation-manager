---
title: Homebrew on Musl Issues
source: https://chatgpt.com/c/6795a5c0-4980-8003-9a6a-c96f72b51970
---

# Homebrew on Musl Issues

#### You:
<time datetime="2025-01-26T03:13:08.173Z" title="1/26/2025, 12:13:08 PM">12:13</time>

root@ranch-router:~# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
==> Checking for `sudo` access (which may request your password)...
Don't run this as root!


#### ChatGPT:
<time datetime="2025-01-26T03:13:20.193Z" title="1/26/2025, 12:13:20 PM">12:13</time>

Homebrew’s install script explicitly refuses to run as the root user. The short answer is: **you need to run the installation under a non-root user**. Below are a few possible approaches and tips for getting Homebrew installed on a system where you currently only have root access.

---

## Why Homebrew refuses to run as root

Homebrew is designed with the expectation that packages and their directories are owned by a regular user, not by the superuser. This helps prevent accidental system-wide damage or security issues. Consequently, Homebrew’s default install script will bail out with `Don't run this as root!` whenever it detects you’re running as root.

---

## Approach 1: Create a non-root user

1. **Create a new user** (if you don’t already have one):
   ```sh
   adduser myuser
   ```
   (Replace `myuser` with your preferred username.)

2. **Switch to that user**:
   ```sh
   su - myuser
   ```

3. **Run the Homebrew installer as that user**:
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   The installation script should now proceed without throwing the “Don’t run this as root!” error.

---

## Approach 2: Use a non-root user within Docker or a container

If you’re in a container (e.g., Rancher, Docker, etc.), you can modify your `Dockerfile` or container setup to:

1. Create a new user in the container.
2. Switch to that user (`USER myuser` in Dockerfile) before running `curl` or the script.
3. Run the script as non-root inside the container.

Example snippet in a Dockerfile:

```dockerfile
FROM ubuntu:latest

# Create a user
RUN useradd -m brewuser

# Switch to that user
USER brewuser
WORKDIR /home/brewuser

# Install Homebrew
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Approach 3: Manual “Tarball” style install

If you **really** cannot create a non-root user for some reason, you can install Homebrew from a compressed tarball. This is an advanced approach and not officially documented in detail, but you can:

1. **Clone** the Homebrew Git repository manually:
   ```sh
   git clone https://github.com/Homebrew/brew /usr/local/Homebrew
   ```
   (Or a directory of your choosing—just be consistent.)

2. **Add Homebrew to your `PATH`**:
   ```sh
   echo 'eval "$(/usr/local/Homebrew/bin/brew shellenv)"' >> /root/.bashrc
   eval "$(/usr/local/Homebrew/bin/brew shellenv)"
   ```

3. **Manually ensure file permissions** for whatever user or group you want to give “ownership” of the Homebrew directories. However, this is highly **not recommended**, because it can lead to permission issues with installed packages, system conflicts, and it defeats some of the security models that Homebrew tries to maintain.

---

## Best practice

The simplest and safest route is always:

1. **Create a regular (non-root) user.**
2. **Run the Homebrew install script as that user.**

This avoids permissions headaches and respects Homebrew’s security and directory structure assumptions.

---

### Summary

- **Don’t run Homebrew’s install script directly as root.**
- **Use a separate user** (regular user in a VM, container, or on the physical machine).
- If you can’t, you’ll have to resort to a non-standard, manual install and handle all the permissions details yourself.

Using a dedicated non-root user is by far the recommended and officially supported solution.


#### You:
<time datetime="2025-01-26T03:14:35.705Z" title="1/26/2025, 12:14:35 PM">12:14</time>

Linux ranch-router 4.19.152-ui-alpine #4.19.152 SMP Tue Dec 24 22:57:14 CST 2024 aarch64

Firmware version: v4.1.13

  ___ ___      .__________.__
 |   |   |____ |__\_  ____/__|
 |   |   /    \|  ||  __) |  |   (c) 2010-2025
 |   |  |   |  \  ||  \   |  |   Ubiquiti Inc.
 |______|___|  /__||__/   |__|
            |_/                  https://www.ui.com

      Welcome to UniFi Dream Machine Pro!

********************************* NOTICE **********************************
* By logging in to, accessing, or using any Ubiquiti product, you are     *
* signifying that you have read our Terms of Service (ToS) and End User   *
* License Agreement (EULA), understand their terms, and agree to be       *
* fully bound to them. The use of CLI (Command Line Interface) can        *
* potentially harm Ubiquiti devices and result in lost access to them and *
* their data. By proceeding, you acknowledge that the use of CLI to       *
* modify device(s) outside of their normal operational scope, or in any   *
* manner inconsistent with the ToS or EULA, will permanently and          *
* irrevocably void any applicable warranty.                               *
***************************************************************************
Last login: Sat Jan 25 19:11:57 2025 from 192.168.1.201
root@ranch-router:~# 
root@ranch-router:~# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
==> Checking for `sudo` access (which may request your password)...
Don't run this as root!
root@ranch-router:~# adduser homebrew
Adding user `homebrew' ...
Adding new group `homebrew' (1000) ...
Adding new user `homebrew' (1000) with group `homebrew' ...
Creating home directory `/home/homebrew' ...
Copying files from `/etc/skel' ...
New password: 
Retype new password: 
passwd: password updated successfully
Changing the user information for homebrew
Enter the new value, or press ENTER for the default
        Full Name []: 
        Room Number []: 
        Work Phone []: 
        Home Phone []: 
        Other []: 
Is the information correct? [Y/n] y
root@ranch-router:~# su - brew
su: user brew does not exist or the user entry does not contain all the required fields
root@ranch-router:~# su - homebrew
homebrew@ranch-router:~$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
==> Checking for `sudo` access (which may request your password)...
Sorry, user homebrew may not run sudo on ranch-router.
Insufficient permissions to install Homebrew to "/home/linuxbrew/.linuxbrew" (the default prefix).

Alternative (unsupported) installation methods are available at:
https://docs.brew.sh/Installation#alternative-installs

Please note this will require most formula to build from source, a buggy, slow and energy-inefficient experience.
We will close any issues without response for these unsupported configurations.
homebrew@ranch-router:~$ 2025 Jan 25 19:13:52 ranch-router homebrew : command not allowed ; TTY=pts/0 ; PWD=/home/homebrew ; USER=root ; COMMAND=validate
2025 Jan 25 19:13:52 ranch-router homebrew : command not allowed ; TTY=pts/0 ; PWD=/usr ; USER=root ; COMMAND=validate

#### ChatGPT:
<time datetime="2025-01-26T03:15:05.609Z" title="1/26/2025, 12:15:05 PM">12:15</time>

It’s quite common to run into issues installing Homebrew on locked-down or embedded systems such as the UniFi Dream Machine Pro (UDM Pro). By design, Ubiquiti does not intend the UDM Pro to be used as a general-purpose Linux server, so *many typical Linux features (like `sudo` for non-root users) are restricted or missing entirely.* As a result, the “normal” Homebrew installer fails, because:

1. It refuses to run as `root`.
2. It expects a non-root user who *can* run `sudo` to perform system tasks.
3. The default installation prefix on Linux (`/home/linuxbrew/.linuxbrew`) also generally requires `sudo` or system-level changes.

Despite these hurdles, you *can* do a manual, “unsupported” installation of Homebrew. **However, be aware this is not recommended, not officially supported, and often leads to incomplete or broken package installations**—especially on a restricted OS like the UDM Pro’s **busybox/alpine** variant. That said, if you’d like to experiment, here’s how.

---

## 1. Create a non-root user (already done)

You’ve already created the user `homebrew`:

```sh
adduser homebrew
```

Then you can log in:

```sh
su - homebrew
```

You’ve confirmed that `sudo` is locked down for `homebrew` (you cannot edit `/etc/sudoers` or install packages). This means the normal Homebrew install script will fail.

---

## 2. Perform a **manual** (git-based) Homebrew installation

We’ll install Homebrew into the home directory of `homebrew` user, at `~/.linuxbrew`.

### 2.1 Ensure you have `git` (or get it somehow)

Check if you have `git` in the UDM Pro environment:

```sh
which git
```

- If `git` is missing, you may be stuck unless you can copy a statically compiled `git` binary onto the device. The Dream Machine Pro does not normally allow installing packages in the usual sense.

Assuming `git` is available (or you have manually placed it in `/usr/bin/git` or similar):

### 2.2 Clone the Homebrew repository

```sh
mkdir -p ~/.linuxbrew/Homebrew
git clone https://github.com/Homebrew/brew.git ~/.linuxbrew/Homebrew
```

### 2.3 Add the `brew` executables to your PATH

Create a bin directory and symlink the `brew` binary:

```sh
mkdir -p ~/.linuxbrew/bin
ln -s ../Homebrew/bin/brew ~/.linuxbrew/bin/brew
```

Then, **add** this to your shell initialization (e.g., `~/.profile` or `~/.bashrc`):

```sh
echo 'eval "$(/home/homebrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
```

Reload your shell or just run:

```sh
eval "$(/home/homebrew/.linuxbrew/bin/brew shellenv)"
```

### 2.4 Verify your Homebrew installation

Now try:

```sh
brew --version
```

You should see some output indicating Homebrew’s version. If it fails, verify your symlinks and paths.

---

## 3. Expect everything to build from source (and often fail)

With no `sudo` privileges and no typical system package manager, Homebrew on the UDM Pro:

1. **Can’t install needed libraries** (like compilers, required system packages, etc.) from the OS.
2. **Bottle (binary) packages** are mostly not made for Alpine or for the Dream Machine’s aarch64 environment.
3. Homebrew will fall back to building everything from source, which **requires** a working compiler toolchain (e.g. `gcc`, `make`, etc.).
4. If the system is missing these development tools (which is very likely on the UDM Pro), the build process will fail.

In other words, you might see endless errors about missing `cc`, missing headers, or “no formula for …” etc.

---

## 4. Potential Workarounds

1. **Manually add build tools.** On typical Linux distros, you’d just do `sudo apt install build-essential git`. On the UDM Pro, you do not have that option. The OS is minimal and read-only in many places. You’d have to drop in static binaries or cross-compile them elsewhere and copy them to the device—very advanced.
2. **Use a container** approach if your UDM Pro firmware allows running Docker or Podman inside. Then you could have a more “normal” Linux environment inside a container, with a normal package manager. This is still quite hacky.
3. **Use an external system** (like a Raspberry Pi, a VM, or another Linux machine) for the tasks you want to do with Homebrew. Then copy over any resulting binaries to the UDM Pro if you truly need them there.

---

## 5. Summing Up

- **Officially, it’s not recommended nor supported** to install Homebrew on the Dream Machine Pro.
- If you want to proceed anyway, you must do a **manual git-based “tarball”** style install in your home directory.
- You’ll likely need to build everything from source (which usually requires a development toolchain).
- The Dream Machine Pro’s OS is **locked down** and **lacks normal Linux distribution tools**.

In many cases, you’ll find it’s far simpler to set up a standard Linux VM or Raspberry Pi on your LAN to run Homebrew-based software, rather than hacking the UDM Pro’s shell. If you do decide to experiment on the UDM Pro, proceed with caution—**it’s easy to break core Ubiquiti services** and your warranty or official support may be voided.
