---
title: Reverse Proxy for Homelab
source: https://chatgpt.com/c/6788915e-a13c-8003-9cfe-2a32310d7915
---

# Reverse Proxy for Homelab

#### You:
<time datetime="2025-01-16T04:55:59.126Z" title="1/16/2025, 1:55:59 PM">13:55</time>

i have a burgeoning homelab with a bunch of internal IPs and port numbers. i've read  that things work much better with a reverse proxuy but i have no idea what that means and how to set one up. help me understand how this helps

#### ChatGPT:
<time datetime="2025-01-16T04:56:49.505Z" title="1/16/2025, 1:56:49 PM">13:56</time>

A **reverse proxy** is a server (or service) that sits in front of your internal services and intercepts incoming requests before passing them along to the correct server on your local network. In other words, external clients only know about the reverse proxy, and the reverse proxy quietly routes the traffic behind the scenes to the right service (at the right port/IP) in your homelab.

Here’s why it can simplify your setup and improve your homelab experience:

---

## 1. Fewer Open Ports

Without a reverse proxy, you might have to open multiple ports on your router for each service (e.g., port 8080 for internal web server A, 8081 for internal web server B, 3000 for some dashboard, etc.). This quickly becomes unmanageable and insecure.

With a reverse proxy, you typically only open **one or two** ports on your router (most commonly HTTP on port 80 and HTTPS on port 443). Then the reverse proxy internally routes to each service based on rules—such as **subdomain** or **URL path**:

- `app1.yourdomain.com` → routes traffic to internal server 192.168.1.5:8080
- `app2.yourdomain.com` → routes traffic to internal server 192.168.1.7:3000

---

## 2. Centralized SSL/TLS Termination

A reverse proxy also makes it easy to manage SSL certificates (for HTTPS). Instead of setting up certificates and Let’s Encrypt on every single service, you can handle it once on the reverse proxy and let the proxy connect to your internal services via HTTP (or HTTPS if you prefer end-to-end encryption).

Having a single place to manage SSL/TLS:

1. Saves time (no need to install certificates on each host).
2. Ensures that all inbound traffic is encrypted and secure.
3. Makes it straightforward to automate certificate renewal (e.g., with **Certbot** or native Let’s Encrypt integration in some proxies).

---

## 3. Easy Routing by Domain and Path

Say you have 10 different internal services, each at a different IP and port. A reverse proxy can elegantly map domain names (or subdomains) to these services.

- **Subdomain-based routing**:
  - `plex.yourdomain.com` → 192.168.1.10:32400
  - `nextcloud.yourdomain.com` → 192.168.1.11:8080

- **Path-based routing**:
  - `yourdomain.com/app1` → 192.168.1.12:8080
  - `yourdomain.com/app2` → 192.168.1.13:8080

This helps you keep a consistent naming scheme, simplifying how you (and others) access your homelab.

---

## 4. Security & Access Control

Reverse proxies can also add layers of security. You can configure them to do:

- **Access control** and authentication (e.g., require a login before passing traffic along).
- **Web application firewall (WAF)** features like rate limiting, blocking suspicious requests, etc.
- **Load balancing** if you want to spread traffic across multiple servers.

By controlling access at the proxy, you reduce the exposure of each service directly to the internet.

---

## 5. Popular Reverse Proxy Options

1. **Nginx**
   - A very common choice; widely documented.
   - Large community, highly configurable.
   - Good balance of performance and flexibility.

2. **Caddy**
   - Automatically handles HTTPS certificates with Let’s Encrypt by default.
   - Very user-friendly configuration (especially the latest version).

3. **Traefik**
   - Built with containerized microservices in mind.
   - Dynamic configuration, great if you run Docker Swarm, Kubernetes, or a container-heavy homelab setup.

Each has a slightly different approach and configuration style, so pick whichever feels most natural or aligns best with your homelab’s future direction (for instance, if you plan to spin up HPC clusters in containers, something like Traefik might fit right in).

---

