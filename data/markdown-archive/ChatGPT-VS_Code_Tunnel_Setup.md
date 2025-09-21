---
title: VS Code Tunnel Setup
source: https://chatgpt.com/c/67b0b718-63cc-8003-9dd3-f7c09de6f08f
---

# VS Code Tunnel Setup

#### You:
<time datetime="2025-02-15T15:47:36.887Z" title="2/16/2025, 12:47:36 AM">00:47</time>

set up a github or microsoft tunnel on my remove vs code server. i have ssh access to the server but the IDE i am using cannot ssh  to a linux server. so i would like to use an alternative connectiopn method

#### ChatGPT:
<time datetime="2025-02-15T15:47:49.604Z" title="2/16/2025, 12:47:49 AM">00:47</time>

Below is a step-by-step guide to setting up a “tunnel” connection so you can develop on a remote Linux server without needing your local IDE to directly SSH into that server. We’ll cover **VS Code Remote Tunnels**, an official Microsoft solution, and briefly mention **GitHub Codespaces** as an alternative. Both options let you connect to a remote environment (where you *do* have SSH access) through a secure tunnel, bypassing the need for direct SSH in your local IDE.

---

## 1. Overview of the Tunneling Options

### **Visual Studio Code Remote Tunnels**

- Developed by Microsoft as part of the VS Code family.
- Lets you run a special “tunnel agent” on the remote machine.
- You then connect to that remote environment from your local VS Code or from a web-based VS Code session (e.g. <https://vscode.dev>).
- No need to open ports or rely on your local machine’s SSH ability.

### **GitHub Codespaces**

- Hosted development environment managed by GitHub.
- Can spin up a dev container in the cloud (on GitHub’s servers) and connect from your local VS Code or via browser.
- Requires pushing your code to GitHub and creating a Codespace from the repo.

If you already have a remote Linux server where you have SSH access, but your local IDE cannot SSH, then **VS Code Remote Tunnels** is often the simplest solution to connect those dots.

---

## 2. Setting Up VS Code Remote Tunnels

Below is the process to set up **VS Code Remote Tunnels** on a remote Linux machine.

### **Prerequisites**

1. **SSH Access** to your remote server (which you already have).
2. **VS Code (latest)** on your local machine, or be prepared to use the [web version](https://vscode.dev).
3. A **Microsoft or GitHub account**. You will sign in with one of these when creating a tunnel.

### **Step-by-Step Guide**

#### **Step 1: Install/Update VS Code on the Remote Machine (Headless)**

- If you can install the full VS Code on the remote, great. However, typically for a headless server, you only need the `code` CLI from VS Code or the “Remote Tunnels” standalone CLI.
- On many distros, you can do:

  ```bash
  # For Debian/Ubuntu:
  sudo apt-get update
  sudo apt-get install wget gpg
  wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
  sudo install -o root -g root -m 644 microsoft.gpg /usr/share/keyrings/
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft.gpg] \
  https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
  sudo apt-get update
  sudo apt-get install code
  ```

  Alternatively, you can install a lightweight, headless build of the VS Code server if you don’t want the entire desktop version. Refer to the [VS Code Remote Tunnels docs](https://code.visualstudio.com/docs/remote/tunnels#_install-the-remote-tunnel-agent) for details on that approach.

#### **Step 2: Sign In and Start a Tunnel**

1. **SSH** into your remote server as usual (the step you can already do).
2. Run the following command:

   ```bash
   code tunnel
   ```

   - If this is your first time, it will prompt you to **sign in** using either your GitHub or Microsoft account.
   - Once signed in, the CLI will start listening and give you a **tunnel name** or **connection ID**.

   If the command `code` is not found, ensure you installed VS Code or the Remote Tunnels agent properly (see Step 1).

> **Tip**: You can also run `code tunnel --help` to see additional options like specifying a custom name for your tunnel or running it in the background.

#### **Step 3: Connect From Local VS Code**

1. On your local computer, open **Visual Studio Code**.
2. Make sure the [**Remote Tunnels extension**](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-server) is installed. In the **Extensions** view, search for *“Remote Tunnels”*.
3. **Sign in** locally with the same GitHub/Microsoft account you used on the server.
   - Easiest way: After installing the extension, open the **Command Palette** (`Ctrl/Cmd + Shift + P`) and type *“Remote Tunnels: Connect to Tunnel”* or just click “Remote Explorer” in the Activity Bar.
4. In the Remote Explorer (Tunnels section), you should see a list of available tunnels associated with your account.
5. Click on the tunnel that you started on your remote server; VS Code will then connect to it.

At this point, your local VS Code will be effectively remoted into the server environment over the tunnel, without requiring local SSH connectivity.

#### **Step 4: Keep the Tunnel Alive**

- By default, `code tunnel` runs interactively in your SSH session. That means if you log out, the tunnel shuts down.
- To keep it running in the background:
  1. Use `tmux` or `screen` (or any process manager) to keep that session alive, **or**
  2. Use the `code tunnel service` commands (preview feature) or systemd services to run it as a service on the remote.

Check the official docs on “running as a service” if you want the tunnel up 24/7.

---

## 3. Using the Tunnel in a Browser (Optional)

If you prefer a browser-based approach (or your local IDE doesn’t support the tunnel extension), you can also connect using [**vscode.dev**](https://vscode.dev/).

1. Go to <https://vscode.dev/tunnel>.
2. Sign in with the same GitHub/Microsoft account.
3. You’ll see your active tunnels and be able to open them in the web-based version of VS Code.

This is a nice fallback if your local IDE environment is restricted or if you want to quickly edit from another machine.

---

## 4. (Alternative) Using GitHub Codespaces

**GitHub Codespaces** is another approach if you prefer a fully managed environment:

1. Push your code to a **GitHub repository**.
2. On GitHub, click the **“Code”** drop-down in your repo and choose **“Codespaces”** → **“Create codespace on main”** (or any branch).
3. Once the Codespace is created, open in the browser or connect from local VS Code by installing the [GitHub Codespaces extension](https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces).

However, note that Codespaces runs on GitHub’s servers, not your private server. So if you specifically need to run on your own remote hardware, **VS Code Remote Tunnels** is the better choice.

---

## 5. Troubleshooting & Key Points

1. **Authentication**\
   Make sure you use the **same** GitHub or Microsoft account for both the remote tunnel (`code tunnel` on the server) and your local VS Code or vscode.dev environment.

2. **Port Conflicts**\
   The tunnel typically communicates over a secure connection out to Microsoft’s servers. You don’t have to open any inbound ports on your remote server, but the remote must be able to make outbound connections on standard HTTPS ports.

3. **Firewall Rules**\
   If you have an outbound firewall restricting traffic on your server, ensure you allow outbound traffic to Microsoft’s tunnel endpoints.

4. **Staying Logged In**\
   If you run `code tunnel` in an interactive SSH session, you’ll need to keep that session alive or run it as a service. Otherwise, the tunnel closes when the session ends.

---

## Summary

- **VS Code Remote Tunnels** is a straightforward way to connect your local IDE (VS Code) to a remote server *without requiring local SSH* capabilities.
- All you do is install & sign in on the remote, run `code tunnel`, then sign in locally to the same account.
- You can also connect from a browser via <https://vscode.dev/tunnel>.
- Alternatively, **GitHub Codespaces** offers a similar approach hosted by GitHub, but that involves hosting your code on GitHub’s servers rather than your own machine.

With these methods, you’ll have a frictionless, secure tunnel that will allow code editing, debugging, and all your usual development workflows—no direct SSH from your local IDE required. This also ties in nicely with concepts like *Dev Containers*, *Containers-as-a-Service*, and advanced ephemeral dev environments if you want to continue expanding your knowledge in remote development practices.


#### You:
<time datetime="2025-02-15T15:50:41.236Z" title="2/16/2025, 12:50:41 AM">00:50</time>

code tunnel worked. how do i make sure that this tunnel is always open

#### ChatGPT:
<time datetime="2025-02-15T15:50:58.249Z" title="2/16/2025, 12:50:58 AM">00:50</time>

Keeping your **VS Code Remote Tunnel** running continuously (even after you detach your SSH session or reboot the server) typically involves running `code tunnel` as a background service. Below are two common approaches:

1. **Using a terminal multiplexer** (like `tmux` or `screen`)
2. **Setting up a systemd service** to start the tunnel at boot

---

## 1. Using a Terminal Multiplexer

If you just need to keep the tunnel running while you remain logged in (but your SSH session might disconnect briefly), a quick fix is to use a **terminal multiplexer** such as `tmux` or `screen`.

1. **SSH** into your server.
2. Start a `tmux` session:
   ```bash
   tmux new -s mytunnel
   ```
3. Inside that tmux session, run:
   ```bash
   code tunnel
   ```
4. Detach from `tmux` by pressing `Ctrl+B`, then `D`.

The tunnel continues running in the background within that `tmux` session. You can reattach anytime with:

```bash
tmux attach -t mytunnel
```

However, if the server reboots or the `tmux` process stops, you lose the tunnel. For a more permanent solution, proceed with **systemd**.

---

## 2. Running `code tunnel` as a Systemd Service

If you want the tunnel to survive **reboots** and always restart automatically, a **systemd service** is more robust. Below is a general recipe on many Linux distributions (e.g. Ubuntu, Debian, CentOS, etc.).

### **Step 1: Interactive Login (One-Time)**

You must ensure you have run `code tunnel` interactively at least **once** so that your GitHub/Microsoft sign-in credentials are stored locally. For example:

```bash
code tunnel
```

- Complete the sign-in process in your browser when prompted.
- Verify that the tunnel is working.
- Press `Ctrl + C` to stop the tunnel after you’ve confirmed it’s functional.

This one-time sign-in ensures that future headless runs of `code tunnel` do not prompt again.

> **Note:** The credentials are typically stored in `~/.config/Code/User/globalStorage/ms-vscode.remote-server/tokens.json`. Make sure the user who runs the systemd service has access to that file.

### **Step 2: Create a systemd Service File**

Create a new service file—let’s call it `vscodetunnel.service`:

```bash
sudo nano /etc/systemd/system/vscodetunnel.service
```

Paste the following contents:

```ini
[Unit]
Description=VS Code Remote Tunnel
After=network.target

[Service]
Type=simple

# Replace 'YOUR_USERNAME' with the user that ran 'code tunnel' interactively
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME

# Example command:
# You can specify a tunnel name with --name if you like.
ExecStart=/usr/bin/code tunnel --name myPersistentTunnel

# Keep trying to restart if the tunnel drops
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Key points**:

- `User=` is the user that owns the configuration where your `code tunnel` credentials are stored.
- `ExecStart=` is the exact command you want run. If your `code` binary is located in a different path, adjust accordingly.
- The `--name myPersistentTunnel` argument is optional but helpful to have a consistent tunnel name.

### **Step 3: Enable and Start the Service**

1. Reload systemd to pick up the new service file:
   ```bash
   sudo systemctl daemon-reload
   ```
2. Enable the service to start on boot:
   ```bash
   sudo systemctl enable vscodetunnel
   ```
3. Start it immediately:
   ```bash
   sudo systemctl start vscodetunnel
   ```

### **Step 4: Verify the Tunnel**

Check the service status:

```bash
sudo systemctl status vscodetunnel
```

You should see something like:

```
● vscodetunnel.service - VS Code Remote Tunnel
     Loaded: loaded (/etc/systemd/system/vscodetunnel.service; enabled; vendor preset: enabled)
     Active: active (running) ...
```

If it’s active and running, it means the tunnel is now up. You can connect to it via your local VS Code (under “Remote Explorer” → “Tunnels”) or via the browser at <https://vscode.dev/tunnel>.

> **Note**: If the tunnel fails, run `journalctl -u vscodetunnel -f` to see logs. That usually helps identify issues like “couldn’t find stored credentials” or path problems.

---

## 3. Optional: Use `tmux` as a Fallback

Even if you decide on a **systemd service** for the main “always running” approach, you can still do quick manual tests with `tmux new -s test` and `code tunnel` if you need to troubleshoot or try new settings without editing your systemd config.

---

## 4. Summary

- **Terminal multiplexer approach** (`tmux` or `screen`): Quick and easy, but you must keep the session alive. Won’t automatically restart on reboot.
- **systemd service**: Best for production or long-term scenarios. Ensures your VS Code tunnel is always up and automatically restarts on server reboot or if the tunnel process crashes.

By running `code tunnel` as a systemd service, you can ensure that your remote environment is always available for you to connect—no matter if you log off SSH or your server reboots. This way, you’ll have a consistent dev environment that’s continuously accessible via the VS Code Remote Explorer or in your browser at [vscode.dev/tunnel](https://vscode.dev/tunnel).


#### You:
<time datetime="2025-02-15T15:53:59.343Z" title="2/16/2025, 12:53:59 AM">00:53</time>

• Failed to connect to the remote extension host server (Error:
WebSocket close with status code 1006)

#### ChatGPT:
<time datetime="2025-02-15T15:54:11.382Z" title="2/16/2025, 12:54:11 AM">00:54</time>

A **WebSocket close with status code `1006`** typically means the connection ended abnormally. In the context of **VS Code Remote Tunnels**, it indicates that the remote tunnel or local client abruptly closed the WebSocket. Below are the main points to check when troubleshooting this error:

---

## 1. Verify Network Connectivity

- **Outbound Firewall**: Make sure your remote server can make outbound connections to Microsoft’s tunnel endpoints over **HTTPS (TCP port 443)**. If the server is behind a strict firewall or proxy, those connections may be blocked.
- **No Inbound Port Required**: You do not need an inbound port open, but you **do** need to ensure outbound access is allowed.
- **Network or Proxy**: If there’s an HTTP/HTTPS proxy on your server, you might need to configure proxy settings so `code tunnel` can connect properly (e.g., environment variables like `HTTP_PROXY` or `HTTPS_PROXY`).

---

## 2. Check Credentials & Sign-In

- **Same Account**: Ensure you’re logged into the same Microsoft/GitHub account on both the server (`code tunnel`) and your local VS Code or [vscode.dev](https://vscode.dev).
- **One-Time Interactive Sign-In**: If you’re running the tunnel as a **systemd service** or in the background, confirm that you performed at least one interactive sign-in with `code tunnel` under the same user, so credentials are stored.

If credentials are missing or mismatched, the tunnel might briefly start and then immediately drop with a WebSocket error.

---

## 3. Inspect Logs

### 3.1 If You’re Running `code tunnel` in the Foreground

- **Verbose Logging**: You can try:
  ```bash
  code tunnel --log trace
  ```
  This will produce more detailed logging to diagnose why the connection is dropping.

### 3.2 If You’re Running as a Systemd Service

1. **Check systemd logs**:
   ```bash
   sudo systemctl status vscodetunnel
   ```
   or
   ```bash
   journalctl -u vscodetunnel -f
   ```
2. Look for error messages such as “invalid credentials,” “failed to connect,” or “WebSocket closed.”

This will help you pinpoint if the tunnel is even starting properly or if it’s terminating immediately.

---

## 4. Common Causes of `1006` Closure

1. **Firewall**: The most frequent cause is that the remote cannot maintain the WebSocket connection to Microsoft’s servers. Check that no outbound filtering is dropping WebSockets over HTTPS.
2. **Proxy Issues**: If your server or environment uses a proxy that doesn’t support WebSockets or requires special config, the connection can close abruptly.
3. **Token / Auth Expired**: If the token stored on the remote is out of sync or got corrupted, `code tunnel` may fail silently after a handshake attempt.

---

## 5. Potential Fixes / Next Steps

1. **Restart the Tunnel**:
   - If you ran `code tunnel` manually, just retry `code tunnel --log trace` and see if the logs show any immediate error.
   - If you used a systemd service, try restarting it:
     ```bash
     sudo systemctl restart vscodetunnel
     ```
2. **Re-authenticate**:
   - Remove or rename the token storage folder, then re-run `code tunnel` to force a clean sign-in:
     ```bash
     rm -rf ~/.config/Code/User/globalStorage/ms-vscode.remote-server/tokens.json
     code tunnel
     ```
   - Complete sign-in in your browser again.
3. **Test Outbound Connectivity**:
   - On the remote, run `curl https://vscode.dev` (or `ping` if that’s allowed) to ensure basic connectivity.
   - If your environment uses a corporate or custom proxy, confirm that `export HTTPS_PROXY=http://my-proxy:port` (or similar) is set before running `code tunnel`.
4. **Update VS Code / Remote Tunnels**:
   - Make sure you’re on the latest version of VS Code on your local machine and that you installed the **Remote Tunnels** extension.
   - On the server, ensure you’re using a recent `code` binary or the official [Remote Tunnels CLI](https://code.visualstudio.com/docs/remote/tunnels#_install-the-remote-tunnel-agent).

---

## 6. Summary

A `1006` WebSocket closure typically signals that something cut the tunnel connection prematurely—usually a **network/firewall** or **authorization** problem. Double-check:

1. **Outbound network connectivity** (port 443)
2. **Credential consistency** (same sign-in)
3. **Logs** to see if a proxy/firewall/tunnel error is reported

After confirming those aspects, re-authenticate or restart the tunnel. That typically resolves abrupt WebSocket closes and ensures the tunnel remains stable for remote development.


#### You:
<time datetime="2025-02-15T15:55:37.067Z" title="2/16/2025, 12:55:37 AM">00:55</time>

[2025-02-15 07:55:20] info [russh::server] read other id
[2025-02-15 07:55:20] info [russh::server] session is running
[2025-02-15 07:55:20] debug [russh::ssh_read] id 33 33
[2025-02-15 07:55:20] debug [russh::client::encrypted] channel_window_adjust
[2025-02-15 07:55:20] debug [russh::client::encrypted] amount: 4194326
[2025-02-15 07:55:20] debug [russh::server::kex] server kexdhdone.exchange = Exchange { client_id: CryptoVec { p: 0x71dc9c007e10, size: 31, capacity: 32 }, server_id: CryptoVec { p: 0x71dc9c005890, size: 20, capacity: 32 }, client_kex_init: CryptoVec { p: 0x71dc9c192e00, size: 453, capacity: 512 }, server_kex_init: CryptoVec { p: 0x71dc9c479800, size: 554, capacity: 1024 }, client_ephemeral: CryptoVec { p: 0x71dc9c002d00, size: 256, capacity: 256 }, server_ephemeral: CryptoVec { p: 0x71dc9c35ea90, size: 256, capacity: 256 } }
[2025-02-15 07:55:20] debug [russh::server::kex] exchange hash: CryptoVec { p: 0x71dc9c002cb0, size: 32, capacity: 32 }
[2025-02-15 07:55:20] debug [russh::server::kex] signing with key 0
[2025-02-15 07:55:20] debug [russh::server::kex] hash: CryptoVec { p: 0x71dc9c002cb0, size: 32, capacity: 32 }
[2025-02-15 07:55:20] debug [russh::server::kex] key: RSA { (hidden) }
[2025-02-15 07:55:20] debug [russh::server::encrypted] request: Ok("ssh-userauth")
[2025-02-15 07:55:20] debug [russh::server::encrypted] name: "tunnel" Ok("ssh-connection") Ok("none")
[2025-02-15 07:55:20] debug [tunnels::connections::relay_tunnel_host] host relay client session successfully authed
[2025-02-15 07:55:20] debug [rpc.10] Serving new connection
[2025-02-15 07:55:20] info [rpc.10] Checking /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/log.txt and /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/pid.txt for a running server...
[2025-02-15 07:55:21] debug [rpc.10] Installing and setting up Visual Studio Code Server...
[2025-02-15 07:55:21] debug [reqwest::connect] starting new connection: https://update.code.visualstudio.com/
[2025-02-15 07:55:21] error [rpc.10] Error installing server: error requesting https://update.code.visualstudio.com/commit:f5f18731406b73244e0558ee7716d77c8096d150/server-linux-x64/stable: 404 Not Found
[2025-02-15 07:55:21] debug [russh::client::encrypted] channel_close
[2025-02-15 07:55:21] debug [tunnels::connections::relay_tunnel_host] no more connections on host relay client session, ending
[2025-02-15 07:55:21] debug [rpc.10] closing socket reader: EOF
[2025-02-15 07:55:21] debug [rpc.10] Closing connection: EOF
[2025-02-15 07:55:21] info [rpc.10] Disposed of connection to running server.
[2025-02-15 07:55:22] debug [russh::client::encrypted] confirming channel: OpenChannelMessage { typ: Unknown { typ: [99, 108, 105, 101, 110, 116, 45, 115, 115, 104, 45, 115, 101, 115, 115, 105, 111, 110, 45, 115, 116, 114, 101, 97, 109] }, recipient_channel: 11, recipient_window_size: 5242880, recipient_maximum_packet_size: 32768 }
[2025-02-15 07:55:22] info [tunnels::connections::relay_tunnel_host] Opened new client on channel 13
[2025-02-15 07:55:22] debug [tunnels::connections::relay_tunnel_host] starting to serve host relay client session
[2025-02-15 07:55:22] info [russh::server] wrote id
[2025-02-15 07:55:22] debug [russh::ssh_read] read_ssh_id: reading
[2025-02-15 07:55:22] debug [russh::client::encrypted] channel_window_adjust
[2025-02-15 07:55:22] debug [russh::client::encrypted] amount: 4194326
[2025-02-15 07:55:22] debug [russh::ssh_read] read 33
[2025-02-15 07:55:22] debug [russh::ssh_read] Ok("SSH-2.0-dev-tunnels-ssh_3.11.36\r\n")
[2025-02-15 07:55:22] debug [russh::server::kex] server kex init: [20, 200, 16, 146, 251, 169, 36, 25, 157, 23, 4, 130, 248, 121, 143, 52, 175, 0, 0, 0, 95, 100, 105, 102, 102, 105, 101, 45, 104, 101, 108, 108, 109, 97, 110, 45, 103, 114, 111, 117, 112, 49, 52, 45, 115, 104, 97, 50, 53, 54, 44, 100, 105, 102, 102, 105, 101, 45, 104, 101, 108, 108, 109, 97, 110, 45, 103, 114, 111, 117, 112, 49, 52, 45, 115, 104, 97, 49, 44, 100, 105, 102, 102, 105, 101, 45, 104, 101, 108, 108, 109, 97, 110, 45, 103, 114, 111, 117, 112, 49, 45, 115, 104, 97, 49, 44, 101, 120, 116, 45, 105, 110, 102, 111, 45, 115, 0, 0, 0, 25, 114, 115, 97, 45, 115, 104, 97, 50, 45, 50, 53, 54, 44, 114, 115, 97, 45, 115, 104, 97, 50, 45, 53, 49, 50, 0, 0, 0, 32, 97, 101, 115, 50, 53, 54, 45, 99, 116, 114, 44, 97, 101, 115, 49, 57, 50, 45, 99, 116, 114, 44, 97, 101, 115, 49, 50, 56, 45, 99, 116, 114, 0, 0, 0, 32, 97, 101, 115, 50, 53, 54, 45, 99, 116, 114, 44, 97, 101, 115, 49, 57, 50, 45, 99, 116, 114, 44, 97, 101, 115, 49, 50, 56, 45, 99, 116, 114, 0, 0, 0, 128, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 53, 49, 50, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 50, 53, 54, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 53, 49, 50, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 50, 53, 54, 44, 104, 109, 97, 99, 45, 115, 104, 97, 49, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 49, 44, 110, 111, 110, 101, 0, 0, 0, 128, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 53, 49, 50, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 50, 53, 54, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 53, 49, 50, 44, 104, 109, 97, 99, 45, 115, 104, 97, 50, 45, 50, 53, 54, 44, 104, 109, 97, 99, 45, 115, 104, 97, 49, 45, 101, 116, 109, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 104, 109, 97, 99, 45, 115, 104, 97, 49, 44, 110, 111, 110, 101, 0, 0, 0, 26, 122, 108, 105, 98, 44, 122, 108, 105, 98, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 110, 111, 110, 101, 0, 0, 0, 26, 122, 108, 105, 98, 44, 122, 108, 105, 98, 64, 111, 112, 101, 110, 115, 115, 104, 46, 99, 111, 109, 44, 110, 111, 110, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#### ChatGPT:
<time datetime="2025-02-15T15:55:49.107Z" title="2/16/2025, 12:55:49 AM">00:55</time>

From the logs, the key line is:

```
[2025-02-15 07:55:21] error [rpc.10] Error installing server: error requesting https://update.code.visualstudio.com/commit:f5f18731406b73244e0558ee7716d77c8096d150/server-linux-x64/stable: 404 Not Found
```

In other words, the VS Code Tunnel process is trying to **download and install the VS Code server** at commit `f5f18731406b73244e0558ee7716d77c8096d150`, but that particular commit or release is **not found** on the update server. Once it can’t install the server, it fails and closes the tunnel connection.

This usually means:

1. The version of VS Code you’re trying to match on the remote is **older** or **not hosted** any longer, or
2. The local VS Code commit ID / version doesn’t correspond to a public build.

Below are some ways to fix this.

---

## 1. Update Your Local VS Code

Most commonly, you see this error if your local VS Code is on a commit that the remote update server no longer has. Simply **updating your local VS Code** to the latest stable build often fixes it. That ensures the remote tries to download a valid current “server-linux-x64” matching the local version.

**Check your local VS Code version** and ensure it’s up to date:

- **Windows/macOS**:
  1. Go to Help → About (or Code → About Visual Studio Code on macOS)
  2. Make sure it says something like *Version: 1.xx.x (commit e.g. `xxx`)* with no updates pending
  3. If an update is available, install it.

- **Linux**:
  - If you installed via official Microsoft repos:
    ```bash
    sudo apt-get update
    sudo apt-get upgrade code
    ```
    or
    ```bash
    sudo dnf update code
    ```
    depending on your distro.

Once updated, try connecting the tunnel again:

```bash
code tunnel
```

If it’s purely the mismatch of an older commit, it should now succeed.

---

## 2. Forcing the Server Install to Use the Latest Release

Occasionally, you may want to force the remote’s server to come from the **latest stable** stream, especially if your local version is behind or you’re seeing 404 errors for the exact commit. One approach is to specify a stable release stream:

```bash
code tunnel --useReleaseStream stable
```

However, note that in most scenarios, the version of the server is auto-matched to your local VS Code version. If your local is out of date, you could still run into conflicts.

---

## 3. Manually Install or Pre-Download the VS Code Server

If you’re unable to update your local VS Code or want to pin a specific version, you can try manually installing the VS Code Server on the remote:

1. Find a valid [VS Code server archive](https://update.code.visualstudio.com/) or [GitHub Releases page](https://github.com/microsoft/vscode/releases).
2. Download and extract it into the folder that Remote Tunnels expects. For example:
   ```
   ~/.vscode/cli/servers/Stable-<commit-id>
   ```
3. Make sure the folder structure matches the normal server distribution for that commit (i.e. `bin`, `node`, etc.).
4. Then run `code tunnel` again, and it should detect the existing files rather than attempting to download them.

This is more advanced, so for most users **updating local VS Code** is simpler.

---

## 4. Double-Check Firewall / Proxy Settings

While the log specifically shows a **404 Not Found** (meaning the server responded but with “not found”), also confirm you don’t have a proxy or firewall altering URLs. Rarely, a proxy might rewrite the request or cause a weird error. But a pure 404 from the official domain is almost certainly because the commit isn’t there.

---

## 5. Summary of the Fix

1. **Update local VS Code** to the latest stable (strongly recommended).
2. Retry the tunnel:
   ```bash
   code tunnel
   ```
   - That should fetch the correct remote server from `update.code.visualstudio.com` without a 404.
3. If you still see a 404, confirm you don’t have an unusual commit ID or custom build. Also, ensure no system or network proxy is hijacking the request.
4. (Advanced) If you need a pinned older version, you can attempt to manually install that version’s server bits to `~/.vscode/cli/servers/`.

Most of the time, simply **updating your local VS Code** and running `code tunnel` again fixes the 404 issue and allows the server to download properly. Once the server is installed, your tunnel should stay up (especially if you’ve configured it via systemd or `tmux`) without that WebSocket closure.


#### You:
<time datetime="2025-02-15T15:58:50.559Z" title="2/16/2025, 12:58:50 AM">00:58</time>

]
[2025-02-15 07:58:40] info [russh::server] read other id
[2025-02-15 07:58:40] info [russh::server] session is running
[2025-02-15 07:58:40] debug [russh::ssh_read] id 33 33
[2025-02-15 07:58:41] debug [russh::server::kex] server kexdhdone.exchange = Exchange { client_id: CryptoVec { p: 0x71dcb03d2330, size: 31, capacity: 32 }, server_id: CryptoVec { p: 0x71dcb0002b30, size: 20, capacity: 32 }, client_kex_init: CryptoVec { p: 0x71dcb07c8180, size: 453, capacity: 512 }, server_kex_init: CryptoVec { p: 0x71dcb0177a50, size: 554, capacity: 1024 }, client_ephemeral: CryptoVec { p: 0x71dcb014a7f0, size: 257, capacity: 512 }, server_ephemeral: CryptoVec { p: 0x71dcb046f590, size: 256, capacity: 256 } }
[2025-02-15 07:58:41] debug [russh::server::kex] exchange hash: CryptoVec { p: 0x71dcb00efbb0, size: 32, capacity: 32 }
[2025-02-15 07:58:41] debug [russh::server::kex] signing with key 0
[2025-02-15 07:58:41] debug [russh::server::kex] hash: CryptoVec { p: 0x71dcb00efbb0, size: 32, capacity: 32 }
[2025-02-15 07:58:41] debug [russh::server::kex] key: RSA { (hidden) }
[2025-02-15 07:58:41] debug [russh::server::encrypted] request: Ok("ssh-userauth")
[2025-02-15 07:58:41] debug [russh::server::encrypted] name: "tunnel" Ok("ssh-connection") Ok("none")
[2025-02-15 07:58:41] debug [tunnels::connections::relay_tunnel_host] host relay client session successfully authed
[2025-02-15 07:58:41] debug [tunnels::connections::ws] received liveness pong
[2025-02-15 07:58:41] debug [rpc.21] Serving new connection
[2025-02-15 07:58:41] info [rpc.21] Checking /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/log.txt and /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/pid.txt for a running server...
[2025-02-15 07:58:41] debug [rpc.21] Installing and setting up Visual Studio Code Server...
[2025-02-15 07:58:41] debug [reqwest::connect] starting new connection: https://update.code.visualstudio.com/
[2025-02-15 07:58:41] error [rpc.21] Error installing server: error requesting https://update.code.visualstudio.com/commit:f5f18731406b73244e0558ee7716d77c8096d150/server-linux-x64/stable: 404 Not Found
[2025-02-15 07:58:41] debug [russh::client::encrypted] channel_close
[2025-02-15 07:58:41] debug [tunnels::connections::relay_tunnel_host] no more connections on host relay client session, ending
[2025-02-15 07:58:41] debug [rpc.21] closing socket reader: EOF
[2025-02-15 07:58:41] info [rpc.21] Disposed of connection to running server.
[2025-02-15 07:58:41] debug [rpc.21] Closing connection: EOF

#### ChatGPT:
<time datetime="2025-02-15T15:59:11.278Z" title="2/16/2025, 12:59:11 AM">00:59</time>

From the logs:

```
error [rpc.21] Error installing server: error requesting https://update.code.visualstudio.com/commit:f5f18731406b73244e0558ee7716d77c8096d150/server-linux-x64/stable: 404 Not Found
```

The VS Code Tunnels agent on your remote server is trying to download a matching VS Code Server for commit `f5f18731406b73244e0558ee7716d77c8096d150` from the public update URL—but that specific commit is returning a **404 Not Found**. This typically means:

1. The local VS Code build you’re using is out of date or otherwise not available on the “stable” channel anymore.
2. The remote side is trying to fetch a commit that is no longer hosted on the update server.

Below are the main ways to fix this:

---

## 1. Update Your Local VS Code to the Latest Stable

### Why it Works

When you connect via VS Code Tunnels, the **remote** attempts to download the *exact* commit that matches your local VS Code version. If your local VS Code is significantly older (or from a build that’s not on the stable channel), the Microsoft update server may no longer host that version.

### Steps

1. **Update** local VS Code:
   - **Windows/macOS**:
     - Use the built-in update mechanism: *Help → Check for Updates*
     - Or download from <https://code.visualstudio.com/download>
   - **Linux** (Debian/Ubuntu example):
     ```bash
     sudo apt-get update
     sudo apt-get install --only-upgrade code
     ```
   - **Linux** (Fedora/CentOS/RHEL):
     ```bash
     sudo dnf check-update
     sudo dnf upgrade code
     ```

2. After updating, re-run:
   ```bash
   code tunnel
   ```
   The remote should then download the correct server commit, which is definitely available on the update server.

---

## 2. Forcibly Use the Current Stable Release Stream (Optional)

If, for some reason, your local machine can’t be updated yet, you can sometimes force the remote to use the **latest stable** release build:

```bash
code tunnel --useReleaseStream stable
```

However, this can introduce version mismatch issues. Typically it’s best to just update your local VS Code and let the system automatically pull the matching commit.

---

## 3. Confirm You Don’t Have an Insider/Dev Build

- If you’re running **Insiders** or a **Dev** build locally, check whether that build’s commit is still available. Some older dev/insider commits might have been pruned from the update server.
- If you want to stick to Insiders, install **Insiders** also on your server or let the remote fetch the Insiders commit. Usually, though, as long as you’re on the latest Insiders build locally, it *should* also be available on the update server.

---

## 4. (Advanced) Manually Install the Required Server

If you absolutely need that specific commit, you can attempt a manual download from older GitHub releases (if they exist) or another source:

1. Download the correct server tarball for your commit (e.g., `vscode-server-linux-x64.tar.gz`)—but only if it’s still hosted somewhere.
2. Place it into:
   ```
   ~/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150
   ```
   matching the directory structure that `code tunnel` expects (e.g., containing `bin/`, `node/`, etc.).
3. Then run `code tunnel` again so it detects the pre-installed bits.

But this is rarely done in practice. The simplest solution is usually just to **update your local VS Code** so the remote tries a valid, hosted build.

---

## TL;DR

**This 404 error indicates the remote can’t find the server for your local VS Code commit.** The most straightforward fix is:

1. **Update your local VS Code** to the newest stable version.
2. Restart the tunnel (`code tunnel`) on the remote.

That ensures the remote server can be fetched successfully from Microsoft’s update servers, resolving the “404 Not Found” error. Once the correct server is installed, the tunnel should stay active and you can connect without further interruptions.


#### You:
<time datetime="2025-02-15T16:02:37.142Z" title="2/16/2025, 1:02:37 AM">01:02</time>

i did sudo apt-get update
sudo apt-get install --only-upgrade code

but still see

[2025-02-15 08:02:17] info [russh::server] read other id
[2025-02-15 08:02:17] info [russh::server] session is running
[2025-02-15 08:02:17] debug [russh::ssh_read] id 33 33
[2025-02-15 08:02:17] debug [russh::client::encrypted] channel_window_adjust
[2025-02-15 08:02:17] debug [russh::client::encrypted] amount: 4194326
[2025-02-15 08:02:17] debug [russh::server::kex] server kexdhdone.exchange = Exchange { client_id: CryptoVec { p: 0x7deb300c9ab0, size: 31, capacity: 32 }, server_id: CryptoVec { p: 0x7deb3005e1a0, size: 20, capacity: 32 }, client_kex_init: CryptoVec { p: 0x7debe410d990, size: 453, capacity: 512 }, server_kex_init: CryptoVec { p: 0x7deb300e3710, size: 554, capacity: 1024 }, client_ephemeral: CryptoVec { p: 0x7debe40ebaa0, size: 257, capacity: 512 }, server_ephemeral: CryptoVec { p: 0x7debe410b0f0, size: 257, capacity: 512 } }
[2025-02-15 08:02:17] debug [russh::server::kex] exchange hash: CryptoVec { p: 0x7debe4004060, size: 32, capacity: 32 }
[2025-02-15 08:02:17] debug [russh::server::kex] signing with key 0
[2025-02-15 08:02:17] debug [russh::server::kex] hash: CryptoVec { p: 0x7debe4004060, size: 32, capacity: 32 }
[2025-02-15 08:02:17] debug [russh::server::kex] key: RSA { (hidden) }
[2025-02-15 08:02:17] debug [russh::server::encrypted] request: Ok("ssh-userauth")
[2025-02-15 08:02:17] debug [russh::server::encrypted] name: "tunnel" Ok("ssh-connection") Ok("none")
[2025-02-15 08:02:17] debug [tunnels::connections::relay_tunnel_host] host relay client session successfully authed
[2025-02-15 08:02:18] debug [rpc.6] Serving new connection
[2025-02-15 08:02:18] info [rpc.6] Checking /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/log.txt and /home/ashwin/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150/pid.txt for a running server...
[2025-02-15 08:02:18] debug [rpc.6] Installing and setting up Visual Studio Code Server...
[2025-02-15 08:02:18] debug [reqwest::connect] starting new connection: https://update.code.visualstudio.com/
[2025-02-15 08:02:18] error [rpc.6] Error installing server: error requesting https://update.code.visualstudio.com/commit:f5f18731406b73244e0558ee7716d77c8096d150/server-linux-x64/stable: 404 Not Found
[2025-02-15 08:02:18] debug [russh::client::encrypted] channel_close
[2025-02-15 08:02:18] debug [tunnels::connections::relay_tunnel_host] no more connections on host relay client session, ending
[2025-02-15 08:02:18] debug [rpc.6] closing socket reader: EOF
[2025-02-15 08:02:18] info [rpc.6] Disposed of connection to running server.
[2025-02-15 08:02:18] debug [rpc.6] Closing connection: EOF

#### ChatGPT:
<time datetime="2025-02-15T16:02:56.412Z" title="2/16/2025, 1:02:56 AM">01:02</time>

It appears the **remote tunnel** is still trying to fetch the VS Code server at commit `f5f18731406b73244e0558ee7716d77c8096d150`, despite you having run:

```
sudo apt-get update
sudo apt-get install --only-upgrade code
```

That’s almost always a sign that the **local** VS Code (the one you actually launch on your local workstation) is still on that old commit, or that the **remote** is still using an old `code` binary. Below are steps to track down what’s going on:

---

## 1. Confirm Your **Local** VS Code Is Really Updated

1. **Check your local version** explicitly.
   - **Windows/macOS**:
     - Click *Help → About* (or on Mac, *Code → About Visual Studio Code*) to see the version and commit.
     - It should not list commit `f5f18731406b73244e0558ee7716d77c8096d150`.
   - **Linux**:
     - Run:
       ```bash
       code --version
       ```
       locally (on the **machine where you open the GUI**).
       - This is *not* the same as running `code --version` on the remote server over SSH.

2. If you still see the old commit (`f5f18731406b7…`), then your local upgrade did not actually apply.
   - Perhaps you have multiple installations of VS Code (Snap vs. Deb, user-level vs. system-level).
   - Or you ran the apt commands on the remote server instead of your local workstation.

> **Important**: The error logs are from the remote, but they reflect the version that your local VS Code is *asking* it to install. So the local side is key.

---

## 2. If You’re Actually Updating Code on the **Remote** Only

If your intent was “update the remote” with:

```bash
sudo apt-get update
sudo apt-get install --only-upgrade code
```

that’s fine, but if your **local** IDE is still old (i.e., you open “About” and see the old commit), then the remote will try to download that old commit each time you tunnel in.

- **VS Code Remote Tunnels** uses your **local** version’s commit to select which server build it needs to fetch.
- So the remote side can be brand-new, but it still sees your local request for an old server commit.

---

## 3. Remove Old Server Folders (If Stuck)

If your local is now up to date, but you still get a 404 for the old commit, the tunnel process may be “stuck” referencing the old commit. You can try these steps on the remote:

1. **Stop** the tunnel (`Ctrl + C` if it’s running interactively, or `systemctl stop vscodetunnel` if running via systemd).
2. Remove any stale server directories:
   ```bash
   rm -rf ~/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150
   ```
   That ensures we don’t keep reusing an old partial install.
3. **Restart** the tunnel (e.g. `code tunnel`). The remote should attempt to fetch the *new* server commit that matches your local version.

---

## 4. Double-Check You’re Actually Launching the Updated VS Code

If you have multiple installations of VS Code:

- The one you updated via apt might be at `/usr/bin/code`.
- But you might still be launching an older copy from somewhere else (e.g. `/snap/bin/code` or in `~/bin/code`).

### **On Linux**

- Run `which code` locally to see the path.
- Then run `code --version` from the same environment to confirm.

If `which code` is pointing to a Snap or an older location, you may need to remove or update that version:

```bash
snap list
sudo snap remove code
```

*(if you want to remove the Snap version and just rely on the .deb version)*

---

## 5. Use the `--useReleaseStream stable` Flag (Optional)

If you absolutely can’t update your local IDE for some reason, you could force the remote to fetch the latest stable server by appending:

```bash
code tunnel --useReleaseStream stable
```

But typically that can lead to a version mismatch. The standard recommendation is to update your local VS Code so that it’s pulling a valid, hosted server commit.

---

## TL;DR

1. **Check your local VS Code version** (where you do actual editing). Make sure it’s no longer on commit `f5f18731406b7...`.
2. **Remove** any stale server folder on the remote named `Stable-f5f18731406b7...`.
3. **Relaunch** the tunnel.

As soon as your local VS Code reports a modern commit (and the remote sees it), you’ll avoid the `404 Not Found` for that old commit.


#### You:
<time datetime="2025-02-15T16:06:20.656Z" title="2/16/2025, 1:06:20 AM">01:06</time>

the local client i am using is not vscode, but a cusom fork called cursor  
```
The AI
Code Editor

Built to make you extraordinarily productive,
Cursor is the best way to code with AI.

Trusted by engineers at
Tab, tab, tab

Cursor lets you breeze through changes by predicting
 your next edit.
Knows your codebase

Get answers from your codebase or refer to files or docs.
 Use the model’s code in one click.
Edit in natural language

Cursor lets you write code using instructions.
 Update entire classes or functions with a simple prompt.
Build software faster

Intelligent, fast, and familiar, Cursor is the best way to code with AI.
See more features

    Frontier Intelligence

    Powered by a mix of purpose-built and frontier models, Cursor is smart and fast.

Feels Familiar

Import all your extensions, themes, and keybindings in one click.
Privacy Options

If you enable Privacy Mode, your code is never stored remotely. Cursor is SOC 2 certified.

Blog
Iterating with Shadow Workspaces

Hidden windows and kernel-level folder proxies to let AIs iterate on code without affecting the user.
Arvid

Posted by Arvid

19 minutes read
Loved by world-class devs

Engineers all around the world reach for Cursor by choice.

    Cursor is 🐐-ed for real
    Steven Tey

    Steven Tey

    Dub

    I really like how Cursor suggests edits to existing code. It noticed I was inconsistent with my markup and popped up this suggestion that matched my other items!
    Wes Bos

    Wes Bos

    Internet

    The most useful AI tool that I currently pay for is, hands down, is Cursor

    It's fast, autocompletes when and where you need it to, handles brackets properly, sensible keyboard shortcuts, bring- your-own-model...everything is well put together.
    shadcn

    shadcn

    Vercel

    I went from never hearing about Cursor to many IC engineers telling me it’s their new favorite tool. Seemingly overnight! Pretty wild product-market fit.
    Josh Miller

    Josh Miller

    The Browser Company

    I installed Cursor

    ... oh
    Kent C. Dodds

    Kent C. Dodds

    Internet

    After many recommendations, I finally switched from VSC to Cursor and ... wow!

    It's absolutely incredible. If you like Copilot (or if you don't), you'll be blown away by Cursor.

    There is no going back. 🤯
    Johannes Schickling

    Johannes Schickling

    Prisma

Cursor Logo

Try Cursor Now
hi@cursor.com

SOC 2 Certified

Made by
Anysphere

Pricing

Downloads

Docs

Forum

Careers

Company

Security

Privacy

Terms

Changelog

GitHub

Twitter


#### ChatGPT:
<time datetime="2025-02-15T16:06:52.773Z" title="2/16/2025, 1:06:52 AM">01:06</time>

Because **Cursor** is a custom fork of VS Code, it’s likely that it uses a modified commit or a pinned version of the VS Code engine. By default, when you use a “VS Code–style” remote tunnel, the remote tries to download the VS Code Server matching the local editor’s commit hash from Microsoft’s update site ([update.code.visualstudio.com](https://update.code.visualstudio.com/)).

Right now, that commit—`f5f18731406b73244e0558ee7716d77c8096d150`—is returning a **404** because Microsoft has either removed it or never hosted it under the “stable” channel. In short, the **Cursor** editor is instructing the remote to fetch a server build that no longer exists at that URL.

Below are some ways you can address this:

---

## 1. Check if Cursor Has an Update

1. **See if there’s a new Cursor release**.
   - Cursor may have moved to a more recent commit. If so, updating Cursor on your local machine could cause the remote to fetch a newer server commit (one that still exists on Microsoft’s servers).

2. **Confirm the commit** after you update.
   - Sometimes an app can remain pinned to an old commit. Even if you update, double-check whether the Cursor version (or commit ID) has changed.

If your updated Cursor uses a valid, modern commit, you shouldn’t see that 404 anymore because the remote side will try to download the updated server build.

---

## 2. Try Forcing the Latest Stable Server

You can sometimes force the remote side to skip your local commit in favor of the newest stable build. For the official VS Code CLI, that looks like:

```bash
code tunnel --useReleaseStream stable
```

However, since you’re using Cursor (which may bundle its own tunnel logic), **this option might not exist** or might not work exactly the same. If Cursor directly calls the underlying “VS Code tunnel” command, you could try passing in that flag. But if Cursor has a custom mechanism, you might need to see if it offers a similar “override server version” or “use stable stream” flag.

---

## 3. Manually Install the Matching VS Code Server

If Cursor truly needs that old commit and you cannot update Cursor, you can attempt a manual workaround:

1. **Find** a `.tar.gz` or `.zip` of the exact server commit `f5f18731406b73244e0558ee7716d77c8096d150`.
   - This might be hard if Microsoft’s stable channel has removed it. You’d have to see if Cursor or some archive has that build.

2. **Extract** that server to:
   ```bash
   ~/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150
   ```
   so it has the typical server structure (`bin/`, `node`, etc.).

3. Run the tunnel again.
   - Because the server bits are already in place locally, the remote won’t attempt to download them from update.code.visualstudio.com and thus won’t 404.

This approach is definitely more involved, but it’s how some people run older commits that are no longer officially hosted.

---

## 4. Confirm Which Tunnel Mechanism Cursor Uses

Cursor may implement:

1. **The same VS Code Remote Tunnels** code under the hood,
2. **A different** or **modified** tunnel library, or
3. Potentially a **self-maintained** update server for its commits.

If they are still pointing to the official MS update server, you might check Cursor’s docs or GitHub issues to see if there’s a known fix (for example, a pointer to a different server for older Cursor-based commits).

---

## 5. Remove the Stale Server Folder & Retry

If you **have** updated your local Cursor to a newer version, it might still be stuck referencing old partial server files:

1. **Stop** the tunnel if running.
2. Remove any existing, partially installed server folders for that commit:
   ```bash
   rm -rf ~/.vscode/cli/servers/Stable-f5f18731406b73244e0558ee7716d77c8096d150
   ```
3. Retry launching the tunnel (via Cursor or a `code tunnel` command, depending on how you’re invoking it).

If the local Cursor editor is genuinely updated to a new commit, that removal step ensures the remote doesn’t keep trying to reuse the old commit folder.

---

## TL;DR

- **Cursor** is pinned to an old commit `f5f187...` that Microsoft’s update site no longer hosts.
- Update Cursor so it references a **newer VS Code commit** (the easiest fix).
- Alternatively, try forcing the remote to use the “latest stable” release stream, if Cursor supports that.
- In the worst case, manually install the needed server files for that commit so the remote doesn’t attempt to fetch from the official site.

Once you’re on a Cursor version with a valid, publicly available commit, the 404 error should go away and your tunnel will succeed.


#### You:
<time datetime="2025-02-15T16:08:06.517Z" title="2/16/2025, 1:08:06 AM">01:08</time>


Skip to content
Navigation Menu

Code
Issues 1.4k
Pull requests 3
Actions
Projects

WSL extension is supported only in Microsoft versions of VS Code #2027
Open
Labels
bugSomething isn't working
extension-issueAn issue regarding the search/installation of extensions in Cursor
Description
@lycfight
lycfight
opened on Sep 29, 2024

    If you can, please include a screenshot of your problem
    Please include the name of your operating system
    If you can, steps to reproduce are super helpful

I am developing using Windows 11 + WSL: Ubuntu 24.04. After installing Cursor and importing the VSCode extension, the terminal shows the following when entering Cursor:

[2024-09-29 07:18:15.385] Extension version: 0.88.4
[2024-09-29 07:18:15.385] L10N bundle: none
[2024-09-29 07:18:15.388] WSL extension is supported only in Microsoft versions of VS Code

Does Cursor not support WSL?
Activity
markjfisher commented on Sep 30, 2024
@markjfisher
markjfisher
on Sep 30, 2024

Also just got this. Using a WSL folder from my "recents" list I get this:
image
markjfisher commented on Sep 30, 2024
@markjfisher
markjfisher
on Sep 30, 2024

I tried going to the extensions, and it showed WSL like this:
image

Clicking it reopened cursor, but then I get the error:

[2024-09-30 19:08:01.189] WSL extension activating for a local WSL instance
[2024-09-30 19:08:01.196] Resolving wsl+ubuntu-24.04, resolveAttempt: 1
[2024-09-30 19:08:01.196] NodeExecServer run: C:\Windows\System32\wsl.exe --status
[2024-09-30 19:08:01.234] WSL feature installed: true (wsl --status)
[2024-09-30 19:08:01.235] NodeExecServer run: C:\Windows\System32\wsl.exe --list --verbose
[2024-09-30 19:08:01.270] 3 distros found
[2024-09-30 19:08:01.271] Starting VS Code Server inside WSL (wsl2)
[2024-09-30 19:08:01.271] Windows build: 22631. Multi distro support: available. WSL path support: enabled
[2024-09-30 19:08:01.271] Scriptless setup: false
[2024-09-30 19:08:01.271] No shell environment set or found for current distro.
[2024-09-30 19:08:01.352] WSL daemon log file: 
[2024-09-30 19:08:01.355] Probing if server is already installed: if [ -d ~/.cursor-server/bin/51c8aff7cb5a89f4a0e462fbacab938bdbfaf140 ]; then printf 'install-found '; fi; if [ -f /etc/alpine-release ]; then printf alpine-; fi; uname -m
[2024-09-30 19:08:01.355] NodeExecServer run: C:\Windows\System32\wsl.exe -d Ubuntu-24.04 -e sh -c if [ -d ~/.cursor-server/bin/51c8aff7cb5a89f4a0e462fbacab938bdbfaf140 ]; then printf 'install-found '; fi; if [ -f /etc/alpine-release ]; then printf alpine-; fi; uname -m
[2024-09-30 19:08:01.437] Probing result: x86_64
[2024-09-30 19:08:01.437] No server install found in WSL, needs linux-x64
[2024-09-30 19:08:01.437] Getting server from client side
[2024-09-30 19:08:01.438] Server available at 
[2024-09-30 19:08:01.439] NodeExecServer run: C:\Windows\System32\wsl.exe -d Ubuntu-24.04 sh -c '"$VSCODE_WSL_EXT_LOCATION/scripts/wslServer.sh" 51c8aff7cb5a89f4a0e462fbacab938bdbfaf140 stable cursor-server .cursor-server --host=127.0.0.1 --port=0 --connection-token=2093602930-2684626555-3433266563-2095195016 --use-host-proxy --without-browser-env-var --disable-websocket-compression --accept-server-license-terms --telemetry-level=all'
[2024-09-30 19:08:01.672] Setting up server environment: Looking for /home/fenrock/.cursor-server/server-env-setup. Not found.
[2024-09-30 19:08:01.672] WSL version: 5.15.153.1-microsoft-standard-WSL2 Ubuntu-24.04
[2024-09-30 19:08:01.672] Updating VS Code Server to version 51c8aff7cb5a89f4a0e462fbacab938bdbfaf140
[2024-09-30 19:08:01.672] Removing previous installation...
[2024-09-30 19:08:01.672] Installing VS Code Server for x64 (51c8aff7cb5a89f4a0e462fbacab938bdbfaf140)
[2024-09-30 19:08:01.672] Downloading:     100%
[2024-09-30 19:08:01.672] Failed
[2024-09-30 19:08:01.673] --2024-09-30 20:08:01--  https://update.code.visualstudio.com/commit:51c8aff7cb5a89f4a0e462fbacab938bdbfaf140/server-linux-x64/stable
[2024-09-30 19:08:01.673] Resolving update.code.visualstudio.com (update.code.visualstudio.com)... 13.107.246.64, 2620:1ec:bdf::64
[2024-09-30 19:08:01.673] Connecting to update.code.visualstudio.com (update.code.visualstudio.com)|13.107.246.64|:443... connected.
[2024-09-30 19:08:01.673] HTTP request sent, awaiting response... 404 Not Found
[2024-09-30 19:08:01.673] 2024-09-30 20:08:01 ERROR 404: Not Found.
[2024-09-30 19:08:01.673] 
[2024-09-30 19:08:01.673] ERROR: Failed to download https://update.code.visualstudio.com/commit:51c8aff7cb5a89f4a0e462fbacab938bdbfaf140/server-linux-x64/stable to /home/fenrock/.cursor-server/bin/51c8aff7cb5a89f4a0e462fbacab938bdbfaf140-1727723281.tar.gz
[2024-09-30 19:08:01.673] For help with startup problems, go to https://code.visualstudio.com/docs/remote/troubleshooting#_wsl-tips

markjfisher commented on Sep 30, 2024
@markjfisher
markjfisher
on Sep 30, 2024 · edited by markjfisher

Ok, I then followed the linked guide from the last line of the log, and what I was missing was the path to windows VS Code on my WSL path, so I added:

export PATH=$PATH:"/mnt/c/Program Files/Microsoft VS Code/bin"

to my bashrc file, restarted cursor, and the server was able to download and install correctly, and the project opened up correctly. So it was a missing path for me.
alvaradojl commented on Oct 2, 2024
@alvaradojl
alvaradojl
on Oct 2, 2024 · edited by alvaradojl

I have the same problem, but the PATH was not an issue, it was already there, I also added the cursor (windows mounted path) to my zshrc profile but didn't help.

Just to be clear, both programs start fine with code . and cursor .
WSL plugin works fine under VSCode but not in Cursor

My Ubuntu version is 22.04, VSCode is 1.93.1 and WSL Plugin is 0.88.4
FelipeB12 commented on Oct 2, 2024
@FelipeB12
FelipeB12
on Oct 2, 2024

I had the same problem with Ubuntu 22.04 and it was solved closing VS and starting Ubuntu from CMD, then reload cursor and connect to WSL with the cursor extension
bnurzhanov commented on Oct 2, 2024
@bnurzhanov
bnurzhanov
on Oct 2, 2024

    I had the same problem with Ubuntu 22.04 and it was solved closing VS and starting Ubuntu from CMD, then reload cursor and connect to WSL with the cursor extension

This sounds promising. Can you please provide a link to the cursor extension?
alvaradojl commented on Oct 3, 2024
@alvaradojl
alvaradojl
on Oct 3, 2024

@FelipeB12 do you mean the VSCode WSL extension? because I don't see any Cursor-specific extension in the gallery
FelipeB12 commented on Oct 3, 2024
@FelipeB12
FelipeB12
on Oct 3, 2024 · edited by FelipeB12

Screenshot_1

Yes, I had it on VSCode, and cursor imported it from VScode, the extension ID is "ms-vscode-remote.remote-wsl"
alvaradojl commented on Oct 3, 2024
@alvaradojl
alvaradojl
on Oct 3, 2024

mmm I see, I think the new WSL extension 0.88.4 is the culprit, don't update your extension or cursor will stop working 😅
danperks commented on Oct 3, 2024
@danperks
danperks
on Oct 3, 2024
Collaborator

Seems like the extension has some code to specifically check for when's it's being used in the usual VSCode environment vs Cursor or any 3rd party VSCode-based editor.

If an older version works, my best suggestion would be to downgrade to the latest working version for now. Not sure if this will get a fix, as if the extension has been coded to block Cursor like this, there's not much Cursor can do to resolve it besides pretend to be VSCode, which probably wouldn't go down very well.

Unfortunately, Microsoft have every right to block their own extensions from working on anything besides their own VSCode releases.
danperks
added
bugSomething isn't working
extension-issueAn issue regarding the search/installation of extensions in Cursor
on Oct 3, 2024
jeggah commented on Oct 14, 2024
@jeggah
jeggah
on Oct 14, 2024

Only started getting this issue today. Been using Cursor with WSL2 for the past 2 months with no problem. Now I can't even open my projects anymore. Anyone know any workarounds?

command 'remote-wsl.connect' not found

image
tuzun89 commented on Oct 15, 2024
@tuzun89
tuzun89
on Oct 15, 2024

In my experience, it seems to be latest WSL extension (0.88.4) causing issues as per the above comments. I've downgraded to 0.88.3 and worked without issues. Link to extension.
jeggah commented on Oct 15, 2024
@jeggah
jeggah
on Oct 15, 2024 · edited by jeggah

    In my experience, it seems to be latest WSL extension (0.88.4) causing issues as per the above comments. I've downgraded to 0.88.3 and worked without issues. Link to extension.

Thanks. What seemed to work for me in the end is after manually installing an incompatible version and getting the WSL extension is supported only in Microsoft versions of VS Code error - the Update button on the Extension downgraded it to 0.81.8. This version seems to work fine like before. Of course I unselected Auto Update too.
22 remaining items
igoralentyev commented on Dec 11, 2024
@igoralentyev
igoralentyev
on Dec 11, 2024

    This doesn't work for me. I removed the extension, closed Cursor, drag 0.88.3 into Cursor again, disabled auto update but still can't open WSL. I tried download 0.88.3 and even older versions like 0.88.1 and no luck.

I have to do it twise cause after i did it first time WSL ext still become updated. So i uninstall ext again (also i remove .vscode folder from wsl), relaunch everything and just did the same steps one more time and it works now.

Also, check version and logs, maybe you have some different error?
pmtarantino commented on Dec 11, 2024
@pmtarantino
pmtarantino
on Dec 11, 2024

No, that didn't work either. The logs show the same error reported originally by @markjfisher:

[2024-12-11 12:07:12.175] Probing if server is already installed: if [ -d ~/.cursor-server/bin/a846435528b4b760494a836f96f0739889253530 ]; then printf 'install-found '; fi; if [ -f /etc/alpine-release ]; then printf 'alpine-'; fi; if [ -s ~/.cursor-server/bin/legacy-mode ]; then printf 'legacy-'; fi; uname -m;
[2024-12-11 12:07:12.175] NodeExecServer run: C:\WINDOWS\System32\wsl.exe -d Ubuntu-20.04 -e sh -c if [ -d ~/.cursor-server/bin/a846435528b4b760494a836f96f0739889253530 ]; then printf 'install-found '; fi; if [ -f /etc/alpine-release ]; then printf 'alpine-'; fi; if [ -s ~/.cursor-server/bin/legacy-mode ]; then printf 'legacy-'; fi; uname -m;
[2024-12-11 12:07:11.883] Extension version: 0.88.3
[2024-12-11 12:07:11.883] L10N bundle: undefined
[2024-12-11 12:07:11.923] authorityHierarchy: wsl+ubuntu-20.04
[2024-12-11 12:07:11.923] WSL extension activating for a local WSL instance
[2024-12-11 12:07:11.944] Resolving wsl+ubuntu-20.04, resolveAttempt: 1
[2024-12-11 12:07:11.945] NodeExecServer run: C:\WINDOWS\System32\wsl.exe --status
[2024-12-11 12:07:12.005] WSL feature installed: true (wsl --status)
[2024-12-11 12:07:12.005] NodeExecServer run: C:\WINDOWS\System32\wsl.exe --list --verbose
[2024-12-11 12:07:12.044] 3 distros found
[2024-12-11 12:07:12.045] Starting VS Code Server inside WSL (wsl2)
[2024-12-11 12:07:12.045] Windows build: 22631. Multi distro support: available. WSL path support: enabled
[2024-12-11 12:07:12.045] Scriptless setup: false
[2024-12-11 12:07:12.045] No shell environment set or found for current distro.
[2024-12-11 12:07:12.278] Probing result: x86_64
[2024-12-11 12:07:12.278] No server install found in WSL, needs linux-x64
[2024-12-11 12:07:12.278] Getting server from client side
[2024-12-11 12:07:12.279] Downloading VS Code Server stable - a846435528b4b760494a836f96f0739889253530 into C:\Users\patri\AppData\Local\Temp\vscode-remote-wsl\stable\a846435528b4b760494a836f96f0739889253530\vscode-server-stable-linux-x64.tar.gz.
[2024-12-11 12:07:13.247] Download checksum: undefined

igoralentyev commented on Dec 11, 2024
@igoralentyev
igoralentyev
on Dec 11, 2024

    No, that didn't work either. The logs show the same error reported originally by @markjfisher:

Oh, got it! Your error is different from mine, sorry cant help with it :(
shmuli9 commented on Dec 30, 2024
@shmuli9
shmuli9
on Dec 30, 2024 · edited by shmuli9

Harumph.... MS just wasted my afternoon - thanks
Thanks for this thread - all sorted by downgrading

For those stuck in google I am adding some keywords to this thread (took me hours to get here)

The error I was getting was
The editor could not be opened due to an unexpected error: ENOPRO: No file system provider found for resource 'vscode-remote://
And it came down the fact that I was no longer able to connect to WSL with Cursor due to a recent VSCode/Server update
shmuli9
mentioned this on Dec 30, 2024

    [Blocking all use] WSL Not working, error in upgrade download #1476

Marxwil commented on Jan 6, 2025
@Marxwil
Marxwil
on Jan 6, 2025

This downgrading of the WSL extension solved my issue as well. However, I did not get any error logs. The VS Code was running on WSL, but the Cursor was not. I will add some keywords as well.
WSL is running but Cursor is not, no error logs
AsaMyth commented on Jan 6, 2025
@AsaMyth
AsaMyth
on Jan 6, 2025

    Harumph.... MS just wasted my afternoon - thanks Thanks for this thread - all sorted by downgrading

    For those stuck in google I am adding some keywords to this thread (took me hours to get here)

    The error I was getting was The editor could not be opened due to an unexpected error: ENOPRO: No file system provider found for resource 'vscode-remote:// And it came down the fact that I was no longer able to connect to WSL with Cursor due to a recent VSCode/Server update

Could you share the particular extension that needs to be downgraeded? Tried downgrading VS Code WSL extension but the issue is still there at my end. Thanks.
AsaMyth commented on Jan 6, 2025
@AsaMyth
AsaMyth
on Jan 6, 2025

        Harumph.... MS just wasted my afternoon - thanks Thanks for this thread - all sorted by downgrading
        For those stuck in google I am adding some keywords to this thread (took me hours to get here)
        The error I was getting was The editor could not be opened due to an unexpected error: ENOPRO: No file system provider found for resource 'vscode-remote:// And it came down the fact that I was no longer able to connect to WSL with Cursor due to a recent VSCode/Server update

    Could you share the particular extension that needs to be downgraeded? Tried downgrading VS Code WSL extension but the issue is still there at my end. Thanks.

Turned out I have to reinstall vs-code to reslove this...
krishnapraveen7 commented on Jan 9, 2025
@krishnapraveen7
krishnapraveen7
on Jan 9, 2025

        In my experience, it seems to be latest WSL extension (0.88.4) causing issues as per the above comments. I've downgraded to 0.88.3 and worked without issues. Link to extension.

    This worked like a charm, thank you so much !!

This worked. Just drag and drop this in the cursor. It will install the extension. Drag and drop into the extensions.
empowerDon commented on Jan 15, 2025
@empowerDon
empowerDon
on Jan 15, 2025

fwiw I was on updated version of WSL extension (0.88.5) before installing cursor, and my tailwind autocomplete and hover wasn't working because the tailwind extension was installed in windows (ie, Local - Installed in the extensions list) when it needed to be installed in WSL (though it wasnt obvious to me)

I couldn't uninstall the WSL extension from Cursor when launched from WSL because No remote extension installed to resolve wsl.

what worked for me:

    launch a new window from cursor in "windows" (that wasn't a WSL directory)
    uninstall the WSL extension
    manually install the older version linked ITT (download + drag and drop as noted)
    launch cursor from WSL (using cursor ., which installed VS Code Server for Linux in WSL environment)
    install tailwind (and other extensions) which now show up under WSL: Ubuntu - Installed

...everything seems back to normal now
chrisdlangton commented on Jan 30, 2025
@chrisdlangton
chrisdlangton
on Jan 30, 2025 · edited by chrisdlangton

Read almost every word in this thread after enjoying Cursor on my Arch laptop and buying a Cursor plan, then trying to use it on Windows with WSL and realising the OP blocker myself.
Nothing worked except just 1 trick.
I don't like it, so I reverted and kept trying other suggestions.

So the only thing that worked today was;

    installing the latest Cursor build for Windows
    uninstall WSL extension (if installed during VSCode migration)
    find WSL extension in the marketplace ms-vscode-remote.remote-wsl
    DON'T click Install
    Choose the cog for settings
    Choose to install a specific version
    I had a version from a year ago offered (0.81.8)

Then you can use WSL normally, Remote Window manager is specifcally what I use personally.

Hope this helps newcomers to this thread until there is a real solution
MarkusEicher commented on Feb 13, 2025
@MarkusEicher
MarkusEicher
on Feb 13, 2025

Many thanks to @tuzun89! 💪 Not all heroes wear capes. I guess we have to prepare for more troubles with Marketplace extensions and Cursor. Thanks for providing the link.
tuzun89 commented on Feb 13, 2025
@tuzun89
tuzun89
on Feb 13, 2025

@MarkusEicher no problem and you're welcome. I'm glad it was helpful. I haven't used Cursor in a few months, I assume it's even better now?
MarkusEicher commented on Feb 13, 2025
@MarkusEicher
MarkusEicher
on Feb 13, 2025

It is pretty good, but something that bothers me is their tendency to implement features without any warning. 😊 And also remove them likewise. But it can do a lot of work. You still need to check everything it does. Nice thing is for 20 bucks you get infinite usage of Claude sonnet. Only 500 fast calls, but the rest of the month you can use sonnet a bit slower, but you still can use it. I like it.
Fearao commented on Feb 13, 2025
@Fearao
Fearao
on Feb 13, 2025

    Read almost every word in this thread after enjoying Cursor on my Arch laptop and buying a Cursor plan, then trying to use it on Windows with WSL and realising the OP blocker myself. Nothing worked except just 1 trick. I don't like it, so I reverted and kept trying other suggestions.

    So the only thing that worked today was;

        installing the latest Cursor build for Windows
        uninstall WSL extension (if installed during VSCode migration)
        find WSL extension in the marketplace ms-vscode-remote.remote-wsl
        DON'T click Install
        Choose the cog for settings
        Choose to install a specific version
        I had a version from a year ago offered (0.81.8)

    Then you can use WSL normally, Remote Window manager is specifcally what I use personally.

    Hope this helps newcomers to this thread until there is a real solution

It works for me, thanks! I simplily install v0.81.8 in vscode and import it into cursor.
wbywfjptrgmuMJxByvFD
Add a comment
new Comment
Markdown input: edit mode selected.
Remember, contributions to this repository should follow its security policy.
Metadata
Assignees
No one assigned

Labels
bugSomething isn't working
extension-issueAn issue regarding the search/installation of extensions in Cursor
Type
No type
Projects
No projects
Milestone
No milestone

Relationships
None yet
Development
No branches or pull requests

Notifications
You're not receiving notifications from this thread.
Participants
@emzo
@bnurzhanov
@markjfisher
@pmtarantino
@jeggah
Issue actions

Footer
© 2025 GitHub, Inc.
Footer navigation

    Terms
    Privacy
    Security
    Status
    Docs
    Contact

WSL extension is supported only in Microsoft versions of VS Code · Issue #2027 · getcursor/cursor

#### ChatGPT:
<time datetime="2025-02-15T16:08:32.531Z" title="2/16/2025, 1:08:32 AM">01:08</time>

Below is a **summary** of the GitHub issue discussion regarding **Cursor** and **WSL support**, plus the **key workarounds** people have used to make the Microsoft WSL extension function under Cursor.

---

## 1. Background

- **Cursor** is a custom fork of VS Code that bundles AI-assisted coding features.
- The official **Remote - WSL extension** (`ms-vscode-remote.remote-wsl`) from Microsoft **checks** if it’s running on “official” VS Code. In newer versions, it can refuse to operate on forks (like Cursor).
- As a result, users upgrading the WSL extension to versions around **0.88.x and above** found themselves **blocked** from using WSL inside Cursor with errors like:
  - *“WSL extension is supported only in Microsoft versions of VS Code”*
  - *`ENOPRO: No file system provider found for resource 'vscode-remote://...'`*

---

## 2. Main Symptoms & Errors

1. **WSL extension logs** mention it’s specifically detecting a non-Microsoft environment.
2. Attempting to open a folder in WSL from Cursor leads to a popup or logs stating:
   - *“WSL extension is supported only in Microsoft versions of VS Code”*
   - Or the extension simply refuses to activate.
3. **Download errors** for the required server bits if Cursor attempts to fetch them from Microsoft’s update service.
4. Some users see partial installs but then a **404** error when the extension tries to download a matching server commit from Microsoft’s servers.

---

## 3. Workarounds Discovered in the Thread

### A. **Downgrade the WSL Extension**

**Most users find success by installing an older version** of the WSL extension that does *not* include the environment check. For example:

1. In **VS Code** (or within Cursor if you can do it there), find **ms-vscode-remote.remote-wsl** in the marketplace or extension list.
2. Click the cog next to the “Install” button (or the drop-down arrow) → **“Install Another Version...”**
3. Choose a version prior to `0.88.4` (commonly `0.88.3`, `0.81.8`, etc.).
4. Make sure **auto-update is turned off** so it doesn’t upgrade back to a newer release.

Then, Cursor can import or use that older WSL extension, which doesn’t block non-Microsoft forks.

### B. **Set Up the Extension in VS Code, Then Import to Cursor**

Some users:

1. Install/downgrade the extension in real Microsoft VS Code.
2. Confirm WSL works there.
3. **Import** that extension into Cursor.

This ensures Cursor gets the older WSL extension without pulling the latest from the Marketplace (where it might block Cursor).

### C. **Check PATH / Re-Install from Windows**

A few users resolved some environment-specific issues (particularly downloads failing) by:

1. Making sure the Windows-based `VS Code/bin` is on their WSL `$PATH`.
2. Launching WSL from a Windows command line.
3. Reinstalling or downgrading the WSL extension after that environment is set up.

This helps with the server install, but does *not* remove the fundamental “blocked in new versions” problem. It just ensures that if you’re on an older version, the server installation proceeds smoothly.

---

## 4. Why This Happens

1. **Microsoft’s Official Extensions**: Some of them (especially remote extensions like WSL, Remote SSH, Docker, etc.) explicitly check if they are running in official VS Code rather than a fork. This might involve a check of product identifiers, certain environment variables, or the presence of Microsoft’s signing.
2. **Cursor** is not recognized by these official remote extensions as a valid “Microsoft VS Code.” So once Microsoft updated the WSL extension to enforce environment checks, new versions started throwing the “only in Microsoft versions of VS Code” error.

---

## 5. Future Outlook

- It’s unclear whether Microsoft or Cursor will provide an official fix or if the WSL extension will remain off-limits for forks.
- The best short-term workaround is to **downgrade** to an older WSL extension version that doesn’t enforce the environment check.
- Users should keep in mind that older WSL extension versions might lack new features or fixes. So there is a trade-off in staying behind on the extension to keep Cursor + WSL working.

---

## 6. Conclusion & Recommended Steps

1. **Downgrade** the WSL extension (e.g., to `0.88.3` or older) and disable auto-updates, or install from a `.vsix` file.
2. **Manually import** that downgraded extension into Cursor.
3. Ensure environment variables (PATH to Windows VS Code) are properly set if you run into server download errors inside WSL.

By following these steps, most people in the thread recovered WSL functionality within Cursor. However, new or upcoming features in later WSL extension releases may remain unavailable as long as the extension enforces the official environment check.


#### You:
<time datetime="2025-02-15T16:10:12.729Z" title="2/16/2025, 1:10:12 AM">01:10</time>

[2025-02-15 08:09:58] trace [rpc.12] Attached to server
[2025-02-15 08:09:58] trace [rpc.12] [codeserver.13] [08:09:58] [<unknown>][7ed990c6] Client refused: version mismatch.
[2025-02-15 08:09:58] trace [rpc.12] Attached to server
[2025-02-15 08:09:58] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:58] trace [rpc.12] [codeserver.13] [08:09:58] [<unknown>][58f1559f] Client refused: version mismatch.
[2025-02-15 08:09:58] trace [rpc.12] Attached to server
[2025-02-15 08:09:58] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:58] trace [rpc.12] [codeserver.13] [08:09:58] [<unknown>][57d227b2] Client refused: version mismatch.
[2025-02-15 08:09:58] trace [rpc.12] Attached to server
[2025-02-15 08:09:58] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:58] trace [rpc.12] [codeserver.13] [08:09:58] [<unknown>][93e9510f] Client refused: version mismatch.
[2025-02-15 08:09:58] trace [rpc.12] Attached to server
[2025-02-15 08:09:58] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:59] trace [rpc.12] [codeserver.13] [08:09:59] [<unknown>][f3ca9ff6] Client refused: version mismatch.
[2025-02-15 08:09:59] trace [rpc.12] Attached to server
[2025-02-15 08:09:59] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:59] trace [rpc.12] [codeserver.13] [08:09:59] [<unknown>][458a3167] Client refused: version mismatch.
[2025-02-15 08:09:59] trace [rpc.12] Attached to server
[2025-02-15 08:09:59] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:59] trace [rpc.12] [codeserver.13] [08:09:59] [<unknown>][ee509fe8] Client refused: version mismatch.
[2025-02-15 08:09:59] trace [rpc.12] Attached to server
[2025-02-15 08:09:59] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:09:59] trace [rpc.12] [codeserver.13] [08:09:59] [<unknown>][5a23f7bf] Client refused: version mismatch.
[2025-02-15 08:09:59] trace [rpc.12] Attached to server
[2025-02-15 08:09:59] warn [rpc.12] error handling call: NoAttachedServerError(NoAttachedServerError)
[2025-02-15 08:10:00] trace [rpc.12] Attached to server
[2025-02-15 08:10:00] trace [rpc.12] [codeserver.13] [08:10:00] [<unknown>][5b0b434e] Client refused: version mismatch.
[2025-02-15 08:10:00] warn [rpc.12] error handling call: NoAttachedServerError

#### ChatGPT:
<time datetime="2025-02-15T16:10:36.843Z" title="2/16/2025, 1:10:36 AM">01:10</time>

These logs show repeated **“Client refused: version mismatch.”** and **“NoAttachedServerError”** messages, which typically means the **remote code server** and the **local client** are on incompatible or mismatched versions. In other words, the “server” that runs on the remote is refusing connections from the editor on the client side because they expect different version commits or protocols.

Below are common causes and solutions for a version mismatch in a VS Code–style remote environment (including Cursor or other forks):

---

## 1. Confirm Both Sides Are on the Same Commit/Version

### **Why It Matters**

VS Code-based “remote” protocols usually require that the **remote code server** match the **local editor**’s commit ID. If your local editor expects commit “XYZ,” it instructs the remote to download or run a matching server build. If the remote is already running a different or older version, it can refuse connections with a “version mismatch” error.

### **What to Do**

1. **Check the Local Editor Version**:
   - For standard VS Code, you would do `code --version` (on your local machine).
   - For Cursor (or another fork), see if there’s an “About” dialog or a version command in the CLI.

2. **Check the Remote Code Server Version**:
   - On your remote machine, find the directory where the code server is installed. Often that’s something like:
     ```
     ~/.vscode/cli/servers/Stable-<commit-id>
     ```
     or for Cursor:
     ```
     ~/.cursor-server/bin/<commit-id>
     ```
   - If that folder’s commit is different from your local editor’s commit, you get mismatch errors.

3. **Update or Sync**
   - **If you can, update the local editor** to the latest stable (or whatever channel it uses), then let the remote code server auto-download the matching commit.
   - Alternatively, **remove** the old server folder on the remote so that the next connection attempt triggers a fresh download. For example:
     ```bash
     rm -rf ~/.vscode/cli/servers/Stable-<old-commit>
     ```
     (or the appropriate folder if you’re using Cursor).
   - After removing the old folder, reconnect from the local editor. If the editor sees no existing server for that commit, it attempts to download a fresh, matching version—thus resolving the mismatch.

---

## 2. Multiple Installations or Forks

- You might have multiple versions of VS Code or Cursor installed locally, each with different commits. If you open the “wrong” one, it tries to connect using a commit ID that the remote doesn’t have.
- Verify which editor binary (`which code` or `which cursor`) is actually launching.

---

## 3. Cursor’s Custom Build vs. Microsoft’s Update Servers

If you’re using **Cursor**, it might be pinned to a custom or older commit that’s **not** hosted on Microsoft’s update servers, or your remote environment might be stuck with a leftover version. This leads to a mismatch if:

- The remote had partial success installing an old commit.
- The local updated to a new commit, but the remote keeps running the old code server.

**Solution**: Remove the stale server folder, then let the Cursor client “push” or download the correct server next time you connect.

---

## 4. Advanced: Manual Installation

If for some reason your local editor uses a commit that’s no longer on Microsoft’s site (404 errors, etc.), you can manually place the server bits into the remote’s folder. But usually, simply updating to a commonly hosted version is easier.

---

## 5. Summary

- **Version mismatch** errors occur because the remote code server version doesn’t match the local editor commit.
- **Fix**: Update your local editor to a version that’s still hosted, remove the old server folder on the remote, and reconnect so the remote automatically installs the matching server. If you are using Cursor, ensure you are truly running the same commit version on both sides (or the version that Cursor expects to use). Once both sides line up, you’ll no longer see “Client refused: version mismatch.” or the “NoAttachedServerError.”
