---
title: Ollama Typing Mind Setup
source: https://chatgpt.com/c/67835572-a2bc-8003-87a5-210eb669a9f8
---

# Ollama Typing Mind Setup

#### You:
<time datetime="2025-01-12T05:38:59.034Z" title="1/12/2025, 2:38:59 PM">14:38</time>

Help me with this. Specially with the step to run terminal commands:
````

50+ Advanced ChatGPT Prompts. Get It Free!
logo
BlogGo to app
TypingMind Docs
/
Chat Models Settings
Use with Ollama (local models: LLaVA, Llama2, Mistral, Orca, etc.)
Ollama is an open-source project that allows you to run many LLM models locally on your device.
You can easily config Typing Mind to run with Ollama, below is the full guide:
💡
Note: This instruction is for the Typing Mind Web version (https://www.typingmind.com). For the macOS version and Setapp version, due to Apple’s security policy, requests to http  protocol are blocked. If you want to connect to the macOS app, you can still follow the instructions here, but with one additional step: you need to setup HTTPS for Ollama. This can be done using various techniques (e.g., using a local HTTPS proxy). For more details on how to run Ollama on HTTPS, please reach out to the Ollama project for support.
Download Ollama
Go to https://ollama.com/ and download Ollama to your device.
Image without caption
Set up Ollama environment variables for CORS
Run the following commands so that Ollama allows connection from Typing Mind.

bash

launchctl setenv OLLAMA_HOST "0.0.0.0"
launchctl setenv OLLAMA_ORIGINS "*"

After that, you need to restart Ollama for the changes to take effect.
Once the set up is done, run the following command to start a model (in this example: llama2 )

bash

ollama run llama2

# Output:
>>> 
>>> Send a message (/? for help)

Add Ollama models to Typing Mind
Open Typing Mind and open the Model Setting button, then click “Add Custom Model”. Then enter the details as show in the screenshot below:
Image without caption
Chat with Ollama
Once the model is tested and added successfully, you can select the custom model and chat with it normally.
Image without caption
Image without caption
Use with Hugging Face models
Use with Groq API (LLaMA 3, Mixtral 8x7b, Gemma 7b)
Powered by Notaku
Helpful?
Share
Content
Use with Ollama (local models: LLaVA, Llama2, Mistral, Orca, etc.)
Download Ollama
Set up Ollama environment variables for CORS
Add Ollama models to Typing Mind
Chat with Ollama

👋 Questions? Chat with our AI!×

#### ChatGPT:
<time datetime="2025-01-12T05:39:38.698Z" title="1/12/2025, 2:39:38 PM">14:39</time>

Here’s a more explicit, step-by-step guide on how to run the necessary terminal commands to get **Ollama** working with **Typing Mind**—including the crucial part of setting environment variables for CORS. I’ve included a bit of extra context to expand your knowledge about what’s going on under the hood.

---

## 1. Download & Install Ollama

1. **Visit**: [https://ollama.com](https://ollama.com/)
2. **Download** the version for your operating system (macOS is the primary target, but there are Linux instructions as well in their docs).
3. **Install** Ollama by following their on-screen instructions.

*Why this matters:* Ollama is the local inference server for LLMs (Large Language Models) like *Llama2*, *Mistral*, *Orca*, etc. It allows you to run these models entirely offline on your own hardware (great for privacy and full control).

---

## 2. Set Environment Variables for CORS

To allow Typing Mind to communicate with Ollama running locally, you need to set a couple of environment variables that handle *CORS (Cross-Origin Resource Sharing)*. By default, Ollama may block requests from external origins. These steps effectively whitelist requests to your local machine.

> **Important**: The commands below assume macOS. If you’re on another Unix-based system (like Linux), you would typically replace `launchctl setenv` with `export` in your `~/.bashrc`, `~/.zshrc`, or shell environment.

### macOS Terminal Steps

1. **Open Terminal**
   - Press `Cmd + Space` and type `Terminal`, then press *Enter*.

2. **Set OLLAMA\_HOST**
   ```bash
   launchctl setenv OLLAMA_HOST "0.0.0.0"
   ```
   *This tells Ollama to listen on all IPs (loopback and LAN).*

3. **Set OLLAMA\_ORIGINS**
   ```bash
   launchctl setenv OLLAMA_ORIGINS "*"
   ```
   *This allows connections from any origin (helpful for local testing).*

4. **Restart Ollama (if running)**
   - If Ollama was previously running, quit it and restart.
   - If it wasn’t running, you’re good to proceed.

> **Why `launchctl setenv` on macOS?**\
> `launchctl setenv` sets environment variables for the *launch daemon*, making them available system-wide. This is needed because Ollama runs as a background process in many cases, and we want those variables recognized by that daemon.

---

## 3. Launch the LLM Model in Ollama

Now you’re ready to **start** Ollama using your chosen model. Below is an example using **Llama2**:

```bash
ollama run llama2
```

You should see:

```
>>>
>>> Send a message (/? for help)
```

This indicates Ollama has successfully started and is listening for your input. You can type in your prompts directly here to interact with the model in the Terminal.

*Note: If you prefer other models, like `mistral` or `orca`, just replace `llama2` with the model name you have installed. For instance:*

```bash
ollama run mistral
```

---

## 4. Add Ollama Model to Typing Mind

1. **Open** [Typing Mind](https://www.typingmind.com).

2. **Go to Model Settings** (usually a button or icon in the app).

3. **Click “Add Custom Model.”**

4. **Configure** the following fields:
   - **Base URL**: The address where Ollama is listening (`http://0.0.0.0:11411` typically).
   - **Model name**: For example, “Llama2” or “Mistral.”
   - **Any additional** parameters as needed (temperature, etc.).

5. **Save** your new custom model.

Once added, select this custom model from the Typing Mind interface. Now you can chat with your locally hosted LLM in the same way you would with an online ChatGPT—only it’s running on your machine.

---

## Extra Notes & Terminology

- **CORS**: Stands for *Cross-Origin Resource Sharing*. It’s a security feature in browsers that prevents scripts from making requests to a different domain than the one that served the web page. Here, we’re opening up our local instance (`localhost` or `0.0.0.0`) so that Typing Mind can send requests to Ollama.
- **Environment Variables**: These are key-value pairs in your operating system’s environment. Programs (like Ollama) read them to configure how they should run.
- **Local Model Inference**: By running a model such as *Llama2* locally, you keep your data on your machine and reduce reliance on external APIs or internet connectivity. This is a powerful approach for privacy-conscious tasks or offline usage.
- **GPU vs. CPU**: Depending on your hardware, Ollama can sometimes leverage your GPU for faster inference. If not, it will run on CPU, which might be slower but still offline.

---

### Troubleshooting

- **Permission Denied**: If you get permission errors on macOS, try running the commands with `sudo`. However, be aware that this sets environment variables for the **root** user.
- **Variables Not Working**: Double-check you spelled everything correctly. Also, if you close Terminal and open a new window, sometimes you need to confirm that the variables persist.
- **Can’t Connect**: Make sure any firewall or security settings aren’t blocking the port (default is `11411` for Ollama).

---

## Wrap-up

That’s it! By following the above steps, you’ll have Ollama listening on your local network with CORS configured to accept requests from Typing Mind. You’ll then be able to chat with cutting-edge models like *Llama2*, *Mistral*, *Orca*, and more—all while keeping everything on your own machine.

If you want to experiment with more advanced prompts, you can do so directly in Typing Mind (which integrates your favorite prompt templates) or via the Terminal window running Ollama (for quick testing).

**Enjoy exploring local AI inference**—it’s a great way to deepen your understanding of how large language models work, enhance your privacy, and level up your generative AI capabilities.


#### You:
<time datetime="2025-01-12T05:39:47.117Z" title="1/12/2025, 2:39:47 PM">14:39</time>

launchctl: command not found

#### ChatGPT:
<time datetime="2025-01-12T05:40:12.039Z" title="1/12/2025, 2:40:12 PM">14:40</time>

If your system is saying `launchctl: command not found`, it typically means one of the following:

1. **You’re not on macOS** and `launchctl` simply doesn’t exist on your operating system (it’s unique to macOS).
2. **You are on macOS**, but your shell’s PATH or environment settings aren’t configured in a way that makes `launchctl` visible (quite rare, but possible).
3. **You’re running in a Docker container or similar environment** that might not have `launchctl` installed.

Below are some workarounds, depending on which scenario you’re in.

---

## 1. If You’re on **macOS** But `launchctl` Isn’t Found

1. **Check your PATH**\
   In Terminal, run:
   ```bash
   echo $PATH
   which launchctl
   ```
   If the result of `which launchctl` is empty, your system cannot see `launchctl`. Normally, `launchctl` lives in `/bin/launchctl` on macOS.

2. **Try running the commands from a standard macOS shell**
   - Open the “Terminal” app from Spotlight (Cmd + Space, then type “Terminal”).
   - Execute your commands again:
     ```bash
     launchctl setenv OLLAMA_HOST "0.0.0.0"
     launchctl setenv OLLAMA_ORIGINS "*"
     ```

3. **Check your environment**
   - macOS now defaults to **zsh** instead of **bash**. If you have a custom shell like fish or a custom environment, you may have to switch to zsh or bash to access the system’s `launchctl`.
   - You can switch temporarily by running:
     ```bash
     bash
     ```
     then try the commands again.

If you still can’t use `launchctl`, you can set environment variables the usual Unix way (explained in section **2** below).

---

## 2. If You’re on **Linux** (or any non-macOS system)

`launchctl` is a macOS utility, so you won’t have it on Linux. Instead, you just export the environment variables in your shell. For example, if you use **bash** or **zsh**, you can do:

```bash
export OLLAMA_HOST="0.0.0.0"
export OLLAMA_ORIGINS="*"
```

After that, you can run:

```bash
ollama run llama2
```

This will launch Ollama with those environment variables set for your **current** shell session.

**Note**: If you want these variables always set for your user, add those `export` commands to your `~/.bashrc` or `~/.zshrc`, depending on which shell you use.

---

## 3. Setting Host and Origins Directly When Running Ollama

As an alternative to environment variables, recent versions of **Ollama** allow specifying host and origins via flags. For example:

```bash
ollama --host 0.0.0.0 --origins "*" run llama2
```

This way, you **don’t** need to rely on environment variables or `launchctl`. Check the Ollama documentation (`ollama --help`) for the exact usage, because flags can change between releases.

---

## 4. Verifying CORS is Working

1. **Run Ollama** with your chosen approach (environment variables or flags).
2. **Open Typing Mind** and set the Base URL to `http://0.0.0.0:11411` (or whichever port your Ollama is using).
3. **Test a sample prompt**. If everything is correct, you should see a response from the local model.
4. If you get a CORS error in your browser console, double-check the `--origins` parameter or your exported environment variables.

---

## 5. Quick Reference: Single Command per OS

- **macOS** (if `launchctl` works):
  ```bash
  launchctl setenv OLLAMA_HOST "0.0.0.0"
  launchctl setenv OLLAMA_ORIGINS "*"
  ollama run llama2
  ```

- **macOS / Linux** (exporting vars):
  ```bash
  export OLLAMA_HOST="0.0.0.0"
  export OLLAMA_ORIGINS="*"
  ollama run llama2
  ```

- **Mac / Linux** (using Ollama flags):
  ```bash
  ollama --host 0.0.0.0 --origins "*" run llama2
  ```

---

### Why So Many Different Approaches?

- **`launchctl setenv`** is a macOS-specific method of setting system-wide environment variables that background services and GUI apps can also see.
- **`export VAR="value"`** is the standard, cross-platform (Unix-like) way to set environment variables in the current shell session.
- **CLI flags** (like `--host` and `--origins`) are convenient if you don’t want to mess with environment variables at all.

---

## Summary

If `launchctl` isn’t found, you’re likely on a non-macOS system or using a shell environment that doesn’t include `launchctl`. Use `export` or Ollama’s CLI flags to set your host and origins. Once that’s done, you can integrate Ollama with Typing Mind by configuring Typing Mind’s “Custom Model” settings to point to the local Ollama server. Then you’ll be able to chat with models like Llama2, Mistral, or Orca entirely offline in Typing Mind. Enjoy exploring local AI!


#### You:
<time datetime="2025-01-12T05:40:14.467Z" title="1/12/2025, 2:40:14 PM">14:40</time>

This is an ubuntu server

#### ChatGPT:
<time datetime="2025-01-12T05:40:56.096Z" title="1/12/2025, 2:40:56 PM">14:40</time>

Below is the **Linux (Ubuntu)–friendly** approach to getting Ollama running and accessible to Typing Mind, **without** using `launchctl` (which is macOS-specific). We’ll cover:

1. **Installing Ollama** on Ubuntu
2. **Setting environment variables** (CORS-related) in a typical Linux way
3. **Running Ollama** with the environment variables
4. **Optional**: Using flags instead of environment variables

---

## 1. Install Ollama on Ubuntu

As of this writing, Ollama does not have an official `.deb` package for Ubuntu, so you’ll need to either:

- **Build from source** (from [Ollama’s GitHub](https://github.com/jmorganca/ollama))
- **Use a script** provided by Ollama (if available)

### Example: Build from Source

1. **Install prerequisites**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential git
   ```
2. **Clone the Ollama repository**:
   ```bash
   git clone https://github.com/jmorganca/ollama.git
   ```
3. **Build Ollama**:
   ```bash
   cd ollama
   make build
   sudo make install
   ```
   Depending on the instructions in their repo, the exact commands may vary.

*(If you already have Ollama installed through another method, skip these steps.)*

---

## 2. Set Environment Variables for CORS

On Ubuntu (and most Linux distros), you **cannot** use `launchctl`; that’s for macOS. Instead, you typically **export** environment variables in your shell.

### Quick One-Time Export

In your current terminal session, run:

```bash
export OLLAMA_HOST="0.0.0.0"
export OLLAMA_ORIGINS="*"
```

- `OLLAMA_HOST="0.0.0.0"` makes Ollama listen on all network interfaces (rather than just `localhost`).
- `OLLAMA_ORIGINS="*"` allows requests from any external origin (necessary for cross-origin requests from Typing Mind).

> **Important**: These `export` statements apply **only** to the current shell session. If you open a new terminal, you’ll need to re-export them or place them in your `~/.bashrc` or `~/.zshrc`.

---

## 3. Run Ollama

Now start Ollama with your desired model:

```bash
ollama run llama2
```

When Ollama starts, you should see something like:

```
>>>
>>> Send a message (/? for help)
```

This means Ollama is running and listening for input on port `11411` (by default).

At this point, because you exported `OLLAMA_HOST` and `OLLAMA_ORIGINS`, remote clients (like Typing Mind) should be able to connect.

---

## 4. Configure Typing Mind

1. **Open** Typing Mind (web version) in a browser.
2. **Go to “Model Settings.”**
3. **Select “Add Custom Model.”**
4. **Enter** something like:
   - **Base URL**: `http://<YOUR_SERVER_IP>:11411` (or `http://0.0.0.0:11411` if local).
   - **Model name**: “Llama2” (or whichever model you’re running).
5. **Save** and select this custom model.

Test a prompt to confirm that Typing Mind can talk to Ollama running on your Ubuntu server.

---

## 5. (Optional) Use Flags Instead of Environment Variables

Newer versions of Ollama allow you to specify CORS-related settings via command-line flags. In other words, you don’t need to do any `export` if you **append flags** like so:

```bash
ollama --host 0.0.0.0 --origins "*" run llama2
```

That single command tells Ollama to listen on all interfaces (`--host 0.0.0.0`) and allow all request origins (`--origins "*"`) for cross-origin requests.

---

## 6. Making It Persist (If Needed)

If you want Ollama to **always** start on boot with those variables or flags, you have a few options:

1. **Systemd service** – create a `.service` file that runs `ollama` with the needed flags, so it starts automatically at boot.
2. **Add to `~/.bashrc` or `~/.zshrc`** – if you only need Ollama accessible whenever you personally log in.
3. **Use a process manager** like `pm2`, `supervisord`, or `screen/tmux` sessions to keep it running in the background.

---

## Common Troubleshooting on Ubuntu

1. **Port 11411 already in use**: If Ollama can’t bind to `11411`, check if another service is using that port (e.g., `sudo lsof -i :11411`).
2. **Firewall blocking connections**: If you can’t access Ollama from another computer, ensure Ubuntu’s firewall (if enabled) or your hosting provider’s firewall is open on port 11411.
3. **Permission issues**: If you see `permission denied` errors when installing or running, try `sudo` carefully or ensure your user has correct privileges.

---

## Summary

- **`launchctl`** is macOS-only.
- On **Ubuntu**, use `export` or **CLI flags** (`--host`, `--origins`) to set CORS parameters for Ollama.
- Then **run Ollama** with your chosen LLM and point **Typing Mind** to your server’s IP and port (`:11411`).
- **Enjoy local inference** of Llama2, Mistral, Orca, etc., all on your own hardware.

That’s it! You should now be able to run Ollama on an Ubuntu server and connect via Typing Mind. If you have any further issues, feel free to follow up or consult [Ollama’s official GitHub](https://github.com/jmorganca/ollama) for more details.