## 6. Basic Steps to Set Up a Reverse Proxy (Example: Nginx)

1. **Install Nginx** on a VM, server, or Docker container that is reachable at your homelab’s IP on port 80/443.
2. **Obtain a domain name** (e.g., `myhomelab.com`), and create DNS records that point to your public IP address.
3. **Forward ports** 80 and/or 443 in your router to your reverse proxy server.
4. **Configure the reverse proxy** (in Nginx, this often goes in `/etc/nginx/sites-available/default` or a separate conf file) to route requests:
   ```nginx
   server {
       listen 80;
       server_name app1.myhomelab.com;

       location / {
           proxy_pass http://192.168.1.5:8080;
       }
   }
   ```
   You’d repeat for each subdomain or use separate files for clarity.
5. **Generate SSL certificates** using Let’s Encrypt (e.g., with Certbot), or let the reverse proxy manage certificates automatically if it supports that (like Caddy does).
6. **Reload/Restart** Nginx (or the reverse proxy service) to apply changes.

---

## 7. Putting It All Together

Once you have a reverse proxy in place:

- You’ll no longer need to remember which port each service runs on; you can simply type the correct domain/subdomain in your browser.
- SSL/TLS is easy to manage (and renew) in one centralized location.
- You can set up advanced authentication or a SSO portal for your homelab services.
- You reduce security risk by exposing only the reverse proxy to the internet, rather than each service individually.

---

### Final Thoughts

A reverse proxy is basically a single front door to your homelab. By directing all traffic through this “smart door,” you can better organize, secure, and scale your internal services—be they media servers, data dashboards, HPC job schedulers, or any other experiments you spin up.

If you want to expand your knowledge further, you might look into:

- **Docker Compose** or **Kubernetes** for easily spinning up your reverse proxy alongside your other containers.
- **Monitoring and Logging** (e.g., using Prometheus or Grafana) to track traffic and performance across your homelab.
- **Authentication gateways** like OAuth2 Proxy if you want single sign-on for multiple services behind the reverse proxy.

Once you get comfortable with a reverse proxy, you’ll find you can much more easily stand up new web services in your homelab without juggling a tangle of open ports or insecure connections. Enjoy the newfound simplicity!


#### You:
<time datetime="2025-01-16T04:57:05.671Z" title="1/16/2025, 1:57:05 PM">13:57</time>

do i need to worry about this if i only want to access my resources inside of my home network

#### ChatGPT:
<time datetime="2025-01-16T04:57:43.835Z" title="1/16/2025, 1:57:43 PM">13:57</time>

**Short Answer**\
If you only want to access your homelab services within your home network and don’t mind typing internal IP addresses or remembering port numbers, you don’t *strictly* need a reverse proxy. It’s completely possible to run everything “as-is” inside your LAN.

However, even for an internal-only setup, a reverse proxy can still bring significant convenience and benefits—especially as your homelab grows beyond a few services.

---

## Why Bother with a Reverse Proxy if It’s All Internal?

1. **Easier Access**
   - You get rid of having to remember that Plex is on “192.168.1.5:32400” and your dashboard is on “192.168.1.7:3000.”
   - Instead, you can type something like `plex.myhomelab.local` or `dashboard.myhomelab.local`.

2. **Consistent User Experience**
   - You can organize multiple services under neat domains or subdomains (like `cluster.myhomelab.local/hpc` or `monitor.myhomelab.local`).
   - It feels more polished and helps keep you in a “production-like” mindset, which is great if you’re also experimenting with HPC clusters or container orchestration.

3. **Centralized SSL/TLS**
   - Even on your home network, you may want encrypted connections. For instance, if you’re logging in to a private GitLab or Nextcloud.
   - A reverse proxy can handle SSL certificates (self-signed or using something like [Let’s Encrypt’s DNS challenge](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) if you have a domain pointing to your home network). This way, you don’t have to configure SSL in each service individually.
   - Encryption internally can be important if you’re using shared Wi-Fi or want to future-proof your setup in case you do open access later.

4. **Better Organization and Future Expansion**
   - Many people start out local-only, but end up wanting to securely access specific services from outside (e.g., from work, while traveling).
   - Having a reverse proxy in place now means you can later open up a single port (443) and securely route traffic to whichever internal services you choose.

5. **Unified Access Control**
   - If you have multiple services, it can be convenient to control access in a single place. For example, you can password-protect or use Single Sign-On (SSO) at the reverse proxy level, ensuring consistent policy across all services.
   - You might enable multi-factor authentication for all your internal resources, especially if you manage sensitive data or HPC job schedulers.

6. **Scalability**
   - If you’re tinkering with HPC or data analytics clusters, you may spin up multiple nodes or container-based services. A reverse proxy (like **Traefik** or **Nginx**) can handle load balancing or route to different containers automatically. This is extremely helpful if you do container orchestration in Docker Swarm or Kubernetes.

---

## When You Can Safely Skip It

- **Small Homelab with 1–2 Services**: If you have just a few services and are okay remembering their ports, you might not need the extra complexity.
- **No Plan to Expose Anything Externally**: If there’s zero chance you will want to access services remotely, or you’re comfortable with a simple VPN solution for remote access, a reverse proxy might feel like overkill.

---

## Middle-Ground Approaches

1. **mDNS/Avahi** for Local Hostnames
   - If you only need local hostname resolution, you can rely on mDNS (on Linux/Apple devices) or something like Avahi. For instance, `myserver.local` might resolve automatically, and you won’t have to remember IPs.
   - This doesn’t solve the “port number” problem, though—it just replaces IP addresses with friendly names.

2. **Internal DNS**
   - You could set up a local DNS server (like **Pi-hole** or **dnsmasq**) that resolves `plex.myhomelab.local` to 192.168.1.5 and `dashboard.myhomelab.local` to 192.168.1.7.
   - Still, you’ll typically need a reverse proxy if you want to serve those multiple internal IPs on ports 80/443 in a more seamless way (with HTTPS, subpaths, etc.).

3. **VPN Tunnels**
   - If you set up a VPN (e.g., WireGuard, OpenVPN), you can access your LAN from outside as though you’re physically there—bypassing any need for a reverse proxy for external access.
   - Yet, you might still choose a reverse proxy on top of that for convenience, central TLS, or advanced routing.

---

## Bottom Line

- **If you’re content with just local IPs/ports** and no immediate plan for external access, you *can* skip the reverse proxy for now.
- **But if you want a more streamlined, “production-like” experience**—with custom domain names, centralized SSL, easier expansion for HPC or distributed services, single sign-on, etc.—even an entirely internal reverse proxy can be a great addition.

It’s a bit of extra setup, but many homelab enthusiasts find it valuable in the long run, especially if they grow their homelab or if they want to keep developing their networking and DevOps skills (like HPC cluster management, container orchestration, or general infrastructure best practices).

---

### Next Steps

- Look into **Dockerizing** your reverse proxy. Tools like **NGINX Proxy Manager**, **Caddy**, or **Traefik** have container images that make them easy to spin up and maintain.
- If you decide to go for it, try some initial config that routes one or two services internally to see how it feels and if it simplifies your workflow.
- Keep learning about HPC cluster schedulers (like **Slurm**) or container orchestration, because as you expand, a reverse proxy often becomes more valuable in tying everything together seamlessly in your homelab.

In other words, a reverse proxy isn’t *mandatory* if you’re staying strictly local and have minimal services, but it can significantly improve how you manage and access your homelab—even behind closed doors.


#### You:
<time datetime="2025-01-16T05:01:15.857Z" title="1/16/2025, 2:01:15 PM">14:01</time>

here are all of my services. how do i access these resources via https
```
# ──────────────────────────────────────────────────────────────
# 1. Monitoring
# ──────────────────────────────────────────────────────────────
- Monitoring:
    - Netdata Cloud:
        icon: /icons/netdata.png
        href: https://app.netdata.cloud/spaces/ranch-space/rooms/all-nodes/nodes
        description: Monitor all nodes in ranch-space

    - Glances (ubuntu-server):
        icon: /icons/glances.png
        href: http://192.168.1.200:61208/
        description: Glances web UI for ubuntu-server


# ──────────────────────────────────────────────────────────────
# 2. My Network
# ──────────────────────────────────────────────────────────────
- My Network:
    - UniFi Gateway:
        icon: /icons/unifi.png
        href: http://192.168.1.1
        description: UniFi OS Gateway admin panel

# ──────────────────────────────────────────────────────────────
# 3. My Tools
# ──────────────────────────────────────────────────────────────
- My Tools:
    - Hoarder Dashboard:
        icon: /icons/hoarder.png
        href: http://192.168.1.200:3000/dashboard/bookmarks
        description: My Hoarder dashboard

# ──────────────────────────────────────────────────────────────
# 4. DNS Servers
# ──────────────────────────────────────────────────────────────
- DNS Servers:
    - rpi-technitium-1:
        icon: /icons/technitium.png
        href: http://192.168.1.234:5380
        description: Technitium DNS on Pi #1

    - rpi-technitium-2:
        icon: /icons/technitium.png
        href: http://192.168.1.235:5380
        description: Technitium DNS on Pi #2

# ──────────────────────────────────────────────────────────────
# 5. Remote Access
# ──────────────────────────────────────────────────────────────
- Remote Access:
    - RDP to 192.168.1.200 (ashwin):
        icon: /icons/rdp.png
        href: rdp://ashwin@192.168.1.200
        description: Start a Remote Desktop session

# ──────────────────────────────────────────────────────────────
# 6. Smart Home
# ──────────────────────────────────────────────────────────────
- Smart Home:
    - Home Assistant:
        icon: /icons/homeassistant.png
        href: http://192.168.1.141:8123
        description: My Home Assistant dashboard

# ──────────────────────────────────────────────────────────────
# 7. Network Storage
# ──────────────────────────────────────────────────────────────
- Network Storage:
    - Synology NAS:
        icon: /icons/synology.png
        href: https://192.168.1.213:2663
        description: Synology DSM web UI

# ──────────────────────────────────────────────────────────────
# 8. SSH Access
# ──────────────────────────────────────────────────────────────
- SSH Access:
    - ranch-router (192.168.1.1):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.1
        description: SSH into ranch-router

    - ubuntu-server (192.168.1.200):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.200
        description: SSH into ubuntu-server

    - home-assistant (192.168.1.141):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.141
        description: SSH into home-assistant

    - living-room-speakers (192.168.1.201):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.201
        description: SSH into living-room-speakers

    - rpi-technitium-1 (192.168.1.234):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.234
        description: SSH into rpi-technitium-1

    - rpi-technitium-2 (192.168.1.235):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.235
        description: SSH into rpi-technitium-2

    - synology-nas (192.168.1.213):
        icon: /icons/ssh.png
        href: ssh://ashwin@192.168.1.213
        description: SSH into synology-nas

# ──────────────────────────────────────────────────────────────
# 9. Databases
# ──────────────────────────────────────────────────────────────
- Databases:
    - MyDB (psql):
        icon: /icons/postgres.png
        # If your system can handle postgres:// links, it may auto-launch a DB client
        href: postgres://myuser@192.168.1.200:5432/mydb
        description: psql -h 192.168.1.200 -U myuser -d mydb

# ──────────────────────────────────────────────────────────────
# 10. Audio & Power
# ──────────────────────────────────────────────────────────────
- Audio & Power:
    - Node-RED Network Streamer:
        icon: /icons/nodered.png
        href: http://192.168.1.176
        description: Node-RED admin for the network streamer

    - PS Audio Powerplant P5:
        icon: /icons/ps-audio.png
        href: http://192.168.1.37
        description: PS Audio Powerplant P5 admin

# ──────────────────────────────────────────────────────────────
# 11. Logs
# ──────────────────────────────────────────────────────────────
- Logs:
    - HQPlayer / Roon Logs:
        icon: /icons/logs.png
        href: http://192.168.1.200:8081/
        description: Detailed HQPlayer / Roon logs viewer

# ──────────────────────────────────────────────────────────────
# 12. Dashboards
# ──────────────────────────────────────────────────────────────
- Dashboards:
    - This Homepage:
        icon: /icons/homepage.png
        href: http://192.168.1.200:8082/
        description: Self-referential link to this very dashboard
- Documentation:
        - Outline Docs:
            icon: /icons/outline.png
            href: http://192.168.1.200:8083/
            description: Internal documentation powered by Outline

#### ChatGPT:
<time datetime="2025-01-16T05:02:12.806Z" title="1/16/2025, 2:02:12 PM">14:02</time>

Below is a high-level overview of how to serve all these internal web UIs and dashboards over HTTPS using a **reverse proxy** (e.g., **Nginx**, **Caddy**, or **Traefik**)—even if they’re only accessible inside your home network. We’ll walk through the core steps, explain the DNS side of things, and mention a few nuances to watch out for. By the end, you’ll know how to map URLs like:

```
https://glances.mylab.local/
https://unifi.mylab.local/
https://hoarder.mylab.local/
...
```

to these existing IP+port combos in your homelab—securely over HTTPS.

---

## 1. Planning Your Internal “Domain”

1. **Decide on a (sub)domain name** to use internally, like:
   - `mylab.local`
   - `mylab.lan`
   - `mydomain.home`
   - Or something similar that’s *not* used on the public internet (if you only want local access).

2. **Use an Internal DNS Server** (e.g., [Technitium](https://github.com/TechnitiumSoftware/DnsServer), *dnsmasq*, or Pi-hole) to resolve that domain to the IP address of your reverse proxy server.
   - E.g., `hoarder.mylab.local → 192.168.1.200 (reverse proxy IP)`

3. Make sure all devices on your LAN use that DNS server so that `*.mylab.local` resolves to the correct IP.

> **Tip**: Since you’re already running Technitium DNS on your Raspberry Pis, you can easily add custom DNS records for each subdomain pointing to your reverse proxy.

---

## 2. Choose a Reverse Proxy

You’ll install and configure a reverse proxy on a machine that’s always on. Common choices:

- **Nginx** (classic, widely documented)
- **Caddy** (automatic HTTPS, simple config)
- **Traefik** (built for dynamic container environments, easy Docker integration)

**All** can do the same fundamental job: route incoming requests on HTTPS port 443 (and optionally HTTP port 80 for redirects) to the right internal IP/port.

---

### Example Setup: Nginx

Below is a conceptual outline (not an exhaustive config) to show how you’d route one service:

```nginx
# /etc/nginx/conf.d/glances.conf
server {
    listen 80;
    server_name glances.mylab.local;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name glances.mylab.local;

    # SSL cert/key (see below on how to generate or manage these)
    ssl_certificate /etc/nginx/certs/glances.crt;
    ssl_certificate_key /etc/nginx/certs/glances.key;

    location / {
        proxy_pass http://192.168.1.200:61208/;
        # (Optional) preserve host headers, etc.
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

You’d repeat similar blocks for each service, changing `server_name` and `proxy_pass` as appropriate.

---

## 3. Obtaining HTTPS Certificates

Even if you’re only using this inside your home network, HTTPS is still valuable for encrypted logins and preventing snooping on your LAN. You have **two** main ways:

### A. Internal/Local CA (Self-Signed or Private CA)

1. Create a self-signed certificate or set up a local Certificate Authority (CA) on your main workstation.
2. Install or trust that CA certificate on all devices that access your homelab (PC, phone, etc.).
3. Generate certificates for each subdomain using that CA.

**Pros**:

- Works fully offline, no need for external DNS or port forwarding.
- Once the CA is trusted by all your devices, each subdomain certificate is recognized as “secure.”

**Cons**:

- Extra step: you must add the CA to your devices’ trust store.
- Not valid outside of your LAN (which is fine if you’re never exposing it publicly).

---

### B. Let’s Encrypt Certificates

If you do want a “real” certificate from Let’s Encrypt, you have two main routes:

1. **DNS Challenge**: You prove domain ownership by adding a DNS TXT record (no need for inbound port 80/443 from the internet).
2. **HTTP Challenge**: You temporarily expose port 80 to the internet so Let’s Encrypt can validate your domain.

**Pros**:

- Certificates are trusted by everyone (browsers, phones, etc.) out of the box.
- No manual CA trust needed.

**Cons**:

- Requires some domain that you own publicly (e.g., `mylab.duckdns.org` or `mylab.example.com`) plus the correct DNS or port-forwarding.
- More complicated if you truly only want local access.

---

## 4. Basic Steps to Configure HTTPS Routing

1. **Install Your Reverse Proxy** (Nginx, Caddy, or Traefik) on a single machine (e.g., the `ubuntu-server (192.168.1.200)`) or another dedicated device.

2. **Configure DNS** so `service.mylab.local` (or any chosen domain) resolves to that proxy machine’s local IP.

3. **Create an Nginx “Server Block” (or config file)** for each service. For instance:
   - `glances.mylab.local.conf`
   - `unifi.mylab.local.conf`
   - `hoarder.mylab.local.conf`
   - etc.

4. **Proxy Traffic** to the internal IP/port:
   ```nginx
   location / {
       proxy_pass http://192.168.1.200:61208/;
   }
   ```

5. **Add SSL Certificate Paths** in each config block if you’re using local CA or Let’s Encrypt.

6. **Reload/Restart** the reverse proxy to apply new configs.

7. **Test** by going to `https://glances.mylab.local`. You should see the Glances web UI.

---

## 5. Mapping Each Service to HTTPS

Here’s an example mapping you might consider:

| Subdomain                   | Proxy Pass Target               | Notes                                                                                                                      |
| --------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `netdata.mylab.local`       | `https://app.netdata.cloud/...` | Actually external (Netdata Cloud). Usually you don’t need to proxy SaaS apps, but you *can* if you want an internal alias. |
| `glances.mylab.local`       | `http://192.168.1.200:61208/`   | Glances UI.                                                                                                                |
| `unifi.mylab.local`         | `http://192.168.1.1`            | UniFi admin panel.                                                                                                         |
| `hoarder.mylab.local`       | `http://192.168.1.200:3000/`    | Hoarder dashboard.                                                                                                         |
| `dns1.mylab.local`          | `http://192.168.1.234:5380/`    | Technitium on Pi #1.                                                                                                       |
| `dns2.mylab.local`          | `http://192.168.1.235:5380/`    | Technitium on Pi #2.                                                                                                       |
| `homeassistant.mylab.local` | `http://192.168.1.141:8123/`    | Home Assistant.                                                                                                            |
| `synology.mylab.local`      | `https://192.168.1.213:2663`    | Synology DSM (already HTTPS, but you can offload SSL at the proxy if you want).                                            |
| `nodered.mylab.local`       | `http://192.168.1.176`          | Node-RED admin.                                                                                                            |
| `psaudio.mylab.local`       | `http://192.168.1.37`           | P5 Powerplant UI.                                                                                                          |
| `roonlogs.mylab.local`      | `http://192.168.1.200:8081/`    | HQPlayer / Roon logs.                                                                                                      |
| `docs.mylab.local`          | `http://192.168.1.200:8083/`    | Outline docs.                                                                                                              |

> **Note**: For the services already running on HTTPS (like Synology DSM), you can:
>
> - Terminate SSL at the proxy and forward HTTP to the Synology, **OR**
> - Use SSL passthrough if you want the Synology to handle its own certificate.

---

## 6. Handling Services That Don’t Like Proxies

Most web dashboards work fine behind a reverse proxy, but occasionally you’ll encounter:

- **Non-HTTP services** (like RDP, SSH, or PostgreSQL). These typically **cannot** be proxied by a standard “HTTP reverse proxy.”
  - For RDP (`rdp://`), you can’t just route that traffic via Nginx. You’d either:
    - Access them directly at `rdp://192.168.1.200`, **or**
    - Use something like a **VPN** or a specialized “TCP-level” proxy.
- **Apps with absolute URLs** or weird web sockets. You may need to configure `proxy_http_version 1.1;` and `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` to handle websockets.

Since your list includes RDP/SSH, just keep in mind these are *not* typically forwarded via an **HTTP** reverse proxy. They either remain “as is” on the local network, or you’d set up a VPN or something like Guacamole for remote RDP/SSH through the browser.

---

## 7. Example Nginx Configuration Snippet (Fuller Example)

Below is a slightly more complete snippet for `glances.mylab.local`. Repeat for each service with changes to the domain and `proxy_pass` target:

```nginx
# /etc/nginx/conf.d/glances.conf

# Redirect all HTTP to HTTPS
server {
    listen 80;
    server_name glances.mylab.local;

    # If someone visits http://glances.mylab.local, redirect them
    return 301 https://glances.mylab.local$request_uri;
}

server {
    # Listen on HTTPS
    listen 443 ssl http2;
    server_name glances.mylab.local;

    # Certificates (self-signed or from your local CA)
    ssl_certificate     /etc/nginx/certs/glances.crt;
    ssl_certificate_key /etc/nginx/certs/glances.key;

    # If using Let's Encrypt, Certbot might manage these paths automatically.

    location / {
        proxy_pass http://192.168.1.200:61208/;
        proxy_http_version 1.1;       # Often recommended for websockets, etc.
        proxy_set_header Host $host;  
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 8. Optional Extras

1. **Single Sign-On (SSO)**: You can protect any site behind an authentication gateway (e.g., [Authelia](https://www.authelia.com/), [OAuth2 Proxy](https://oauth2-proxy.github.io/)). This way, each dashboard can be behind a login page, even if the app itself doesn’t support authentication.

2. **Path-Based Routing**: Instead of subdomains, you can do something like `https://mylab.local/glances`, `https://mylab.local/hoarder`, but subdomains are usually cleaner.

3. **Automatic HTTPS with Caddy**: If you use [Caddy](https://caddyserver.com/), it can automatically fetch and renew certificates—especially if you have a valid public DNS and use Let’s Encrypt. For local-only usage with a private CA, you’d still feed Caddy your certificates or trust an internal CA.

4. **Load Balancing & Health Checks**: Overkill for a small homelab, but if you’re doing HPC or container orchestration, you can have your proxy do round-robin or more advanced routing to multiple backend instances.

---

## Putting It All Together

1. **Set up or designate a server** (like your `ubuntu-server`) to run the reverse proxy.
2. **Install** Nginx/Caddy/Traefik.
3. **Create internal DNS records** in Technitium DNS (e.g., `glances.mylab.local → 192.168.1.200`).
4. **Configure the proxy** for each web-based service:
   - Add a server block/subdomain config pointing to the internal IP/port.
   - Make sure you have valid certificates (internal CA or Let’s Encrypt).
5. **Restart & Test**: Go to `https://glances.mylab.local`.

At this point, you should be able to access everything with a nice HTTPS URL, no messy port numbers, and centralized TLS security. If you ever decide you want external access (e.g., from the road), you can simply open or forward a single port (443) to the reverse proxy, rather than exposing all your services individually.

---

### Final Takeaway

Even if you only run everything on your LAN, a reverse proxy with HTTPS:

- **Cleans up** the user experience (no more `http://192.168.x.x:port`).
- **Centralizes** certificate management (one place to handle SSL).
- **Prepares** you for future expansions (e.g., HPC clusters, container orchestration, or external access).

It’s a bit of initial work to set up, but pays off in convenience, security, and consistency. Happy labbing!
