---
title: Securing Login Pages with Auth
source: https://chatgpt.com/c/678a8e75-fe18-8003-a491-6a0f652c8148
---

# Securing Login Pages with Auth

#### You:
<time datetime="2025-01-17T17:08:06.887Z" title="1/18/2025, 2:08:06 AM">02:08</time>

i'm setting up nginx on my homelab to enable ssl access everywhere. i am concerned about having login pages to my services public to the internet. can i secure these pages behind a single auth?

#### ChatGPT:
<time datetime="2025-01-17T17:08:54.680Z" title="1/18/2025, 2:08:54 AM">02:08</time>

Absolutely! A common solution in homelab setups is to put a reverse proxy (like Nginx) in front of all your internal services, terminate SSL/TLS there, and enforce a single authentication layer before granting access. This way, you only expose the reverse proxy’s login screen to the internet, and if someone can’t pass that, they never see the individual service logins. Below are a few approaches to consider:

---

## 1. Simple Approach: HTTP Basic Auth

If you just need a quick username/password gate, HTTP Basic Auth is the easiest method:

1. **Generate a password file**:
   ```bash
   sudo apt-get install apache2-utils
   htpasswd -c /etc/nginx/.htpasswd yourUser
   # Enter a password when prompted
   ```

2. **Reference it in your Nginx config**:
   ```nginx
   server {
       listen 443 ssl;
       server_name your_domain.com;

       ssl_certificate /etc/ssl/certs/your_cert.crt;
       ssl_certificate_key /etc/ssl/private/your_key.key;

       location / {
           auth_basic "Restricted Access";
           auth_basic_user_file /etc/nginx/.htpasswd;
           proxy_pass http://internal_service:port;
       }
   }
   ```

3. **Result**:
   - Visitors hitting `https://your_domain.com` will be prompted for the username and password stored in the `.htpasswd` file.
   - Once they pass Basic Auth, they’re forwarded to the internal service’s login page.

### Pros

- Simple to set up (no extra services needed).
- Quick for a small homelab environment.

### Cons

- Not really *single sign-on*—each subdomain/host would need the same snippet or a shared file.
- HTTP Basic Auth has no extra security features like MFA or advanced token-based auth.

---

## 2. Auth Request Module with a Central Gate

If you want a bit more power but still within Nginx, you could use the [`auth_request` directive][1]. Essentially, you set up a small “authentication endpoint” (another Nginx server block or a small web service) that issues 200/401 responses based on whether the user is authenticated. This approach can let you handle sessions, cookies, or something more elegant than Basic Auth.

A simplified structure:

```nginx
# Auth service
server {
    listen 127.0.0.1:8080;
    location /auth {
        # Check cookie or session
        # If user is authenticated -> return 200
        # If not -> return 401
    }
}

# Main proxy
server {
    listen 443 ssl;
    server_name your_domain.com;

    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;

    location / {
       auth_request /internal-auth; 
       error_page 401 = /login;

       # Once authenticated, pass to the service
       proxy_pass http://internal_service:port;
    }

    location /internal-auth {
       proxy_pass http://127.0.0.1:8080/auth;
    }

    location /login {
       # Present a login page from your auth service
       # This is where the user logs in to get a session cookie
    }
}
```

This setup is more flexible—you could store sessions in Redis or a local DB, add 2FA, track logins, etc. But it’s definitely more complex than Basic Auth.

---

## 3. True Single Sign-On (SSO) with Identity Providers

If you want a “one login to rule them all” experience (with Multi-Factor Auth, OIDC, SAML, etc.), consider an identity provider (IdP). Popular self-hosted solutions include:

- **Keycloak**
- **Authelia**
- **Authentik**

### General Flow

1. **User visits** your service (e.g., `https://service1.your_domain.com`).
2. **Nginx** sees no valid session/cookie and redirects them to your IdP login page (e.g., `https://idp.your_domain.com`).
3. **User logs in** with username/password, possibly MFA.
4. **IdP issues** an authentication token/cookie that indicates the user is now authenticated.
5. **Nginx** sees the valid token and **forwards** the user to their desired service, bypassing the service’s internal login if configured for SSO.

### Why bother?

- **Consistency**: All services use the same login portal.
- **Security**: You can centrally manage MFA, password policies, session timeouts.
- **Scalability**: As your homelab grows, you won’t duplicate auth logic across multiple apps.

---

## 4. Other Network-Based Solutions

Beyond Nginx-based auth, some homelab enthusiasts offload everything behind a VPN or mesh network like **Tailscale** or **ZeroTier**. These tools create a secure overlay network so you don’t even need to expose your services publicly—only devices authorized into your Tailscale/ZeroTier network can see them. It’s a different approach than a single web-based login, but worth mentioning if you’re concerned about internet exposure at all.

---

## Which Approach to Choose?

- **Basic Auth**: If you just want a quick gate and accept the trade-offs.
- **Auth Request Module**: If you’re comfortable customizing Nginx conf to unify the login flow and possibly integrate your own session/cookie logic.
- **Full-Fledged SSO with Keycloak/Authelia/Authentik**: For a robust solution with MFA, roles, groups, and advanced security policies.
- **VPN/Mesh**: Hide the services altogether unless you’re on a secure network.

In a homelab context—especially if you’re curious about **Kubernetes** clusters or want deeper knowledge of **identity and access management**—running something like Keycloak or Authelia is an excellent way to learn about modern authentication flows. But if you’re just getting started, Basic Auth is a fine first step.

---

### TL;DR

**Yes**, you can absolutely secure all your login pages behind a single authentication. The easiest is a global Basic Auth in Nginx, but for advanced features like MFA or single sign-on across multiple subdomains, look into solutions like Authelia or Keycloak in tandem with Nginx’s reverse proxy capabilities.

[1]: https://nginx.org/en/docs/http/ngx_http_auth_request_module.html


#### You:
<time datetime="2025-01-18T03:18:43.434Z" title="1/18/2025, 12:18:43 PM">12:18</time>

help me setup oidc provider Authentik on a dedicated rpi4to secure my homelab

#### ChatGPT:
<time datetime="2025-01-18T03:19:26.780Z" title="1/18/2025, 12:19:26 PM">12:19</time>

Below is a step-by-step guide for running Authentik—an open-source identity provider (IdP) that supports **OIDC**, **SAML**, **LDAP**, and more—on a dedicated Raspberry Pi 4 to secure your homelab. By the end, you’ll have a fully functioning OIDC provider (and SSO) that you can use to protect your internal services.

> **Note:** These steps assume you have a Raspberry Pi 4 running a 64-bit OS (e.g., Raspberry Pi OS 64-bit, Ubuntu 64-bit). Authentik’s containers require a 64-bit architecture, so 32-bit images won’t work.

---

# 1. Prerequisites

1. **Raspberry Pi 4** with at least 4GB RAM (8GB is preferred if you plan to run multiple services in parallel).
2. **64-bit OS** installed (e.g., Raspberry Pi OS 64-bit).
3. **Docker** and **Docker Compose** installed.
4. **A domain name** (optional but strongly recommended), so you can expose Authentik at `auth.mydomain.com` or similar.
5. **Nginx reverse proxy** (or Traefik, Caddy, etc.) to front Authentik with TLS. You can also let Authentik handle TLS directly, but most homelab setups use a dedicated reverse proxy.

If you haven’t installed Docker + Docker Compose, follow these official steps or run:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sudo bash

# Install Docker Compose (using pip or the official binary)
sudo apt-get update
sudo apt-get install -y python3-pip libffi-dev
sudo pip3 install docker-compose
```

---

# 2. Create a Docker Compose File for Authentik

In a dedicated directory on your Pi (e.g., `/home/pi/authentik`), create `docker-compose.yml`:

```yaml
version: "3.4"
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    # Expose Authentik on port 9000 internally (we'll reverse proxy externally)
    ports:
      - "127.0.0.1:9000:9000"
    env_file:
      - .env  # We'll define environment variables here
    depends_on:
      - redis
      - postgresql
    volumes:
      - authentik_media:/media
      - authentik_pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped

  postgresql:
    image: postgres:13-alpine
    container_name: authentik_postgresql
    environment:
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: supersecurepassword
      POSTGRES_DB: authentik
    restart: unless-stopped

volumes:
  authentik_media:
  authentik_pgdata:
```

**Key Points**:

- We map Authentik’s internal port to **`127.0.0.1:9000`**, meaning it is only accessible on localhost. This way, only your reverse proxy (running on the same host) can reach it.
- We added a Redis and a Postgres container. Authentik needs both for session caching and persistent storage.
- We’re storing data in Docker volumes (`authentik_media` and `authentik_pgdata`).

---

# 3. Environment Variables

Create an `.env` file in the same directory:

```bash
# The "external" URL for Authentik. Adjust if you're using HTTP or a different domain.
AUTHENTIK_HOST=http://127.0.0.1:9000
# If you already have a domain set up (e.g., auth.mydomain.com) via reverse proxy with TLS:
# AUTHENTIK_HOST=https://auth.mydomain.com

# Important for generating correct URLs in OIDC and SAML flows.
AUTHENTIK_OUTPOST_DOMAIN=auth.mydomain.com

# Set up your email config if you want password resets and notifications
AUTHENTIK_EMAIL__HOST=smtp.gmail.com
AUTHENTIK_EMAIL__PORT=587
AUTHENTIK_EMAIL__USERNAME=your_smtp_user
AUTHENTIK_EMAIL__PASSWORD=your_smtp_password
AUTHENTIK_EMAIL__USE_TLS=True
```

(You can also configure these in the Authentik admin UI later, but environment variables are handy if you want to keep your config consistent across restarts.)

---

# 4. Launch Authentik

From `/home/pi/authentik`:

```bash
docker-compose up -d
```

Docker Compose will pull the required images and start the services. Check with:

```bash
docker-compose logs -f
```

When Authentik first starts, it will run database migrations and create an admin account. Keep an eye on the logs for a message like:

```
[...]
User created: 
    Username: akadmin 
    Password: <randomly-generated-or-empty-if-you-set-env-var>
```

Make sure to copy this password if it is displayed; otherwise, you’ll need to reset it later via CLI. If you don’t see a password, you can set one with:

```bash
docker-compose exec authentik authentik bootstrap
```

(This command also helps you reset the default admin user or password.)

---

# 5. Access the Authentik Admin Interface

If you’re exposing Authentik locally on port 9000, you can browse to `http://<YOUR_PI_IP>:9000/if/flow/auth-standalone/` or just `http://<YOUR_PI_IP>:9000` to see the login page. Log in with the admin credentials from the logs.

> **If you’re behind a reverse proxy** (recommended for SSL), configure your DNS or `/etc/hosts` to point `auth.mydomain.com` to your Pi’s IP, and route traffic from Nginx to `127.0.0.1:9000`.

---

# 6. Configure SSL with Nginx Reverse Proxy (Recommended)

To protect the traffic to Authentik, you can offload SSL to Nginx (the same Nginx instance that secures your other homelab services). For example, in your **Nginx** config:

```nginx
server {
    listen 443 ssl http2;
    server_name auth.mydomain.com;

    ssl_certificate /etc/letsencrypt/live/auth.mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auth.mydomain.com/privkey.pem;

    location / {
        proxy_pass       http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- Replace `auth.mydomain.com` with your domain and correct certificate paths.
- Make sure you have `server_name auth.mydomain.com;` and the SSL certs from Let’s Encrypt or a CA you control.

Now, going to **`https://auth.mydomain.com`** should bring up the Authentik login screen securely via TLS.

---

# 7. Basic Authentik Configuration

1. **Login & Admin**: Head to `https://auth.mydomain.com` and log in with your admin account.
2. **Configure the “Root” Domain** in *Admin > Administration > Core > Tenants*. Set the *Issuer* or *external host* to `https://auth.mydomain.com` so the OIDC endpoints generate correct URLs.
3. **Enable Email** if needed, under *Admin > Administration > Core > Email*, matching the SMTP settings you put in `.env`.
4. **Set up a Directory** (e.g., the default “User Database”) for storing your homelab accounts, or configure external providers like LDAP/AD if you have them.

---

# 8. Protecting Services with Authentik (OIDC/Forward Auth)

Authentik has a concept of “Applications” which define how external services authenticate. For example, if you want to secure a web service (like Nextcloud, Home Assistant, or Gitea) behind Authentik, you have two popular approaches:

1. **Use Authentik as an OIDC Provider**:
   - Configure the application (Nextcloud, etc.) to use OIDC for single sign-on, pointing it to Authentik’s OIDC discovery URL at `https://auth.mydomain.com/application/o/`.
   - This requires the application to support OIDC natively.

2. **Forward Auth (Auth Proxy)** via Authentik Outposts:
   - You can use **Nginx**’s `auth_request` in combination with Authentik’s “Outpost” container or built-in forward-auth endpoints.
   - This is great if your application doesn’t natively support OIDC/SAML. Nginx checks if the user is authenticated with Authentik, and if not, it redirects them to the Authentik login flow.

### Example: Authentik as OIDC for Another Service

1. **Create an Application** in Authentik:
   - *Applications > Add Application*
   - Enter a name (e.g., `Nextcloud`), pick *Provider Type: OIDC*, and *Redirect URI* that matches your service.
2. **Get Client ID / Secret** in Authentik for that application.
3. **In Nextcloud** (or whatever service):
   - Go to its OIDC configuration section.
   - Enter the *Client ID*, *Client Secret*, and *OIDC Issuer URL* (which is typically `https://auth.mydomain.com/application/o/`)
   - Provide the callback URL to the *Redirect URI* in Authentik.
4. **Test Logging In**: When you open Nextcloud’s web interface, it should redirect to Authentik to sign in, then bounce back.

### Example: Forward Auth With Nginx

1. **Add an “Outpost”** in Authentik for Forward Auth:
   - *Admin > Outposts*
   - Define a new Outpost of type “Reverse Proxy” or “Forward Auth.”
2. **Add your service as an Application** so Authentik knows which flow to use.
3. **Nginx Config** might look like:

   ```nginx
   server {
       listen 443 ssl;
       server_name service.mydomain.com;

       ssl_certificate /etc/letsencrypt/live/service.mydomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/service.mydomain.com/privkey.pem;

       # Forward authentication to Authentik
       auth_request /authenticate;

       location / {
           # If the user is authenticated, proxy to internal service
           proxy_pass http://127.0.0.1:8080;
       }

       location = /authenticate {
           internal;
           proxy_pass https://auth.mydomain.com/outpost.goauthentik.io/forward_auth/...
           # Additional headers, etc.
       }
   }
   ```

   - When a request hits `service.mydomain.com`, Nginx calls `/authenticate` first.
   - If Authentik sees an authenticated session, it returns `200`. Otherwise, it returns `401` and triggers a redirect to the Authentik login.

---

# 9. Additional Security Enhancements

1. **Enable MFA**: In Authentik, you can configure 2FA methods (TOTP, WebAuthn, etc.) so that users have to provide a second factor at login.
2. **Use Groups & Policies**: Authentik can limit access to certain applications based on user group membership or advanced policies.
3. **Audit Logging**: Check *Admin > Administration > Events* to see sign-in attempts, application usage, etc.
4. **Backup**: Regularly back up your `authentik_pgdata` volume and any configuration you store in `.env`.

---

# 10. Wrap-Up

By placing Authentik behind Nginx (or another reverse proxy) on your Raspberry Pi 4, you get:

- **A secure OIDC/SAML identity provider** for your homelab.
- **Single Sign-On (SSO)** for multiple services.
- **Optional MFA/2FA** for stronger authentication.
- **Centralized user and policy management** in an easy-to-use admin console.

Now you can protect all your homelab’s login pages with **one** authentication flow instead of juggling multiple logins. This approach is more powerful and secure than using HTTP Basic Auth alone, and it’s an excellent learning opportunity for modern **Identity and Access Management (IAM)** concepts.

**Next steps**:

- Integrate each of your homelab services with Authentik using either OIDC or forward auth.
- Experiment with advanced Authentik features (custom flows, policies, outposts, etc.).

**Useful References**:

- [Authentik Official Docs](https://goauthentik.io/docs/)
- [Authentik Docker/Compose Examples](https://goauthentik.io/docs/deployment/docker)
- [Nginx Auth Request Doc](https://nginx.org/en/docs/http/ngx_http_auth_request_module.html)

Enjoy your newly secured, SSO-enabled homelab!


#### You:
<time datetime="2025-01-18T03:19:42.413Z" title="1/18/2025, 12:19:42 PM">12:19</time>

let's setup a reverse proxy first using traefik

#### ChatGPT:
<time datetime="2025-01-18T03:20:26.587Z" title="1/18/2025, 12:20:26 PM">12:20</time>

Below is a step-by-step guide to deploy **Traefik** on a Raspberry Pi (or similar ARM-based system) as a reverse proxy for your homelab. Traefik will handle incoming requests on ports 80 and 443, automatically obtain SSL/TLS certificates from Let’s Encrypt, and route traffic to other containers or internal services (like Authentik or anything else you plan to run).

---

# 1. Prerequisites

1. **Raspberry Pi 4 (64-bit OS)**
   - Make sure you’re running a 64-bit OS if you plan to host containers like Authentik later on.
2. **Docker & Docker Compose installed**
   - If not, follow official instructions or run:
     ```bash
     curl -fsSL https://get.docker.com | sh
     sudo apt-get install -y python3-pip
     sudo pip3 install docker-compose
     ```
3. **A domain name**
   - For example, `mydomain.com` (subdomains like `auth.mydomain.com` or `service.mydomain.com` will be routed by Traefik).
   - You need to point DNS records at your Pi’s **public** IP (or use a dynamic DNS service).
4. **Ports 80 and 443 open/forwarded** to your Pi if you want automatic Let’s Encrypt certificates.

---

# 2. Create a Traefik Project Folder

On your Raspberry Pi, make a dedicated folder for Traefik’s configuration and Docker Compose:

```bash
mkdir ~/traefik
cd ~/traefik
```

We’ll keep `traefik.yml` (the main config), an `acme.json` file (to store Let’s Encrypt certificates), and `docker-compose.yml` here.

---

# 3. Create the Main Traefik Configuration (traefik.yml)

Inside `~/traefik/`, create a file called `traefik.yml` (or `traefik.toml`—we’ll use YAML here). This file will define the entrypoints, providers, and ACME (Let’s Encrypt) settings for Traefik. For example:

```yaml
# traefik.yml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "your-email@mydomain.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"
      # Alternatively, you can use DNS challenge if your ISP blocks port 80.

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false  # So Traefik only routes containers you explicitly label
```

**Key Points**:

- **`api.dashboard: true`** enables Traefik’s web dashboard (we’ll protect it with authentication or IP restrictions later).
- **`entryPoints.web`** listens on port 80, and **`websecure`** listens on port 443 for HTTPS.
- **`certificatesResolvers.letsencrypt`** configures Let’s Encrypt via HTTP challenge.
- **`providers.docker`** allows Traefik to read Docker labels and create routes automatically.

---

# 4. Prepare the acme.json File

This file will securely store your Let’s Encrypt certificates. Create it and set permissions so only root (inside the container) can read it:

```bash
touch acme.json
chmod 600 acme.json
```

---

# 5. Create the Docker Compose File (docker-compose.yml)

Now let’s define how to run Traefik via Docker Compose. In `~/traefik/docker-compose.yml`:

```yaml
version: "3.3"

services:
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=your-email@mydomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--api.dashboard=true"
      # The above command args mirror what's in traefik.yml.
      # We could rely on the file, but including them here is also valid.
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "./traefik.yml:/traefik.yml:ro"  # If you want to use the file-based config
      - "./acme.json:/letsencrypt/acme.json"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    labels:
      # Label for the Traefik dashboard route (optional)
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.mydomain.com`)"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
      # Optionally add basic auth or IP whitelist to secure the dashboard
      #- "traefik.http.routers.traefik.middlewares=dashboard-auth"
      #- "traefik.http.middlewares.dashboard-auth.basicauth.users=<user:hashedpass>"
      # You can generate a hashed password using: htpasswd -nbB myuser mypassword

```

**Key Points**:

- **`image: traefik:latest`**: Traefik provides multi-arch images, so it should pull the correct ARM-based image for Raspberry Pi automatically.
- **`ports`** maps host ports 80/443 to the container’s 80/443.
- **`volumes`**:
  - We mount `acme.json` at `/letsencrypt/acme.json` so Traefik can write SSL certs to it.
  - We mount the Docker socket read-only to let Traefik discover other containers via labels.
  - We also mount `traefik.yml` as read-only for additional config.
- **`labels`** can define the route for the Traefik dashboard. If you want to see the dashboard at `https://traefik.mydomain.com`, you can add a DNS record `traefik.mydomain.com` -> Pi’s IP.

> If you prefer to keep all your config in `traefik.yml`, you can remove some `command` entries from Docker Compose. Traefik merges file-based config (`traefik.yml`) with Docker-based config. For simplicity, we show both approaches.

---

# 6. Launch Traefik

From `~/traefik`:

```bash
docker-compose up -d
```

Check logs:

```bash
docker-compose logs -f
```

You should see Traefik start, listen on port 80/443, and not error out about ACME. Once you set your DNS properly (point `traefik.mydomain.com` or any other subdomain at your Pi’s IP), you can test:

- `http://traefik.mydomain.com` → Should redirect to HTTPS if everything is correct.
- `https://traefik.mydomain.com` → Should serve the Traefik dashboard if you didn’t secure it.

If Let’s Encrypt is set up correctly, Traefik will automatically request a certificate the first time you browse to the subdomain, and store it in `acme.json`.

---

# 7. Routing Additional Services Behind Traefik

To have Traefik route traffic to other containers or hosts on your network, you generally:

1. **Run another container** with the appropriate Docker labels (for Docker-based services).
2. Or define a **file-based route** in a `.yml` if the service is on a different host or not containerized.

### Example: Container Labels Approach

Imagine you have a simple whoami service:

```yaml
version: "3"

services:
  whoami:
    image: containous/whoami # Simple test container that returns info
    container_name: whoami
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whoami.rule=Host(`whoami.mydomain.com`)"
      - "traefik.http.routers.whoami.entrypoints=websecure"
      - "traefik.http.routers.whoami.tls.certresolver=letsencrypt"
    networks:
      - default
```

When you `docker-compose up -d`, Traefik sees these labels and creates a route:

- `https://whoami.mydomain.com` → routes to this container.
- Certs are automatically handled by `certresolver=letsencrypt`.

### Example: File-Based Routing

In `traefik.yml` (or a separate `dynamic.yml`), you could define:

```yaml
http:
  routers:
    my-service:
      rule: "Host(`app.mydomain.com`)"
      entryPoints:
        - websecure
      service: my-service
      tls:
        certResolver: letsencrypt

  services:
    my-service:
      loadBalancer:
        servers:
          - url: "http://192.168.1.100:8080"
```

That way, **`app.mydomain.com`** routes to an internal IP/service.

---

# 8. Next Steps: Integrating Authentik

Once Traefik is up and running:

1. **Deploy Authentik** using Docker Compose or another method (e.g. in `~/authentik`).
2. **Expose Authentik** on a subdomain (e.g., `auth.mydomain.com`) by adding the relevant labels to the Authentik container or a file-based route in Traefik.
3. **Secure the Dashboard** so only you or trusted users can see it (e.g., Basic Auth middlewares, IP whitelist, or full SSO with Authentik).

A typical label-based snippet to route to Authentik might look like:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.authentik.rule=Host(`auth.mydomain.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
      # Optionally some middlewares if you want to force HTTPS or add extra headers
    # ...rest of Authentik config
```

Then, go to `https://auth.mydomain.com` to access Authentik.

---

## Wrapping Up

1. **You have Traefik** running on your Pi, listening on ports 80 and 443, ready to handle inbound requests.
2. **Let’s Encrypt** is automatically issuing certificates for any subdomain you label with `traefik.http.routers.[name].tls.certresolver=letsencrypt`.
3. **Dashboard** is at `traefik.mydomain.com` (or any subdomain you set in labels). Remember to protect it!

**Traefik** is a powerful choice for reverse proxy and certificate management in a homelab—especially if you plan to have multiple services (like Nextcloud, Home Assistant, Authentik, Gitea, etc.). Label-based routing keeps everything organized in Docker Compose, and auto-SSL via Let’s Encrypt means you don’t have to fuss with certificates manually.

---

### Helpful Links

- **Traefik Docs**: <https://doc.traefik.io/traefik/>
- **Docker Labels Reference**: <https://doc.traefik.io/traefik/providers/docker/>
- **Homelab Example with Traefik + Authentik**: [Authentik docs on proxies](https://goauthentik.io/docs/integrations/proxy)

Once you’ve got Traefik stable, the next step is to integrate your services under subdomains—potentially with **OIDC** or **SAML** from Authentik for a full single sign-on experience across your homelab. Enjoy!


#### You:
<time datetime="2025-01-18T03:23:13.602Z" title="1/18/2025, 12:23:13 PM">12:23</time>

ashwin@ubuntu-server:~$ cd ~/traefik/
ashwin@ubuntu-server:~/traefik$ ls
docker-compose.yml  letsencrypt  traefik.yaml
ashwin@ubuntu-server:~/traefik$ sudo micro traefik.yml
[sudo] password for ashwin: 
ashwin@ubuntu-server:~/traefik$ sudo micro traefik.yaml
ashwin@ubuntu-server:~/traefik$ rm traefik.yaml
rm: cannot remove 'traefik.yaml': Permission denied
ashwin@ubuntu-server:~/traefik$ sudo rm traefik.yaml 
ashwin@ubuntu-server:~/traefik$ sudo micro traefik.yml
ashwin@ubuntu-server:~/traefik$ sudo micro traefik.yml
ashwin@ubuntu-server:~/traefik$ touch acme.json
chmod 600 acme.json
touch: cannot touch 'acme.json': Permission denied
chmod: cannot access 'acme.json': No such file or directory
ashwin@ubuntu-server:~/traefik$ sudo micro ~/traefik/docker-compose.yml
ashwin@ubuntu-server:~/traefik$ sudo micro ~/traefik/docker-compose.yml
ashwin@ubuntu-server:~/traefik$ docker-compose up -d
Command 'docker-compose' not found, but can be installed with:
sudo snap install docker          # version 27.2.0, or
sudo apt  install docker-compose  # version 1.29.2-6
See 'snap info docker' for additional versions.
ashwin@ubuntu-server:~/traefik$ docker compose up -d
[+] Running 5/5
 ✔ traefik 4 layers [⣿⣿⣿⣿]      0B/0B      Pulled                                         3.8s 
   ✔ 1f3e46996e29 Already exists                                                          0.0s 
   ✔ 546f86135cc0 Pull complete                                                           0.6s 
   ✔ a8e9a2da4a5e Pull complete                                                           1.6s 
   ✔ 0c7e1a2deb57 Pull complete                                                           1.7s 
[+] Running 1/1
 ✔ Container traefik  Started                                                             0.6s 
ashwin@ubuntu-server:~/traefik$ docker-compose logs -f
Command 'docker-compose' not found, but can be installed with:
sudo snap install docker          # version 27.2.0, or
sudo apt  install docker-compose  # version 1.29.2-6
See 'snap info docker' for additional versions.
ashwin@ubuntu-server:~/traefik$ docker compose logs -f
traefik  | 2025-01-18T03:22:49Z ERR The ACME resolve is skipped from the resolvers list error="unable to get ACME account: permissions 755 for /letsencrypt/acme.json are too open, please use 600" resolver=letsencrypt
traefik  | 2025-01-18T03:22:49Z ERR error="HTTP challenge is not enabled" entryPointName=web routerName=acme-http@internal
traefik  | 2025-01-18T03:22:49Z ERR error="HTTP challenge is not enabled" entryPointName=web routerName=acme-http@internal
traefik  | 2025-01-18T03:22:49Z ERR Router uses a nonexistent certificate resolver certificateResolver=letsencrypt routerName=traefik@docker
traefik  | 2025-01-18T03:22:49Z ERR Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https@docker

#### ChatGPT:
<time datetime="2025-01-18T03:23:27.762Z" title="1/18/2025, 12:23:27 PM">12:23</time>

It looks like you’ve run into a couple of common Traefik/ACME setup issues on your Ubuntu server:

1. **Permission problems** with `acme.json` (Traefik insists on `chmod 600`).
2. **Certificate resolver mismatch** or missing settings (Traefik complains that HTTP challenge is not enabled).

Below is how you can resolve these issues step by step.

---

## 1. Fix Directory Ownership & Permissions

Because you got “Permission denied” when creating `acme.json`, it suggests the `~/traefik/` directory might be owned by `root` or otherwise restricted. Let’s fix that so your normal user (ashwin) can create and edit files there:

```bash
# Make ashwin the owner of everything under ~/traefik
sudo chown -R ashwin:ashwin ~/traefik

# Double-check ownership
ls -l ~/traefik
```

Now you can create `acme.json` without `sudo`:

```bash
cd ~/traefik
touch acme.json
chmod 600 acme.json
```

This resolves the **“unable to get ACME account: permissions 755 for /letsencrypt/acme.json are too open”** error and ensures Traefik can read/write the file securely.

---

## 2. Verify the Traefik Configuration

### A) Example `traefik.yml` (or `traefik.yaml`)

Make sure your Traefik config has an **HTTP challenge** mapped to the `web` entrypoint. A minimal example:

```yaml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "your-email@example.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"  # Make sure this matches 'web'
        
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
```

> Notice that the `certificatesResolvers.letsencrypt.acme.httpChallenge` block specifically references `entryPoint: "web"`. This is critical for the HTTP challenge to work. If your logs say **“HTTP challenge is not enabled”**, it usually means Traefik can’t find the correct challenge or entrypoint in your config.

### B) Matching Certificate Resolver Names

If in your **Docker labels** (or in your `docker-compose.yml`) you use something like:

```yaml
labels:
  - "traefik.http.routers.myservice.tls.certresolver=myresolver"
```

Then you must define **`myresolver`** in the `traefik.yml` under `certificatesResolvers:`. If your `traefik.yml` only defines `letsencrypt`, but your container references `myresolver`, Traefik will complain that the certificate resolver does not exist. The safest approach is to keep things consistent—use one resolver name everywhere, for instance **`letsencrypt`**:

```yaml
labels:
  - "traefik.http.routers.myservice.tls.certresolver=letsencrypt"
```

### C) Confirm the `entryPoints` in Your Compose vs. Config

If you’ve repeated arguments in the `docker-compose.yml` under `command: [...]`, verify they match your `traefik.yml`. For example, if you see:

```yaml
command:
  - "--entrypoints.web.address=:80"
  - "--entrypoints.websecure.address=:443"
  - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
  - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
```

then your file-based config should not conflict with those or override them. Traefik merges (and can override) file-based settings with CLI flags. If you’re new to Traefik, **pick one method** (fully file-based or mostly CLI-based) to reduce confusion.

---

## 3. Clean Up Any Old Containers or References

Your logs show references to:

```
Router uses a nonexistent certificate resolver certificateResolver=myresolver
routerName=outline-https@docker
```

That implies you have a container or service labeled `outline-https` referencing a `myresolver` that doesn’t exist. You can:

1. **Remove** or **stop** the “outline” container if you’re not using it.
2. **Update its labels** to use the same resolver as the rest of your setup (e.g., `letsencrypt`).

For example, if you see something like:

```yaml
services:
  outline:
    ...
    labels:
      - "traefik.http.routers.outline-https.rule=Host(`outline.mydomain.com`)"
      - "traefik.http.routers.outline-https.tls=true"
      - "traefik.http.routers.outline-https.tls.certresolver=myresolver"
      ...
```

change `myresolver` → `letsencrypt` or define a `myresolver` block in your `traefik.yml`. Once consistent, re-deploy.

---

## 4. Redeploy Traefik and Check Logs

After fixing permissions, double-checking your `traefik.yml`, and aligning the labels, run:

```bash
cd ~/traefik
docker compose up -d
docker compose logs -f
```

Look for the ACME info:

```
traefik  | time="..." level=info msg="Register... ACME..."
traefik  | time="..." level=info msg="Certificates obtained for domain..."

```

If Let’s Encrypt completes the challenge, you’ll see no more “skipped from the resolvers list” messages.

**Common pitfalls**:

- DNS not pointing to your server’s public IP (make sure your domain’s A/AAAA record is correct).
- Port 80 blocked by ISP or firewall. The HTTP challenge uses port 80 inbound. If your ISP blocks 80, consider the **DNS challenge** instead.
- Using the same email or domain too many times in a short period can rate-limit Let’s Encrypt. (Check logs if you see “429 Too Many Requests.”)

---

## Summary of Fixes

1. **Change ownership** of your Traefik folder so you can create and edit files as your normal user.
2. **Set `acme.json` to `chmod 600`** so Traefik can use it without security warnings.
3. **Ensure the certificate resolver name** in your Docker labels matches exactly what’s defined in `traefik.yml`.
4. **Enable the HTTP challenge** for your `letsencrypt` (or any named) certificate resolver if you want automatic HTTP-based certificate issuance.
5. **Remove or correct** any containers referencing a nonexistent resolver (like “myresolver”).

Once these steps are done, Traefik should be able to issue certificates via Let’s Encrypt and route traffic properly without the errors you’re seeing.

---

### Next Steps

- Secure the Traefik dashboard (by adding a middleware for Basic Auth or hooking it up to your SSO once you deploy Authentik).
- Add additional services behind Traefik by labeling them with `- "traefik.enable=true"` and pointing them to the correct domain, entrypoint, and resolver.
- If you plan to integrate **Authentik** (OIDC, SAML) next, you can route `auth.mydomain.com` through Traefik to your Authentik container.

Good luck, and enjoy your newly streamlined homelab reverse proxy setup!


#### You:
<time datetime="2025-01-18T03:25:29.510Z" title="1/18/2025, 12:25:29 PM">12:25</time>

 1 api:                                                                                        
 2   dashboard: true                                                                           
 3                                                                                             
 4 entryPoints:                                                                                
 5   web:                                                                                      
 6     address: ":80"                                                                          
 7   websecure:                                                                                
 8     address: ":443"                                                                         
 9                                                                                             
10 certificatesResolvers:                                                                      
11   letsencrypt:                                                                              
12     acme:                                                                                   
13       email: "your-email@example.com"                                                       
14       storage: "/letsencrypt/acme.json"                                                     
15       httpChallenge:                                                                        
16         entryPoint: "web"  # Make sure this matches 'web'                                   
17                                                                                             
18 providers:                                                                                  
19   docker:                                                                                   
20     endpoint: "unix:///var/run/docker.sock"                                                 
21     exposedByDefault: false                                                                 
22                                                                                             
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
traefik.yml (21,28) | ft:yaml | unix | utf-8                      Alt-g: bindings, Ctrl-g: help
                                                                                               


 1 version: "3.3"                                                                              
 2                                                                                             
 3 services:                                                                                   
 4   traefik:                                                                                  
 5     image: traefik:latest                                                                   
 6     container_name: traefik                                                                 
 7     restart: unless-stopped                                                                 
 8     command:                                                                                
 9       - "--providers.docker=true"                                                           
10       - "--providers.docker.exposedbydefault=false"                                         
11       - "--entrypoints.web.address=:80"                                                     
12       - "--entrypoints.websecure.address=:443"                                              
13       - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"                       
14       - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"             
15       - "--certificatesresolvers.letsencrypt.acme.email=your-email@mydomain.com"            
16       - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"           
17       - "--api.dashboard=true"                                                              
18       # The above command args mirror what's in traefik.yml.                                
19       # We could rely on the file, but including them here is also valid.                   
20     ports:                                                                                  
21       - "80:80"                                                                             
22       - "443:443"                                                                           
23     volumes:                                                                                
24       - "./traefik.yml:/traefik.yml:ro"  # If you want to use the file-based config         
25       - "./acme.json:/letsencrypt/acme.json"                                                
26       - "/var/run/docker.sock:/var/run/docker.sock:ro"                                      
27     labels:                                                                                 
28       # Label for the Traefik dashboard route (optional)                                    
29       - "traefik.enable=true"                                                               
30       - "traefik.http.routers.traefik.rule=Host(`traefik.mydomain.com`)"                    
31       - "traefik.http.routers.traefik.service=api@internal"                                 
32       - "traefik.http.routers.traefik.entrypoints=websecure"                                
33       - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"                         
34       # Optionally add basic auth or IP whitelist to secure the dashboard                   
35       #- "traefik.http.routers.traefik.middlewares=dashboard-auth"                          
36       #- "traefik.http.middlewares.dashboard-auth.basicauth.users=<user:hashedpass>"        
37       # You can generate a hashed password using: htpasswd -nbB myuser mypassword           
38                                                                                             
39                                                                                             
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
docker-compose.yml (39,1) | ft:yaml | unix | utf-8                Alt-g: bindings, Ctrl-g: help
                                                                                               

#### ChatGPT:
<time datetime="2025-01-18T03:26:12.319Z" title="1/18/2025, 12:26:12 PM">12:26</time>

Below is an explanation of what’s in each file, how they work together, and what you need to watch out for when combining file-based config (`traefik.yml`) with CLI flags (the `command:` lines in `docker-compose.yml`). If everything is correct, Traefik will spin up, listen on ports 80/443, automatically fetch Let’s Encrypt certificates, and serve the dashboard at `traefik.mydomain.com`.

---

## 1. Understanding Your Two Configuration Files

### A) `traefik.yml` (file-based configuration)

```yaml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "your-email@example.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
```

1. **Enables the API Dashboard** on Traefik.
2. Defines two **entry points**:
   - `web` on port 80 (for HTTP).
   - `websecure` on port 443 (for HTTPS).
3. Sets up an **ACME/Let’s Encrypt** resolver named `letsencrypt`, using the HTTP challenge on port 80.
4. Tells Traefik to read Docker labels from the Docker socket.
5. Tells Traefik not to expose containers by default unless they have `traefik.enable=true`.

### B) `docker-compose.yml` (container definition)

```yaml
version: "3.3"

services:
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=your-email@mydomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--api.dashboard=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "./traefik.yml:/traefik.yml:ro"
      - "./acme.json:/letsencrypt/acme.json"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.mydomain.com`)"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

1. Launches the **Traefik container** on your host, mapping ports 80 → `:80`, 443 → `:443`.
2. Uses the local file `traefik.yml` as a read-only mount **inside** the container.
3. Mounts `acme.json` to `/letsencrypt/acme.json` so Traefik can store certificates there.
4. Passes a bunch of **CLI flags** (under `command:`) that basically replicate what’s in `traefik.yml`.

### Which One “Wins”: File Config vs. CLI Flags?

Traefik **merges** configuration from file-based config, CLI flags, and providers (like Docker labels). In general:

- **CLI flags** (the `command:` lines) override or supplement the file-based config.
- If you have the same setting in both places, you may see duplicates in logs or partial overrides.

In your setup, it’s okay to have them both if they align exactly—but you must ensure they don’t conflict. For example, you set the ACME email to `your-email@example.com` in `traefik.yml` and `your-email@mydomain.com` in the CLI flags. One of these will effectively override the other. Make sure you pick one.

---

## 2. Matching Resolver Names & Fixing ACME Permissions

1. **Make sure `acme.json` has `chmod 600`.**
   - If Traefik complains about “permissions are too open” or you can’t create the file, run:
     ```bash
     cd ~/traefik
     sudo chown -R ashwin:ashwin ~/traefik  # Let your normal user manage it
     touch acme.json
     chmod 600 acme.json
     ```
   - This ensures Traefik can read/write certificates without a security warning.

2. **Use the same resolver name** in your labels as you define in the config.
   - In your example, you have `certificatesResolvers.letsencrypt`. The label is `traefik.http.routers.traefik.tls.certresolver=letsencrypt`. That matches fine.
   - If you had labeled something like `myresolver`, you would need `myresolver:` in the `traefik.yml`.

3. **Ensure your DNS points `traefik.mydomain.com` to your server’s public IP** (and you have port 80 and 443 open/forwarded). Otherwise, Let’s Encrypt can’t complete the HTTP challenge.

---

## 3. Verifying the Dashboard Works

With the above in place, do:

```bash
cd ~/traefik
docker compose up -d
docker compose logs -f
```

- Watch for messages like:
  ```
  traefik  | time="..." level=info msg="Starting provider..."
  traefik  | time="..." level=info msg="Server running on :80, :443..."
  traefik  | time="..." level=info msg="Register... ACME"
  traefik  | time="..." level=info msg="Certificates obtained for domain..."
  ```
- If all is well, hitting **`http://traefik.mydomain.com`** should redirect to **HTTPS**, with a valid certificate, and show the Traefik dashboard.

You might see a warning about an **unsecured dashboard**—meaning anyone who visits that domain can see it. If you want to secure it with Basic Auth, add something like:

```yaml
labels:
  - "traefik.http.routers.traefik.middlewares=dashboard-auth"
  - "traefik.http.middlewares.dashboard-auth.basicauth.users=user:$$apr1$$1iqrK7NF$$mEgb..."
```

(You can generate a hashed password with `htpasswd -nbB user password` on your system.)

---

## 4. Keep Your Config Simple (Optional Tips)

You’re effectively **duplicating** your config: once in `traefik.yml` and once in the `command:`. If you prefer purely file-based configuration:

1. Remove the lines under `command:` in `docker-compose.yml`.
2. Ensure your `traefik.yml` includes **all** the settings you need (entryPoints, ACME config, etc.).
3. Make sure the container knows to load that file. You already have:
   ```yaml
   volumes:
     - "./traefik.yml:/traefik.yml:ro"
   ```
   Then in the `Dockerfile` or `docker-compose`, you can add:
   ```yaml
   command:
     - "--configFile=/traefik.yml"
   ```
   or rely on `Traefik` automatically reading `/traefik.yml` as the default if no other flags are provided.

Alternatively, if you prefer **only CLI-based config**, you can remove or empty the `traefik.yml` and rely entirely on your `command:` flags. Either approach works, but mixing them can sometimes cause confusion.

---

## 5. Next Steps

1. **Add More Services**: For each web app or container you want behind Traefik, give it the appropriate labels:
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.myapp.rule=Host(`myapp.mydomain.com`)"
     - "traefik.http.routers.myapp.entrypoints=websecure"
     - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
   ```
2. **Integrate Single Sign-On** (Authelia, Authentik, or Keycloak). Route a subdomain like `auth.mydomain.com` to your IdP container and implement forward auth or OIDC for your internal services.
3. **Secure the Dashboard** so only you can access it (Basic Auth or IP whitelisting).
4. **Monitor Logs**: `docker compose logs -f` to see if Let’s Encrypt certs get issued successfully. If you see “Trying to challenge…,” but it fails, verify port 80 is open and DNS is correct.

With those steps, you’ll have a clean, automatically SSL-enabled reverse proxy in your homelab, plus an open path to setting up advanced authentication, single sign-on, or any other services you want to expose externally. Enjoy your streamlined setup!


#### You:
<time datetime="2025-01-18T03:28:15.844Z" title="1/18/2025, 12:28:15 PM">12:28</time>

 1 version: "3.3"                                                                              
 2                                                                                             
 3 services:                                                                                   
 4   traefik:                                                                                  
 5     image: traefik:latest                                                                   
 6     container_name: traefik                                                                 
 7     restart: unless-stopped                                                                 
 8     command:                                                                                
 9       - "--providers.docker=true"                                                           
10       - "--providers.docker.exposedbydefault=false"                                         
11       - "--entrypoints.web.address=:80"                                                     
12       - "--entrypoints.websecure.address=:443"                                              
13       - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"                       
14       - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"             
15       - "--certificatesresolvers.letsencrypt.acme.email=green.text5235@fastmail.com"        
16       - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"           
17       - "--api.dashboard=true"                                                              
18     ports:                                                                                  
19       - "80:80"                                                                             
20       - "443:443"                                                                           
21     volumes:                                                                                
22       - "./traefik.yml:/traefik.yml:ro"                                                     
23       - "./acme.json:/letsencrypt/acme.json"                                                
24       - "/var/run/docker.sock:/var/run/docker.sock:ro"                                      
25     labels:                                                                                 
26       - "traefik.enable=true"                                                               
27       - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"                     
28       - "traefik.http.routers.traefik.service=api@internal"                                 
29       - "traefik.http.routers.traefik.entrypoints=websecure"                                
30       - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"                         
31                                                                                             
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
docker-compose.yml (27,69) | ft:yaml | unix | utf-8               Alt-g: bindings, Ctrl-g: help
Saved docker-compose.yml                                                                       



 1 api:                                                                                        
 2   dashboard: true                                                                           
 3                                                                                             
 4 entryPoints:                                                                                
 5   web:                                                                                      
 6     address: ":80"                                                                          
 7   websecure:                                                                                
 8     address: ":443"                                                                         
 9                                                                                             
10 certificatesResolvers:                                                                      
11   letsencrypt:                                                                              
12     acme:                                                                                   
13       email: "green.text5235@fastmail.com"                                                  
14       storage: "/letsencrypt/acme.json"                                                     
15       httpChallenge:                                                                        
16         entryPoint: "web"                                                                   
17                                                                                             
18 providers:                                                                                  
19   docker:                                                                                   
20     endpoint: "unix:///var/run/docker.sock"                                                 
21     exposedByDefault: false                                                                 
22                                                                                             
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
                                                                                               
traefik.yml (22,1) | ft:yaml | unix | utf-8                       Alt-g: bindings, Ctrl-g: help
                                                                                               

#### ChatGPT:
<time datetime="2025-01-18T03:28:28.188Z" title="1/18/2025, 12:28:28 PM">12:28</time>

Let’s walk through how this setup works and what you should check to ensure it operates smoothly:

---

## 1. What You Have So Far

### `docker-compose.yml`

```yaml
version: "3.3"

services:
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=green.text5235@fastmail.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--api.dashboard=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "./traefik.yml:/traefik.yml:ro"
      - "./acme.json:/letsencrypt/acme.json"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
      - "traefik.http.routers.traefik.service=api@internal"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

1. **Maps ports 80 → :80** and **443 → :443** on the host for HTTP/HTTPS.
2. **Mounts**:
   - `traefik.yml` inside the container (read-only).
   - `acme.json` inside the container to store Let’s Encrypt certificates.
   - Docker socket (read-only) so Traefik can detect other container labels.
3. **Sets** Traefik to read from Docker, doesn’t expose containers by default, and sets up an ACME/Let’s Encrypt HTTP challenge on port 80.
4. **Adds labels** to expose the **Traefik dashboard** at `traefik.apsjado.com` over HTTPS using the `letsencrypt` resolver.

### `traefik.yml`

```yaml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "green.text5235@fastmail.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
```

1. Mirrors much of the same configuration in the CLI flags:
   - Dashboard, entryPoints, Let’s Encrypt with HTTP challenge, Docker provider settings.

Traefik merges both sets of configuration (the CLI flags from `command:` and the file-based config in `traefik.yml`). As long as they **match** and **don’t conflict**, you’ll be fine.

---

## 2. Ensure `acme.json` Permissions Are Correct

Traefik requires `acme.json` to have `chmod 600`, otherwise you might see errors like:

```
permissions 755 for /letsencrypt/acme.json are too open, please use 600
```

Make sure you own the file and set permissions properly (as your non-root user if desired):

```bash
cd ~/traefik
sudo chown ashwin:ashwin acme.json   # or your user/group
chmod 600 acme.json
```

*(Replace `ashwin:ashwin` with your actual username if different.)*

---

## 3. Check Your DNS & Ports

For Let’s Encrypt’s HTTP-01 challenge, you must ensure:

1. **DNS**: `traefik.apsjado.com` points to your server’s **public** IP.
2. **Port 80** is open/forwarded on your router/firewall, so Let’s Encrypt can complete the challenge.

You can verify DNS by running:

```bash
dig A traefik.apsjado.com
```

and confirm it resolves to the correct public IP.

---

## 4. Bring Up the Stack

Now just do:

```bash
cd ~/traefik
docker compose up -d
docker compose logs -f
```

Look for these messages in the logs:

1. **ACME registration**:
   ```
   "Register... ACME"
   "Certificates obtained for domain [traefik.apsjado.com]"
   ```
2. **No permission errors** about `/letsencrypt/acme.json`.
3. **EntryPoints listening** on :80 and :443 with no conflicts.

If it fails and says something like “Error getting challenge for domain,” double-check:

- DNS is correct.
- Port 80 → your server is open.
- No firewall or ISP is blocking inbound 80/443.

---

## 5. Access the Dashboard

If all goes well, visiting **`http://traefik.apsjado.com`** should redirect to **HTTPS** and present you with the Traefik dashboard. There should be a **valid TLS certificate** (no browser warnings). If you see an “unsecured / not private” error, Let’s Encrypt might not have succeeded or DNS might be incorrect.

### *Securing the Dashboard*

By default, **anyone** who knows `traefik.apsjado.com` can see your Traefik dashboard. You probably want to add **Basic Auth** or IP Whitelisting. For Basic Auth, add labels in your `docker-compose.yml`:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
  - "traefik.http.routers.traefik.service=api@internal"
  - "traefik.http.routers.traefik.entrypoints=websecure"
  - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
  - "traefik.http.routers.traefik.middlewares=dashboard-auth"
  - "traefik.http.middlewares.dashboard-auth.basicauth.users=user:$$apr1$$f4Ki..."
```

Generate the hashed password with:

```bash
htpasswd -nbB user password
```

and then escape any `$` signs by doubling them in `docker-compose.yml` (`$$`).

---

## 6. Next Steps

1. **Add More Services**\
   For each container or host-based service you want to route, just add labels (if it’s a Docker container) or file-based config (if it’s an external host). For example, to expose a container on **`whoami.apsjado.com`**:

   ```yaml
   version: "3.3"
   services:
     whoami:
       image: traefik/whoami
       container_name: whoami
       labels:
         - "traefik.enable=true"
         - "traefik.http.routers.whoami.rule=Host(`whoami.apsjado.com`)"
         - "traefik.http.routers.whoami.entrypoints=websecure"
         - "traefik.http.routers.whoami.tls.certresolver=letsencrypt"
   ```

2. **Integrate SSO**\
   Later, if you deploy Authentik or another IdP, you can have Traefik forward-auth requests, or let each service use OIDC.

3. **Decide on Config Approach**\
   You’re currently **duplicating** config with both CLI flags and a `traefik.yml`. This is allowed, but can lead to confusion. If you want to rely **purely** on the file, remove the `command:` lines. Alternatively, remove `traefik.yml` if you prefer to keep everything in CLI flags.

4. **Stay Up-to-Date**\
   `traefik:latest` is fine for a homelab, but consider using a specific version (e.g. `traefik:v2.10`) for stability.

---

### In Summary

1. **Your `docker-compose.yml` and `traefik.yml`** are aligned; they define the same `letsencrypt` ACME resolver and `web`/`websecure` entrypoints.
2. **Check** `acme.json` ownership and permissions (`chmod 600`).
3. **Ensure** DNS + port 80 open → Let’s Encrypt can do HTTP challenge.
4. **Spin up** the stack, watch logs, verify certificates get issued.
5. **Visit** `https://traefik.apsjado.com` → see the dashboard.
6. **Secure** the dashboard with Basic Auth or IP restrictions.

That’s it! You should have a working Traefik reverse proxy with automated Let’s Encrypt certificates. Next, you can add subdomain rules for other services and eventually integrate advanced authentication if you’d like. Enjoy your newly secured homelab reverse proxy.


#### You:
<time datetime="2025-01-18T03:28:36.858Z" title="1/18/2025, 12:28:36 PM">12:28</time>

 ✔ Container traefik  Started                                                             0.6s 
traefik  | 2025-01-18T03:28:27Z ERR The ACME resolve is skipped from the resolvers list error="unable to get ACME account: read /letsencrypt/acme.json: is a directory" resolver=letsencrypt
traefik  | 2025-01-18T03:28:27Z ERR error="HTTP challenge is not enabled" entryPointName=web routerName=acme-http@internal
traefik  | 2025-01-18T03:28:27Z ERR error="HTTP challenge is not enabled" entryPointName=web routerName=acme-http@internal
traefik  | 2025-01-18T03:28:27Z ERR Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https@docker
traefik  | 2025-01-18T03:28:27Z ERR Router uses a nonexistent certificate resolver certificateResolver=letsencrypt routerName=traefik@docker

#### ChatGPT:
<time datetime="2025-01-18T03:28:48.916Z" title="1/18/2025, 12:28:48 PM">12:28</time>

You’re seeing several related errors:

1. **`read /letsencrypt/acme.json: is a directory`**\
   Traefik expects `/letsencrypt/acme.json` to be **a file**, but right now there’s a **directory** mounted at that path.

2. **`HTTP challenge is not enabled`**\
   Traefik can’t issue certificates via HTTP challenge because of a config mismatch (or the ACME resolver is being skipped due to the first error).

3. **`Router uses a nonexistent certificate resolver certificateResolver=myresolver`**\
   One of your containers (Outline) references `myresolver` in its Docker labels, but there’s no such resolver defined in your Traefik config.

4. **`Router uses a nonexistent certificate resolver certificateResolver=letsencrypt`**\
   Traefik is also skipping the `letsencrypt` resolver because of the `acme.json` directory problem.

---

## 1. Fix the `acme.json` Directory Problem

First, stop Traefik:

```bash
docker compose down
```

Then check what you actually have in your `~/traefik` folder:

```bash
cd ~/traefik
ls -l
```

If there’s a **directory** named `acme.json`, remove it:

```bash
sudo rm -r acme.json
```

Now create a **file** named `acme.json`:

```bash
touch acme.json
chmod 600 acme.json
```

Make sure your `docker-compose.yml` mounts this file (not a directory) at `"/letsencrypt/acme.json"`, like so:

```yaml
services:
  traefik:
    ...
    volumes:
      - "./acme.json:/letsencrypt/acme.json"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
```

This ensures Traefik can read/write certificate data in that file without complaining about it being a directory or having the wrong permissions.

---

## 2. Remove or Fix the “myresolver” Reference

You have another container (likely Outline) that sets labels something like:

```yaml
labels:
  - "traefik.http.routers.outline-https.tls.certresolver=myresolver"
```

But your `traefik.yml` and CLI flags only define a resolver called `letsencrypt`—there’s no `myresolver`. To fix:

- **Either** remove or update that Outline container’s label to use `letsencrypt`:
  ```yaml
  - "traefik.http.routers.outline-https.tls.certresolver=letsencrypt"
  ```
- **Or** define a new resolver named `myresolver` in `traefik.yml`, just like you did for `letsencrypt`.

If you leave it as “myresolver,” Traefik will complain that it can’t find a matching resolver.

---

## 3. Make Sure the HTTP Challenge Is Enabled Correctly

Your file-based config and CLI flags should both enable the HTTP challenge on the `web` entrypoint. For example, in your `traefik.yml`:

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: "your-email@domain.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"
```

And in your Compose `command:` lines:

```yaml
command:
  - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
  - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
```

As soon as Traefik no longer “skips” the ACME resolver (due to the `acme.json` file error), you should see it attempt to get certificates using the HTTP challenge on port 80.

---

## 4. Retry & Monitor Logs

After fixing the file vs. directory issue and removing “myresolver” references:

1. **Start Traefik** again:
   ```bash
   docker compose up -d
   ```
2. **Check logs**:
   ```bash
   docker compose logs -f
   ```
3. Look for:
   - **No** more “is a directory” error.
   - Traefik registering/renewing with Let’s Encrypt:
     ```
     level=info msg="Register... ACME"
     level=info msg="Certificates obtained for domain [traefik.example.com]"
     ```
   - “HTTP challenge is not enabled” should disappear once the config is aligned.

---

## 5. Summary

1. **Delete** the accidental `acme.json` directory, create a **file** instead, and set `chmod 600`.
2. **Fix** or remove any references to `myresolver` in your containers or define that resolver.
3. **Ensure** your Let’s Encrypt config is consistent so the HTTP challenge is actually enabled on port 80.

Once Traefik sees a proper `acme.json` file, it should stop skipping the resolver, attempt the HTTP challenge on `web`, and finally obtain valid certificates for your domains. That will also resolve the “HTTP challenge not enabled” warnings. After that, you can expand Traefik’s config to protect more services in your homelab.


#### You:
<time datetime="2025-01-18T03:31:45.854Z" title="1/18/2025, 12:31:45 PM">12:31</time>

ashwin@ubuntu-server:~/traefik$ cd ~/traefik
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Network traefik_default  Created                                                       0.1s 
 ✔ Container traefik        Started                                                       0.3s 
traefik  | 2025-01-18T03:31:40Z ERR Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https@docker

#### ChatGPT:
<time datetime="2025-01-18T03:31:59.158Z" title="1/18/2025, 12:31:59 PM">12:31</time>

That final error means you have a container labeled with `certresolver=myresolver`, but your Traefik configuration only defines a resolver called `letsencrypt` (or none named `myresolver`). Traefik sees that label and complains it doesn’t know about any resolver named “myresolver.”

---

## 1. Find the Container with `myresolver`

Most likely this is your “Outline” container. You can confirm by checking each container’s labels:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

Then inspect the one you suspect has Outline:

```bash
docker inspect <container_name> | grep -i myresolver
```

You’ll see something like:

```
"traefik.http.routers.outline-https.tls.certresolver=myresolver"
```

---

## 2. Fix the Label

You have two basic choices:

### A) Change the Label to `letsencrypt`

If you want Outline to use the same ACME certificate resolver as everything else, just edit the container’s labels to reference `letsencrypt`, for example:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.outline-https.rule=Host(`outline.mydomain.com`)"
  - "traefik.http.routers.outline-https.entrypoints=websecure"
  - "traefik.http.routers.outline-https.tls.certresolver=letsencrypt"
  # or remove this line if you use a default resolver
```

Then re-deploy that container so it picks up the updated labels.

### B) Define a “myresolver” in `traefik.yml`

If you actually want a separate resolver named `myresolver`, you must define it in your `traefik.yml` (or as CLI flags) like so:

```yaml
certificatesResolvers:
  myresolver:
    acme:
      email: "you@example.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"
```

Then Outline’s label referencing `myresolver` will work.

---

## 3. Restart Traefik

Once you remove or correct the `myresolver` label, run:

```bash
docker compose up -d
docker compose logs -f
```

Now Traefik should no longer complain about a nonexistent certificate resolver, and it can properly issue/renew certificates for your Outline container.

---

### Why This Happens

Traefik’s logs specifically say, **“Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https\@docker”** because there’s no matching definition for “myresolver” in your config. A resolver name is completely arbitrary, but you must define it **both** in your labels (or app config) **and** in your Traefik config.

If you’re only using one resolver across all services, simply use the same name—commonly `letsencrypt`—everywhere. That keeps things simpler and avoids confusion.


#### You:
<time datetime="2025-01-18T03:35:15.968Z" title="1/18/2025, 12:35:15 PM">12:35</time>

 1 version: "3.8"                                                                                                                                    
 2                                                                                                                                                   
 3 networks:                                                                                                                                         
 4   traefik-net:                                                                                                                                    
 5     external: false                                                                                                                               
 6                                                                                                                                                   
 7 services:                                                                                                                                         
 8   outline:                                                                                                                                        
 9     image: outlinewiki/outline:latest                                                                                                             
10     container_name: outline_app                                                                                                                   
11     depends_on:                                                                                                                                   
12       - redis                                                                                                                                     
13     restart: always                                                                                                                               
14                                                                                                                                                   
15     # Connect Outline to the shared "traefik-net" network.                                                                                        
16     networks:                                                                                                                                     
17       - traefik-net                                                                                                                               
18                                                                                                                                                   
19     # Map host port 8083 → container port 3000 (for direct local access)                                                                          
20     ports:                                                                                                                                        
21       - "8083:3000"                                                                                                                               
22                                                                                                                                                   
23     # Map your local "config" folder to /app/config inside the container                                                                          
24     volumes:                                                                                                                                      
25       - ./config:/app/config                                                                                                                      
26                                                                                                                                                   
27     environment:                                                                                                                                  
28       # PostgreSQL connection details                                                                                                             
29       DATABASE_URL: "postgres://myuser:mypassword@192.168.1.200:5432/mydb"                                                                        
30       PGSSLMODE: disable                                                                                                                          
31                                                                                                                                                   
32       # Redis runs as "redis" on this network at port 6379                                                                                        
33       REDIS_URL: "redis://redis:6379"                                                                                                             
34                                                                                                                                                   
35       # Required secrets for Outline                                                                                                              
36       SECRET_KEY: "87f367dc3dc42d5d3c77377e6dc3ba564cb905196a2390662408abf1b430eb7f"                                                              
37       UTILS_SECRET: "35e632a4c39c49dfb3525b6b123e37f4e9688b2cd3cb3e3c13665d14dd27dd5e"                                                            
38                                                                                                                                                   
39       # Base URL for Outline’s own reference (Force HTTPS is off for now)                                                                         
40       FORCE_HTTPS: "true"                                                                                                                         
41       URL: "https://wiki.apsjado.com"                                                                                                             
42                                                                                                                                                   
43       # Example Slack OAuth credentials                                                                                                           
44       SLACK_KEY: "6482325282.8299666186421"                                                                                                       
45       SLACK_SECRET: "77688c2bff091fac18177fd85e5cab6c"                                                                                            
46                                                                                                                                                   
47     # Traefik labels for routing domain traffic to Outline                                                                                        
48     labels:                                                                                                                                       
49       # Enable Traefik for this container                                                                                                         
50       - "traefik.enable=true"                                                                                                                     
51                                                                                                                                                   
52       # HTTP router: if request Host == wiki.apsjado.com, on entrypoint "web" (port 80)                                                           
53       - "traefik.http.routers.outline-http.rule=Host(`wiki.apsjado.com`)"                                                                         
54       - "traefik.http.routers.outline-http.entrypoints=web"                                                                                       
55       # Redirect all HTTP to HTTPS                                                                                                                
56       - "traefik.http.routers.outline-http.middlewares=redirect-to-https"                                                                         
57       - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"                                                                  
58                                                                                                                                                   
59       # HTTPS router: Host == wiki.apsjado.com, on entrypoint "websecure" (port 443)                                                              
60       - "traefik.http.routers.outline-https.rule=Host(`wiki.apsjado.com`)"                                                                        
61       - "traefik.http.routers.outline-https.entrypoints=websecure"                                                                                
62       - "traefik.http.routers.outline-https.tls.certresolver=letsencrypt"                                                                         
63                                                                                                                                                   
64       # The service is on port 3000 inside the container                                                                                          
65       - "traefik.http.services.outline.loadbalancer.server.port=3000"                                                                             
66                                                                                                                                                   
67   redis:                                                                                                                                          
68     image: redis:alpine                                                                                                                           
69     container_name: outline_redis                                                                                                                 
70     restart: always                                                                                                                               
71                                                                                                                                                   
72     # Put Redis on the same network so "redis" hostname works for Outline                                                                         
73     networks:                                                                                                                                     
74       - traefik-net                                                                                                                               
75                                                                                                                                                   
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
/home/ashwin/outlinewiki/docker-compose.yml (1,1) | ft:yaml | unix | utf-8                                              Alt-g: bindings, Ctrl-g: help
                                                                                                                                                     traefik  | 2025-01-18T03:31:40Z ERR Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https@docker
traefik  | 2025-01-18T03:31:46Z ERR Unable to obtain ACME certificate for domains error="unable to generate a certificate for the domains [traefik.apsjado.com]: error: one or more domains had a problem:\n[traefik.apsjado.com] acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: NXDOMAIN looking up A for traefik.apsjado.com - check that a DNS record exists for this domain; DNS problem: NXDOMAIN looking up AAAA for traefik.apsjado.com - check that a DNS record exists for this domain\n" ACME CA=https://acme-v02.api.letsencrypt.org/directory acmeCA=https://acme-v02.api.letsencrypt.org/directory domains=["traefik.apsjado.com"] providerName=letsencrypt.acme routerName=traefik@docker rule=Host(`traefik.apsjado.com`)
^Ccanceled
ashwin@ubuntu-server:~/traefik$ 

#### ChatGPT:
<time datetime="2025-01-18T03:35:28.022Z" title="1/18/2025, 12:35:28 PM">12:35</time>

You have **two separate issues** showing up in your logs:

1. **“Router uses a nonexistent certificate resolver certificateResolver=myresolver routerName=outline-https\@docker”**
   - This implies some **old/leftover label** (possibly from an older Outline container or another service) is still referencing `myresolver`—but your current docker-compose for Outline references `letsencrypt`, so it’s not coming from your new config.

2. **“DNS problem: NXDOMAIN looking up A for traefik.apsjado.com”**
   - Let’s Encrypt can’t find a DNS record for `traefik.apsjado.com`, so the certificate request fails. You need to create (or fix) a DNS record pointing `traefik.apsjado.com` to your server’s **public** IP.

Below are the steps to resolve each issue.

---

## 1. Remove or Fix the “myresolver” Reference

Even though your new Outline `docker-compose.yml` has `"- traefik.http.routers.outline-https.tls.certresolver=letsencrypt"`, Traefik is still seeing a container with a label referencing `myresolver`. Common scenarios:

- **An older Outline container** is still running or present. Maybe you renamed the service in your `docker-compose.yml` without removing the old one.
- **Another container** or leftover config in a different folder still references `myresolver`.
- A **stale Docker service** from a prior stack never got removed.

### How to find it

1. **List all running containers**:
   ```bash
   docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
   ```
2. **Inspect each** suspicious container for `myresolver` in its labels:
   ```bash
   docker inspect <container_name> | grep -i myresolver
   ```
   If you see a label like:
   ```
   "traefik.http.routers.outline-https.tls.certresolver=myresolver"
   ```
   that’s the culprit.

### How to fix it

- **Option A**: Remove/stop that leftover container if you no longer need it:
  ```bash
  docker stop <container_name>
  docker rm <container_name>
  ```
- **Option B**: If you do need it, **update its label** to use your existing resolver (`letsencrypt`), or define a new `myresolver` in `traefik.yml` like:
  ```yaml
  certificatesResolvers:
    myresolver:
      acme:
        email: ...
        storage: "/letsencrypt/acme.json"
        httpChallenge:
          entryPoint: "web"
  ```
  and match your domain setup accordingly. But usually, it’s simpler to use the single `letsencrypt` resolver for everything.

Once that container’s label is gone or fixed, Traefik will stop complaining about `myresolver`.

---

## 2. Create a DNS Record for “traefik.apsjado.com”

The second error:

```
unable to generate a certificate for the domains [traefik.apsjado.com]: ...
DNS problem: NXDOMAIN looking up A for traefik.apsjado.com
```

means that **Let’s Encrypt can’t find any A/AAAA record** in DNS for `traefik.apsjado.com`. In other words, the domain name doesn’t resolve to your server’s public IP.

1. **Log into your DNS provider** (where you manage `apsjado.com` domain).
2. **Add/verify an A record** for `traefik.apsjado.com` pointing to your server’s public IP (e.g., `1.2.3.4`).
3. Wait 5-10 minutes for DNS propagation (sometimes more, depending on your TTL settings).
4. Test from your server or a DNS lookup:
   ```bash
   dig traefik.apsjado.com +short
   # Should return your IP
   ```

If you only need `wiki.apsjado.com` for Outline and **don’t** actually need `traefik.apsjado.com`, just remove or update that reference in your `traefik` container labels (where you specify the Host rule for the Traefik dashboard). Otherwise, create that DNS record so Let’s Encrypt can complete HTTP validation at `traefik.apsjado.com`.

---

## 3. After Fixes: Restart and Check Logs

After you’ve:

1. Removed the old container referencing `myresolver`, **or** updated it to use `letsencrypt`.
2. Created a DNS record for `traefik.apsjado.com` → your server’s IP (or removed references if you don’t need it).

Do:

```bash
docker compose down
docker compose up -d
docker compose logs -f
```

Look for:

- **No** more “myresolver” or “nonexistent resolver” errors.
- **ACME** tries to issue a certificate for `traefik.apsjado.com` and/or `wiki.apsjado.com`.
- A successful issuance message, like:
  ```
  level=info msg="Certificates obtained for domain [wiki.apsjado.com]"
  level=info msg="Certificates obtained for domain [traefik.apsjado.com]"
  ```

---

## Summary

1. **You have leftover config** referencing `myresolver`—remove or update it.
2. **Your DNS** is missing for `traefik.apsjado.com`, so Let’s Encrypt can’t issue a cert. Either add an A record or remove that domain from your config.
3. **Redeploy Traefik** and confirm in logs that the certificate issuance succeeds.

Once those are handled, Outline should be accessible at `https://wiki.apsjado.com` with a valid SSL certificate, and you’ll have a working Traefik environment for your homelab. Enjoy!


#### You:
<time datetime="2025-01-18T03:39:47.348Z" title="1/18/2025, 12:39:47 PM">12:39</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.3s 
 ✔ Network traefik_default  Removed                                                                                                             0.2s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.3s 
traefik  | 2025-01-18T03:38:43Z ERR Unable to obtain ACME certificate for domains error="unable to generate a certificate for the domains [traefik.apsjado.com]: error: one or more domains had a problem:\n[traefik.apsjado.com] acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: NXDOMAIN looking up A for traefik.apsjado.com - check that a DNS record exists for this domain; DNS problem: NXDOMAIN looking up AAAA for traefik.apsjado.com - check that a DNS record exists for this domain\n" ACME CA=https://acme-v02.api.letsencrypt.org/directory acmeCA=https://acme-v02.api.letsencrypt.org/directory domains=["traefik.apsjado.com"] providerName=letsencrypt.acme routerName=traefik@docker rule=Host(`traefik.apsjado.com`)
^Ccanceled
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.7s 
 ✔ Network traefik_default  Removed                                                                                                             0.2s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.2s 

#### ChatGPT:
<time datetime="2025-01-18T03:40:01.421Z" title="1/18/2025, 12:40:01 PM">12:40</time>

You’re still seeing the **NXDOMAIN** error for `traefik.apsjado.com` because Let’s Encrypt can’t find a DNS record for that domain. Essentially:

> **Let’s Encrypt** tries to verify ownership of `traefik.apsjado.com` by looking up its DNS (A/AAAA record) and attempting an HTTP challenge on that address. Since there is no DNS record pointing `traefik.apsjado.com` to your server’s public IP, the lookup fails.

You have **two simple options**:

---

## Option 1: Create the DNS Record for `traefik.apsjado.com`

1. **Go to your domain registrar or DNS provider** (where you manage `apsjado.com`).
2. **Add an “A” record** for `traefik.apsjado.com` → your server’s **public** IP address.
   - For example, `traefik.apsjado.com A 1.2.3.4` (replace `1.2.3.4` with your real public IP).
3. Wait a few minutes for DNS to propagate.
4. Test from your server or a local machine:
   ```bash
   dig traefik.apsjado.com +short
   # Should show your public IP
   ```
5. **Re-run** `docker compose up -d && docker compose logs -f`. Let’s Encrypt will now be able to resolve `traefik.apsjado.com` and complete the HTTP-01 challenge on port 80. If ports are open and your config is correct, you’ll get a certificate.

This is the best approach if you **do** want to serve the Traefik dashboard at `traefik.apsjado.com`.

---

## Option 2: Remove the `traefik.apsjado.com` Reference

If you **don’t** actually need `traefik.apsjado.com`, just remove (or comment out) the lines in your `docker-compose.yml` that define that router. For example, remove or comment:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
  - "traefik.http.routers.traefik.service=api@internal"
  - "traefik.http.routers.traefik.entrypoints=websecure"
  - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

Then Traefik won’t try to request a certificate for `traefik.apsjado.com`. Re-run:

```bash
docker compose down
docker compose up -d
docker compose logs -f
```

You’ll see no more errors about that domain. Of course, you then lose the “nice domain” for your dashboard. You can either skip a custom domain entirely or use a domain you **do** own and have an A record for.

---

## Verifying the Fix

- **If you keep `traefik.apsjado.com`**:
  - Ensure DNS is set properly, your domain resolves to the server, and ports 80/443 are open. Let’s Encrypt should issue a cert once it can reach the domain via HTTP-01 challenge.

- **If you remove `traefik.apsjado.com`**:
  - Traefik will no longer attempt to get a cert for that subdomain. The NXDOMAIN error goes away. If you still want to access the dashboard, you can do so via IP or an internal hostname (but it won’t have a valid cert unless you add a correct domain).

That’s it! Just pick which method makes sense for your homelab:

1. **Proper DNS** for `traefik.apsjado.com`
2. **Remove** the domain references if you don’t plan to use it

Once Let’s Encrypt sees a valid DNS record, you’ll stop getting that NXDOMAIN error in the logs and Traefik can serve traffic with a valid certificate.


#### You:
<time datetime="2025-01-18T03:40:27.922Z" title="1/18/2025, 12:40:27 PM">12:40</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.8s 
 ✔ Network traefik_default  Removed                                                                                                             0.3s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.3s 

#### ChatGPT:
<time datetime="2025-01-18T03:40:43.468Z" title="1/18/2025, 12:40:43 PM">12:40</time>

It looks like Traefik started successfully this time—**no errors** are displayed in your snippet. That typically means Traefik isn’t trying (and failing) to get a certificate for any domain that lacks a DNS record. If you removed all references to `traefik.apsjado.com` (or fixed your DNS), that would have resolved the previous **NXDOMAIN** errors.

Here’s how to confirm everything is working and what to do next:

---

## 1. Confirm No Errors in the Logs

Since your snippet only shows the containers starting, try:

```bash
docker compose logs -f
```

and wait a bit. If there’s no error about ACME or nonexistent resolvers, you’re good. You might just see standard Traefik info messages about providers and entrypoints starting up.

---

## 2. Check If You Removed `traefik.apsjado.com` References

- **If you commented out or removed** any labels/routers referencing `traefik.apsjado.com`, then Traefik won’t attempt to issue a certificate for that domain. That means no more NXDOMAIN errors, which explains why the logs are quiet now.

- **If you set up DNS** (an A record pointing `traefik.apsjado.com` to your server’s IP) and left the references in place, you should see Traefik attempting to acquire a certificate. You can confirm by looking for log messages like:
  ```
  level=info msg="Register... ACME"
  level=info msg="Certificates obtained for domain [traefik.apsjado.com]"
  ```

---

## 3. Test Any Other Subdomains

If you have other services (like Outline at `wiki.apsjado.com`), make sure **that** domain resolves in DNS to your server’s public IP and you have corresponding labels in your `docker-compose.yml`. For example:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.outline-https.rule=Host(`wiki.apsjado.com`)"
  - "traefik.http.routers.outline-https.tls.certresolver=letsencrypt"
  # etc...
```

Then watch the logs for any mention of a certificate being requested/issued for `wiki.apsjado.com`. If everything is configured correctly, you’ll see:

```
level=info msg="Certificates obtained for domain [wiki.apsjado.com]"
```

and can browse to `https://wiki.apsjado.com` with a valid SSL certificate.

---

## 4. Secure (or Remove) the Traefik Dashboard

- If you want to keep a dashboard domain (e.g. `traefik.apsjado.com`), then set up DNS and add Basic Auth or IP restrictions.
- If you don’t need an externally accessible dashboard, **remove** those labels or restrict it to your local network.

---

## 5. Summary / Next Steps

1. **No errors in your snippet** suggests Traefik is running without issue.
2. **Verify DNS** for any domains you do want certificates for.
3. **Check logs** to confirm certificates are being issued (or not).
4. **Access** your services at their configured domain names to ensure everything is working.

If you’ve removed references to `traefik.apsjado.com` and don’t see any new errors, you can proceed to protect additional services behind Traefik. If you’re aiming to integrate single sign-on (like Authentik or Authelia) next, just apply the same approach: create DNS records, add correct labels, and watch the logs for successful certificate issuance.

That’s it! It looks like you’re back to a clean slate—enjoy your error-free Traefik deployment.


#### You:
<time datetime="2025-01-18T03:41:40.325Z" title="1/18/2025, 12:41:40 PM">12:41</time>

 1 version: "3.3"                                                                                                                                    
 2                                                                                                                                                   
 3 services:                                                                                                                                         
 4   traefik:                                                                                                                                        
 5     image: traefik:latest                                                                                                                         
 6     container_name: traefik                                                                                                                       
 7     restart: unless-stopped                                                                                                                       
 8     command:                                                                                                                                      
 9       - "--providers.docker=true"                                                                                                                 
10       - "--providers.docker.exposedbydefault=false"                                                                                               
11       - "--entrypoints.web.address=:80"                                                                                                           
12       - "--entrypoints.websecure.address=:443"                                                                                                    
13       - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"                                                                             
14       - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"                                                                   
15       - "--certificatesresolvers.letsencrypt.acme.email=green.text5235@fastmail.com"                                                              
16       - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"                                                                 
17       - "--api.dashboard=true"                                                                                                                    
18     ports:                                                                                                                                        
19       - "80:80"                                                                                                                                   
20       - "443:443"                                                                                                                                 
21     volumes:                                                                                                                                      
22       - "./traefik.yml:/traefik.yml:ro"                                                                                                           
23       - "./acme.json:/letsencrypt/acme.json"                                                                                                      
24       - "/var/run/docker.sock:/var/run/docker.sock:ro"                                                                                            
25     labels:                                                                                                                                       
26       - "traefik.enable=true"                                                                                                                     
27       - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"                                                                           
28       - "traefik.http.routers.traefik.service=api@internal"                                                                                       
29       - "traefik.http.routers.traefik.entrypoints=websecure"                                                                                      
30       - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"                                                                               
31                                                                                                                                                   
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
docker-compose.yml (31,1) | ft:yaml | unix | utf-8                                                                      Alt-g: bindings, Ctrl-g: help
                                                                                                                                                     

 1 api:                                                                                                                                              
 2   dashboard: true                                                                                                                                 
 3                                                                                                                                                   
 4 entryPoints:                                                                                                                                      
 5   web:                                                                                                                                            
 6     address: ":80"                                                                                                                                
 7   websecure:                                                                                                                                      
 8     address: ":443"                                                                                                                               
 9                                                                                                                                                   
10 certificatesResolvers:                                                                                                                            
11   letsencrypt:                                                                                                                                    
12     acme:                                                                                                                                         
13       email: "green.text5235@fastmail.com"                                                                                                        
14       storage: "/letsencrypt/acme.json"                                                                                                           
15       httpChallenge:                                                                                                                              
16         entryPoint: "web"                                                                                                                         
17                                                                                                                                                   
18 providers:                                                                                                                                        
19   docker:                                                                                                                                         
20     endpoint: "unix:///var/run/docker.sock"                                                                                                       
21     exposedByDefault: false                                                                                                                       
22                                                                                                                                                   
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
traefik.yml (22,1) | ft:yaml | unix | utf-8                                                                             Alt-g: bindings, Ctrl-g: help
                                                                                                                                                     

#### ChatGPT:
<time datetime="2025-01-18T03:41:58.300Z" title="1/18/2025, 12:41:58 PM">12:41</time>

Below is a quick review of your **Traefik** setup based on the two files you’ve shared. You’ve got:

1. **docker-compose.yml** that starts the Traefik container, mapping ports 80/443, mounting the configuration files, and labeling Traefik’s own dashboard router.
2. **traefik.yml** (file-based config) that defines entry points, sets up Let’s Encrypt via HTTP challenge, and configures the Docker provider.

---

## 1. Why You’re Still Seeing `traefik.apsjado.com`

Your `docker-compose.yml` file still includes:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
  - "traefik.http.routers.traefik.service=api@internal"
  - "traefik.http.routers.traefik.entrypoints=websecure"
  - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

This means Traefik will attempt to issue a certificate for **`traefik.apsjado.com`** via the `letsencrypt` resolver. If you **do not have** a valid DNS record pointing `traefik.apsjado.com` → your server’s public IP, you’ll continue to see NXDOMAIN errors and certificate failures in the logs.

### How to Fix This

1. **Add a DNS A record** for `traefik.apsjado.com` that points to your server’s **public IP**. This way, Let’s Encrypt can complete the HTTP-01 challenge and issue an SSL certificate for that domain.

2. **Remove or comment out those label lines** if you don’t actually need `traefik.apsjado.com`. For instance:

   ```yaml
   labels:
     - "traefik.enable=true"
     # - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
     # - "traefik.http.routers.traefik.service=api@internal"
     # - "traefik.http.routers.traefik.entrypoints=websecure"
     # - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
   ```

   Then Traefik won’t request a cert for that domain (which doesn’t resolve in DNS).

---

## 2. File-Based Config vs. CLI Flags

In your setup, you’ve **duplicated** some configuration in both `traefik.yml` (file-based) and the `command:` lines (CLI flags). This is perfectly valid—Traefik merges them—but it can lead to confusion. If they match exactly, it’s fine; if they differ, one can override the other. Typically, you pick one approach:

- **All in `traefik.yml`:**
  - Remove the extra lines under `command:` in the `docker-compose.yml`.
  - In `docker-compose.yml`, add:
    ```yaml
    command:
      - "--configFile=/traefik.yml"
    ```
  - Then keep your entire config (entrypoints, ACME, etc.) in `traefik.yml`.

- **All in CLI flags:**
  - Remove or empty `traefik.yml`.
  - Keep `command:` lines as your single source of truth.

As is, you’re mostly consistent (both define the same `letsencrypt` resolver, same entrypoints, etc.), so it’s not a big deal—but be mindful if you change one file and forget the other.

---

## 3. Permissions on `acme.json`

Make sure `acme.json` is a **file** (not a folder) with `chmod 600`. For example:

```bash
cd ~/traefik
sudo chown $USER:$USER acme.json    # Replace $USER with your username if needed
chmod 600 acme.json
```

If Traefik ever complains about “permissions too open” or “acme.json is a directory,” this is where to look.

---

## 4. Final Checklist

1. **DNS**: If you keep `traefik.apsjado.com` in your labels, create the A record. Otherwise, remove those lines in `docker-compose.yml`.
2. **Logs**: `docker compose logs -f`. If no new errors appear, you’re good. If you see NXDOMAIN or ACME errors, that means DNS or port 80 is still an issue.
3. **Dashboard**: If/when `traefik.apsjado.com` resolves properly, you can visit `https://traefik.apsjado.com` and see the Traefik dashboard. You might want to secure it with Basic Auth:

   ```yaml
   labels:
     - "traefik.http.routers.traefik.middlewares=dashboard-auth"
     - "traefik.http.middlewares.dashboard-auth.basicauth.users=user:$$apr1$$somehash"
   ```

   (Generate the password hash with `htpasswd -nbB user password`.)

---

### Wrapping Up

- **Everything** in your `docker-compose.yml` and `traefik.yml` looks functionally correct—Traefik will listen on ports 80/443, use Let’s Encrypt’s HTTP challenge, and read Docker labels for routing.
- **The only real issue** that can show up is the NXDOMAIN error if `traefik.apsjado.com` doesn’t have a DNS record.
- **Remove** references to that domain if you don’t need it, or **set up** the DNS record if you do.

After handling DNS or removing that domain, you should have a fully operational reverse proxy with automatic SSL for any subdomains you specify in Docker labels. Good luck!


#### You:
<time datetime="2025-01-18T03:42:38.168Z" title="1/18/2025, 12:42:38 PM">12:42</time>

i guess i'm confused. am i using wiki. or traefik. subdomain?

#### ChatGPT:
<time datetime="2025-01-18T03:42:51.189Z" title="1/18/2025, 12:42:51 PM">12:42</time>

It’s totally up to you which subdomains you want to use! Typically, you might use:

- **`traefik.apsjado.com`** for Traefik’s own dashboard (where you can see logs, routes, etc.).
- **`wiki.apsjado.com`** for Outline (your wiki service).

But you don’t have to keep both unless you specifically want separate URLs—one for the dashboard, one for your wiki. Here’s how to decide:

---

## 1. If You Want Two Separate Subdomains

- **`traefik.apsjado.com`** will serve the Traefik dashboard.
- **`wiki.apsjado.com`** will serve your Outline wiki.

In that case:

1. Create **two DNS A-records** with your DNS provider:
   - `traefik.apsjado.com` → **public IP** of your server
   - `wiki.apsjado.com` → **public IP** of your server

2. Make sure each service has the correct **labels** in `docker-compose.yml` for routing:
   - The **Traefik container** should have labels referencing `Host(\`traefik.apsjado.com\`)\`.
   - The **Outline container** should have labels referencing `Host(\`wiki.apsjado.com\`)\`.

3. Traefik will request a Let’s Encrypt certificate for both subdomains. Just watch the logs to ensure each domain has a valid DNS record.

---

## 2. If You Only Want One Subdomain (e.g., for Outline Only)

If you **don’t** care about the Traefik dashboard being on a fancy domain (or you don’t want it publicly exposed at all), you can remove the references to `traefik.apsjado.com` from your **Traefik container** labels. For example, remove these lines in your `docker-compose.yml` for Traefik:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.traefik.rule=Host(`traefik.apsjado.com`)"
  - "traefik.http.routers.traefik.service=api@internal"
  - "traefik.http.routers.traefik.entrypoints=websecure"
  - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

Then Traefik will **not** attempt to serve a domain called `traefik.apsjado.com`. You only keep your Outline container labels for `wiki.apsjado.com`. In that scenario:

- You’ll have **one** DNS A-record: `wiki.apsjado.com` → **server’s IP**.
- Let’s Encrypt will issue a certificate just for `wiki.apsjado.com`.
- The Traefik dashboard can still be accessed internally on `http://<IP>:8080` (or `:80` / `:443` with no domain labels), but it won’t be publicly exposed with a domain name and a Let’s Encrypt certificate.

---

## 3. Common Practice in a Homelab

In many homelabs, people do like to have multiple subdomains:

- **`traefik.mydomain.com`** for the dashboard (often secured by Basic Auth or IP restrictions).
- **`wiki.mydomain.com`** for Outline.
- **`homeassistant.mydomain.com`** for Home Assistant, etc.

But it’s 100% your call. If you’d rather keep it simple and only have `wiki.apsjado.com`, that’s perfectly fine—just remove any references to `traefik.apsjado.com`.

---

### TL;DR

- **`wiki.apsjado.com`**: Subdomain for your Outline wiki.
- **`traefik.apsjado.com`**: Optional subdomain for the Traefik dashboard.
- If you use both, create **two** DNS records. If you don’t want `traefik.apsjado.com`, remove those labels so Traefik doesn’t keep trying to issue a cert for that domain.

Pick whichever subdomains you want (one or multiple), ensure DNS is set up accordingly, and Traefik will handle the SSL certificates once it sees a valid DNS record.


#### You:
<time datetime="2025-01-18T03:44:43.913Z" title="1/18/2025, 12:44:43 PM">12:44</time>

i just want to expose the Authentik login dashboard to all logged-out users. is that what we're on track to do?

#### ChatGPT:
<time datetime="2025-01-18T03:45:17.503Z" title="1/18/2025, 12:45:17 PM">12:45</time>

In short, **yes**, you can definitely set up Traefik so that *only* the Authentik login page (i.e., `auth.yourdomain.com`) is publicly accessible, and all other services remain behind that SSO login. Here’s the high-level idea of how to do that:

---

## 1. Publicly Expose Only Authentik

- Pick a subdomain (for example, **`auth.apsjado.com`**) for Authentik.
- Make sure DNS points `auth.apsjado.com` → your server’s public IP.
- In your Traefik config, label the Authentik container so requests to `auth.apsjado.com` get routed **directly** to Authentik:
  ```yaml
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.authentik.rule=Host(`auth.apsjado.com`)"
    - "traefik.http.routers.authentik.entrypoints=websecure"
    - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
    - "traefik.http.services.authentik.loadbalancer.server.port=8000"  # or whatever Authentik listens on
  ```
  With this, anyone who isn’t logged in yet can at least reach the **Auth** server to log in.

---

## 2. Hide Everything Else Behind Authentik (Optional Next Step)

Now that Authentik is public, you can secure other services (e.g., Nextcloud, Outline wiki, Home Assistant) so that they **require** an Authentik login. There are two common methods:

1. **OIDC or SAML**: If your services support SSO natively, you configure each app to “sign in with OIDC/SAML,” pointing it to `auth.apsjado.com` as the identity provider. Then the user is redirected to Authentik if they aren’t logged in, logs in, and gets bounced back to the service.

2. **Forward Auth**: If an app doesn’t support OIDC/SAML, you can use a Traefik “forward auth” or “forward auth middleware” that calls Authentik. Essentially, Traefik checks if the user is authenticated (via Authentik) before forwarding them to the real app. If not logged in, the user is redirected to `auth.apsjado.com`.

---

## 3. Remove or Ignore Extra Subdomains

If you **don’t** actually need a “`traefik.apsjado.com`” dashboard domain or a “`wiki.apsjado.com`” domain for Outline, you can remove those from your Traefik labels to avoid DNS/cert issues. Stick to the one domain (`auth.apsjado.com`) that hosts your Authentik login portal.

- **Deleting the Traefik dashboard subdomain**: In your `docker-compose.yml`, remove (or comment out) labels referencing `traefik.apsjado.com`. That way Traefik won’t try to obtain a certificate for it or expose it publicly.

---

## 4. Confirming You’re “On Track”

From your questions and setup, it sounds like:

1. You **already have** Traefik up and running on ports 80/443.
2. You **don’t** really want a separate subdomain for the Traefik dashboard; you mainly want Authentik to be publicly accessible so that logged-out users see only the Authentik login page.
3. **Next steps**: You’ll deploy Authentik, give it a subdomain and DNS record, and either do an OIDC integration or a forward-auth approach for any other internal services you want to protect.

Yes, that means you’re absolutely on track to expose **only** the Authentik login page to unauthenticated users. Once Authentik is running behind Traefik at (say) `auth.apsjado.com`, everything else can stay private or require an Authentik login to see.

---

### TL;DR

- Pick **one subdomain** for Authentik (e.g. `auth.apsjado.com`).
- **Create a DNS record** so Let’s Encrypt can issue a cert.
- Give Authentik the correct Traefik labels so that **only** `auth.apsjado.com` is public.
- Remove any references to `traefik.apsjado.com` if you don’t want that.
- Any other service in your homelab either uses OIDC or forward-auth to ensure that if a user is *not* authenticated, they get redirected to Authentik’s login page.

With that, Authentik’s login dashboard is the only thing “visible” to the outside world. Once a user logs in, they gain access to whichever services you’ve configured behind Authentik.


#### You:
<time datetime="2025-01-18T03:49:32.845Z" title="1/18/2025, 12:49:32 PM">12:49</time>

 1 version: "3.3"                                                                                                                                    
 2                                                                                                                                                   
 3 services:                                                                                                                                         
 4   traefik:                                                                                                                                        
 5     image: traefik:latest                                                                                                                         
 6     container_name: traefik                                                                                                                       
 7     restart: unless-stopped                                                                                                                       
 8     command:                                                                                                                                      
 9       - "--providers.docker=true"                                                                                                                 
10       - "--providers.docker.exposedbydefault=false"                                                                                               
11       - "--entrypoints.web.address=:80"                                                                                                           
12       - "--entrypoints.websecure.address=:443"                                                                                                    
13       - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"                                                                             
14       - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"                                                                   
15       - "--certificatesresolvers.letsencrypt.acme.email=green.text5235@fastmail.com"                                                              
16       - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"                                                                 
17       - "--api.dashboard=true"                                                                                                                    
18     ports:                                                                                                                                        
19       - "80:80"                                                                                                                                   
20       - "443:443"                                                                                                                                 
21     volumes:                                                                                                                                      
22       - "./traefik.yml:/traefik.yml:ro"                                                                                                           
23       - "./acme.json:/letsencrypt/acme.json"                                                                                                      
24       - "/var/run/docker.sock:/var/run/docker.sock:ro"                                                                                            
25     labels:                                                                                                                                       
26       - "traefik.enable=true"                                                                                                                     
27       - "traefik.http.routers.traefik.rule=Host(`login.apsjado.com`)"                                                                             
28  #     - "traefik.http.routers.traefik.service=api@internal"                                                                                       
29       - "traefik.http.routers.traefik.entrypoints=websecure"                                                                                      
30       - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"                                                                               
31                                                                                                                                                   
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
docker-compose.yml (31,1) | ft:yaml | unix | utf-8                                                                      Alt-g: bindings, Ctrl-g: help
                                                                                                                                                     

#### ChatGPT:
<time datetime="2025-01-18T03:50:06.894Z" title="1/18/2025, 12:50:06 PM">12:50</time>

With these edits, you’ve effectively **renamed** the domain where Traefik is listening from `traefik.apsjado.com` to `login.apsjado.com` and **commented out** the line referencing `api@internal` (which displays the Traefik dashboard). Let’s walk through what this means and what you should do if your end goal is to expose an Authentik login at `login.apsjado.com`.

---

## 1. You Still Have a Traefik Router Named “traefik”

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.traefik.rule=Host(`login.apsjado.com`)"
  # - "traefik.http.routers.traefik.service=api@internal"
  - "traefik.http.routers.traefik.entrypoints=websecure"
  - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
```

- The router is called **`traefik`** (based on `traefik.http.routers.traefik`).
- The rule is `Host(\`login.apsjado.com\`)\`.
- You’ve **commented out** the line that says `service=api@internal`, which would normally point this router to the built-in Traefik dashboard.

As a result, this router still **exists** but doesn’t point to **any** service. If you left it like this, Traefik wouldn’t know what service to serve when a request hits `login.apsjado.com`. That means if you browse to `https://login.apsjado.com`, you’d likely get a 404 from Traefik (or a default error page) because there’s no backend service specified.

---

## 2. If You Want “login.apsjado.com” to Serve Authentik

1. **Deploy Authentik** in Docker (either in the same `docker-compose.yml` or a separate one) with a container name like `authentik`:
   ```yaml
   services:
     authentik:
       image: ghcr.io/goauthentik/server:latest
       container_name: authentik
       ports:
         - "9000:9000"  # or map how you like
       # or rely on an internal network if you prefer
       # ...
   ```

2. **Remove or rename** the `traefik` router lines in your Traefik labels. Instead, define a router for Authentik. For example, if Authentik listens on port 9000 inside its container, add labels like:
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
     - "traefik.http.routers.authentik.entrypoints=websecure"
     - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
     - "traefik.http.services.authentik.loadbalancer.server.port=9000"
   ```
   This way, **requests to `login.apsjado.com`** will be passed to Authentik’s container on port 9000.

3. **Remove or comment out** the current `traefik.http.routers.traefik...` lines if you don’t need the dashboard at all. That means Traefik won’t attempt to route `login.apsjado.com` to the internal dashboard.

4. **Create a DNS A-record** for `login.apsjado.com` → your server’s public IP, so Let’s Encrypt can verify ownership and issue a certificate.

After these steps, going to **`https://login.apsjado.com`** should bring up Authentik’s login page, assuming your ports are open and DNS is correct.

---

## 3. If You Actually Wanted the Traefik Dashboard on “login.apsjado.com”

- **Uncomment** the `service=api@internal` line:
  ```yaml
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.traefik.rule=Host(`login.apsjado.com`)"
    - "traefik.http.routers.traefik.service=api@internal"
    - "traefik.http.routers.traefik.entrypoints=websecure"
    - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
  ```
- Then `login.apsjado.com` will serve Traefik’s dashboard.
- But typically, you don’t want your main “login” subdomain to go to Traefik’s dashboard—especially if your plan is to serve your Authentik login there.

---

## 4. Summary of What’s Happening

- **Commenting out `service=api@internal`** means you’re no longer routing `login.apsjado.com` to Traefik’s dashboard.
- **Keeping** the rest of the lines for “traefik” router but not pointing them at anything else leads to a router that doesn’t serve a real service.
- If your goal is to serve the **Authentik login** at `login.apsjado.com`, you’ll need to define that route on your Authentik container.

### Next Steps

1. Decide whether “login.apsjado.com” is for **the Traefik dashboard** or **Auth’s login page**.
2. If it’s for Authentik, remove the old `traefik` router lines entirely or rename them to something like `authentik`.
3. In your Authentik container’s labels (or a file-based config), define a route for `login.apsjado.com`.
4. Verify DNS, open ports, watch logs to confirm Let’s Encrypt issues the certificate.

Once set up, anyone visiting **`https://login.apsjado.com`** gets the Authentik login screen, and that’s the only public “door” to your homelab.

---

**TL;DR**: By commenting out `service=api@internal` and renaming the host rule to `login.apsjado.com`, you’ve removed the Traefik dashboard from `traefik.apsjado.com` but haven’t yet told Traefik where to route requests for `login.apsjado.com`. If Authentik is your goal, just define a new router pointed to the Authentik container. Then you’ll truly expose only the Authentik login to the outside world.


#### You:
<time datetime="2025-01-18T03:51:04.948Z" title="1/18/2025, 12:51:04 PM">12:51</time>

2. If You Want “login.apsjado.com” to Serve Authentik

create a the docker-compose file of traefik and authentik

#### ChatGPT:
<time datetime="2025-01-18T03:51:44.227Z" title="1/18/2025, 12:51:44 PM">12:51</time>

Below is an **example** `docker-compose.yml` file that runs **both Traefik and Authentik**. With this setup:

- **Traefik** listens on ports 80 and 443, handles Let’s Encrypt certificates, and routes traffic to Authentik.
- **Authentik** listens internally on port 9000, but publicly appears at `login.apsjado.com`.
- **Redis** and **PostgreSQL** are also spun up for Authentik. (Authentik requires them for caching and persistent storage.)

You’ll just need to adjust your **domain**, **DNS**, and any specific environment variables (like your own passwords).

---

## 1. Example `docker-compose.yml`

```yaml
version: "3.3"

networks:
  traefik-net:
    external: false

services:
  ##########################################
  # Traefik
  ##########################################
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    networks:
      - traefik-net
    
    ports:
      - "80:80"     # HTTP
      - "443:443"   # HTTPS
    
    # We'll store Traefik config in the same folder as this docker-compose.yml
    volumes:
      # Traefik File-based config (if you use traefik.yml)
      - "./traefik.yml:/traefik.yml:ro"

      # ACME (Let's Encrypt) certificate file
      - "./acme.json:/letsencrypt/acme.json"

      # Docker socket (read-only) so Traefik can detect container labels
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

    command:
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      
      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt (ACME) settings
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"

    # No labels here for the dashboard domain, unless you want to expose it.
    # If you do, you can add your domain rule for the dashboard.

  ##########################################
  # Authentik
  ##########################################
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    restart: unless-stopped
    networks:
      - traefik-net

    # If you want to access it directly on the host (optional):
    # ports:
    #   - "127.0.0.1:9000:9000"

    labels:
      # Enable Traefik for this service
      - "traefik.enable=true"

      # Route domain login.apsjado.com to the Authentik container
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"

      # Authentik container listens on port 9000, so direct traffic there
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"

    environment:
      # Make sure your domain here matches your external URL
      AUTHENTIK_HOST: "https://login.apsjado.com"

      # Database configuration (PostgreSQL)
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik

      # Redis configuration
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"

      # Email configuration (optional but recommended)
      AUTHENTIK_EMAIL__HOST: smtp.yourprovider.com
      AUTHENTIK_EMAIL__PORT: "587"
      AUTHENTIK_EMAIL__USERNAME: your_smtp_user
      AUTHENTIK_EMAIL__PASSWORD: your_smtp_pass
      AUTHENTIK_EMAIL__USE_TLS: "True"

  ##########################################
  # PostgreSQL
  ##########################################
  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    restart: unless-stopped
    networks:
      - traefik-net
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: your_db_password

  ##########################################
  # Redis
  ##########################################
  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped
    networks:
      - traefik-net
```

### Key Points to Adjust

1. **`login.apsjado.com`**:
   - Replace with your real domain.
   - Confirm an **A record** in DNS points `login.apsjado.com` → your server’s public IP.
2. **`AUTHENTIK_HOST`**:
   - Must match the domain above (including `https://`).
3. **Email environment** if you want Authentik to send password reset emails etc.
4. **PostgreSQL credentials** (use a real password in both the `postgresql` environment and `authentik` environment).
5. Make sure you `touch acme.json` and `chmod 600 acme.json` in the same folder as the compose file.

---

## 2. Minimal `traefik.yml` (Optional)

If you want to store some config in a file named `traefik.yml`, put it next to your `docker-compose.yml`:

```yaml
api:
  dashboard: true

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "youremail@example.com"
      storage: "/letsencrypt/acme.json"
      httpChallenge:
        entryPoint: "web"
```

Traefik merges these file settings with the CLI flags in your `command:`. If you’re comfortable using just the CLI, you can skip this file or keep it as an alternative approach.

---

## 3. Deployment Steps

1. **Create a folder**, say `/home/ashwin/traefik-authentik/`, and put:
   - `docker-compose.yml` (from above)
   - `traefik.yml` (optional)
   - `acme.json` (an empty file)
2. `chmod 600 acme.json`, ensure your user owns it:
   ```bash
   cd /home/ashwin/traefik-authentik
   touch acme.json
   chmod 600 acme.json
   ```
3. **Launch**:
   ```bash
   docker compose up -d
   ```
4. **Check logs**:
   ```bash
   docker compose logs -f
   ```
   Wait for Traefik to pull images, start containers, and see if Let’s Encrypt obtains a cert for `login.apsjado.com`. You should see no NXDOMAIN errors if DNS is correct.

---

## 4. Testing Authentik

- Once up, go to **`https://login.apsjado.com`** in a browser.
- You should see Authentik’s login or setup page.
- On first startup, Authentik runs migrations and outputs an admin user. Check `docker compose logs -f authentik` for the generated admin credentials or run `docker compose exec authentik authentik bootstrap` if you need to reset them.

---

## 5. Next Steps

- **Secure** the Traefik dashboard if you do re-enable it under a domain.
- **Configure** Authentik flows, providers, etc. so it can serve as your IdP for other apps.
- Optionally, set up an **Outpost** or **Forward Auth** for apps that don’t support SSO natively.

Once this compose stack is running, your Authentik login page is publicly accessible at `login.apsjado.com`, using a valid TLS certificate from Let’s Encrypt, and the rest of your homelab can remain behind Authentik-based SSO. Enjoy!


#### You:
<time datetime="2025-01-18T03:55:47.564Z" title="1/18/2025, 12:55:47 PM">12:55</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.8s 
 ✔ Network traefik_default  Removed                                                                                                             0.3s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.3s 
docker compose logs -f

^Q^Ccanceled
ashwin@ubuntu-server:~/traefik$ docker compose logs -f
^Cç^Ccanceled
ashwin@ubuntu-server:~/traefik$ sudo micro docker-compose.yml 
ashwin@ubuntu-server:~/traefik$ sudo micro traefik.yml 
ashwin@ubuntu-server:~/traefik$ sudo micro docker-compose.yml
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.2s 
 ✔ Network traefik_default  Removed                                                                                                             0.2s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.3s 
^Ccanceled
ashwin@ubuntu-server:~/traefik$ sudo micro docker-compose.yml
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 2/2
 ✔ Container traefik        Removed                                                                                                             0.3s 
 ✔ Network traefik_default  Removed                                                                                                             0.2s 
[+] Running 2/2
 ✔ Network traefik_default  Created                                                                                                             0.1s 
 ✔ Container traefik        Started                                                                                                             0.3s 
^Ccanceled
ashwin@ubuntu-server:~/traefik$ sudo micro docker-compose.yml 
ashwin@ubuntu-server:~/traefik$ touch acme.json
chmod 600 acme.json
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
parsing /home/ashwin/traefik/docker-compose.yml: yaml: line 5: found character that cannot start any token
parsing /home/ashwin/traefik/docker-compose.yml: yaml: line 5: found character that cannot start any token
parsing /home/ashwin/traefik/docker-compose.yml: yaml: line 5: found character that cannot start any token
ashwin@ubuntu-server:~/traefik$ sudo micro docker-compose.yml 
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 0/1
[+] Running 2/2aefik  Stopping                                                                                                                  0.2s 
 ✔ Container traefik            Removed                                                                                                        10.3s 
 ✔ Network traefik_traefik-net  Removed                                                                                                         0.2s 
[+] Running 49/49
 ✔ postgresql 10 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                                                    11.8s 
   ✔ c01996cb3d63 Pull complete                                                                                                                 6.7s 
   ✔ 8aaa3be049e2 Pull complete                                                                                                                 7.1s 
   ✔ fe636956e4ee Pull complete                                                                                                                 7.1s 
   ✔ ac3db02c78f1 Pull complete                                                                                                                 7.4s 
   ✔ 04602106ce3f Pull complete                                                                                                                 9.5s 
   ✔ eba2ad92e11a Pull complete                                                                                                                 9.5s 
   ✔ 82168ddea431 Pull complete                                                                                                                 9.6s 
   ✔ 5c8a13e8b8d8 Pull complete                                                                                                                 9.6s 
   ✔ 565de088ba86 Pull complete                                                                                                                 9.7s 
   ✔ edc768b3865a Pull complete                                                                                                                 9.7s 
 ✔ redis 8 layers [⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                                                             8.7s 
   ✔ 1f3e46996e29 Already exists                                                                                                                0.0s 
   ✔ 2a4a8619026d Pull complete                                                                                                                 5.3s 
   ✔ 27b38dcb2b9d Pull complete                                                                                                                 6.2s 
   ✔ 4f8076e8e667 Pull complete                                                                                                                 6.2s 
   ✔ 5f62c32baa58 Pull complete                                                                                                                 6.4s 
   ✔ ea2c9629163b Pull complete                                                                                                                 6.6s 
   ✔ 4f4fb700ef54 Pull complete                                                                                                                 6.8s 
   ✔ 7b09df54997d Pull complete                                                                                                                 6.8s 
 ✔ authentik 28 layers [⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿]      0B/0B      Pulled                                                                   12.3s 
   ✔ 302e3ee49805 Pull complete                                                                                                                 1.5s 
   ✔ 106e608f0824 Pull complete                                                                                                                 1.6s 
   ✔ 72bd0f12b179 Pull complete                                                                                                                 1.7s 
   ✔ dfac4f97b390 Pull complete                                                                                                                 1.9s 
   ✔ 5322dcb4a319 Pull complete                                                                                                                 2.2s 
   ✔ 6502bdff6d09 Pull complete                                                                                                                 2.2s 
   ✔ 050468feccc7 Pull complete                                                                                                                 2.5s 
   ✔ d16de566a055 Pull complete                                                                                                                 2.5s 
   ✔ 502a6c18fe11 Pull complete                                                                                                                 2.7s 
   ✔ 1d125643d499 Pull complete                                                                                                                 2.8s 
   ✔ b571c48e13bf Pull complete                                                                                                                 3.0s 
   ✔ bac602b99d9e Pull complete                                                                                                                 3.1s 
   ✔ 99696484c275 Pull complete                                                                                                                 3.3s 
   ✔ d1a97c143604 Pull complete                                                                                                                 3.4s 
   ✔ da9d4569cd04 Pull complete                                                                                                                 3.4s 
   ✔ f543ae94f6af Pull complete                                                                                                                 3.5s 
   ✔ faff23aca032 Pull complete                                                                                                                 3.6s 
   ✔ c4c49219aff2 Pull complete                                                                                                                 3.6s 
   ✔ 928088034f07 Pull complete                                                                                                                 3.7s 
   ✔ e74568cfa5a8 Pull complete                                                                                                                 3.8s 
   ✔ 7997ad3b3c56 Pull complete                                                                                                                 3.8s 
   ✔ 5280c521782a Pull complete                                                                                                                 3.9s 
   ✔ ce0ffdbb4ccf Pull complete                                                                                                                 5.0s 
   ✔ c013d25db4d8 Pull complete                                                                                                                10.1s 
   ✔ 961027150def Pull complete                                                                                                                10.4s 
   ✔ 24d755c64d75 Pull complete                                                                                                                10.5s 
   ✔ ef57a0785cfc Pull complete                                                                                                                11.0s 
   ✔ 969b202b7b9a Pull complete                                                                                                                11.3s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_postgres  Started                                                                                                        0.8s 
 ✔ Container authentik_redis     Started                                                                                                        0.9s 
 ✔ Container traefik             Started                                                                                                        1.0s 
 ✔ Container authentik           Started                                                                                                        0.9s 
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_redis     | 1:C 18 Jan 2025 03:55:26.944 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 03:55:26.944 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 03:55:26.944 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 03:55:26.944 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 03:55:26.945 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 03:55:26.945 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 03:55:26.945 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 03:55:26.945 * Ready to accept connections
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_postgres  | selecting default time zone ... UTC
authentik_postgres  | creating configuration files ... ok
authentik_postgres  | running bootstrap script ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172527.1134355, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172527.1137962, "count": 12}
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 03:55:27.196 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172527.399576}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172527.3995998}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172527.3996067}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172527.399613}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik exited with code 0
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172527.8312128, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172527.8314238, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.1253788}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.1253958}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.125403}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.1254098}
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to start....2025-01-18 03:55:28.170 UTC [41] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 03:55:28.177 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 03:55:28.193 UTC [42] LOG:  database system was shut down at 2025-01-18 03:55:27 UTC
authentik_postgres  | 2025-01-18 03:55:28.201 UTC [41] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik exited with code 1
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down....2025-01-18 03:55:28.565 UTC [41] LOG:  received fast shutdown request
authentik_postgres  | 2025-01-18 03:55:28.570 UTC [41] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 03:55:28.571 UTC [41] LOG:  background worker "logical replication launcher" (PID 48) exited with exit code 1
authentik_postgres  | 2025-01-18 03:55:28.571 UTC [43] LOG:  shutting down
authentik_postgres  | 2025-01-18 03:55:28.604 UTC [41] LOG:  database system is shut down
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172528.611365, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172528.6115825, "count": 12}
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 03:55:28.686 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 03:55:28.687 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 03:55:28.687 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 03:55:28.696 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 03:55:28.708 UTC [56] LOG:  database system was shut down at 2025-01-18 03:55:28 UTC
authentik_postgres  | 2025-01-18 03:55:28.714 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.89218}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.892203}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.8922098}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172528.892217}
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172529.5920334, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172529.5922556, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172529.8819437}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172529.8819668}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172529.8819737}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172529.8819797}
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172530.9516287, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172530.9518461, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172531.235497}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172531.2355185}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172531.2355254}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172531.235532}
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172533.09714, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172533.0973601, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172533.395579}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172533.3955982}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172533.3956053}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172533.3956113}
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172536.8718708, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172536.8720853, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172537.1678703}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172537.1678863}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172537.1678932}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172537.1678998}
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172543.848004, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172543.8482113, "count": 12}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172544.1458101}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172544.1458266}
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/.", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172544.145834}
authentik           | {"event": "----------------------------------------------------------------------", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172544.1458402}
authentik exited with code 1

#### ChatGPT:
<time datetime="2025-01-18T03:55:59.618Z" title="1/18/2025, 12:55:59 PM">12:55</time>

The key issue here is:

```
authentik           | {"event": "Secret key missing, check https://goauthentik.io/docs/installation/."}
authentik exited with code 1
```

**Authentik** needs a **persistent secret key** to function. By default, if it can’t find one (via environment variable or config file), it will generate an in-memory key—and if the container restarts, it loses that key and fails bootstrap. In your logs, it’s repeatedly exiting because it’s missing that key.

Below is how to fix it by **defining a secret key** in your Docker Compose.

---

## 1. Generate a Secure Secret Key

You can generate a random key locally:

```bash
openssl rand -base64 45
```

This will produce a random string you can copy/paste as your `AUTHENTIK_SECRET_KEY`. (At least 32 bytes recommended.)

---

## 2. Add the `AUTHENTIK_SECRET_KEY` to the Authentik Environment

In your `docker-compose.yml` (where you define the **authentik** service), add something like:

```yaml
environment:
  AUTHENTIK_SECRET_KEY: "PASTE_YOUR_LONG_RANDOM_STRING_HERE"

  # Make sure you keep the other environment variables too
  AUTHENTIK_HOST: "https://login.apsjado.com"
  AUTHENTIK_POSTGRESQL__HOST: postgresql
  AUTHENTIK_POSTGRESQL__USER: authentik
  AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
  AUTHENTIK_POSTGRESQL__NAME: authentik
  AUTHENTIK_REDIS__HOST: redis
  AUTHENTIK_REDIS__PORT: "6379"
  AUTHENTIK_EMAIL__HOST: smtp.yourprovider.com
  AUTHENTIK_EMAIL__PORT: "587"
  AUTHENTIK_EMAIL__USERNAME: your_smtp_user
  AUTHENTIK_EMAIL__PASSWORD: your_smtp_pass
  AUTHENTIK_EMAIL__USE_TLS: "True"
```

> **Important**: Don’t lose this value—if you change it later, Authentik won’t be able to decrypt existing session or token data. Keep it **stable** across container restarts.

---

## 3. Redeploy

1. **Stop** the containers:
   ```bash
   docker compose down
   ```
2. **Pull up** again:
   ```bash
   docker compose up -d
   docker compose logs -f
   ```
3. Now Authentik should see the **`AUTHENTIK_SECRET_KEY`** environment variable, use it at startup, and no longer exit with code 1.

---

## 4. Verify in the Logs

Check for these steps in `authentik` logs:

- Database migrations
- “Bootstrap complete” or user creation messages
- No repeated “Secret key missing” messages

You can also see the generated admin credentials if it’s the first time you’re running Authentik. If you need to reset the **initial admin user** or password, you can do:

```bash
docker compose exec authentik authentik bootstrap
```

That will guide you through re-creating an admin account.

---

## 5. Why the Key is Important

- **Persistent secrets**: Authentik encrypts tokens, session data, and more. Losing or changing the key breaks existing data.
- For **production/homelab** usage, you must define it once and keep it safe.
- If you want ephemeral secrets for a test or dev environment, you can set `AUTHENTIK_SECRET_KEY=""`, but **every** restart regenerates the key—**not recommended** for real usage.

---

### Final Steps

1. **Include** `AUTHENTIK_SECRET_KEY` in your `.env` or `docker-compose.yml` environment.
2. **Verify** the container starts normally.
3. Browse to **`https://login.apsjado.com`** (assuming you have DNS + Let’s Encrypt set up) and see the Authentik login page.

With this fix, Authentik should **stop exiting** and properly finish its bootstrap process. You can then start configuring flows, providers, and so on. Enjoy your new Authentik IdP!


#### You:
<time datetime="2025-01-18T03:57:37.350Z" title="1/18/2025, 12:57:37 PM">12:57</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 5/5
 ✔ Container authentik_postgres  Removed                                                                                                        0.3s 
 ✔ Container authentik_redis     Removed                                                                                                        0.2s 
 ✔ Container traefik             Removed                                                                                                        0.3s 
 ✔ Container authentik           Removed                                                                                                        0.1s 
 ✔ Network traefik_traefik-net   Removed                                                                                                        0.2s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_postgres  Started                                                                                                        0.5s 
 ✔ Container authentik_redis     Started                                                                                                        0.5s 
 ✔ Container traefik             Started                                                                                                        0.4s 
 ✔ Container authentik           Started                                                                                                        0.5s 
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_redis     | 1:C 18 Jan 2025 03:57:29.579 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 03:57:29.579 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 03:57:29.579 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 03:57:29.579 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 03:57:29.579 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 03:57:29.579 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 03:57:29.579 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 03:57:29.580 * Ready to accept connections
authentik_postgres  | selecting default time zone ... UTC
authentik_postgres  | creating configuration files ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172649.698424, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172649.6986558, "count": 13}
authentik_postgres  | running bootstrap script ... ok
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 03:57:29.922 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172649.9869895}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | waiting for server to start....2025-01-18 03:57:30.709 UTC [41] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 03:57:30.714 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 03:57:30.730 UTC [43] LOG:  database system was shut down at 2025-01-18 03:57:30 UTC
authentik_postgres  | 2025-01-18 03:57:30.737 UTC [41] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172650.9886258}
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down....2025-01-18 03:57:31.016 UTC [41] LOG:  received fast shutdown request
authentik_postgres  | 2025-01-18 03:57:31.020 UTC [41] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 03:57:31.022 UTC [41] LOG:  background worker "logical replication launcher" (PID 49) exited with exit code 1
authentik_postgres  | 2025-01-18 03:57:31.022 UTC [44] LOG:  shutting down
authentik_postgres  | 2025-01-18 03:57:31.053 UTC [41] LOG:  database system is shut down
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 03:57:31.138 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 03:57:31.138 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 03:57:31.138 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 03:57:31.147 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 03:57:31.158 UTC [57] LOG:  database system was shut down at 2025-01-18 03:57:31 UTC
authentik_postgres  | 2025-01-18 03:57:31.165 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172651.9892638}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172651.999357}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172652.0000644}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172652.000129}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737172652.9286392, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172652.9290771, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172652.930389}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9309113, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.931193, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.931424, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9320762, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9326854, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.933775, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.934879, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9358096, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9364734, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9377072, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9381402, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9392633, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9396303, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.9401774, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.940474, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172652.941417, "path": "authentik.events.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:33.268812"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:33.269434"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.286956"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.287236"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.296530"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.296756"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.297306"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.314896"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.333639"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.334096"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.334578"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.340981"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.341300"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.341619"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.341862"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.343213"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.343857"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.344423"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.345555"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.345928"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.349694"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.351602"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.359963"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.360265"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.360629"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.360984"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.361248"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.386248"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.386383"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.387509"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.387563"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.387829"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.388120"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.388499"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.388717"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.389025"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.389222"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.392079"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.392295"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T03:57:34.392339"}
authentik           | 
authentik           | 
authentik           | Type 'manage.py help <subcommand>' for help on a specific subcommand.
authentik           | 
authentik           | 
authentik           | Available subcommands:
authentik           | 
authentik           | 
authentik           | [auth]
authentik           |     changepassword
authentik           |     createsuperuser
authentik           | 
authentik           | 
authentik           | [authenticator_webauthn]
authentik           |     update_webauthn_mds
authentik           | 
authentik           | 
authentik           | [blueprints]
authentik           |     apply_blueprint
authentik           |     export_blueprint
authentik           |     make_blueprint_schema
authentik           | 
authentik           | 
authentik           | [channels]
authentik           |     runworker
authentik           | 
authentik           | 
authentik           | [contenttypes]
authentik           |     remove_stale_contenttypes
authentik           | 
authentik           | 
authentik           | [core]
authentik           |     bootstrap_tasks
authentik           |     build_source_docs
authentik           |     change_user_type
authentik           |     dev_server
authentik           |     repair_permissions
authentik           |     shell
authentik           |     worker
authentik           | 
authentik           | 
authentik           | [crypto]
authentik           |     import_certificate
authentik           | 
authentik           | 
authentik           | [django]
authentik           |     check
authentik           |     compilemessages
authentik           |     createcachetable
authentik           |     dbshell
authentik           |     diffsettings
authentik           |     dumpdata
authentik           |     flush
authentik           |     inspectdb
authentik           |     loaddata
authentik           |     makemessages
authentik           |     makemigrations
authentik           |     optimizemigration
authentik           |     sendtestemail
authentik           |     showmigrations
authentik           |     sqlflush
authentik           |     sqlmigrate
authentik           |     sqlsequencereset
authentik           |     squashmigrations
authentik           |     startapp
authentik           |     startproject
authentik           |     test
authentik           |     testserver
authentik           | 
authentik           | 
authentik           | [django_tenants]
authentik           |     all_tenants_command
authentik           |     clone_tenant
authentik           |     collectstatic_schemas
authentik           |     create_missing_schemas
authentik           |     create_tenant
authentik           |     create_tenant_superuser
authentik           |     delete_tenant
authentik           |     migrate
authentik           |     migrate_schemas
authentik           |     rename_schema
authentik           |     tenant_command
authentik           | 
authentik           | 
authentik           | [drf_spectacular]
authentik           |     spectacular
authentik           | 
authentik           | 
authentik           | [email]
authentik           |     test_email
authentik           | 
authentik           | 
authentik           | [flows]
authentik           |     benchmark
authentik           | 
authentik           | 
authentik           | [guardian]
authentik           |     clean_orphan_obj_perms
authentik           | 
authentik           | 
authentik           | [kerberos]
authentik           |     kerberos_check_connection
authentik           |     kerberos_sync
authentik           | 
authentik           | 
authentik           | [ldap]
authentik           |     ldap_check_connection
authentik           |     ldap_sync
authentik           | 
authentik           | 
authentik           | [pgactivity]
authentik           |     pgactivity
authentik           | 
authentik           | 
authentik           | [pglock]
authentik           |     pglock
authentik           | 
authentik           | 
authentik           | [recovery]
authentik           |     create_admin_group
authentik           |     create_recovery_key
authentik           | 
authentik           | 
authentik           | [rest_framework]
authentik           |     generateschema
authentik           | 
authentik           | 
authentik           | [scim]
authentik           |     scim_sync
authentik           | 
authentik           | 
authentik           | [sessions]
authentik           |     clearsessions
authentik           | 
authentik           | 
authentik           | [staticfiles]
authentik           |     collectstatic
authentik           |     findstatic
authentik           |     runserver

#### ChatGPT:
<time datetime="2025-01-18T03:58:01.446Z" title="1/18/2025, 12:58:01 PM">12:58</time>

Good news: Authentik **successfully started** this time, and the “secret key missing” error is gone. From your logs, we can see:

- Postgres initialized successfully.
- Redis is running.
- Authentik connected to both (“PostgreSQL connection successful” and “Redis Connection successful”).
- It ran its “authentik bootstrap” phase.
- Then it printed out all the possible `manage.py` subcommands (the last part of the logs showing commands like `createsuperuser`, etc.).

That **command list** is how Authentik’s container shows you the embedded Django management commands. **No error** is shown at the end, so Authentik should now be up and listening on port 9000 internally, proxied by Traefik over HTTPS at your chosen domain.

---

## 1. Verify Authentik in the Browser

If you set the Authentik labels to route requests to `login.apsjado.com`, do:

1. **Check DNS**: Make sure an **A record** for `login.apsjado.com` points to your server’s public IP.
2. **Open** `https://login.apsjado.com` in your browser.
3. If Let’s Encrypt succeeded, you’ll have a valid SSL cert, and Authentik’s login page or setup page should appear.

If you see a 404 or invalid cert, double-check that:

- You used the same **domain** in Authentik’s environment variable `AUTHENTIK_HOST` and in Traefik’s router labels.
- Ports **80** and **443** are forwarded/open.

---

## 2. Create (or Reset) the Admin User

When Authentik starts for the first time, it usually prints an admin username and random password in the logs. If you missed it or want to force a new admin account, run:

```bash
docker compose exec authentik authentik bootstrap
```

It will let you set an admin username and password. Then you can log in via `login.apsjado.com`.

---

## 3. Confirm No More Errors

The logs show:

```
authentik           | {"event": "Finished authentik bootstrap", "level": "info", ...
```

That’s a good sign. No more “secret key missing” loops or container crashes. The process is now stable.

---

## 4. Common Next Steps

1. **Log In** at `https://login.apsjado.com` (assuming that’s your Authentik domain).
2. **Configure** email settings in the UI (or via environment variables) so password resets and notifications work.
3. **Add flows, providers, and outposts** for other apps in your homelab to require Authentik login.
4. (Optional) **Secure** the Traefik dashboard under a separate domain or remove it entirely if not needed.

---

### TL;DR

- Authentik is now **running** and **connected** to Postgres + Redis.
- The container printing out “manage.py” commands is normal at the end of startup; it means Authentik’s CLI is available inside the container.
- **Go to your configured domain** in a browser, and you should see Authentik’s login page.
- **Use** `authentik bootstrap` (inside the container) if you need to create or reset the admin user.

You’ve successfully deployed Authentik behind Traefik with Let’s Encrypt. Enjoy your new IdP and single sign-on setup!


#### You:
<time datetime="2025-01-18T04:01:40.718Z" title="1/18/2025, 1:01:40 PM">13:01</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 5/5
 ✔ Container authentik_redis     Removed                                                                                                        0.4s 
 ✔ Container traefik             Removed                                                                                                        3.3s 
 ✔ Container authentik           Removed                                                                                                        0.2s 
 ✔ Container authentik_postgres  Removed                                                                                                        0.3s 
 ✔ Network traefik_traefik-net   Removed                                                                                                        0.2s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_postgres  Started                                                                                                        0.6s 
 ✔ Container traefik             Started                                                                                                        0.5s 
 ✔ Container authentik           Started                                                                                                        0.6s 
 ✔ Container authentik_redis     Started                                                                                                        0.5s 
authentik_redis     | 1:C 18 Jan 2025 04:01:26.999 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 04:01:26.999 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 04:01:26.999 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 04:01:26.999 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 04:01:26.999 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 04:01:26.999 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 04:01:26.999 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 04:01:26.999 * Ready to accept connections
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_postgres  | selecting default time zone ... UTC
authentik_postgres  | creating configuration files ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172887.1415074, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172887.141752, "count": 13}
authentik_postgres  | running bootstrap script ... ok
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 04:01:27.363 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172887.4359767}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172888.4375963}
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to start....2025-01-18 04:01:28.751 UTC [42] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 04:01:28.756 UTC [42] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 04:01:28.778 UTC [43] LOG:  database system was shut down at 2025-01-18 04:01:27 UTC
authentik_postgres  | 2025-01-18 04:01:28.787 UTC [42] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down...2025-01-18 04:01:29.265 UTC [42] LOG:  received fast shutdown request
authentik_postgres  | .2025-01-18 04:01:29.271 UTC [42] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 04:01:29.272 UTC [42] LOG:  background worker "logical replication launcher" (PID 49) exited with exit code 1
authentik_postgres  | 2025-01-18 04:01:29.272 UTC [44] LOG:  shutting down
authentik_postgres  | 2025-01-18 04:01:29.316 UTC [42] LOG:  database system is shut down
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 04:01:29.391 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 04:01:29.391 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 04:01:29.391 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 04:01:29.404 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 04:01:29.415 UTC [57] LOG:  database system was shut down at 2025-01-18 04:01:29 UTC
authentik_postgres  | 2025-01-18 04:01:29.423 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172889.4383156}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172889.448243}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172889.449012}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172889.4490845}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737172890.410906, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172890.4113305, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172890.412652}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4131596, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4137964, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4142206, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4152603, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.416458, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.417292, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.418749, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.419491, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4195087, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4199138, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.420195, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4207191, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4212232, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.421583, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.422116, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172890.4229515, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:30.754299"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:30.754912"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.780771"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.781049"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.790747"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.790969"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.791542"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.809681"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.828796"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.829251"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.829752"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.836297"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.836618"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.836941"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.837183"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.838546"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.839189"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.839788"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.840937"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.841307"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.844974"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.846907"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.855363"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.855671"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.856046"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.856406"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.856681"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.881856"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.881985"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.883121"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.883178"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.883437"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.883737"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.884118"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.884329"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.884641"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.884842"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.887858"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.888078"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:31.888125"}
authentik           | 
authentik           | 
authentik           | Type 'manage.py help <subcommand>' for help on a specific subcommand.
authentik           | 
authentik           | 
authentik           | Available subcommands:
authentik           | 
authentik           | 
authentik           | [auth]
authentik           |     changepassword
authentik           |     createsuperuser
authentik           | 
authentik           | 
authentik           | [authenticator_webauthn]
authentik           |     update_webauthn_mds
authentik           | 
authentik           | 
authentik           | [blueprints]
authentik           |     apply_blueprint
authentik           |     export_blueprint
authentik           |     make_blueprint_schema
authentik           | 
authentik           | 
authentik           | [channels]
authentik           |     runworker
authentik           | 
authentik           | 
authentik           | [contenttypes]
authentik           |     remove_stale_contenttypes
authentik           | 
authentik           | 
authentik           | [core]
authentik           |     bootstrap_tasks
authentik           |     build_source_docs
authentik           |     change_user_type
authentik           |     dev_server
authentik           |     repair_permissions
authentik           |     shell
authentik           |     worker
authentik           | 
authentik           | 
authentik           | [crypto]
authentik           |     import_certificate
authentik           | 
authentik           | 
authentik           | [django]
authentik           |     check
authentik           |     compilemessages
authentik           |     createcachetable
authentik           |     dbshell
authentik           |     diffsettings
authentik           |     dumpdata
authentik           |     flush
authentik           |     inspectdb
authentik           |     loaddata
authentik           |     makemessages
authentik           |     makemigrations
authentik           |     optimizemigration
authentik           |     sendtestemail
authentik           |     showmigrations
authentik           |     sqlflush
authentik           |     sqlmigrate
authentik           |     sqlsequencereset
authentik           |     squashmigrations
authentik           |     startapp
authentik           |     startproject
authentik           |     test
authentik           |     testserver
authentik           | 
authentik           | 
authentik           | [django_tenants]
authentik           |     all_tenants_command
authentik           |     clone_tenant
authentik           |     collectstatic_schemas
authentik           |     create_missing_schemas
authentik           |     create_tenant
authentik           |     create_tenant_superuser
authentik           |     delete_tenant
authentik           |     migrate
authentik           |     migrate_schemas
authentik           |     rename_schema
authentik           |     tenant_command
authentik           | 
authentik           | 
authentik           | [drf_spectacular]
authentik           |     spectacular
authentik           | 
authentik           | 
authentik           | [email]
authentik           |     test_email
authentik           | 
authentik           | 
authentik           | [flows]
authentik           |     benchmark
authentik           | 
authentik           | 
authentik           | [guardian]
authentik           |     clean_orphan_obj_perms
authentik           | 
authentik           | 
authentik           | [kerberos]
authentik           |     kerberos_check_connection
authentik           |     kerberos_sync
authentik           | 
authentik           | 
authentik           | [ldap]
authentik           |     ldap_check_connection
authentik           |     ldap_sync
authentik           | 
authentik           | 
authentik           | [pgactivity]
authentik           |     pgactivity
authentik           | 
authentik           | 
authentik           | [pglock]
authentik           |     pglock
authentik           | 
authentik           | 
authentik           | [recovery]
authentik           |     create_admin_group
authentik           |     create_recovery_key
authentik           | 
authentik           | 
authentik           | [rest_framework]
authentik           |     generateschema
authentik           | 
authentik           | 
authentik           | [scim]
authentik           |     scim_sync
authentik           | 
authentik           | 
authentik           | [sessions]
authentik           |     clearsessions
authentik           | 
authentik           | 
authentik           | [staticfiles]
authentik           |     collectstatic
authentik           |     findstatic
authentik           |     runserver
authentik exited with code 0
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172892.4669511, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172892.4671638, "count": 13}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172892.760581}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172892.7664547}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172892.7670753}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172892.767135}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737172893.6543405, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172893.6547587, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737172893.6563044}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6568189, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6575632, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.658438, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6586516, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6600416, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6606646, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6610298, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6620195, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.66263, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.662915, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6631932, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6641524, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6651328, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.665585, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6659877, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737172893.6666074, "path": "authentik.sources.ldap.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:33.984183"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:33.984795"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.946138"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.946401"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.955983"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.956312"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.957083"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.975879"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.995779"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.996239"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:34.996746"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.003359"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.003689"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.004004"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.004249"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.005599"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.006244"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.006918"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.008067"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.008438"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.012106"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.014039"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.022399"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.022708"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.023080"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.023432"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.023714"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.048761"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.048896"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.050038"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.050092"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.050357"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.050658"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.051042"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.051255"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.051564"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.051774"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.054627"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.054850"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T04:01:35.054899"}
authentik           | 
authentik           | 
authentik           | Type 'manage.py help <subcommand>' for help on a specific subcommand.
authentik           | 
authentik           | 
authentik           | Available subcommands:
authentik           | 
authentik           | 
authentik           | [auth]
authentik           |     changepassword
authentik           |     createsuperuser
authentik           | 
authentik           | 
authentik           | [authenticator_webauthn]
authentik           |     update_webauthn_mds
authentik           | 
authentik           | 
authentik           | [blueprints]
authentik           |     apply_blueprint
authentik           |     export_blueprint
authentik           |     make_blueprint_schema
authentik           | 
authentik           | 
authentik           | [channels]
authentik           |     runworker
authentik           | 
authentik           | 
authentik           | [contenttypes]
authentik           |     remove_stale_contenttypes
authentik           | 
authentik           | 
authentik           | [core]
authentik           |     bootstrap_tasks
authentik           |     build_source_docs
authentik           |     change_user_type
authentik           |     dev_server
authentik           |     repair_permissions
authentik           |     shell
authentik           |     worker
authentik           | 
authentik           | 
authentik           | [crypto]
authentik           |     import_certificate
authentik           | 
authentik           | 
authentik           | [django]
authentik           |     check
authentik           |     compilemessages
authentik           |     createcachetable
authentik           |     dbshell
authentik           |     diffsettings
authentik           |     dumpdata
authentik           |     flush
authentik           |     inspectdb
authentik           |     loaddata
authentik           |     makemessages
authentik           |     makemigrations
authentik           |     optimizemigration
authentik           |     sendtestemail
authentik           |     showmigrations
authentik           |     sqlflush
authentik           |     sqlmigrate
authentik           |     sqlsequencereset
authentik           |     squashmigrations
authentik           |     startapp
authentik           |     startproject
authentik           |     test
authentik           |     testserver
authentik           | 
authentik           | 
authentik           | [django_tenants]
authentik           |     all_tenants_command
authentik           |     clone_tenant
authentik           |     collectstatic_schemas
authentik           |     create_missing_schemas
authentik           |     create_tenant
authentik           |     create_tenant_superuser
authentik           |     delete_tenant
authentik           |     migrate
authentik           |     migrate_schemas
authentik           |     rename_schema
authentik           |     tenant_command
authentik           | 
authentik           | 
authentik           | [drf_spectacular]
authentik           |     spectacular
authentik           | 
authentik           | 
authentik           | [email]
authentik           |     test_email
authentik           | 
authentik           | 
authentik           | [flows]
authentik           |     benchmark
authentik           | 
authentik           | 
authentik           | [guardian]
authentik           |     clean_orphan_obj_perms
authentik           | 
authentik           | 
authentik           | [kerberos]
authentik           |     kerberos_check_connection
authentik           |     kerberos_sync
authentik           | 
authentik           | 
authentik           | [ldap]
authentik           |     ldap_check_connection
authentik           |     ldap_sync
authentik           | 
authentik           | 
authentik           | [pgactivity]
authentik           |     pgactivity
authentik           | 
authentik           | 
authentik           | [pglock]
authentik           |     pglock
authentik           | 
authentik           | 
authentik           | [recovery]
authentik           |     create_admin_group
authentik           |     create_recovery_key
authentik           | 
authentik           | 
authentik           | [rest_framework]
authentik           |     generateschema
authentik           | 
authentik           | 
authentik           | [scim]
authentik           |     scim_sync
authentik           | 
authentik           | 
authentik           | [sessions]
authentik           |     clearsessions
authentik           | 
authentik           | 
authentik           | [staticfiles]
authentik           |     collectstatic
authentik           |     findstatic
authentik           |     runserver
authentik exited with code 0

#### ChatGPT:
<time datetime="2025-01-18T04:02:02.389Z" title="1/18/2025, 1:02:02 PM">13:02</time>

From the logs, Authentik **has successfully started** and completed its “bootstrap” phase. The container then prints out a list of available management commands (like `createsuperuser`) and exits with code 0, which is actually **normal behavior** for Authentik in **“command” mode**. Here’s what that means and what to do next:

---

## 1. Why Authentik Exited with Code 0

By default, the Authentik Docker image runs its **bootstrap** (which configures the database and checks environment variables), shows you the help for its internal `manage.py` commands, then **exits** if you haven’t specified a different “run mode.” Essentially:

1. Authentik sees your environment variables, connects to Postgres & Redis, does initial setup.
2. It prints the management commands (like `createsuperuser`).
3. **Because** the command finishes, the container stops with exit code 0 (successful).

This is normal for the image’s *default* command if you don’t override it to **run the actual Authentik server**.

---

## 2. How to Actually Run Authentik as a Server

To keep Authentik running and serving web traffic on port 9000 (so Traefik can route to it), you need to run Authentik in **“server”** or **“server+worker”** mode. Typically, you do this by setting:

```yaml
command: server
```

(or `command: server+worker` if you want background tasks in the same container)

### Example in `docker-compose.yml`:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    command: "server"
    # or: command: "server+worker"
    ...
```

If you leave the default `command`, Authentik runs the bootstrap process and quits, which explains why the container repeatedly shows you the command list and exits. By specifying `command: "server"`, the container will stay **running** as a web server.

---

## 3. Full Docker Compose Snippet

Your Authentik service might look like:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    restart: unless-stopped
    command: "server"
    environment:
      AUTHENTIK_HOST: "https://login.apsjado.com"
      AUTHENTIK_SECRET_KEY: "yourlongrandomkey..."
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"
    networks:
      - traefik-net
```

Then, after `docker compose up -d`, the **`authentik`** container will **stay running** in “server” mode, and you can visit **`https://login.apsjado.com`** to access the Authentik UI.

---

## 4. Verify Authentik is in “Server” Mode

After switching to `command: "server"`, check logs:

```bash
docker compose logs -f authentik
```

You should see lines like:

```
[info] Starting server...
[info] Listening on 0.0.0.0:9000
```

or similar. It won’t exit with code 0; it will keep running indefinitely as a service.

---

## 5. Create Your Admin User

Once Authentik is running in server mode:

1. Browse to `https://login.apsjado.com` and see if it prompts you to create an admin user, or
2. Run:
   ```bash
   docker compose exec authentik authentik bootstrap
   ```
   This helps you set an admin username and password if you haven’t already done so.

---

### Summary

- The logs show Authentik completes bootstrap then **exits** → That’s the **default** container behavior.
- **Switch** to `command: "server"` (or `server+worker`) so Authentik runs continuously, listening on port 9000 for web traffic.
- **Restart** with `docker compose up -d` and confirm Authentik remains up.
- Finally, visit `https://login.apsjado.com` to manage Authentik’s web UI, create users, and set up your identity provider flows. Enjoy!


#### You:
<time datetime="2025-01-18T04:12:03.741Z" title="1/18/2025, 1:12:03 PM">13:12</time>

ashwin@ubuntu-server:~/traefik$ docker compose exec authentik authentik bootstrap
Error: unknown command "bootstrap" for "authentik"
Run 'authentik --help' for usage.
ashwin@ubuntu-server:~/traefik$ 

#### ChatGPT:
<time datetime="2025-01-18T04:12:22.212Z" title="1/18/2025, 1:12:22 PM">13:12</time>

It looks like the **`bootstrap`** subcommand no longer exists (or has changed) in the current Authentik image you’re using. That’s why you see an “unknown command ‘bootstrap’” error. In newer Authentik versions, you have two main approaches to create or reset an admin user:

1. **`authentik createsuperuser`**
2. **`authentik core bootstrap_tasks`**

From the command list you see in the container logs (the big list of subcommands), `createsuperuser` is under the `[auth]` category, and `bootstrap_tasks` is under `[core]`. The older `authentik bootstrap` command was removed or changed in newer releases.

---

## 1. Creating an Admin User with `createsuperuser`

The most straightforward option is to run:

```bash
docker compose exec authentik authentik createsuperuser
```

- You’ll be prompted for a username, email, and password.
- Once complete, you can log in to Authentik’s web UI (e.g., `https://login.apsjado.com`) with that account.

---

## 2. Running “Bootstrap Tasks” (Optional)

If you need to run the full “bootstrap tasks” that used to happen automatically, you can do:

```bash
docker compose exec authentik authentik core bootstrap_tasks
```

This re-checks certain initial setup items and can generate a user if none exist. But generally, **`createsuperuser`** is enough if all you want is an admin login.

---

## 3. Confirm You’re in “Server” Mode

Also ensure your `docker-compose.yml` for Authentik uses:

```yaml
command: "server"
```

or

```yaml
command: "server+worker"
```

Otherwise, Authentik will run once (show the subcommand list) and then exit. You want it to keep running as a web server so you can actually access `https://login.apsjado.com`.

---

### TL;DR

- **`bootstrap`** command is gone in newer Authentik releases.
- Use **`authentik createsuperuser`** to create an admin account, or **`core bootstrap_tasks`** if you need the old-style bootstrap routine.
- Make sure Authentik is running in **server mode** so you can log in and configure it further via the browser.


#### You:
<time datetime="2025-01-18T04:15:01.627Z" title="1/18/2025, 1:15:01 PM">13:15</time>

ashwin@ubuntu-server:~/traefik$ docker compose exec authentik authentik createsuperuser
Error: unknown command "createsuperuser" for "authentik"
Run 'authentik --help' for usage.
ashwin@ubuntu-server:~/traefik$ 
--Skip to main content
authentik logo
Blog
Documentation
Integrations
Pricing

    Version: 2024.12
    Welcome to authentik
    Core Concepts
    Enterprise

Installation and Configuration
Add and Secure Applications
Customize your instance

    Policies

Interfaces
Blueprints
Export
File structure
YAML Tags
Example
Models

    Brands

Manage Users and Sources

    Users

    Manage users
    User properties and attributes
    Invitations

Groups
Roles
Access Control
Federated and Social Sources
System Management
Developer Documentation
Security
Troubleshooting
Release Notes

    Manage Users and SourcesUsersManage users

Manage users

The following topics are for the basic management of users: how to create, modify, delete or deactivate users, and using a recovery email.

Policies can be used to further manage how users are authenticated. For example, by default authentik does not require email addresses be unique, but you can use a policy to enforce unique email addresses.
Create a user

    If you want to automate user creation, you can do that either by invitations, user_write stage, or using the API.

    In the Admin interface of your authentik instance, select Directory > Users in the left side menu.
    Select the folder where you want to create a user.
    Click Create (for a default user).
    Fill in the required fields:

    Username: This value must be unique across your user folders.
    Path: The path where the user will be created. It will be automatically populated with the folder you selected in the previous step.

    Fill the optional fields if needed:

    Name: The display name of the user.
    Email: The email address of the user. Email addresses are used in email stages and to receive notifications, if configured.
    Is active: Define if the newly created user account is active. Selected by default.
    Attributes: Custom attributes definition for the user, in YAML or JSON format. These attributes can be used to enforce additional prompts on authentication stages or define conditions to enforce specific policies if the current implementation does not fit your use case. The value is an empty dictionary by default.

    Click Create

You should see a confirmation pop-up on the top-right of the screen that the user has been created, and see the new user in the user list. You can directly click the username if you want to modify your user.
info

To create a super-user, you need to add the user to a group that has super-user permissions. For more information, refer to Create a Group.
View user details

In the Directory > Users menu of the Admin interface, you can browse all the users in your authentik instance.

To view details about a specific user:

    In the list of all users, click on the name of the user you want to check.

    This takes you to the Overview tab, with basic information about the user, and also quick access to perform basic actions to the user.

    To see further details, click any of the other tabs:

    Session shows the active sessions established by the user. If there is any need, you can clean up the connected devices for a user by selecting the device(s) and then clicking Delete. This forces the user to authenticate again on the deleted devices.
    Groups allows you to manage the group membership of the user. You can find more details on groups.
    User events displays all the events generated by the user during a session, such as login, logout, application authorisation, password reset, user info update, etc.
    Explicit consent lists all the permissions the user has given explicitly to an application. Entries will only appear if the user is validating an explicit consent flow in an OAuth2 provider. If you want to delete the explicit consent (because the application is requiring new permissions, or the user has explicitly asked to reset his consent on third-party apps), select the applications and click Delete. The user will be asked to again give explicit consent to share information with the application.
    OAuth Refresh Tokens lists all the OAuth tokens currently distributed. You can remove the tokens by selecting the applications and then clicking Delete.
    MFA Authenticators shows all the authentications that the user has registered to their user profile. You can remove the tokens if the user has lost their authenticator and want to enroll a new one.

Modify a user

After the creation of the user, you can edit any parameter defined during the creation.

To modify a user object, go to Directory > Users, and click the edit icon beside the name. You can also go into user details, and click Edit.
Assign, modify, or remove permissions for a user

You can grant a user specific global or object-level permissions. Alternatively, you can add a user to a group that has the appropriate permissions, and the user inherits all of the group's permissions.

For more information, review "Permissions".
Add a user to a group

    To add a user to a group, navigate to Directory > Users to display all users.
    Click the name of the user to display the full user details page.
    Click the Groups tab, and then click either Add to existing group or Add to new group.

User credentials recovery

If a user has lost their credentials, there are several options.
Generate a recovery link
info

This option is only available if a default recovery flow was configured for the currently active brand.

    In the Admin interface, navigate to Directory > Users to display all users.
    Either click the name of the user to display the full User details page, or click the chevron (the › symbol) beside their name to expand the options.
    To generate a recovery link, which you can then copy and paste into an email, click Create recovery link.

A pop-up will appear on your browser with the link for you to copy and to send to the user.
Email them a recovery link
info

This option is only available if a default recovery flow was configured for the currently active brand and if the configured flow has an Email Stage bound to it.

You can send a link with the URL for the user to reset their password via Email. This option will only work if you have properly configured a SMTP server during the installation and set an email address for the user.

    In the Admin interface, navigate to Directory > Users to display all users.
    Either click the name of the user to display the full User details page, or click the chevron beside their name to expand the toptions.
    To send the email to the user, click Email recovery link.

If the user does not receive the email, check if the mail server parameters are properly configured.
Reset the password for the user

As an Admin, you can simply reset the password for the user.

    In the Admin interface, navigate to Directory > Users to display all users.
    Either click the name of the user to display the full User details page, or click the chevron beside their name to expand the options.
    To reset the user's password, click Reset password, and then define the new value.

Deactivate or Delete user
To deactivate a user:

    Go into the user list or detail, and click Deactivate.
    Review the changes and click Update.

The active sessions are revoked and the authentication of the user blocked. You can reactivate the account by following the same procedure.
To delete a user:
caution

This deletion is not reversible, so be sure you do not need to recover any identity data of the user. You may instead deactivate the account to preserve identity data.

    Go into the user list and select one (or multiple users) to delete and click Delete on the top-right of the page.
    Review the changes and click Delete.

The user list refreshes and no longer displays the removed users.
Impersonate a user

With authentik, an Admin can impersonate a user, meaning that the Admin temporarily assumes the identity of the user.

    In the Admin interface, navigate to Directory > Users to display all users.
    Click the name of the user to display the full User details page.
    On the Overview tab, beneath User Details, in the Actions area, click Impersonate.
    At the prompt, provide a reason why you are impersonating this user, and then click Impersonate.

info

An Admin can globally enable or disable impersonation in the System Settings. By default, this option is set to true, meaning all users can be impersonated.

An Admin can also configure whether inputting a reason for impersonation is required in the System Settings.
Edit this page
Previous
About users
Next
User properties and attributes

    Create a user
    View user details
    Modify a user
        Assign, modify, or remove permissions for a user
    Add a user to a group
    User credentials recovery
        Generate a recovery link
        Email them a recovery link
        Reset the password for the user
    Deactivate or Delete user
        To deactivate a user:
        To delete a user:
    Impersonate a user

Copyright © 2025 Authentik Security Inc. Built with Docusaurus.

#### ChatGPT:
<time datetime="2025-01-18T04:15:43.048Z" title="1/18/2025, 1:15:43 PM">13:15</time>

It turns out the `createsuperuser` command in newer Authentik releases is nested under the **`auth`** subcommand rather than being invoked directly. In other words, you won’t run:

```
authentik createsuperuser
```

Instead, you must prefix it with `auth`:

```
docker compose exec authentik authentik auth createsuperuser
```

That should prompt you for the username, email, and password—exactly like a standard Django `createsuperuser`. Once you’ve created the account, here’s what to do next:

---

## 1. Adding “Superuser” Privileges

By default, **creating a user** does not automatically grant “superuser” privileges in Authentik. Per Authentik’s own docs, you must either:

- Place the user in a **group** that has superuser permissions, or
- Explicitly grant them admin-level permissions within the Admin UI.

### Via the Admin UI

1. Log in with your newly created user (assuming you gave them an easy password).
2. Go to **Directory > Groups** in the Admin interface.
3. Either **edit** an existing group with the needed permissions or **create** a new group that includes superuser-level privileges.
4. From **Directory > Users**, click on the user → **Groups** tab → **Add to existing group**. Choose the group that has superuser permission.

Once that’s done, your user can manage system-wide settings.

---

## 2. If You Need Full CLI-Only Management

If you prefer not to use the UI at all, you can:

1. Create a user with:
   ```bash
   docker compose exec authentik authentik auth createsuperuser
   ```
2. Create (or modify) a group that has superuser permissions.
3. Assign that user to the group via a relevant CLI command or API call.

However, Authentik’s documentation primarily encourages using the Admin interface to manage groups and user roles.

---

## 3. Confirm Authentik is in “Server” Mode

Lastly, ensure your `docker-compose.yml` for Authentik includes:

```yaml
command: "server"
```

(or `server+worker`)

Otherwise, Authentik will just show the subcommand list and exit. With `command: "server"`, Authentik keeps running and listens on port 9000, so Traefik can proxy requests from `https://login.apsjado.com`.

**Example** snippet for Authentik:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    command: "server"
    environment:
      AUTHENTIK_SECRET_KEY: "yoursecretkeyhere"
      AUTHENTIK_HOST: "https://login.apsjado.com"
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: yourpassword
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"
    # ...
```

Then once Authentik is running, you can exec into the container:

```bash
docker compose exec authentik authentik auth createsuperuser
```

and properly manage your account. After that, the UI at `https://login.apsjado.com` will let you handle more granular settings.

That’s it—now you can log in as an admin-level user and configure Authentik however you like!


#### You:
<time datetime="2025-01-18T04:20:46.883Z" title="1/18/2025, 1:20:46 PM">13:20</time>

ashwin@ubuntu-server:~/traefik$ docker compose exec authentik authentik auth createsuperuser
Error: unknown command "auth" for "authentik"
Run 'authentik --help' for usage.
ashwin@ubuntu-server:~/traefik$ 

Skip to content
Navigation Menu

    netbirdio

    netbird

Code
Issues 825
Pull requests 20
Actions
Projects 1
Security

    Insights

Unable to authenticate with Authentik SSO #2515
Open
Open
Unable to authenticate with Authentik SSO
#2515
@excaliburzarau
Description
excaliburzarau
opened on Sep 2, 2024 · edited by excaliburzarau

Describe the problem

When trying to connect a mobile device or a laptop, after pressing to connect, the Netbird redirects me to Authentik, then it redirects me to a localhost:53000 page saying that i am now connected.
After i go back to the Netbird menu, i press to connect and it gets stuck on connecting. On the logs it reports that no peer auth method provided, please use a setup key or interactive SSO login and i can actually see that on the it does not get an user Id with the code accountID: UNKNOWN this can be verified on the image below.

To Reproduce

Steps to reproduce the behavior:

    Go to the Netbird client.
    Click on Change Server.
    Add the server.
    Authenticate on Authentik.
    Go back to the Netbird client and connect.

Expected behavior

Authenticate with the Authentik user and connect the Netbird client to my self-hosted server.

Are you using NetBird Cloud?

It is a self-host NetBird's control plane.

NetBird version

v0.28.9

NetBird status -dA output:

Not applicable

Do you face any (non-mobile) client issues?

I have issues both on the mobile client and the laptop.
Unable to run the command for the same reason as above.

Screenshots

Sem título

363506711-3ba8edcf-b368-4a31-a7aa-8d292b6d38c7

363506706-149e918a-b354-4318-8847-f976333d772e

Additional context

I believe that the Authentik application is sending the User ID but for some reason the Netbird does not receive the User ID presenting the error accountID: UNKNOWN .
If i try to set a different scope on the Authentik application it does get the data from Authentik which i can see on the Netbird logs.

Can someone give me an idea of what i might be missing?

Thank you all in advance.
Activity
excaliburzarau
added
triage-needed
on Sep 2, 2024
excaliburzarau
excaliburzarau commented on Sep 4, 2024
excaliburzarau
on Sep 4, 2024
Author

Hello guys,

An update on the issue.

I AM using the cloudflare provider, i already enabled the grc streaming option on my DNS profile.

I also tried to create a new flow device-code-flow and assign it to a brand on Authentik, the issue still remains.

Thank you all in advance.

Best Regards
excaliburzarau
mentioned this on Sep 21, 2024

    Authentik SSO Login is not functioning #1288

zoechi
mentioned this on Sep 25, 2024

    Error: Unauthenticated, signin works only using setup keys #2123

Kartel1
Kartel1 commented on Nov 4, 2024
Kartel1
on Nov 4, 2024

Hello, I'm trying to use netbird with Authentik and Traefik and I'm facing the same issue.
I was able to add peers, but they never connect as I have the issue with the SSO.
I have a device flow and it's correctly set up.
I can't figure out where I failed in my conf or if it's just a bug.
I'm looking forward some help too

Thanks in advance :)
Kartel1
Kartel1 commented on Nov 4, 2024
Kartel1
on Nov 4, 2024 · edited by Kartel1

Actually I figure out what was wrong.
I'm using Traefik as reverse proxy with letsencrypt for SSL and the acme.json file had this entry:
*.myDomain.tld
I had to delete this entry (and only this one)
When you check Traefik's logs there is an error message about signal-management (netbird). LetsEncrypt doesn't consider the domain for signal is valid.
I made some test with the netbird docker client and the log was pretty explicit, Signal was the culprit.

You should check your netbird docker-compose file and for dashboard and signal, make sure you're not specifying any https
for traefik labels you should have something like this:

    dashboard
    labels:
    - "traefik.enable=true"
    - "traefik.http.routers.netbird-http.rule=Host(netbird.myDomain.tld)"
    - "traefik.http.routers.netbird-http.entrypoints=websecure,web"
    - "traefik.http.routers.netbird-http.tls=true"
    - "traefik.http.routers.netbird-http.service=netbird-svc@docker"
    - "traefik.http.services.netbird-svc.loadBalancer.server.port=80"
    - "traefik.docker.network=Your_network"
    Signal:

labels:
- "traefik.enable=true"
- "traefik.http.routers.netbird-signal-http.rule=Host(netbird.myDomain.tld) && PathPrefix(/signalexchange.SignalExchange/)"
- "traefik.http.routers.netbird-signal-http.entrypoints=websecure,web"
- "traefik.http.routers.netbird-signal-http.tls=true"
- "traefik.http.routers.netbird-signal-http.service=netbird-signal-svc@docker"
- "traefik.http.services.netbird-signal-svc.loadBalancer.server.port=80"
- "traefik.http.services.netbird-signal-svc.loadBalancer.server.scheme=h2c"
- "traefik.docker.network=Your_network"

With that you should be able to connect your peer to netbird as you can see on this picture (green dot)
the first one is a docker container on my windows machine and the second one is my phone

image

The only thing I have to try now is to connect my phone through mobile network because i was on wifi here (it didn't work so far, but that's 100% on my side this one)
wbywfjptrgmuMJxByvFD
Add a comment
new Comment
Markdown input: edit mode selected.
Remember, contributions to this repository should follow its contributing guidelines, security policy and code of conduct.
Assignees
No one assigned

Labels
triage-needed
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
@Kartel1
@excaliburzarau
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

Unable to authenticate with Authentik SSO · Issue #2515 · netbirdio/netbird

#### ChatGPT:
<time datetime="2025-01-18T04:21:19.093Z" title="1/18/2025, 1:21:19 PM">13:21</time>

Based on your logs, Authentik **does** show an `[auth]` section with subcommands `changepassword` and `createsuperuser`, but you’re getting “unknown command ‘auth.’” That typically means **those subcommands are nested under the `manage` command** rather than top-level. In other words, Authentik’s CLI has a structure like:

```
authentik [top-level-subcommand] [next-level-subcommand] ...
```

and `[auth]` is actually a sub-subcommand under `manage`.

---

## 1. Use `authentik manage auth createsuperuser`

Try running:

```bash
docker compose exec authentik authentik manage auth createsuperuser
```

This is the most common pattern in newer Authentik versions, where:

- **`manage`** is a top-level subcommand (basically the “Django manage.py” equivalent).
- **`auth`** is the second-level subcommand group containing `createsuperuser`.

If you run `authentik --help`, you should see something like:

```
Available top-level subcommands:
[core] ...
[manage] ...
[sessions] ...
[auth] ...
```

But since `[auth]` only appears **under** `manage`, you have to do `authentik manage auth ...`.

---

## 2. Verify You’re in “Server” Mode

Make sure your **docker-compose.yml** for the Authentik service specifies:

```yaml
command: "server"
```

or

```yaml
command: "server+worker"
```

Otherwise, Authentik might just exit after listing commands. In “server” mode, Authentik will keep running and serve traffic on port 9000.

---

## 3. Granting Superuser/Admin Permissions

Running `createsuperuser` will create a new user with **basic** permissions. However, in Authentik >=2023.x, simply creating a user named “admin” doesn’t always give that account full superuser privileges. Depending on your version/configuration:

1. **Add** that user to a group with superuser or administrative permissions in the **Admin UI** under *Directory > Users > (your user) > Groups*.
2. Or use the UI to give that user the needed global permissions directly.

---

## 4. Summary

- **Command to create a user**:
  ```bash
  docker compose exec authentik authentik manage auth createsuperuser
  ```
- **Then** log in at `https://login.example.com` (whatever domain you used).
- **Assign** superuser rights via *Directory > Users* or *Directory > Groups* in the Authentik admin interface.

Once that’s done, you’ll have a fully privileged admin account and can manage Authentik’s settings, flows, and providers in the web UI without further CLI steps.


#### You:
<time datetime="2025-01-18T04:22:58.179Z" title="1/18/2025, 1:22:58 PM">13:22</time>

ashwin@ubuntu-server:~/traefik$ docker compose exec authentik --help
OCI runtime exec failed: exec failed: unable to start container process: exec: "--help": executable file not found in $PATH: unknown
ashwin@ubuntu-server:~/traefik$ docker compose exec authentik authentik --help
Start authentik instance

Usage:
  authentik [flags]
  authentik [command]

Available Commands:
  completion  Generate the autocompletion script for the specified shell
  healthcheck 
  help        Help about any command

Flags:
  -h, --help      help for authentik
  -v, --version   version for authentik

Use "authentik [command] --help" for more information about a command.
ashwin@ubuntu-server:~/traefik$ 

#### ChatGPT:
<time datetime="2025-01-18T04:23:29.094Z" title="1/18/2025, 1:23:29 PM">13:23</time>

It looks like you’re running **Authentik’s newer Go-based container**, which only provides a few top-level commands (`completion`, `healthcheck`, `help`) when you run `authentik --help`. In older versions or the Python-based Authentik container, you had commands like `manage` or `bootstrap`; now, those don’t appear in your image.

### Why This Is Happening

- **Older docs** reference `authentik manage ...` or `authentik bootstrap ...` subcommands, which were part of the Python-based container.
- **Your container** shows only `completion`, `healthcheck`, and `help`, meaning it’s the new minimal Go wrapper, and **the Django “manage.py” style commands are gone**.

---

## How to Create an Admin User Now

### 1. Use Environment Variables (Auto-Bootstrap)

The **recommended** approach on newer Authentik versions is to **auto-create** an admin user by setting environment variables when the container starts. For example, in your `docker-compose.yml` for the Authentik **server** container:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    command: "server"
    environment:
      # ... other required variables ...
      AUTHENTIK_SECRET_KEY: "random-long-secret"
      
      # BOOTSTRAP an admin user
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "admin@example.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "supersecure"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"

      # Host, Redis, Postgres config, etc...
    # volumes, networks, labels for Traefik, etc.
```

On first launch, **Authentik** will see those environment variables and **automatically** create an admin user with the given username, email, and password. Check the logs to confirm.

> **Note**: The exact variable names can differ slightly depending on your Authentik version. In some docs, you may see `AUTHENTIK_ADMIN_EMAIL` or `AUTHENTIK_BOOTSTRAP_USER_EMAIL`; refer to the [Authentik deployment docs](https://goauthentik.io/docs/deployment/docker) for your version.

---

### 2. Create a User from the Web UI

If Authentik is already running in **server** mode on port 9000 (e.g., behind Traefik at `https://login.yourdomain.com`), you can:

1. **Browse** to that URL in your browser.
2. If this is a **fresh** install and no admin user exists, Authentik **may** prompt you to create an admin or initial user. (This depends on version and environment variables.)
3. If you can sign in with a random admin user from logs or a prior bootstrap, you can create a new user or grant admin rights to an existing user:
   - **Go to**: “Directory → Users”
   - **Create** a new user, then “Groups” tab to add them to a group with **superuser** permissions.

*Some releases do not pop up a “create user” wizard if you didn’t set environment variables, so you may have to rely on environment-based bootstrap or the logs for default credentials.*

---

### 3. No “authentik manage” or “createsuperuser” in the Go-Based Container

Since you see:

```
Available Commands:
  completion
  healthcheck
  help
```

…that indicates the **CLI doesn’t expose Django subcommands**. The new container workflow is:

- **Set environment variables** to bootstrap an admin automatically, or
- **Use** the web UI to create the first user if the container already started.

This is by design in newer versions—**the container is a minimal binary** that runs the server. The old “Python manage.py” approach doesn’t exist in the same way.

---

## 4. Check That You’re in “server” Mode

Make sure in `docker-compose.yml` you have:

```yaml
command: "server"
```

(or `"server+worker"`). That ensures Authentik **keeps running** as a web server, rather than exiting after printing help. If it’s set to “server,” watch logs for:

```
PostgreSQL connection successful
Redis connection successful
Listening on 0.0.0.0:9000
```

Then you can reach it behind Traefik at your chosen domain.

---

## 5. Summary

1. **Old references** to `authentik bootstrap` or `authentik manage createsuperuser` don’t apply to your Go-based container.
2. **Set environment variables** like `AUTHENTIK_BOOTSTRAP_ADMIN_*` for an **auto-created admin** on startup **or** use the web UI (if it allows first-time user creation).
3. **Ensure** you’re in `server` mode so the Authentik container stays running.
4. **Check logs** for a randomly created admin user or confirm the environment-variable-based user was created.
5. **Log in** at `https://login.yourdomain.com`, manage users and groups in the Admin UI.

That’s it! Once you adopt the environment variable or UI approach, you won’t need legacy subcommands. Your Authentik instance will create (or prompt for) an admin user automatically, allowing you to configure the rest of your single sign-on environment.


#### You:
<time datetime="2025-01-18T04:58:21.471Z" title="1/18/2025, 1:58:21 PM">13:58</time>

https://login.apsjado.com/flows/-/default/authentication/?next=/
authentik Logo
Not Found

    Powered by authentik


#### ChatGPT:
<time datetime="2025-01-18T04:58:38.646Z" title="1/18/2025, 1:58:38 PM">13:58</time>

Seeing a **Not Found** error when visiting a URL like

```
https://login.apsjado.com/flows/-/default/authentication/?next=/
```

usually indicates that the **“default/authentication”** flow doesn’t exist or isn’t properly configured in your Authentik instance. By default, Authentik uses named flows like `auth-standalone`, but if your brand or tenant settings point to a “default” flow that doesn’t exist, you’ll get a 404 (Not Found).

Below are a few common reasons and how to fix them:

---

## 1. No “default/authentication” Flow

In many Authentik installations, the main login flow is named something like **`auth-standalone`** or **`auth-embedded`**. If a link points to `flows/-/default/authentication`, but Authentik has no flow with that slug or ID, you’ll see “Not Found.”

**How to Check**:

1. Log into the Admin UI (assuming you have an admin account and can reach it at `https://login.apsjado.com/if/admin/` or something similar).
2. Go to **Flows** (Under “Applications & Flows” in the menu).
3. Look for an existing flow named `authentication` (or “default/authentication”). If it’s missing, that explains the 404.

**How to Fix**:

- Either **rename** an existing flow to `authentication` if that’s what your brand/tenant references, or
- **Update** your brand/tenant configuration to point to an existing flow name (like `auth-standalone`).

---

## 2. Misconfigured Brand / Tenant Settings

If you set your brand or tenant to use a specific “default authentication flow,” but that flow doesn’t exist, Authentik will generate a link to `flows/-/default/authentication` and return a 404.

**How to Check**:

1. In the Admin UI, go to **System > Brands** or **Administration > Tenants**.
2. Look for fields like “Default Authentication Flow,” “Recovery Flow,” etc.
3. If one is set to `default/authentication` (or some slug that doesn’t match a real flow), you’ll see the 404 link on the login page.

**How to Fix**:

- Change that field to a real flow slug, e.g. `auth-standalone`, or create a flow named `authentication`.

---

## 3. Trying to Access a Flow That’s Been Deleted or Renamed

If you previously had a flow called “default/authentication” and you renamed or deleted it, old links or references will break.

**How to Fix**:

- Either create a new flow with the old slug, or update references in your brand, outposts, or tenant to point to the new slug.

---

## 4. Directly Accessing the Wrong URL

If you typed or bookmarked `flows/-/default/authentication` on your own, you might be referencing an old doc or a different version. In many Authentik versions, the standard login link is:

```
https://login.apsjado.com/if/flow/auth-standalone/
```

Try going there instead—if that shows the login page, then your main flow is named `auth-standalone` rather than `default/authentication`.

---

## 5. Restoring the Flow from a Blueprint (If Needed)

If your Authentik install is new and you want the standard “authentication” flow that’s used in official docs, you can:

1. Create a new flow in the Admin UI with the slug set to `authentication`.
2. Add the typical “Identification Stage,” “Password Stage,” etc.
3. Mark that flow as your “Default Authentication Flow” under your brand or tenant.

Or, if you have a blueprint for that flow, apply it again so it re-creates the “default/authentication” slug.

---

### Quick Fix Summary

1. **Check your flows** in Admin: see which ones exist.
2. **Confirm** your brand or tenant config references a flow slug that actually exists.
3. If you truly want a “default/authentication” flow, **create** it or rename an existing flow to that slug.
4. If your real flow is called “auth-standalone,” **update** references in brand/tenant to point to `auth-standalone`.

Once your references match a real flow slug, you won’t get the **Not Found** error at `flows/-/default/authentication/`. You’ll see Authentik’s login interface as expected.


#### You:
<time datetime="2025-01-18T05:00:05.204Z" title="1/18/2025, 2:00:05 PM">14:00</time>

when i visit https://login.apsjado.com/if/admin/ i briefly see an admin page and then it disappears and the "not found" page appears again

#### ChatGPT:
<time datetime="2025-01-18T05:00:24.251Z" title="1/18/2025, 2:00:24 PM">14:00</time>

This behavior (seeing the Admin UI for a moment, then disappearing into a “Not Found” page) usually happens when **Authentik tries to send you to a login or authentication flow that doesn’t exist** or isn’t correctly configured. It often indicates Authentik’s admin interface is briefly rendered, then checks whether you’re authenticated (and/or have admin privileges), and attempts to redirect you to a missing flow to log in—resulting in a 404.

Below are the most common reasons and how to fix each:

---

## 1. Missing or Incorrect Authentication Flow

### Symptoms

- You open `https://login.apsjado.com/if/admin/`.
- The Admin UI flashes briefly.
- You get redirected to a URL like `/flows/-/default/authentication` (or similar) which doesn’t exist → “Not Found.”

### Why It Happens

In Authentik, **Brand** or **Tenant** configurations often specify the default authentication flow (e.g., `default/authentication`). If that flow slug doesn’t actually exist, the redirect is broken.

**Check** under:

- **Admin > Administration > Tenants** or
- **Admin > System > Brands**

Look for fields like “Default Authentication Flow” or “Authentication Flow Slug.” If it’s set to `default/authentication` but your actual flow is named `auth-standalone` (or something else), Authentik will redirect you to a nonexistent flow.

### How to Fix

1. Create (or rename) a flow to match the slug your brand/tenant expects.
2. **Or** update your brand/tenant config to point to an existing flow like `auth-standalone`.

Once they match, you’ll be properly redirected to Authentik’s login page if you’re not already signed in as an admin.

---

## 2. No Valid Admin Account or Not Properly Logged In

### Symptoms

- Briefly see admin UI, then forced away to a 404 or login error.
- Possibly never set up a superuser or admin group membership.

### Why It Happens

When you visit `/if/admin/`, Authentik checks if you have admin permissions:

- If **not** (or you’re not logged in), it tries to redirect you to the login flow.
- If that login flow slug is missing or broken, you end up at a 404.

### How to Fix

1. **Confirm** you have a user with admin permissions:
   - (Old versions) `authentik manage createsuperuser` or (new versions) environment variables for bootstrap or the UI-based user creation.
   - Then, in *Directory > Users > (your user) > Groups*, ensure it’s in a group with “Superuser” or “Administrator” privileges.
2. **Make sure** Authentik’s login flow exists (as explained in #1).
3. Retry visiting `https://login.apsjado.com/if/admin/`—this time, you should be recognized as an admin or get a valid login page.

---

## 3. Brand or Tenant Mismatch

### Symptoms

- If you have multiple tenants/brands and are using a brand that references a missing flow.
- The system might briefly show the admin UI from one tenant, then jump to the brand’s login flow from another tenant → 404.

### How to Fix

- Verify that your **active brand** and **active tenant** have correct settings for “Authentication Flow” and “Recovery Flow.”
- If you only have one brand/tenant, ensure they reference a real flow.

---

## 4. Direct Link to a Stale Flow

If you bookmarked a link to a stale flow (e.g., `flows/-/old_auth_flow`) that was deleted or renamed, you’ll get a 404 after partial loading.

- **Solution**: Update your bookmark or use the correct login flow name.

---

### Checking the Actual Redirect URL

If you open your browser’s **Network** or **Developer Tools** when you visit `/if/admin/`, you’ll see the exact URL Authentik tries to redirect you to. If it’s something like `/flows/-/default/authentication`, but your Flow list doesn’t have “authentication,” that’s your culprit.

---

## TL;DR

- **Root Cause**: Authentik is redirecting you to a **missing login flow** after checking you’re not authenticated for `/if/admin/`.
- **Steps to Resolve**:
  1. Go to *Admin > Flows*—confirm you have a valid login flow (like `auth-standalone`).
  2. Go to *System > Brands* (or *Administration > Tenants*)—make sure the “Default Authentication Flow” matches a real flow’s slug.
  3. Ensure you do have an **admin user** or **superuser**. If not, create it (via UI or bootstrap env variables).
  4. Now, visiting `/if/admin/` either logs you straight in (if you’re already authenticated) or prompts a real login flow instead of 404.

Once the brand/tenant references a valid flow and you have an admin account, you can reliably access the Admin UI at `https://login.apsjado.com/if/admin/` without that “Not Found” page.


#### You:
<time datetime="2025-01-18T05:03:41.367Z" title="1/18/2025, 2:03:41 PM">14:03</time>

version: "3.3"

networks:
  traefik-net:
    external: false

services:
  ##########################################
  # Traefik
  ##########################################
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    networks:
      - traefik-net
    
    ports:
      - "80:80"     # HTTP
      - "443:443"   # HTTPS
    
    # We'll store Traefik config in the same folder as this docker-compose.yml
    volumes:
      # Traefik File-based config (if you use traefik.yml)
      - "./traefik.yml:/traefik.yml:ro"

      # ACME (Let's Encrypt) certificate file
      - "./acme.json:/letsencrypt/acme.json"

      # Docker socket (read-only) so Traefik can detect container labels
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

    command:
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      
      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt (ACME) settings
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"

    # No labels here for the dashboard domain, unless you want to expose it.
    # If you do, you can add your domain rule for the dashboard.

  ##########################################
  # Authentik
  ##########################################
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    restart: unless-stopped
    command: "server"
    networks:
      - traefik-net

    # If you want to access it directly on the host (optional):
    # ports:
    #   - "127.0.0.1:9000:9000"

    labels:
      # Enable Traefik for this service
      - "traefik.enable=true"

      # Route domain login.apsjado.com to the Authentik container
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"

      # Authentik container listens on port 9000, so direct traffic there
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"

    environment:

      AUTHENTIK_SECRET_KEY: "3PqLoxRxB6B7oCGw9MLWSRWU7BhNhbktqa1i5wJgn46K8klPUyu5"
      # Make sure your domain here matches your external URL
      AUTHENTIK_HOST: "https://login.apsjado.com"

      # Database configuration (PostgreSQL)
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik

      # Redis configuration
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"

      # BOOTSTRAP an admin user
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"

      # Email configuration (optional but recommended)
#      AUTHENTIK_EMAIL__HOST: smtp.yourprovider.com
#      AUTHENTIK_EMAIL__PORT: "587"
#      AUTHENTIK_EMAIL__USERNAME: your_smtp_user
#      AUTHENTIK_EMAIL__PASSWORD: your_smtp_pass
#      AUTHENTIK_EMAIL__USE_TLS: "True"

  ##########################################
  # PostgreSQL
  ##########################################
  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    restart: unless-stopped
    networks:
      - traefik-net
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: your_db_password

  ##########################################
  # Redis
  ##########################################
  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped
    networks:
      - traefik-net

#### ChatGPT:
<time datetime="2025-01-18T05:04:10.644Z" title="1/18/2025, 2:04:10 PM">14:04</time>

Here’s a quick walkthrough and explanation of your **docker-compose.yml**. It sets up:

1. **Traefik** as your reverse proxy (handling ports 80/443, Let’s Encrypt SSL, etc.).
2. **Authentik** (running in “server” mode) behind Traefik, accessible at `https://login.apsjado.com`.
3. **PostgreSQL** and **Redis** containers for Authentik’s database and caching needs.

Below is a line-by-line overview of what’s happening and some tips on customizing it further.

---

## 1. Networks

```yaml
networks:
  traefik-net:
    external: false
```

- Defines a private Docker network named `traefik-net` for these services.
- **external: false** means Docker Compose creates and manages this network.

All your containers below attach to this network so Traefik can communicate with Authentik, Postgres, and Redis without exposing them externally.

---

## 2. Traefik Service

```yaml
traefik:
  image: traefik:latest
  container_name: traefik
  restart: unless-stopped
  networks:
    - traefik-net

  ports:
    - "80:80"
    - "443:443"

  volumes:
    - "./traefik.yml:/traefik.yml:ro"
    - "./acme.json:/letsencrypt/acme.json"
    - "/var/run/docker.sock:/var/run/docker.sock:ro"

  command:
    - "--api.dashboard=true"
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
    - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
```

### Explanation

1. **Ports 80 & 443**: Expose HTTP and HTTPS on the host machine.
2. **Volumes**:
   - `traefik.yml` → optional file-based config (if you use it).
   - `acme.json` → stores Let’s Encrypt certificates (ensure `chmod 600 acme.json`).
   - Docker socket (read-only) → allows Traefik to discover and route to containers based on labels.
3. **Commands**:
   - `--api.dashboard=true`: Enables Traefik’s dashboard (if you later add labels for a domain).
   - `--providers.docker=true`: Tells Traefik to read Docker labels for routing rules.
   - `--providers.docker.exposedbydefault=false`: Containers are *not* automatically exposed unless labeled.
   - **ACME** (Let’s Encrypt) config: `--certificatesresolvers.letsencrypt.acme...` sets up an **HTTP-01** challenge on port 80.
   - The email `youremail@example.com` is used by Let’s Encrypt for registration and renewal reminders. Replace with your real email.

### Tips

- Once deployed, Traefik will issue TLS certificates automatically for any domain that points to your server’s IP.
- If you want the Traefik dashboard, you can add labels to the Traefik container (something like `traefik.http.routers.traefik.rule=Host(\`traefik.example.com\`)\`, etc.).

---

## 3. Authentik Service

```yaml
authentik:
  image: ghcr.io/goauthentik/server:latest
  container_name: authentik
  restart: unless-stopped
  command: "server"
  networks:
    - traefik-net

  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
    - "traefik.http.routers.authentik.entrypoints=websecure"
    - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
    - "traefik.http.services.authentik.loadbalancer.server.port=9000"

  environment:
    AUTHENTIK_SECRET_KEY: "3PqLoxRxB6B7..."
    AUTHENTIK_HOST: "https://login.apsjado.com"
    AUTHENTIK_POSTGRESQL__HOST: postgresql
    AUTHENTIK_POSTGRESQL__USER: authentik
    AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
    AUTHENTIK_POSTGRESQL__NAME: authentik
    AUTHENTIK_REDIS__HOST: redis
    AUTHENTIK_REDIS__PORT: "6379"
    AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
    AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
    AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"
    # AUTHENTIK_EMAIL__HOST, etc. (optional)
```

### Explanation

1. **`command: "server"`**: Ensures the container runs Authentik’s web server (rather than just showing a help screen and exiting).
2. **Labels**: Tells Traefik how to route traffic:
   - `traefik.enable=true` → This container is exposed to Traefik.
   - `traefik.http.routers.authentik.rule=Host(\`login.apsjado.com\`)`→ If the request’s Host header is`login.apsjado.com\`, route to this container.
   - `traefik.http.services.authentik.loadbalancer.server.port=9000` → Authentik listens on port 9000 **inside** the container.
   - `traefik.http.routers.authentik.tls.certresolver=letsencrypt` → Tells Traefik to get an SSL cert for `login.apsjado.com`.
3. **Environment Variables**:
   - `AUTHENTIK_SECRET_KEY`: A **persistent secret** for encrypting Authentik sessions and tokens.
   - `AUTHENTIK_HOST`: The external URL for Authentik (`https://login.apsjado.com`).
   - **Database** config: Host, user, password, name → points to the `postgresql` container.
   - **Redis** config: Host is `redis`, port `6379` → matches the `redis` container.
   - **Bootstrapping** an admin user: On first startup, Authentik will create an admin account with the provided username, email, and password if none exists.

### Tips

- Confirm you have **A DNS record** for `login.apsjado.com` pointing to your server’s public IP.
- **Check logs**: `docker compose logs -f authentik` to see if the admin user was created. After that, you can log in at **`https://login.apsjado.com`**.
- If you want password reset emails, configure the email environment variables (`AUTHENTIK_EMAIL__HOST`, etc.) and ensure your Authentik brand or flows include an Email Stage.

---

## 4. PostgreSQL and Redis Containers

### PostgreSQL

```yaml
postgresql:
  image: postgres:14-alpine
  container_name: authentik_postgres
  restart: unless-stopped
  networks:
    - traefik-net
  environment:
    POSTGRES_DB: authentik
    POSTGRES_USER: authentik
    POSTGRES_PASSWORD: your_db_password
```

- Provides the main database for Authentik.
- **Environment** sets DB name, username, password.
- Authentik’s environment references these values (`AUTHENTIK_POSTGRESQL__HOST=postgresql`).
- Alpine-based image is smaller/faster.

### Redis

```yaml
redis:
  image: redis:6-alpine
  container_name: authentik_redis
  restart: unless-stopped
  networks:
    - traefik-net
```

- Serves as a caching layer and for storing sessions.
- Authentik’s config points to this with `AUTHENTIK_REDIS__HOST=redis`.

---

## 5. Running Everything

From the directory containing this `docker-compose.yml`:

1. **Create an empty `acme.json`** file and set permissions:
   ```bash
   touch acme.json
   chmod 600 acme.json
   ```
2. **(Optional) Create** an empty `traefik.yml` if you plan on using file-based config, or remove that volume mount if you’re not using a Traefik file config.
3. **Launch**:
   ```bash
   docker compose up -d
   docker compose logs -f
   ```
4. **Watch logs**:
   - Traefik should say it’s listening on :80 and :443, try fetching a certificate for `login.apsjado.com`.
   - Authentik should connect to Postgres & Redis, mention “bootstrap” for the admin user, and finally say it’s serving on port 9000.

---

## 6. Testing Authentik

1. Ensure your DNS is set: `login.apsjado.com A <server IP>`.
2. **Browse** to `https://login.apsjado.com`.
3. Authentik typically shows a login page. Use the bootstrap admin credentials:
   - **Username**: `admin`
   - **Password**: `password`
   - If that doesn’t work, check the Authentik logs for any relevant message.

If you see a **valid SSL certificate** and can log in, you’ve successfully deployed Authentik behind Traefik with Let’s Encrypt.

---

## 7. Next Steps

- **Secure** the Traefik dashboard (if desired) by adding domain/labels.
- **Configure** Authentik flows, brand, and tenants as needed. For example, set a real “Default Authentication Flow,” brand icons, etc.
- Integrate SSO for more services (Docker containers with OIDC or forward-auth).
- Set up email or 2FA within Authentik to secure admin logins.

Once running, you have a robust identity provider that can unify authentication across your homelab. Enjoy!


#### You:
<time datetime="2025-01-18T05:06:40.271Z" title="1/18/2025, 2:06:40 PM">14:06</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 5/5
 ✔ Container authentik           Removed                                                                                                        0.2s 
 ✔ Container authentik_postgres  Removed                                                                                                        0.3s 
 ✔ Container authentik_redis     Removed                                                                                                        0.4s 
 ✔ Container traefik             Removed                                                                                                        0.4s 
 ✔ Network traefik_traefik-net   Removed                                                                                                        0.2s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_redis     Started                                                                                                        0.6s 
 ✔ Container traefik             Started                                                                                                        0.4s 
 ✔ Container authentik           Started                                                                                                        0.6s 
 ✔ Container authentik_postgres  Started                                                                                                        0.6s 
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 05:05:34.265 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 * Ready to accept connections
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_postgres  | selecting default time zone ... UTC
authentik_postgres  | creating configuration files ... ok
authentik           | {"event":"Loaded config","level":"debug","path":"inbuilt-default","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Loaded config","level":"debug","path":"/authentik/lib/default.yml","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Loaded config from environment","level":"debug","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"not enabling debug server, set `AUTHENTIK_DEBUG` to `true` to enable it.","level":"info","logger":"authentik.go_debugger","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Starting Metrics server","level":"info","listen":"0.0.0.0:9300","logger":"authentik.router.metrics","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Starting HTTP server","level":"info","listen":"0.0.0.0:9000","logger":"authentik.router","timestamp":"2025-01-18T05:05:34Z"}
authentik_postgres  | running bootstrap script ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176734.438687, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176734.438887, "count": 11}
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 05:05:34.569 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event":"Starting HTTPS server","level":"info","listen":"0.0.0.0:9443","logger":"authentik.router","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176734.8544438}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176735.855273}
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to start....2025-01-18 05:05:35.962 UTC [42] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:05:35.969 UTC [42] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:05:35.990 UTC [43] LOG:  database system was shut down at 2025-01-18 05:05:34 UTC
authentik_postgres  | 2025-01-18 05:05:35.999 UTC [42] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down....2025-01-18 05:05:36.449 UTC [42] LOG:  received fast shutdown request
authentik_postgres  | 2025-01-18 05:05:36.454 UTC [42] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 05:05:36.455 UTC [42] LOG:  background worker "logical replication launcher" (PID 49) exited with exit code 1
authentik_postgres  | 2025-01-18 05:05:36.455 UTC [44] LOG:  shutting down
authentik_postgres  | 2025-01-18 05:05:36.499 UTC [42] LOG:  database system is shut down
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 05:05:36.587 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:05:36.600 UTC [57] LOG:  database system was shut down at 2025-01-18 05:05:36 UTC
authentik_postgres  | 2025-01-18 05:05:36.608 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8559859}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.865493}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8660128}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8660517}
authentik_postgres  | 2025-01-18 05:05:36.870 UTC [65] ERROR:  relation "public.authentik_install_id" does not exist at character 16
authentik_postgres  | 2025-01-18 05:05:36.870 UTC [65] STATEMENT:  SELECT id FROM public.authentik_install_id ORDER BY id LIMIT 1;
authentik           | 2025-01-18 05:05:36 [info     ] waiting to acquire database lock
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=install_id.py
authentik_postgres  | 2025-01-18 05:05:36.880 UTC [66] WARNING:  there is already a transaction in progress
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=install_id.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=template_schema.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=template_schema.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=tenant_files.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=tenant_files.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=version_history_create.py
authentik_postgres  | 2025-01-18 05:05:36.904 UTC [66] WARNING:  there is already a transaction in progress
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=version_history_create.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=version_history_update.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=version_history_update.py
authentik           | 2025-01-18 05:05:36 [info     ] applying django migrations
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737176737.7043197, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176737.7046652, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176737.7059383}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7064414, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7072363, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7077956, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7084992, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7110476, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7113278, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7117403, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7123122, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7130513, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7133982, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7137039, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7139425, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7149587, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7160487, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7163422, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.71678, "path": "authentik.events.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:38.019814"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:38.020427"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.012263"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.012547"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.022059"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.022379"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.023145"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.042030"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.062153"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.062651"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.063176"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.070016"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.070839"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.071182"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.071448"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.072897"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.073575"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.074184"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.075374"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.075764"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.079563"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.081601"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.090418"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.090739"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091128"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091504"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091791"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.118084"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.118216"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119449"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119506"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119790"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120103"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120520"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120756"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.121160"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.121379"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124425"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124659"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124709"}
authentik           | === Starting migration
authentik           | Operations to perform:
authentik           |   Apply all migrations: auth, authentik_blueprints, authentik_brands, authentik_core, authentik_crypto, authentik_enterprise, authentik_events, authentik_flows, authentik_outposts, authentik_policies, authentik_policies_dummy, authentik_policies_event_matcher, authentik_policies_expiry, authentik_policies_expression, authentik_policies_geoip, authentik_policies_password, authentik_policies_reputation, authentik_providers_google_workspace, authentik_providers_ldap, authentik_providers_microsoft_entra, authentik_providers_oauth2, authentik_providers_proxy, authentik_providers_rac, authentik_providers_radius, authentik_providers_saml, authentik_providers_scim, authentik_rbac, authentik_sources_kerberos, authentik_sources_ldap, authentik_sources_oauth, authentik_sources_plex, authentik_sources_saml, authentik_sources_scim, authentik_stages_authenticator_duo, authentik_stages_authenticator_endpoint_gdtc, authentik_stages_authenticator_sms, authentik_stages_authenticator_static, authentik_stages_authenticator_totp, authentik_stages_authenticator_validate, authentik_stages_authenticator_webauthn, authentik_stages_captcha, authentik_stages_consent, authentik_stages_deny, authentik_stages_dummy, authentik_stages_email, authentik_stages_identification, authentik_stages_invitation, authentik_stages_password, authentik_stages_prompt, authentik_stages_redirect, authentik_stages_source, authentik_stages_user_delete, authentik_stages_user_login, authentik_stages_user_logout, authentik_stages_user_write, authentik_tenants, contenttypes, guardian, sessions
authentik           | Running migrations:
authentik           |   Applying contenttypes.0001_initial...
authentik           |  OK
authentik           |   Applying contenttypes.0002_remove_content_type_name...
authentik           |  OK
authentik           |   Applying auth.0001_initial...
authentik           |  OK
authentik           |   Applying auth.0002_alter_permission_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0003_alter_user_email_max_length...
authentik           |  OK
authentik           |   Applying auth.0004_alter_user_username_opts...
authentik           |  OK
authentik           |   Applying auth.0005_alter_user_last_login_null...
authentik           |  OK
authentik           |   Applying auth.0006_require_contenttypes_0002...
authentik           |  OK
authentik           |   Applying auth.0007_alter_validators_add_error_messages...
authentik           |  OK
authentik           |   Applying auth.0008_alter_user_username_max_length...
authentik           |  OK
authentik           |   Applying auth.0009_alter_user_last_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0010_alter_group_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0011_update_proxy_permissions...
authentik           |  OK
authentik           |   Applying auth.0012_alter_user_first_name_max_length...
authentik           |  OK
authentik           |   Applying authentik_policies.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies.0002_auto_20200528_1647...
authentik           |  OK
authentik           |   Applying authentik_flows.0001_squashed_0007_auto_20200703_2059...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0002_blueprintinstance_content...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0003_alter_blueprintinstance_name...
authentik           |  OK
authentik           |   Applying authentik_rbac.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_rbac.0002_systempermission...
authentik           |  OK
authentik           |   Applying authentik_rbac.0003_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_tenants.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_tenants.0002_tenant_default_token_duration_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0008_default_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0009_source_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0010_provider_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0011_flow_title...
authentik           |  OK
authentik           |   Applying authentik_flows.0012_auto_20200908_1542_squashed_0017_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_flows.0018_oob_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0019_alter_flow_background_squashed_0024_alter_flow_compatibility_mode...
authentik           |  OK
authentik           |   Applying authentik_crypto.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_core.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0001_squashed_0005_remove_samlprovider_processor_path...
authentik           |  OK
authentik           |   Applying authentik_core.0002_auto_20200523_1133_squashed_0011_provider_name_temp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0006_remove_samlprovider_name...
authentik           |  OK
authentik           |   Applying authentik_crypto.0002_create_self_signed_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0002_oauth2provider_sub_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0003_auto_20200916_2129...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0004_remove_oauth2provider_post_logout_redirect_uris...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0005_auto_20200920_1240...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0006_remove_oauth2provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0012_auto_20201003_1737_squashed_0016_auto_20201202_2234...
authentik           |  OK
authentik           |   Applying authentik_core.0017_managed...
authentik           |  OK
authentik           |   Applying authentik_core.0018_auto_20210330_1345_squashed_0028_alter_token_intent...
authentik           |  OK
authentik           |   Applying authentik_flows.0020_flowtoken...
authentik           |  OK
authentik           |   Applying authentik_flows.0021_auto_20211227_2103...
authentik           |  OK
authentik           |   Applying authentik_flows.0022_flow_layout...
authentik           |  OK
authentik           |   Applying authentik_flows.0023_flow_denied_action...
authentik           |  OK
authentik           |   Applying authentik_flows.0024_flow_authentication...
authentik           |  OK
authentik           |   Applying authentik_flows.0025_alter_flowstagebinding_evaluate_on_plan_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0019_application_group...
authentik           |  OK
authentik           |   Applying authentik_core.0020_application_open_in_new_tab...
authentik           |  OK
authentik           |   Applying authentik_core.0021_source_user_path_user_path...
authentik           |  OK
authentik           |   Applying authentik_core.0022_alter_group_parent...
authentik           |  OK
authentik           |   Applying authentik_core.0023_source_authentik_c_slug_ccb2e5_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0024_source_icon...
authentik           |  OK
authentik           |   Applying authentik_core.0025_alter_provider_authorization_flow...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0001_squashed_0006_rename_parent_group_scimprovider_filter_group...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0001_squashed_0005_ldapprovider_search_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0002_ldapprovider_bind_mode...
authentik           |  OK
authentik           |   Applying authentik_core.0026_alter_propertymapping_name_alter_provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0027_alter_user_uuid...
authentik           |  OK
authentik           |   Applying authentik_core.0028_provider_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0029_provider_backchannel_applications_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0030_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0031_alter_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0032_group_roles...
authentik           |  OK
authentik           |   Applying authentik_core.0033_alter_user_options...
authentik           |  OK
authentik           |   Applying authentik_core.0034_alter_authenticatedsession_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0035_alter_group_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0003_auto_20200908_1542...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0002_auto_20200920_1859...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0003_auto_20210222_1821...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0004_prompt_sub_text...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0005_alter_prompt_field_key...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0006_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0007_prompt_placeholder_expression...
authentik           |  OK
authentik           |   Applying authentik_crypto.0003_certificatekeypair_managed...
authentik           |  OK
authentik           |   Applying authentik_brands.0001_squashed_0005_tenant_web_certificate...
authentik           |  OK
authentik           |   Applying authentik_brands.0002_tenant_flow_user_settings...
authentik           |  OK
authentik           |   Applying authentik_brands.0003_tenant_attributes...
authentik           |  OK
authentik           |   Applying authentik_brands.0004_tenant_flow_device_code...
authentik           |  OK
authentik           |   Applying authentik_brands.0005_tenantuuid_to_branduuid...
authentik           |  OK
authentik           |   Applying authentik_brands.0006_brand_authentik_b_domain_b9b24a_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_brands.0007_brand_default_application...
authentik           |  OK
authentik           |   Applying authentik_policies.0004_policy_execution_logging...
authentik           |  OK
authentik           |   Applying authentik_policies.0005_binding_group...
authentik           |  OK
authentik           |   Applying authentik_policies.0006_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_policies.0007_policybindingmodel_policy_engine_mode...
authentik           |  OK
authentik           |   Applying authentik_policies.0008_policybinding_authentik_p_policy__534e15_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0009_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0010_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0011_policybinding_failure_result_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0026_alter_flow_options...
authentik           |  OK
authentik           |   Applying authentik_flows.0027_auto_20231028_1424...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0001_squashed_0012_auto_20210812_1703...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0002_auto_20211203_0900...
authentik           |  OK
authentik           |   Applying authentik_crypto.0004_alter_certificatekeypair_name...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0003_ldapsource_client_certificate_ldapsource_sni_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0004_ldapsource_password_login_update_internal_password...
authentik           |  OK
authentik           |   Applying authentik_core.0036_source_group_property_mappings_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0005_remove_ldappropertymapping_object_field_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0037_remove_source_property_mappings...
authentik           |  OK
authentik           |   Applying authentik_core.0038_source_authentik_c_enabled_d72365_idx...
authentik           |  OK
authentik           |   Applying authentik_core.0039_source_group_matching_mode_alter_group_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0040_provider_invalidation_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0041_applicationentitlement...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0002_rename_users_license_internal_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0003_remove_licenseusage_within_limits_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0001_squashed_0018_alter_eventmatcherpolicy_action...
authentik           |  OK
authentik           |   Applying authentik_events.0001_squashed_0019_alter_notificationtransport_webhook_url...
authentik           |  OK
authentik           |   Applying authentik_events.0002_alter_notificationtransport_mode...
authentik           |  OK
authentik           |   Applying authentik_events.0003_rename_tenant_event_brand...
authentik           |  OK
authentik           |   Applying authentik_events.0004_systemtask_squashed_0005_remove_systemtask_finish_timestamp_and_more...
authentik           |  OK
authentik           |   Applying authentik_events.0006_alter_systemtask_expires...
authentik           |  OK
authentik           |   Applying authentik_events.0007_event_authentik_e_action_9a9dd9_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0001_squashed_0017_outpost_managed...
authentik           |  OK
authentik           |   Applying authentik_outposts.0018_kubernetesserviceconnection_verify_ssl...
authentik           |  OK
authentik           |   Applying authentik_outposts.0019_alter_outpost_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0020_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_outposts.0021_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0002_dummypolicy_authentik_p_policy__648f9b_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0019_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0020_eventmatcherpolicy_authentik_p_policy__e605cf_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0021_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0022_eventmatcherpolicy_model...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0023_alter_eventmatcherpolicy_action_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0002_passwordexpirypolicy_authentik_p_policy__cf73a7_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0002_auto_20200926_1156...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0003_auto_20201203_1223...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0004_expressionpolicy_authentik_p_policy__fb6feb_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_geoip.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0002_passwordpolicy_password_field...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0003_passwordpolicy_amount_digits...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0004_passwordpolicy_authentik_p_policy__855e80_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0005_passwordpolicy_check_have_i_been_pwned_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0002_auto_20210529_2046...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0003_reputation_delete_ipreputation_delete_userreputation...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0004_reputationpolicy_authentik_p_policy__8f0d70_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0005_reputation_expires_reputation_expiring...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0006_reputation_ip_asn_data...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0007_reputation_authentik_p_identif_9434d7_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0001_squashed_0002_alter_googleworkspaceprovidergroup_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0003_googleworkspaceprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying guardian.0001_initial...
authentik           |  OK
authentik           |   Applying guardian.0002_generic_permissions_index...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0003_ldapprovider_mfa_support_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0004_alter_ldapprovider_options_and_more...
authentik           | Adding content type 'authentik_providers_ldap | ldapprovider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can add LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can change LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can delete LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can view LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Search full LDAP directory'
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0002_microsoftentraprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0002_auto_20200520_1108...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0003_auto_20210416_0726...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0004_auto_20210417_1900...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0005_update_provider_type_names...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0006_oauthsource_additional_scopes...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0007_oauthsource_oidc_jwks_oauthsource_oidc_jwks_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0007_auto_20201016_1107_squashed_0017_alter_oauth2provider_token_validity...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0008_rename_rsa_key_oauth2provider_signing_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0009_oauth2provider_verification_keys_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0010_alter_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0011_oauth2provider_jwks_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0012_remove_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0013_devicetoken...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0014_alter_refreshtoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0015_accesstoken_auth_time_authorizationcode_auth_time_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0016_alter_refreshtoken_token...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0017_accesstoken_session_id_authorizationcode_session_id_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0018_alter_accesstoken_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0019_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0020_remove_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0021_oauth2provider_encryption_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0022_remove_accesstoken_session_id_and_more...
authentik           | 
authentik           | 
authentik           | Fetching session keys, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to Authorization Code, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Access Token, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Refresh Token, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0023_alter_accesstoken_refreshtoken_use_hash_index...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0024_remove_oauth2provider_redirect_uris_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0025_rename_jwks_sources_oauth2provider_jwt_federation_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0026_alter_accesstoken_session_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0001_squashed_0014_proxy_v2...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0015_proxyprovider_receive_header_auth...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0001_squashed_0003_alter_connectiontoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0004_alter_connectiontoken_expires...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0005_alter_racpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0002_radiusprovider_mfa_support...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0003_radiusproviderpropertymapping...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0004_alter_radiusproviderpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0007_samlprovider_verification_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0008_auto_20201112_1036...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0009_auto_20201112_2016...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0010_auto_20201230_2112...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0011_samlprovider_name_id_mapping...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0012_managed...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0013_samlprovider_default_relay_state...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0014_alter_samlprovider_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0015_alter_samlpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0016_samlprovider_encryption_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0007_scimgroup_scim_id_scimuser_scim_id_and_more...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM users, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM groups, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0008_rename_scimgroup_scimprovidergroup_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0009_alter_scimmapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0010_scimprovider_verify_certificates...
authentik           |  OK
authentik           |   Applying authentik_rbac.0004_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0002_kerberossource_kadmin_type...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0006_rename_ldappropertymapping_ldapsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0008_groupoauthsourceconnection_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0002_auto_20210505_1717...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0003_alter_plexsource_plex_token...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0004_groupplexsourceconnection_plexsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0001_squashed_0009_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0010_samlsource_pre_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0011_auto_20210324_0736...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0012_usersamlsourceconnection...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0013_samlsource_verification_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0014_alter_samlsource_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0015_groupsamlsourceconnection_samlsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0016_samlsource_encryption_kp...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0017_fix_x509subjectname...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0002_scimsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0002_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0003_duodevice_last_t...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0004_authenticatorduostage_admin_integration_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0005_authenticatorduostage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0006_duodevice_created_duodevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_endpoint_gdtc.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0001_squashed_0004_auto_20211014_0936...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0002_alter_authenticatorsmsstage_from_number...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0003_smsdevice_last_used_on...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0004_authenticatorsmsstage_verify_only_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0005_authenticatorsmsstage_mapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0006_authenticatorsmsstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0007_smsdevice_created_smsdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0002_otpstaticstage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0003_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0004_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0005_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0006_authenticatorstaticstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0007_authenticatorstaticstage_token_length_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0009_throttling...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0010_staticdevice_created_staticdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0002_auto_20200701_1900...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0003_otptimestage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0004_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0005_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0006_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0007_authenticatortotpstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0009_auto_20190420_0723...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0010_alter_totpdevice_key...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0011_totpdevice_created_totpdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0001_squashed_0011_webauthndevice_aaguid...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0002_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0003_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0004_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0005_authenticatorvalidatestage_configuration_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0006_auto_20210301_1757...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0007_auto_20210403_0927...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0008_alter_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0009_default_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0010_remove_authenticatorvalidatestage_configuration_stage_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0011_authenticatorvalidatestage_last_auth_threshold...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0012_authenticatorvalidatestage_webauthn_user_verification...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0013_authenticatorvalidatestage_webauthn_allowed_device_types...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0012_webauthndevice_created_webauthndevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0002_captchastage_api_url_captchastage_js_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0003_captchastage_error_on_invalid_score_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0004_captchastage_interactive...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0002_auto_20200720_0941...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0003_auto_20200924_1403...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0004_alter_userconsent_unique_together_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0005_alter_consentstage_mode...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0006_alter_userconsent_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0002_denystage_deny_message...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0002_dummystage_throw_error...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0002_emailstage_use_global_settings...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0003_auto_20210404_1054...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0004_emailstage_activate_user_on_success...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0002_passwordstage_change_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0003_passwordstage_failed_attempts_before_cancel...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0004_auto_20200925_1057...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0005_auto_20210402_2221...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0002_auto_20200530_2204_squashed_0013_identificationstage_passwordless_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0014_identificationstage_pretend...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0015_identificationstage_captcha_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0001_squashed_0006_invitation_name...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0007_invitation_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0008_alter_invitation_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0006_passwordchange_rename...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0007_app_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0008_replace_inbuilt...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0009_passwordstage_allow_show_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0010_alter_passwordstage_backends...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0008_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0009_prompt_name...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0010_alter_prompt_placeholder_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0011_prompt_initial_value_prompt_initial_value_expression_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_redirect.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_source.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_delete.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0002_userloginstage_session_duration...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0003_session_duration_delta...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0004_userloginstage_terminate_other_sessions...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0005_userloginstage_remember_me_offset...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0006_userloginstage_geoip_binding_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_logout.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0002_auto_20200918_1653...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0003_userwritestage_create_users_as_inactive...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0004_userwritestage_create_users_group...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0005_userwritestage_user_path_template...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0006_userwritestage_can_create_users...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0007_remove_userwritestage_can_create_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0008_userwritestage_user_type...
authentik           |  OK
authentik           |   Applying authentik_tenants.0003_alter_tenant_default_token_duration...
authentik           |  OK
authentik           |   Applying authentik_tenants.0004_tenant_impersonation_require_reason...
authentik           |  OK
authentik           |   Applying sessions.0001_initial...
authentik           |  OK
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:00Z"}
authentik           | === Starting migration
authentik           | Operations to perform:
authentik           |   Apply all migrations: auth, authentik_blueprints, authentik_brands, authentik_core, authentik_crypto, authentik_enterprise, authentik_events, authentik_flows, authentik_outposts, authentik_policies, authentik_policies_dummy, authentik_policies_event_matcher, authentik_policies_expiry, authentik_policies_expression, authentik_policies_geoip, authentik_policies_password, authentik_policies_reputation, authentik_providers_google_workspace, authentik_providers_ldap, authentik_providers_microsoft_entra, authentik_providers_oauth2, authentik_providers_proxy, authentik_providers_rac, authentik_providers_radius, authentik_providers_saml, authentik_providers_scim, authentik_rbac, authentik_sources_kerberos, authentik_sources_ldap, authentik_sources_oauth, authentik_sources_plex, authentik_sources_saml, authentik_sources_scim, authentik_stages_authenticator_duo, authentik_stages_authenticator_endpoint_gdtc, authentik_stages_authenticator_sms, authentik_stages_authenticator_static, authentik_stages_authenticator_totp, authentik_stages_authenticator_validate, authentik_stages_authenticator_webauthn, authentik_stages_captcha, authentik_stages_consent, authentik_stages_deny, authentik_stages_dummy, authentik_stages_email, authentik_stages_identification, authentik_stages_invitation, authentik_stages_password, authentik_stages_prompt, authentik_stages_redirect, authentik_stages_source, authentik_stages_user_delete, authentik_stages_user_login, authentik_stages_user_logout, authentik_stages_user_write, authentik_tenants, contenttypes, guardian, sessions
authentik           | Running migrations:
authentik           |   Applying contenttypes.0001_initial...
authentik           |  OK
authentik           |   Applying contenttypes.0002_remove_content_type_name...
authentik           |  OK
authentik           |   Applying auth.0001_initial...
authentik           |  OK
authentik           |   Applying auth.0002_alter_permission_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0003_alter_user_email_max_length...
authentik           |  OK
authentik           |   Applying auth.0004_alter_user_username_opts...
authentik           |  OK
authentik           |   Applying auth.0005_alter_user_last_login_null...
authentik           |  OK
authentik           |   Applying auth.0006_require_contenttypes_0002...
authentik           |  OK
authentik           |   Applying auth.0007_alter_validators_add_error_messages...
authentik           |  OK
authentik           |   Applying auth.0008_alter_user_username_max_length...
authentik           |  OK
authentik           |   Applying auth.0009_alter_user_last_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0010_alter_group_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0011_update_proxy_permissions...
authentik           |  OK
authentik           |   Applying auth.0012_alter_user_first_name_max_length...
authentik           |  OK
authentik           |   Applying authentik_policies.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies.0002_auto_20200528_1647...
authentik           |  OK
authentik           |   Applying authentik_flows.0001_squashed_0007_auto_20200703_2059...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0001_initial...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_blueprints.0002_blueprintinstance_content...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0003_alter_blueprintinstance_name...
authentik           |  OK
authentik           |   Applying authentik_rbac.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_rbac.0002_systempermission...
authentik           |  OK
authentik           |   Applying authentik_rbac.0003_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_tenants.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_tenants.0002_tenant_default_token_duration_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0008_default_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0009_source_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0010_provider_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0011_flow_title...
authentik           |  OK
authentik           |   Applying authentik_flows.0012_auto_20200908_1542_squashed_0017_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_flows.0018_oob_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0019_alter_flow_background_squashed_0024_alter_flow_compatibility_mode...
authentik           |  OK
authentik           |   Applying authentik_crypto.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_core.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0001_squashed_0005_remove_samlprovider_processor_path...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0002_auto_20200523_1133_squashed_0011_provider_name_temp...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0006_remove_samlprovider_name...
authentik           |  OK
authentik           |   Applying authentik_crypto.0002_create_self_signed_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0002_oauth2provider_sub_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0003_auto_20200916_2129...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0004_remove_oauth2provider_post_logout_redirect_uris...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0005_auto_20200920_1240...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0006_remove_oauth2provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0012_auto_20201003_1737_squashed_0016_auto_20201202_2234...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0017_managed...
authentik           |  OK
authentik           |   Applying authentik_core.0018_auto_20210330_1345_squashed_0028_alter_token_intent...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_flows.0020_flowtoken...
authentik           |  OK
authentik           |   Applying authentik_flows.0021_auto_20211227_2103...
authentik           |  OK
authentik           |   Applying authentik_flows.0022_flow_layout...
authentik           |  OK
authentik           |   Applying authentik_flows.0023_flow_denied_action...
authentik           |  OK
authentik           |   Applying authentik_flows.0024_flow_authentication...
authentik           |  OK
authentik           |   Applying authentik_flows.0025_alter_flowstagebinding_evaluate_on_plan_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0019_application_group...
authentik           |  OK
authentik           |   Applying authentik_core.0020_application_open_in_new_tab...
authentik           |  OK
authentik           |   Applying authentik_core.0021_source_user_path_user_path...
authentik           |  OK
authentik           |   Applying authentik_core.0022_alter_group_parent...
authentik           |  OK
authentik           |   Applying authentik_core.0023_source_authentik_c_slug_ccb2e5_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0024_source_icon...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0025_alter_provider_authorization_flow...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0001_squashed_0006_rename_parent_group_scimprovider_filter_group...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:03Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0001_squashed_0005_ldapprovider_search_mode...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:03Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0002_ldapprovider_bind_mode...
authentik           |  OK
authentik           |   Applying authentik_core.0026_alter_propertymapping_name_alter_provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0027_alter_user_uuid...
authentik           |  OK
authentik           |   Applying authentik_core.0028_provider_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0029_provider_backchannel_applications_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0030_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0031_alter_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0032_group_roles...
authentik           |  OK
authentik           |   Applying authentik_core.0033_alter_user_options...
authentik           |  OK
authentik           |   Applying authentik_core.0034_alter_authenticatedsession_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0035_alter_group_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0003_auto_20200908_1542...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0002_auto_20200920_1859...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0003_auto_20210222_1821...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0004_prompt_sub_text...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0005_alter_prompt_field_key...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0006_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0007_prompt_placeholder_expression...
authentik           |  OK
authentik           |   Applying authentik_crypto.0003_certificatekeypair_managed...
authentik           |  OK
authentik           |   Applying authentik_brands.0001_squashed_0005_tenant_web_certificate...
authentik           |  OK
authentik           |   Applying authentik_brands.0002_tenant_flow_user_settings...
authentik           |  OK
authentik           |   Applying authentik_brands.0003_tenant_attributes...
authentik           |  OK
authentik           |   Applying authentik_brands.0004_tenant_flow_device_code...
authentik           |  OK
authentik           |   Applying authentik_brands.0005_tenantuuid_to_branduuid...
authentik           |  OK
authentik           |   Applying authentik_brands.0006_brand_authentik_b_domain_b9b24a_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_brands.0007_brand_default_application...
authentik           |  OK
authentik           |   Applying authentik_policies.0004_policy_execution_logging...
authentik           |  OK
authentik           |   Applying authentik_policies.0005_binding_group...
authentik           |  OK
authentik           |   Applying authentik_policies.0006_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_policies.0007_policybindingmodel_policy_engine_mode...
authentik           |  OK
authentik           |   Applying authentik_policies.0008_policybinding_authentik_p_policy__534e15_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0009_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0010_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0011_policybinding_failure_result_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0026_alter_flow_options...
authentik           |  OK
authentik           |   Applying authentik_flows.0027_auto_20231028_1424...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0001_squashed_0012_auto_20210812_1703...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0002_auto_20211203_0900...
authentik           |  OK
authentik           |   Applying authentik_crypto.0004_alter_certificatekeypair_name...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0003_ldapsource_client_certificate_ldapsource_sni_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0004_ldapsource_password_login_update_internal_password...
authentik           |  OK
authentik           |   Applying authentik_core.0036_source_group_property_mappings_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0005_remove_ldappropertymapping_object_field_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0037_remove_source_property_mappings...
authentik           |  OK
authentik           |   Applying authentik_core.0038_source_authentik_c_enabled_d72365_idx...
authentik           |  OK
authentik           |   Applying authentik_core.0039_source_group_matching_mode_alter_group_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0040_provider_invalidation_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0041_applicationentitlement...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0002_rename_users_license_internal_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0003_remove_licenseusage_within_limits_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0001_squashed_0018_alter_eventmatcherpolicy_action...
authentik           |  OK
authentik           |   Applying authentik_events.0001_squashed_0019_alter_notificationtransport_webhook_url...
authentik           |  OK
authentik           |   Applying authentik_events.0002_alter_notificationtransport_mode...
authentik           |  OK
authentik           |   Applying authentik_events.0003_rename_tenant_event_brand...
authentik           |  OK
authentik           |   Applying authentik_events.0004_systemtask_squashed_0005_remove_systemtask_finish_timestamp_and_more...
authentik           |  OK
authentik           |   Applying authentik_events.0006_alter_systemtask_expires...
authentik           |  OK
authentik           |   Applying authentik_events.0007_event_authentik_e_action_9a9dd9_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0001_squashed_0017_outpost_managed...
authentik           |  OK
authentik           |   Applying authentik_outposts.0018_kubernetesserviceconnection_verify_ssl...
authentik           |  OK
authentik           |   Applying authentik_outposts.0019_alter_outpost_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0020_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_outposts.0021_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0002_dummypolicy_authentik_p_policy__648f9b_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0019_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0020_eventmatcherpolicy_authentik_p_policy__e605cf_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0021_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0022_eventmatcherpolicy_model...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0023_alter_eventmatcherpolicy_action_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0002_passwordexpirypolicy_authentik_p_policy__cf73a7_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0002_auto_20200926_1156...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0003_auto_20201203_1223...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0004_expressionpolicy_authentik_p_policy__fb6feb_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_geoip.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0002_passwordpolicy_password_field...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0003_passwordpolicy_amount_digits...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0004_passwordpolicy_authentik_p_policy__855e80_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0005_passwordpolicy_check_have_i_been_pwned_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0002_auto_20210529_2046...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0003_reputation_delete_ipreputation_delete_userreputation...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0004_reputationpolicy_authentik_p_policy__8f0d70_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0005_reputation_expires_reputation_expiring...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0006_reputation_ip_asn_data...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0007_reputation_authentik_p_identif_9434d7_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0001_squashed_0002_alter_googleworkspaceprovidergroup_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0003_googleworkspaceprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying guardian.0001_initial...
authentik           |  OK
authentik           |   Applying guardian.0002_generic_permissions_index...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0003_ldapprovider_mfa_support_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0004_alter_ldapprovider_options_and_more...
authentik           | Adding content type 'authentik_providers_ldap | ldapprovider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can add LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can change LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can delete LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can view LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Search full LDAP directory'
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0002_microsoftentraprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0002_auto_20200520_1108...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0003_auto_20210416_0726...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0004_auto_20210417_1900...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0005_update_provider_type_names...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0006_oauthsource_additional_scopes...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0007_oauthsource_oidc_jwks_oauthsource_oidc_jwks_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0007_auto_20201016_1107_squashed_0017_alter_oauth2provider_token_validity...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0008_rename_rsa_key_oauth2provider_signing_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0009_oauth2provider_verification_keys_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0010_alter_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0011_oauth2provider_jwks_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0012_remove_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0013_devicetoken...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0014_alter_refreshtoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0015_accesstoken_auth_time_authorizationcode_auth_time_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0016_alter_refreshtoken_token...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0017_accesstoken_session_id_authorizationcode_session_id_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0018_alter_accesstoken_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0019_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0020_remove_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0021_oauth2provider_encryption_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0022_remove_accesstoken_session_id_and_more...
authentik           | 
authentik           | 
authentik           | Fetching session keys, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to Authorization Code, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Access Token, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Refresh Token, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0023_alter_accesstoken_refreshtoken_use_hash_index...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0024_remove_oauth2provider_redirect_uris_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0025_rename_jwks_sources_oauth2provider_jwt_federation_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0026_alter_accesstoken_session_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0001_squashed_0014_proxy_v2...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0015_proxyprovider_receive_header_auth...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0001_squashed_0003_alter_connectiontoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0004_alter_connectiontoken_expires...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0005_alter_racpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0002_radiusprovider_mfa_support...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0003_radiusproviderpropertymapping...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0004_alter_radiusproviderpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0007_samlprovider_verification_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0008_auto_20201112_1036...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0009_auto_20201112_2016...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0010_auto_20201230_2112...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0011_samlprovider_name_id_mapping...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0012_managed...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0013_samlprovider_default_relay_state...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0014_alter_samlprovider_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0015_alter_samlpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0016_samlprovider_encryption_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0007_scimgroup_scim_id_scimuser_scim_id_and_more...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM users, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM groups, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0008_rename_scimgroup_scimprovidergroup_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0009_alter_scimmapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0010_scimprovider_verify_certificates...
authentik           |  OK
authentik           |   Applying authentik_rbac.0004_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0002_kerberossource_kadmin_type...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0006_rename_ldappropertymapping_ldapsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0008_groupoauthsourceconnection_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0002_auto_20210505_1717...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0003_alter_plexsource_plex_token...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0004_groupplexsourceconnection_plexsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0001_squashed_0009_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0010_samlsource_pre_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0011_auto_20210324_0736...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0012_usersamlsourceconnection...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0013_samlsource_verification_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0014_alter_samlsource_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0015_groupsamlsourceconnection_samlsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0016_samlsource_encryption_kp...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0017_fix_x509subjectname...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0002_scimsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0002_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0003_duodevice_last_t...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0004_authenticatorduostage_admin_integration_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0005_authenticatorduostage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0006_duodevice_created_duodevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_endpoint_gdtc.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0001_squashed_0004_auto_20211014_0936...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0002_alter_authenticatorsmsstage_from_number...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0003_smsdevice_last_used_on...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0004_authenticatorsmsstage_verify_only_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0005_authenticatorsmsstage_mapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0006_authenticatorsmsstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0007_smsdevice_created_smsdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0002_otpstaticstage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0003_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0004_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0005_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0006_authenticatorstaticstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0007_authenticatorstaticstage_token_length_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0009_throttling...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0010_staticdevice_created_staticdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0002_auto_20200701_1900...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0003_otptimestage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0004_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0005_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0006_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0007_authenticatortotpstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0009_auto_20190420_0723...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0010_alter_totpdevice_key...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0011_totpdevice_created_totpdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0001_squashed_0011_webauthndevice_aaguid...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0002_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0003_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0004_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0005_authenticatorvalidatestage_configuration_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0006_auto_20210301_1757...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0007_auto_20210403_0927...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0008_alter_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0009_default_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0010_remove_authenticatorvalidatestage_configuration_stage_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0011_authenticatorvalidatestage_last_auth_threshold...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0012_authenticatorvalidatestage_webauthn_user_verification...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0013_authenticatorvalidatestage_webauthn_allowed_device_types...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0012_webauthndevice_created_webauthndevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0002_captchastage_api_url_captchastage_js_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0003_captchastage_error_on_invalid_score_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0004_captchastage_interactive...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0002_auto_20200720_0941...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0003_auto_20200924_1403...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0004_alter_userconsent_unique_together_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0005_alter_consentstage_mode...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0006_alter_userconsent_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0002_denystage_deny_message...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0002_dummystage_throw_error...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0002_emailstage_use_global_settings...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0003_auto_20210404_1054...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0004_emailstage_activate_user_on_success...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0002_passwordstage_change_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0003_passwordstage_failed_attempts_before_cancel...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0004_auto_20200925_1057...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0005_auto_20210402_2221...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0002_auto_20200530_2204_squashed_0013_identificationstage_passwordless_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0014_identificationstage_pretend...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0015_identificationstage_captcha_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0001_squashed_0006_invitation_name...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0007_invitation_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0008_alter_invitation_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0006_passwordchange_rename...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0007_app_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0008_replace_inbuilt...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0009_passwordstage_allow_show_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0010_alter_passwordstage_backends...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0008_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0009_prompt_name...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0010_alter_prompt_placeholder_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0011_prompt_initial_value_prompt_initial_value_expression_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_redirect.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_source.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_delete.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0002_userloginstage_session_duration...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0003_session_duration_delta...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0004_userloginstage_terminate_other_sessions...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0005_userloginstage_remember_me_offset...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0006_userloginstage_geoip_binding_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_logout.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0002_auto_20200918_1653...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0003_userwritestage_create_users_as_inactive...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0004_userwritestage_create_users_group...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0005_userwritestage_user_path_template...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0006_userwritestage_can_create_users...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0007_remove_userwritestage_can_create_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0008_userwritestage_user_type...
authentik           |  OK
authentik           |   Applying authentik_tenants.0003_alter_tenant_default_token_duration...
authentik           |  OK
authentik           |   Applying authentik_tenants.0004_tenant_impersonation_require_reason...
authentik           |  OK
authentik           |   Applying sessions.0001_initial...
authentik           |  OK
authentik           | System check identified no issues (4 silenced).
authentik           | {"domain_url": null, "event": "releasing database lock", "level": "info", "logger": "lifecycle.migrate", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:06:21.437837"}
authentik           | {"event": "Starting gunicorn 23.0.0", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5352387}
authentik           | {"event": "Listening at: unix:/dev/shm/authentik-core.sock (18)", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5357366}
authentik           | {"event": "Using worker: lifecycle.worker.DjangoUvicornWorker", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5357742}
authentik           | {"event": "Booting worker with pid: 76", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5404963}
authentik           | {"event": "Booting worker with pid: 77", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5705762}
authentik           | {"auth_via": "unauthenticated", "domain_url": "localhost", "event": "/-/health/live/", "host": "localhost:8000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "255.255.255.255", "request_id": "91031223a9ad4ae3a373324ae2bc88c6", "runtime": 13, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:22.318272", "user": "", "user_agent": "goauthentik.io/router/healthcheck"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "b4371d9d35ea411799e73e79af2eae8f", "runtime": 13, "schema_name": "public", "scheme": "http", "status": 403, "timestamp": "2025-01-18T05:06:22.341350", "user": "", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"error":"403 Forbidden","event":"Failed to fetch outpost configuration, retrying in 3 seconds","level":"error","logger":"authentik.outpost.ak-api-controller","timestamp":"2025-01-18T05:06:22Z"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "3b118f08d1fc49baa1c7b5d04a73f752", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:23.819775"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "4dd64da42cfd42ae8fff00933b364333", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.242577"}
authentik           | {"domain_url": null, "event": "New outpost saved, ensuring initial token and user are created", "level": "info", "logger": "authentik.outposts.signals", "pid": 76, "schema_name": "public", "timestamp": "2025-01-18T05:06:24.249293"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "6c10715b576343728d23d2b242a32ec5", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.278844"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "9449bfe48cd04c8f94aff57cf165ef79", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.285232"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "b23c1366f7b440d9a919289fa7e2bdff", "task_name": "authentik.blueprints.v1.tasks.blueprints_discovery", "timestamp": "2025-01-18T05:06:24.291908"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "9dc85e56ae444382954d83ad253c5d9f", "task_name": "authentik.blueprints.v1.tasks.clear_failed_blueprints", "timestamp": "2025-01-18T05:06:24.292629"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "b1812b6f152049ce82d3964f6426eea1", "task_name": "authentik.core.tasks.clean_expired_models", "timestamp": "2025-01-18T05:06:24.334496"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "ab90a331e3f04e02a7566e45e5bd6730", "task_name": "authentik.core.tasks.clean_temporary_users", "timestamp": "2025-01-18T05:06:24.335986"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "6ae2039eaacc4606b6b50c3e7b5cf174", "task_name": "authentik.enterprise.tasks.enterprise_update_usage", "timestamp": "2025-01-18T05:06:24.337342"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "e58ca1ecfd8d4fbe8e9776a88264045d", "task_name": "authentik.stages.authenticator_webauthn.tasks.webauthn_mds_import", "timestamp": "2025-01-18T05:06:24.338882"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "cc4a63158f9840448512c5c55f0a407f", "task_name": "authentik.crypto.tasks.certificate_discovery", "timestamp": "2025-01-18T05:06:24.340275"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "ddaae92ba8d24bce834c8a2c8ea75564", "task_name": "authentik.admin.tasks.update_latest_version", "timestamp": "2025-01-18T05:06:24.341751"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "68ba9ceef5594ab38dfd107b12f6753d", "task_name": "authentik.blueprints.v1.tasks.blueprints_discovery", "timestamp": "2025-01-18T05:06:24.343643"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "40621db519684051a9dc020c3f0ab15f", "task_name": "authentik.outposts.tasks.outpost_service_connection_monitor", "timestamp": "2025-01-18T05:06:24.345088"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "d81726eb3af047118956134444a80ea8", "task_name": "authentik.outposts.tasks.outpost_token_ensurer", "timestamp": "2025-01-18T05:06:24.346387"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "54823535f4594390bc3a2c47daf018cd", "task_name": "authentik.events.tasks.notification_cleanup", "timestamp": "2025-01-18T05:06:24.348956"}
authentik           | {"domain_url": null, "event": "authentik Core Worker finished starting", "level": "info", "logger": "authentik.root.signals", "pid": 76, "schema_name": "public", "timestamp": "2025-01-18T05:06:24.349151", "took_s": 2.802407}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "8ef40f68c0784a25b87ed842f46f22cd", "runtime": 32, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.384952", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/root/config/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "1fab68f6f78743b1af4d764ef06e93a2", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.409164", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"domain_url": null, "event": "/ws/outpost/1a2812d4-f65c-4197-881d-0bb066054b86/", "level": "info", "logger": "authentik.asgi", "pid": 77, "remote": "127.0.0.1", "schema_name": "public", "scheme": "ws", "timestamp": "2025-01-18T05:06:25.411078", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"Successfully connected websocket","level":"info","logger":"authentik.outpost.ak-ws","outpost":"1a2812d4-f65c-4197-881d-0bb066054b86","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"event":"Starting Brand TLS Checker","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"event":"updating brand certificates","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/core/brands/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "4b7afe743cd24ec2a452c92d4a075bea", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.595200", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "5ae87c736cec491d85b6121f766cf59f", "runtime": 26, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.730112", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"Starting authentik outpost","hash":"tagged","level":"info","logger":"authentik.outpost","timestamp":"2025-01-18T05:06:25Z","version":"2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/proxy/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "86693c5d7dce47a29111b3f52003b0a1", "runtime": 25, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.765354", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"updating brand certificates","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/core/brands/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "cfd98b49dc7e4dbe9f8df5e9d0da6881", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.789866", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}

#### ChatGPT:
<time datetime="2025-01-18T05:07:06.803Z" title="1/18/2025, 2:07:06 PM">14:07</time>

**Great news**: Your logs show Authentik has **successfully installed**, applied migrations, and is now **running** in “server” mode on port 9000, with Traefik proxying at `login.apsjado.com`. Here’s a quick explanation of what you see in the logs and **what to do next**:

---

## 1. Postgres & Redis Initialization

- **Postgres**: It runs an initialization sequence (locale warnings, creating subdirectories, setting up the `authentik` DB), then logs `database system is ready to accept connections`.
- **Redis**: Starts quickly in standalone mode, ready on port 6379.
- **Authentik** tries connecting to both but occasionally sees “connection refused” while Postgres is still initializing. That’s normal—Authentik retries until Postgres is up.

**All good**—no errors or permission problems here.

---

## 2. Authentik “Bootstrap” & Migrations

You see lines like:

```
"Finished authentik bootstrap"
"Migration needs to be applied" 
"Migration finished applying"
…
Applying migrations:
auth, contenttypes, authentik_core, authentik_flows, etc.
```

This means:

1. **Authentik** detected a fresh install: it’s creating or updating the database schema, installing default flows, etc.
2. **BOOTSTRAP\_ADMIN\_USERNAME** and **BOOTSTRAP\_ADMIN\_PASSWORD** environment variables are recognized. If no user existed, Authentik will create the “admin” account with “password” (unless you changed it).

Towards the end, you see:

```
System check identified no issues (4 silenced).
Starting gunicorn 23.0.0
Listening at: unix:/dev/shm/authentik-core.sock
Booting worker…
```

That’s Authentik’s internal web server (Gunicorn + Django). It’s fully up and serving the web interface on port 9000.

---

## 3. `Not Found` / “Page not Found” or “403 Forbidden” in the Logs

- You see a few lines:
  ```
  {"event":"failed to proxy to backend","error":"authentik starting","level":"warning"...}
  ```
  This typically happens **during startup** if Traefik or the internal router tries to contact an endpoint that isn’t ready yet. Once Authentik fully boots, these messages disappear. It’s just a temporary warning.
- The `403 Forbidden` is from Authentik’s own outpost logic, meaning the internal “outpost” (bundled in the new container) tries to connect before it’s fully configured. It resolves itself when Authentik finishes booting and sets up an internal token.
- By the end of the logs, Authentik is happily running and responding to requests with 200 or 403 when appropriate.

**No problem**—these warnings are common on first startup or reboots. They go away once everything is fully initialized.

---

## 4. Checking if Authentik is Working

Assuming your DNS record **`login.apsjado.com`** points to the server’s IP:

1. In a browser, **go to** `https://login.apsjado.com`.
2. If Traefik obtains a Let’s Encrypt certificate, you should see a valid SSL certificate (no browser warning).
3. Authentik’s **login page** or “admin creation” page should appear.
4. **Try** the bootstrap admin credentials:
   - **Username**: `admin`
   - **Password**: `password` (unless you changed `AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD`)

If successful, you’ll land in Authentik’s UI. Go to **`/if/admin/`** (or click “Admin” in the UI) to manage flows, brand, etc.

### If you see a 404 or “Not Found”

- You might need to create/adjust the **Default Authentication Flow** in *Admin > Administration > Core > Tenants* or *System > Brands*.
- Check that the flow slug matches a real flow (e.g. `auth-standalone`).
- Or see if your brand references a missing `default/authentication` flow.

### If you get a Traefik “404 Not Found”

- Make sure the **labels** for Authentik in `docker-compose.yml` have `traefik.http.routers.authentik.rule=Host(\`login.apsjado.com\`)\`.
- Confirm your DNS A-record is set to your server’s public IP.

---

## 5. Next Steps

1. **Log into Authentik** at `https://login.apsjado.com` using admin credentials.
2. **Set Up** your brand, flows, and tenants. For example, give it a custom name/logo, check “Default Authentication Flow,” etc.
3. **Secure** the admin user:
   - Change the default `password`.
   - Optionally set up 2FA or email verification.
4. **Integrate Services**: Start protecting internal apps (Nextcloud, Home Assistant, etc.) with Authentik SSO.

You can also tweak your **Traefik** config to secure the dashboard, or add more subdomains if you want multiple services behind it.

---

### TL;DR

- Your logs show a **successful** fresh install of Authentik with no fatal errors.
- The big block of migrations is normal—Authentik created its entire schema and default flows.
- The container is now **listening** on port 9000, with Traefik proxying at `login.apsjado.com`.
- Check your DNS & certificates, then **browse** to `https://login.apsjado.com` to confirm everything is working.

That’s it! You’re ready to log in as **“admin”** and configure your brand-new Authentik setup. Enjoy your SSO solution!


#### You:
<time datetime="2025-01-18T05:08:14.583Z" title="1/18/2025, 2:08:14 PM">14:08</time>

https://login.apsjado.com/flows/-/default/authentication/?next=/

If you see a 404 or “Not Found”

how do i do this? i cannot access any page with this ment

#### ChatGPT:
<time datetime="2025-01-18T05:08:27.165Z" title="1/18/2025, 2:08:27 PM">14:08</time>

If Authentik is redirecting you to

```
https://login.apsjado.com/flows/-/default/authentication/?next=/
```

and you get a **404 “Not Found”**, it means Authentik is trying to use a flow slug called `default/authentication` but **that exact flow does not exist** in your configuration. Typically, the standard login flow is named something like `auth-standalone` or `auth-embedded`.

Below are **two main ways** to fix it:

---

## 1. Point Your Brand/Tenant to a Real Flow Instead of `default/authentication`

If you can reach the **Admin interface** at all (e.g., `https://login.apsjado.com/if/admin/`), you can:

1. **Log into** Authentik as an admin. (If you still can’t get in, see [Method 2](#2-create-the-missing-flow).)
2. **Go to** **System > Brands** (or **Administration > Tenants** in older versions).
3. Find fields like **“Default Authentication Flow”** or “Default Flow” that reference `default/authentication`.
4. **Set** it to a flow that **actually exists**, like `auth-standalone`. For example:
   - In the dropdown for “Default Authentication Flow,” select **`auth-standalone`** (or whichever flow you see in *Flows*).
5. **Save** changes.

Next time Authentik needs to log you in, it’ll use the existing `auth-standalone` flow instead of `default/authentication`, so you won’t see that 404.

---

## 2. Create the Missing `default/authentication` Flow

If you prefer to keep the brand/tenant setting as `default/authentication`, then you need to **create** a flow with that slug:

1. In the Admin UI, go to **Flows**.
2. **Create** a new Flow. In the “Slug” field, put **`authentication`** and for the “Flow type” choose **Authentication** (if required).
3. Add the usual stages (e.g., **Identification stage**, **Password stage**, maybe an **User Login** stage).
4. Make sure the final slug in the URL looks like:
   ```
   /if/admin/flows/default/authentication
   ```
   That means the top-level *Flow Folder* is `default`, and the *Flow Slug* is `authentication`.
5. Save the flow, and ensure your brand or tenant is referencing `default/authentication`.

Once you have a real flow at `flows/-/default/authentication`, that 404 goes away because Authentik can actually find it.

> **Note**: If you don’t have a “default” folder, you can simply name the flow’s **“Folder/Parent Folder”** = `default` and the “Flow Slug” = `authentication`.

---

## If You Can’t Even Reach `/if/admin/`

### Option A: **Direct Flow Link**

Try going directly to a known working flow URL, like the built-in `auth-standalone`:

```
https://login.apsjado.com/if/flow/auth-standalone/
```

If that loads a login page, log in as admin, and then proceed with [Method 1 or 2](#1-point-your-brandtenant-to-a-real-flow-instead-of-defaultauthentication).

### Option B: **Local Access**

- If you mapped `127.0.0.1:9000:9000` in your Docker Compose, you could try `http://127.0.0.1:9000/if/admin/` from the same machine.
- This bypasses Traefik and any broken brand/tenant references.

### Option C: **Editing via Database or Blueprint**

In extreme cases, you can modify the brand or tenant record in the database directly (using a Postgres client) or apply a small blueprint that updates the brand’s “Default Authentication Flow” to `auth-standalone`. This is advanced and usually unnecessary if you can reach `/if/admin/`.

---

## Summary

- **Why You See 404**: The brand/tenant references a flow slug `default/authentication` that doesn’t exist.
- **Two Fixes**:
  1. **Change** the brand/tenant to use a real flow slug (like `auth-standalone`).
  2. **Create** a flow actually named `default/authentication` so it exists.
- If you’re completely locked out of `/if/admin/`, try the **direct flow link** approach or a local port bind to bypass Traefik, then fix brand/tenant settings.

Once Authentik can actually find the flow it references, the 404s at

```
/flows/-/default/authentication/?next=/
```

will go away, and you’ll get a functional login page.


#### ChatGPT:
<time datetime="2025-01-18T05:08:57.907Z" title="1/18/2025, 2:08:57 PM">14:08</time>

If Authentik is stuck redirecting you to a missing flow (e.g. `/flows/-/default/authentication`) and you **can’t** reach the Admin UI to fix it, you essentially have a “chicken-and-egg” problem: you need the Admin UI to fix the flow references, but you can’t get into the Admin UI because Authentik keeps sending you to a 404 page.

The solution is to **override** or **correct** the flow references **outside** the UI—typically by using a **blueprint**. This way, Authentik will apply your corrected config at startup, so you no longer get the invalid `/default/authentication` link.

Below is a step-by-step approach using **blueprints**.

---

## 1. Create a “Fix Brand” Blueprint

In Authentik, the **Brand** or **Tenant** typically has a field like `authentication_flow` set to `default/authentication` (which doesn’t exist). We can override that setting by providing a small YAML blueprint that sets the brand’s `authentication_flow` to a **real** slug such as `auth-standalone` (the default Authentik flow).

1. **On your host**, in the same folder as your `docker-compose.yml`, create a file named `fix-brand.yml` (for example):
   ```yaml
   version: v1
   metadata:
     name: fix-default-brand
     label: Fix the brand to point to auth-standalone
     # This type means it modifies the Brand model
     type: authentik/brand
   spec:
     # Slug of your brand (most likely "default")
     slug: default
     # Overwrite the flow slug for authentication. 
     # "auth-standalone" is the typical built-in login flow in Authentik.
     authentication_flow: "auth-standalone"
   ```

2. This YAML says:
   - We’re defining (or updating) a “brand” with slug `default`.
   - We’re telling it to use **`auth-standalone`** instead of `default/authentication`.

*(If you know the exact brand slug is something else, adjust accordingly. But typically the “default” brand is the culprit.)*

---

## 2. Mount the Blueprint into the Container

By default, Authentik **automatically** loads any `.yml` (or `.yaml`) files in `/blueprints` on startup. So, we just need to place `fix-brand.yml` in a folder we can mount at `/blueprints`.

In your `docker-compose.yml` (the same one that runs Authentik), modify the `authentik` service to mount a local `blueprints` folder:

```yaml
services:
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    command: "server"
    restart: unless-stopped
    networks:
      - traefik-net

    # Existing labels, environment, etc.

    volumes:
      # Mount your local "blueprints" dir into Authentik's /blueprints
      - "./blueprints:/blueprints"
```

Then, on your host machine:

1. **Create** a folder called `blueprints` next to your `docker-compose.yml`.
2. **Move** the `fix-brand.yml` file into that `blueprints` folder.
3. Your host folder structure might look like:
   ```
   .
   ├─ docker-compose.yml
   ├─ traefik.yml
   ├─ blueprints/
   │    └─ fix-brand.yml
   └─ acme.json
   ```

---

## 3. Relaunch Authentik

Now that we have `fix-brand.yml` mounted to `/blueprints/fix-brand.yml` inside the container:

1. **Stop** the containers:
   ```bash
   docker compose down
   ```
2. **Start** them again:
   ```bash
   docker compose up -d
   docker compose logs -f
   ```
3. **Watch** the Authentik logs. You should see something like:
   ```
   Task published: "blueprints_discovery"
   ...
   Found blueprint fix-brand.yml
   Applying brand changes...
   ...
   ```

Authentik will apply the blueprint at startup, overwriting the brand’s `authentication_flow` to `auth-standalone`. This means it no longer references the broken `default/authentication` slug.

---

## 4. Test the Login Page

After the container finishes starting, open your browser to:

```
https://login.apsjado.com
```

or possibly:

```
https://login.apsjado.com/if/admin/
```

- **If** everything worked, Authentik should send you to the **auth-standalone** flow. That is a valid built-in flow, so you’ll see the normal login page, not a 404.
- **Log in** with your admin user (the one you bootstrapped or created previously).

Now you can manage brand settings or flow slugs from the Admin UI.

---

## 5. Clean Up or Keep the Blueprint

- If you **no longer need** the blueprint (i.e., the brand is fixed permanently), you can remove `fix-brand.yml` from the `blueprints` folder.
- Or leave it in place if you want to keep your config in code.

---

### Alternative: Another Brand or Tenant Slug

If you have multiple brands/tenants, you might need to fix the slug on each. For example, if your brand slug is something else, just match it in the blueprint. The main idea is the same: override the field that references `default/authentication` with a known good flow like `auth-standalone`.

---

## Summary

1. **Why you’re stuck**: Authentik’s brand or tenant config references a flow that doesn’t exist → immediate 404 loop.
2. **Solution**: Use a **blueprint** to forcibly correct the `authentication_flow` to a valid slug (`auth-standalone`).
3. **Steps**:
   - Make `fix-brand.yml`.
   - Mount it at `/blueprints` in your Authentik container.
   - Restart.
   - Authentik picks up the blueprint and changes the brand to the correct flow.
   - The 404 loop is gone, and you can finally access the login or admin page.

That’s how you fix “I cannot access any page to fix the flow reference” by **applying a blueprint** behind the scenes. Once done, you’ll be able to sign in normally and fully configure Authentik from the UI going forward. Good luck!


#### You:
<time datetime="2025-01-18T05:10:56.568Z" title="1/18/2025, 2:10:56 PM">14:10</time>

ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 5/5
 ✔ Container authentik           Removed                                                                                                        0.2s 
 ✔ Container authentik_postgres  Removed                                                                                                        0.3s 
 ✔ Container authentik_redis     Removed                                                                                                        0.4s 
 ✔ Container traefik             Removed                                                                                                        0.4s 
 ✔ Network traefik_traefik-net   Removed                                                                                                        0.2s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_redis     Started                                                                                                        0.6s 
 ✔ Container traefik             Started                                                                                                        0.4s 
 ✔ Container authentik           Started                                                                                                        0.6s 
 ✔ Container authentik_postgres  Started                                                                                                        0.6s 
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 05:05:34.265 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 05:05:34.265 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 05:05:34.266 * Ready to accept connections
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_postgres  | selecting default time zone ... UTC
authentik_postgres  | creating configuration files ... ok
authentik           | {"event":"Loaded config","level":"debug","path":"inbuilt-default","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Loaded config","level":"debug","path":"/authentik/lib/default.yml","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Loaded config from environment","level":"debug","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"not enabling debug server, set `AUTHENTIK_DEBUG` to `true` to enable it.","level":"info","logger":"authentik.go_debugger","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Starting Metrics server","level":"info","listen":"0.0.0.0:9300","logger":"authentik.router.metrics","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event":"Starting HTTP server","level":"info","listen":"0.0.0.0:9000","logger":"authentik.router","timestamp":"2025-01-18T05:05:34Z"}
authentik_postgres  | running bootstrap script ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176734.438687, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176734.438887, "count": 11}
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 05:05:34.569 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event":"Starting HTTPS server","level":"info","listen":"0.0.0.0:9443","logger":"authentik.router","timestamp":"2025-01-18T05:05:34Z"}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176734.8544438}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176735.855273}
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to start....2025-01-18 05:05:35.962 UTC [42] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:05:35.969 UTC [42] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:05:35.990 UTC [43] LOG:  database system was shut down at 2025-01-18 05:05:34 UTC
authentik_postgres  | 2025-01-18 05:05:35.999 UTC [42] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down....2025-01-18 05:05:36.449 UTC [42] LOG:  received fast shutdown request
authentik_postgres  | 2025-01-18 05:05:36.454 UTC [42] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 05:05:36.455 UTC [42] LOG:  background worker "logical replication launcher" (PID 49) exited with exit code 1
authentik_postgres  | 2025-01-18 05:05:36.455 UTC [44] LOG:  shutting down
authentik_postgres  | 2025-01-18 05:05:36.499 UTC [42] LOG:  database system is shut down
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 05:05:36.573 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 05:05:36.587 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:05:36.600 UTC [57] LOG:  database system was shut down at 2025-01-18 05:05:36 UTC
authentik_postgres  | 2025-01-18 05:05:36.608 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8559859}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.865493}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8660128}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176736.8660517}
authentik_postgres  | 2025-01-18 05:05:36.870 UTC [65] ERROR:  relation "public.authentik_install_id" does not exist at character 16
authentik_postgres  | 2025-01-18 05:05:36.870 UTC [65] STATEMENT:  SELECT id FROM public.authentik_install_id ORDER BY id LIMIT 1;
authentik           | 2025-01-18 05:05:36 [info     ] waiting to acquire database lock
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=install_id.py
authentik_postgres  | 2025-01-18 05:05:36.880 UTC [66] WARNING:  there is already a transaction in progress
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=install_id.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=template_schema.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=template_schema.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=tenant_files.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=tenant_files.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=version_history_create.py
authentik_postgres  | 2025-01-18 05:05:36.904 UTC [66] WARNING:  there is already a transaction in progress
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=version_history_create.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration needs to be applied  migration=version_history_update.py
authentik           | 2025-01-18 05:05:36 [info     ] Migration finished applying    migration=version_history_update.py
authentik           | 2025-01-18 05:05:36 [info     ] applying django migrations
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737176737.7043197, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176737.7046652, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176737.7059383}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7064414, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7072363, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7077956, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7084992, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7110476, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7113278, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7117403, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7123122, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7130513, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7133982, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7137039, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7139425, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7149587, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7160487, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.7163422, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176737.71678, "path": "authentik.events.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:38.019814"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:38.020427"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.012263"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.012547"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.022059"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.022379"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.023145"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.042030"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.062153"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.062651"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.063176"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.070016"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.070839"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.071182"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.071448"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.072897"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.073575"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.074184"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.075374"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.075764"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.079563"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.081601"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.090418"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.090739"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091128"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091504"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.091791"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.118084"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.118216"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119449"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119506"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.119790"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120103"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120520"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.120756"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.121160"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.121379"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124425"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124659"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:05:39.124709"}
authentik           | === Starting migration
authentik           | Operations to perform:
authentik           |   Apply all migrations: auth, authentik_blueprints, authentik_brands, authentik_core, authentik_crypto, authentik_enterprise, authentik_events, authentik_flows, authentik_outposts, authentik_policies, authentik_policies_dummy, authentik_policies_event_matcher, authentik_policies_expiry, authentik_policies_expression, authentik_policies_geoip, authentik_policies_password, authentik_policies_reputation, authentik_providers_google_workspace, authentik_providers_ldap, authentik_providers_microsoft_entra, authentik_providers_oauth2, authentik_providers_proxy, authentik_providers_rac, authentik_providers_radius, authentik_providers_saml, authentik_providers_scim, authentik_rbac, authentik_sources_kerberos, authentik_sources_ldap, authentik_sources_oauth, authentik_sources_plex, authentik_sources_saml, authentik_sources_scim, authentik_stages_authenticator_duo, authentik_stages_authenticator_endpoint_gdtc, authentik_stages_authenticator_sms, authentik_stages_authenticator_static, authentik_stages_authenticator_totp, authentik_stages_authenticator_validate, authentik_stages_authenticator_webauthn, authentik_stages_captcha, authentik_stages_consent, authentik_stages_deny, authentik_stages_dummy, authentik_stages_email, authentik_stages_identification, authentik_stages_invitation, authentik_stages_password, authentik_stages_prompt, authentik_stages_redirect, authentik_stages_source, authentik_stages_user_delete, authentik_stages_user_login, authentik_stages_user_logout, authentik_stages_user_write, authentik_tenants, contenttypes, guardian, sessions
authentik           | Running migrations:
authentik           |   Applying contenttypes.0001_initial...
authentik           |  OK
authentik           |   Applying contenttypes.0002_remove_content_type_name...
authentik           |  OK
authentik           |   Applying auth.0001_initial...
authentik           |  OK
authentik           |   Applying auth.0002_alter_permission_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0003_alter_user_email_max_length...
authentik           |  OK
authentik           |   Applying auth.0004_alter_user_username_opts...
authentik           |  OK
authentik           |   Applying auth.0005_alter_user_last_login_null...
authentik           |  OK
authentik           |   Applying auth.0006_require_contenttypes_0002...
authentik           |  OK
authentik           |   Applying auth.0007_alter_validators_add_error_messages...
authentik           |  OK
authentik           |   Applying auth.0008_alter_user_username_max_length...
authentik           |  OK
authentik           |   Applying auth.0009_alter_user_last_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0010_alter_group_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0011_update_proxy_permissions...
authentik           |  OK
authentik           |   Applying auth.0012_alter_user_first_name_max_length...
authentik           |  OK
authentik           |   Applying authentik_policies.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies.0002_auto_20200528_1647...
authentik           |  OK
authentik           |   Applying authentik_flows.0001_squashed_0007_auto_20200703_2059...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0002_blueprintinstance_content...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0003_alter_blueprintinstance_name...
authentik           |  OK
authentik           |   Applying authentik_rbac.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_rbac.0002_systempermission...
authentik           |  OK
authentik           |   Applying authentik_rbac.0003_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_tenants.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_tenants.0002_tenant_default_token_duration_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0008_default_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0009_source_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0010_provider_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0011_flow_title...
authentik           |  OK
authentik           |   Applying authentik_flows.0012_auto_20200908_1542_squashed_0017_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_flows.0018_oob_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0019_alter_flow_background_squashed_0024_alter_flow_compatibility_mode...
authentik           |  OK
authentik           |   Applying authentik_crypto.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_core.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0001_squashed_0005_remove_samlprovider_processor_path...
authentik           |  OK
authentik           |   Applying authentik_core.0002_auto_20200523_1133_squashed_0011_provider_name_temp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0006_remove_samlprovider_name...
authentik           |  OK
authentik           |   Applying authentik_crypto.0002_create_self_signed_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0002_oauth2provider_sub_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0003_auto_20200916_2129...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0004_remove_oauth2provider_post_logout_redirect_uris...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0005_auto_20200920_1240...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0006_remove_oauth2provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0012_auto_20201003_1737_squashed_0016_auto_20201202_2234...
authentik           |  OK
authentik           |   Applying authentik_core.0017_managed...
authentik           |  OK
authentik           |   Applying authentik_core.0018_auto_20210330_1345_squashed_0028_alter_token_intent...
authentik           |  OK
authentik           |   Applying authentik_flows.0020_flowtoken...
authentik           |  OK
authentik           |   Applying authentik_flows.0021_auto_20211227_2103...
authentik           |  OK
authentik           |   Applying authentik_flows.0022_flow_layout...
authentik           |  OK
authentik           |   Applying authentik_flows.0023_flow_denied_action...
authentik           |  OK
authentik           |   Applying authentik_flows.0024_flow_authentication...
authentik           |  OK
authentik           |   Applying authentik_flows.0025_alter_flowstagebinding_evaluate_on_plan_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0019_application_group...
authentik           |  OK
authentik           |   Applying authentik_core.0020_application_open_in_new_tab...
authentik           |  OK
authentik           |   Applying authentik_core.0021_source_user_path_user_path...
authentik           |  OK
authentik           |   Applying authentik_core.0022_alter_group_parent...
authentik           |  OK
authentik           |   Applying authentik_core.0023_source_authentik_c_slug_ccb2e5_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0024_source_icon...
authentik           |  OK
authentik           |   Applying authentik_core.0025_alter_provider_authorization_flow...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0001_squashed_0006_rename_parent_group_scimprovider_filter_group...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0001_squashed_0005_ldapprovider_search_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0002_ldapprovider_bind_mode...
authentik           |  OK
authentik           |   Applying authentik_core.0026_alter_propertymapping_name_alter_provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0027_alter_user_uuid...
authentik           |  OK
authentik           |   Applying authentik_core.0028_provider_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0029_provider_backchannel_applications_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0030_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0031_alter_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0032_group_roles...
authentik           |  OK
authentik           |   Applying authentik_core.0033_alter_user_options...
authentik           |  OK
authentik           |   Applying authentik_core.0034_alter_authenticatedsession_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0035_alter_group_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0003_auto_20200908_1542...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0002_auto_20200920_1859...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0003_auto_20210222_1821...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0004_prompt_sub_text...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0005_alter_prompt_field_key...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0006_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0007_prompt_placeholder_expression...
authentik           |  OK
authentik           |   Applying authentik_crypto.0003_certificatekeypair_managed...
authentik           |  OK
authentik           |   Applying authentik_brands.0001_squashed_0005_tenant_web_certificate...
authentik           |  OK
authentik           |   Applying authentik_brands.0002_tenant_flow_user_settings...
authentik           |  OK
authentik           |   Applying authentik_brands.0003_tenant_attributes...
authentik           |  OK
authentik           |   Applying authentik_brands.0004_tenant_flow_device_code...
authentik           |  OK
authentik           |   Applying authentik_brands.0005_tenantuuid_to_branduuid...
authentik           |  OK
authentik           |   Applying authentik_brands.0006_brand_authentik_b_domain_b9b24a_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_brands.0007_brand_default_application...
authentik           |  OK
authentik           |   Applying authentik_policies.0004_policy_execution_logging...
authentik           |  OK
authentik           |   Applying authentik_policies.0005_binding_group...
authentik           |  OK
authentik           |   Applying authentik_policies.0006_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_policies.0007_policybindingmodel_policy_engine_mode...
authentik           |  OK
authentik           |   Applying authentik_policies.0008_policybinding_authentik_p_policy__534e15_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0009_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0010_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0011_policybinding_failure_result_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0026_alter_flow_options...
authentik           |  OK
authentik           |   Applying authentik_flows.0027_auto_20231028_1424...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0001_squashed_0012_auto_20210812_1703...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0002_auto_20211203_0900...
authentik           |  OK
authentik           |   Applying authentik_crypto.0004_alter_certificatekeypair_name...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0003_ldapsource_client_certificate_ldapsource_sni_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0004_ldapsource_password_login_update_internal_password...
authentik           |  OK
authentik           |   Applying authentik_core.0036_source_group_property_mappings_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0005_remove_ldappropertymapping_object_field_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0037_remove_source_property_mappings...
authentik           |  OK
authentik           |   Applying authentik_core.0038_source_authentik_c_enabled_d72365_idx...
authentik           |  OK
authentik           |   Applying authentik_core.0039_source_group_matching_mode_alter_group_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0040_provider_invalidation_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0041_applicationentitlement...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0002_rename_users_license_internal_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0003_remove_licenseusage_within_limits_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0001_squashed_0018_alter_eventmatcherpolicy_action...
authentik           |  OK
authentik           |   Applying authentik_events.0001_squashed_0019_alter_notificationtransport_webhook_url...
authentik           |  OK
authentik           |   Applying authentik_events.0002_alter_notificationtransport_mode...
authentik           |  OK
authentik           |   Applying authentik_events.0003_rename_tenant_event_brand...
authentik           |  OK
authentik           |   Applying authentik_events.0004_systemtask_squashed_0005_remove_systemtask_finish_timestamp_and_more...
authentik           |  OK
authentik           |   Applying authentik_events.0006_alter_systemtask_expires...
authentik           |  OK
authentik           |   Applying authentik_events.0007_event_authentik_e_action_9a9dd9_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0001_squashed_0017_outpost_managed...
authentik           |  OK
authentik           |   Applying authentik_outposts.0018_kubernetesserviceconnection_verify_ssl...
authentik           |  OK
authentik           |   Applying authentik_outposts.0019_alter_outpost_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0020_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_outposts.0021_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0002_dummypolicy_authentik_p_policy__648f9b_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0019_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0020_eventmatcherpolicy_authentik_p_policy__e605cf_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0021_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0022_eventmatcherpolicy_model...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0023_alter_eventmatcherpolicy_action_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0002_passwordexpirypolicy_authentik_p_policy__cf73a7_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0002_auto_20200926_1156...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0003_auto_20201203_1223...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0004_expressionpolicy_authentik_p_policy__fb6feb_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_geoip.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0002_passwordpolicy_password_field...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0003_passwordpolicy_amount_digits...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0004_passwordpolicy_authentik_p_policy__855e80_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0005_passwordpolicy_check_have_i_been_pwned_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0002_auto_20210529_2046...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0003_reputation_delete_ipreputation_delete_userreputation...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0004_reputationpolicy_authentik_p_policy__8f0d70_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0005_reputation_expires_reputation_expiring...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0006_reputation_ip_asn_data...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0007_reputation_authentik_p_identif_9434d7_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0001_squashed_0002_alter_googleworkspaceprovidergroup_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0003_googleworkspaceprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying guardian.0001_initial...
authentik           |  OK
authentik           |   Applying guardian.0002_generic_permissions_index...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0003_ldapprovider_mfa_support_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0004_alter_ldapprovider_options_and_more...
authentik           | Adding content type 'authentik_providers_ldap | ldapprovider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can add LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can change LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can delete LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can view LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Search full LDAP directory'
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0002_microsoftentraprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0002_auto_20200520_1108...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0003_auto_20210416_0726...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0004_auto_20210417_1900...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0005_update_provider_type_names...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0006_oauthsource_additional_scopes...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0007_oauthsource_oidc_jwks_oauthsource_oidc_jwks_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0007_auto_20201016_1107_squashed_0017_alter_oauth2provider_token_validity...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0008_rename_rsa_key_oauth2provider_signing_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0009_oauth2provider_verification_keys_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0010_alter_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0011_oauth2provider_jwks_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0012_remove_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0013_devicetoken...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0014_alter_refreshtoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0015_accesstoken_auth_time_authorizationcode_auth_time_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0016_alter_refreshtoken_token...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0017_accesstoken_session_id_authorizationcode_session_id_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0018_alter_accesstoken_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0019_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0020_remove_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0021_oauth2provider_encryption_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0022_remove_accesstoken_session_id_and_more...
authentik           | 
authentik           | 
authentik           | Fetching session keys, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to Authorization Code, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Access Token, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Refresh Token, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0023_alter_accesstoken_refreshtoken_use_hash_index...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0024_remove_oauth2provider_redirect_uris_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0025_rename_jwks_sources_oauth2provider_jwt_federation_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0026_alter_accesstoken_session_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0001_squashed_0014_proxy_v2...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0015_proxyprovider_receive_header_auth...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0001_squashed_0003_alter_connectiontoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0004_alter_connectiontoken_expires...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0005_alter_racpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0002_radiusprovider_mfa_support...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0003_radiusproviderpropertymapping...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0004_alter_radiusproviderpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0007_samlprovider_verification_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0008_auto_20201112_1036...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0009_auto_20201112_2016...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0010_auto_20201230_2112...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0011_samlprovider_name_id_mapping...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0012_managed...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0013_samlprovider_default_relay_state...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0014_alter_samlprovider_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0015_alter_samlpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0016_samlprovider_encryption_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0007_scimgroup_scim_id_scimuser_scim_id_and_more...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM users, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM groups, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0008_rename_scimgroup_scimprovidergroup_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0009_alter_scimmapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0010_scimprovider_verify_certificates...
authentik           |  OK
authentik           |   Applying authentik_rbac.0004_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0002_kerberossource_kadmin_type...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0006_rename_ldappropertymapping_ldapsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0008_groupoauthsourceconnection_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0002_auto_20210505_1717...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0003_alter_plexsource_plex_token...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0004_groupplexsourceconnection_plexsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0001_squashed_0009_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0010_samlsource_pre_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0011_auto_20210324_0736...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0012_usersamlsourceconnection...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0013_samlsource_verification_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0014_alter_samlsource_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0015_groupsamlsourceconnection_samlsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0016_samlsource_encryption_kp...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0017_fix_x509subjectname...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0002_scimsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0002_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0003_duodevice_last_t...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0004_authenticatorduostage_admin_integration_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0005_authenticatorduostage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0006_duodevice_created_duodevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_endpoint_gdtc.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0001_squashed_0004_auto_20211014_0936...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0002_alter_authenticatorsmsstage_from_number...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0003_smsdevice_last_used_on...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0004_authenticatorsmsstage_verify_only_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0005_authenticatorsmsstage_mapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0006_authenticatorsmsstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0007_smsdevice_created_smsdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0002_otpstaticstage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0003_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0004_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0005_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0006_authenticatorstaticstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0007_authenticatorstaticstage_token_length_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0009_throttling...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0010_staticdevice_created_staticdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0002_auto_20200701_1900...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0003_otptimestage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0004_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0005_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0006_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0007_authenticatortotpstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0009_auto_20190420_0723...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0010_alter_totpdevice_key...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0011_totpdevice_created_totpdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0001_squashed_0011_webauthndevice_aaguid...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0002_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0003_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0004_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0005_authenticatorvalidatestage_configuration_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0006_auto_20210301_1757...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0007_auto_20210403_0927...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0008_alter_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0009_default_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0010_remove_authenticatorvalidatestage_configuration_stage_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0011_authenticatorvalidatestage_last_auth_threshold...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0012_authenticatorvalidatestage_webauthn_user_verification...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0013_authenticatorvalidatestage_webauthn_allowed_device_types...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0012_webauthndevice_created_webauthndevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0002_captchastage_api_url_captchastage_js_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0003_captchastage_error_on_invalid_score_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0004_captchastage_interactive...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0002_auto_20200720_0941...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0003_auto_20200924_1403...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0004_alter_userconsent_unique_together_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0005_alter_consentstage_mode...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0006_alter_userconsent_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0002_denystage_deny_message...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0002_dummystage_throw_error...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0002_emailstage_use_global_settings...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0003_auto_20210404_1054...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0004_emailstage_activate_user_on_success...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0002_passwordstage_change_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0003_passwordstage_failed_attempts_before_cancel...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0004_auto_20200925_1057...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0005_auto_20210402_2221...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0002_auto_20200530_2204_squashed_0013_identificationstage_passwordless_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0014_identificationstage_pretend...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0015_identificationstage_captcha_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0001_squashed_0006_invitation_name...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0007_invitation_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0008_alter_invitation_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0006_passwordchange_rename...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0007_app_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0008_replace_inbuilt...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0009_passwordstage_allow_show_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0010_alter_passwordstage_backends...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0008_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0009_prompt_name...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0010_alter_prompt_placeholder_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0011_prompt_initial_value_prompt_initial_value_expression_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_redirect.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_source.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_delete.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0002_userloginstage_session_duration...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0003_session_duration_delta...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0004_userloginstage_terminate_other_sessions...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0005_userloginstage_remember_me_offset...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0006_userloginstage_geoip_binding_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_logout.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0002_auto_20200918_1653...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0003_userwritestage_create_users_as_inactive...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0004_userwritestage_create_users_group...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0005_userwritestage_user_path_template...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0006_userwritestage_can_create_users...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0007_remove_userwritestage_can_create_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0008_userwritestage_user_type...
authentik           |  OK
authentik           |   Applying authentik_tenants.0003_alter_tenant_default_token_duration...
authentik           |  OK
authentik           |   Applying authentik_tenants.0004_tenant_impersonation_require_reason...
authentik           |  OK
authentik           |   Applying sessions.0001_initial...
authentik           |  OK
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:00Z"}
authentik           | === Starting migration
authentik           | Operations to perform:
authentik           |   Apply all migrations: auth, authentik_blueprints, authentik_brands, authentik_core, authentik_crypto, authentik_enterprise, authentik_events, authentik_flows, authentik_outposts, authentik_policies, authentik_policies_dummy, authentik_policies_event_matcher, authentik_policies_expiry, authentik_policies_expression, authentik_policies_geoip, authentik_policies_password, authentik_policies_reputation, authentik_providers_google_workspace, authentik_providers_ldap, authentik_providers_microsoft_entra, authentik_providers_oauth2, authentik_providers_proxy, authentik_providers_rac, authentik_providers_radius, authentik_providers_saml, authentik_providers_scim, authentik_rbac, authentik_sources_kerberos, authentik_sources_ldap, authentik_sources_oauth, authentik_sources_plex, authentik_sources_saml, authentik_sources_scim, authentik_stages_authenticator_duo, authentik_stages_authenticator_endpoint_gdtc, authentik_stages_authenticator_sms, authentik_stages_authenticator_static, authentik_stages_authenticator_totp, authentik_stages_authenticator_validate, authentik_stages_authenticator_webauthn, authentik_stages_captcha, authentik_stages_consent, authentik_stages_deny, authentik_stages_dummy, authentik_stages_email, authentik_stages_identification, authentik_stages_invitation, authentik_stages_password, authentik_stages_prompt, authentik_stages_redirect, authentik_stages_source, authentik_stages_user_delete, authentik_stages_user_login, authentik_stages_user_logout, authentik_stages_user_write, authentik_tenants, contenttypes, guardian, sessions
authentik           | Running migrations:
authentik           |   Applying contenttypes.0001_initial...
authentik           |  OK
authentik           |   Applying contenttypes.0002_remove_content_type_name...
authentik           |  OK
authentik           |   Applying auth.0001_initial...
authentik           |  OK
authentik           |   Applying auth.0002_alter_permission_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0003_alter_user_email_max_length...
authentik           |  OK
authentik           |   Applying auth.0004_alter_user_username_opts...
authentik           |  OK
authentik           |   Applying auth.0005_alter_user_last_login_null...
authentik           |  OK
authentik           |   Applying auth.0006_require_contenttypes_0002...
authentik           |  OK
authentik           |   Applying auth.0007_alter_validators_add_error_messages...
authentik           |  OK
authentik           |   Applying auth.0008_alter_user_username_max_length...
authentik           |  OK
authentik           |   Applying auth.0009_alter_user_last_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0010_alter_group_name_max_length...
authentik           |  OK
authentik           |   Applying auth.0011_update_proxy_permissions...
authentik           |  OK
authentik           |   Applying auth.0012_alter_user_first_name_max_length...
authentik           |  OK
authentik           |   Applying authentik_policies.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies.0002_auto_20200528_1647...
authentik           |  OK
authentik           |   Applying authentik_flows.0001_squashed_0007_auto_20200703_2059...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0001_initial...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_blueprints.0002_blueprintinstance_content...
authentik           |  OK
authentik           |   Applying authentik_blueprints.0003_alter_blueprintinstance_name...
authentik           |  OK
authentik           |   Applying authentik_rbac.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_rbac.0002_systempermission...
authentik           |  OK
authentik           |   Applying authentik_rbac.0003_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_tenants.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_tenants.0002_tenant_default_token_duration_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0008_default_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0009_source_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0010_provider_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0011_flow_title...
authentik           |  OK
authentik           |   Applying authentik_flows.0012_auto_20200908_1542_squashed_0017_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_flows.0018_oob_flows...
authentik           |  OK
authentik           |   Applying authentik_flows.0019_alter_flow_background_squashed_0024_alter_flow_compatibility_mode...
authentik           |  OK
authentik           |   Applying authentik_crypto.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_core.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0001_squashed_0005_remove_samlprovider_processor_path...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0002_auto_20200523_1133_squashed_0011_provider_name_temp...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:01Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0006_remove_samlprovider_name...
authentik           |  OK
authentik           |   Applying authentik_crypto.0002_create_self_signed_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0002_oauth2provider_sub_mode...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0003_auto_20200916_2129...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0004_remove_oauth2provider_post_logout_redirect_uris...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0005_auto_20200920_1240...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0006_remove_oauth2provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0012_auto_20201003_1737_squashed_0016_auto_20201202_2234...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0017_managed...
authentik           |  OK
authentik           |   Applying authentik_core.0018_auto_20210330_1345_squashed_0028_alter_token_intent...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_flows.0020_flowtoken...
authentik           |  OK
authentik           |   Applying authentik_flows.0021_auto_20211227_2103...
authentik           |  OK
authentik           |   Applying authentik_flows.0022_flow_layout...
authentik           |  OK
authentik           |   Applying authentik_flows.0023_flow_denied_action...
authentik           |  OK
authentik           |   Applying authentik_flows.0024_flow_authentication...
authentik           |  OK
authentik           |   Applying authentik_flows.0025_alter_flowstagebinding_evaluate_on_plan_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0019_application_group...
authentik           |  OK
authentik           |   Applying authentik_core.0020_application_open_in_new_tab...
authentik           |  OK
authentik           |   Applying authentik_core.0021_source_user_path_user_path...
authentik           |  OK
authentik           |   Applying authentik_core.0022_alter_group_parent...
authentik           |  OK
authentik           |   Applying authentik_core.0023_source_authentik_c_slug_ccb2e5_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0024_source_icon...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           |  OK
authentik           |   Applying authentik_core.0025_alter_provider_authorization_flow...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0001_squashed_0006_rename_parent_group_scimprovider_filter_group...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:02Z"}
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:03Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0001_squashed_0005_ldapprovider_search_mode...
authentik           | {"error":"authentik starting","event":"failed to proxy to backend","level":"warning","logger":"authentik.router","timestamp":"2025-01-18T05:06:03Z"}
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0002_ldapprovider_bind_mode...
authentik           |  OK
authentik           |   Applying authentik_core.0026_alter_propertymapping_name_alter_provider_name...
authentik           |  OK
authentik           |   Applying authentik_core.0027_alter_user_uuid...
authentik           |  OK
authentik           |   Applying authentik_core.0028_provider_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0029_provider_backchannel_applications_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0030_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0031_alter_user_type...
authentik           |  OK
authentik           |   Applying authentik_core.0032_group_roles...
authentik           |  OK
authentik           |   Applying authentik_core.0033_alter_user_options...
authentik           |  OK
authentik           |   Applying authentik_core.0034_alter_authenticatedsession_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0035_alter_group_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0003_auto_20200908_1542...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0002_auto_20200920_1859...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0003_auto_20210222_1821...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0004_prompt_sub_text...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0005_alter_prompt_field_key...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0006_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0007_prompt_placeholder_expression...
authentik           |  OK
authentik           |   Applying authentik_crypto.0003_certificatekeypair_managed...
authentik           |  OK
authentik           |   Applying authentik_brands.0001_squashed_0005_tenant_web_certificate...
authentik           |  OK
authentik           |   Applying authentik_brands.0002_tenant_flow_user_settings...
authentik           |  OK
authentik           |   Applying authentik_brands.0003_tenant_attributes...
authentik           |  OK
authentik           |   Applying authentik_brands.0004_tenant_flow_device_code...
authentik           |  OK
authentik           |   Applying authentik_brands.0005_tenantuuid_to_branduuid...
authentik           |  OK
authentik           |   Applying authentik_brands.0006_brand_authentik_b_domain_b9b24a_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_brands.0007_brand_default_application...
authentik           |  OK
authentik           |   Applying authentik_policies.0004_policy_execution_logging...
authentik           |  OK
authentik           |   Applying authentik_policies.0005_binding_group...
authentik           |  OK
authentik           |   Applying authentik_policies.0006_auto_20210329_1334...
authentik           |  OK
authentik           |   Applying authentik_policies.0007_policybindingmodel_policy_engine_mode...
authentik           |  OK
authentik           |   Applying authentik_policies.0008_policybinding_authentik_p_policy__534e15_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies.0009_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0010_alter_policy_name...
authentik           |  OK
authentik           |   Applying authentik_policies.0011_policybinding_failure_result_and_more...
authentik           |  OK
authentik           |   Applying authentik_flows.0026_alter_flow_options...
authentik           |  OK
authentik           |   Applying authentik_flows.0027_auto_20231028_1424...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0001_squashed_0012_auto_20210812_1703...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0002_auto_20211203_0900...
authentik           |  OK
authentik           |   Applying authentik_crypto.0004_alter_certificatekeypair_name...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0003_ldapsource_client_certificate_ldapsource_sni_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0004_ldapsource_password_login_update_internal_password...
authentik           |  OK
authentik           |   Applying authentik_core.0036_source_group_property_mappings_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0005_remove_ldappropertymapping_object_field_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0037_remove_source_property_mappings...
authentik           |  OK
authentik           |   Applying authentik_core.0038_source_authentik_c_enabled_d72365_idx...
authentik           |  OK
authentik           |   Applying authentik_core.0039_source_group_matching_mode_alter_group_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_core.0040_provider_invalidation_flow...
authentik           |  OK
authentik           |   Applying authentik_core.0041_applicationentitlement...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0002_rename_users_license_internal_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_enterprise.0003_remove_licenseusage_within_limits_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0001_squashed_0018_alter_eventmatcherpolicy_action...
authentik           |  OK
authentik           |   Applying authentik_events.0001_squashed_0019_alter_notificationtransport_webhook_url...
authentik           |  OK
authentik           |   Applying authentik_events.0002_alter_notificationtransport_mode...
authentik           |  OK
authentik           |   Applying authentik_events.0003_rename_tenant_event_brand...
authentik           |  OK
authentik           |   Applying authentik_events.0004_systemtask_squashed_0005_remove_systemtask_finish_timestamp_and_more...
authentik           |  OK
authentik           |   Applying authentik_events.0006_alter_systemtask_expires...
authentik           |  OK
authentik           |   Applying authentik_events.0007_event_authentik_e_action_9a9dd9_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0001_squashed_0017_outpost_managed...
authentik           |  OK
authentik           |   Applying authentik_outposts.0018_kubernetesserviceconnection_verify_ssl...
authentik           |  OK
authentik           |   Applying authentik_outposts.0019_alter_outpost_name_and_more...
authentik           |  OK
authentik           |   Applying authentik_outposts.0020_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_outposts.0021_alter_outpost_type...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_dummy.0002_dummypolicy_authentik_p_policy__648f9b_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0019_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0020_eventmatcherpolicy_authentik_p_policy__e605cf_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0021_alter_eventmatcherpolicy_app...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0022_eventmatcherpolicy_model...
authentik           |  OK
authentik           |   Applying authentik_policies_event_matcher.0023_alter_eventmatcherpolicy_action_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expiry.0002_passwordexpirypolicy_authentik_p_policy__cf73a7_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0002_auto_20200926_1156...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0003_auto_20201203_1223...
authentik           |  OK
authentik           |   Applying authentik_policies_expression.0004_expressionpolicy_authentik_p_policy__fb6feb_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_geoip.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0002_passwordpolicy_password_field...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0003_passwordpolicy_amount_digits...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0004_passwordpolicy_authentik_p_policy__855e80_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_password.0005_passwordpolicy_check_have_i_been_pwned_and_more...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0002_auto_20210529_2046...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0003_reputation_delete_ipreputation_delete_userreputation...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0004_reputationpolicy_authentik_p_policy__8f0d70_idx...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0005_reputation_expires_reputation_expiring...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0006_reputation_ip_asn_data...
authentik           |  OK
authentik           |   Applying authentik_policies_reputation.0007_reputation_authentik_p_identif_9434d7_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0001_squashed_0002_alter_googleworkspaceprovidergroup_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_google_workspace.0003_googleworkspaceprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying guardian.0001_initial...
authentik           |  OK
authentik           |   Applying guardian.0002_generic_permissions_index...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0003_ldapprovider_mfa_support_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_ldap.0004_alter_ldapprovider_options_and_more...
authentik           | Adding content type 'authentik_providers_ldap | ldapprovider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can add LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can change LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can delete LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Can view LDAP Provider'
authentik           | Adding permission 'authentik Providers.LDAP | LDAP Provider | Search full LDAP directory'
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_microsoft_entra.0002_microsoftentraprovidergroup_attributes_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0002_auto_20200520_1108...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0003_auto_20210416_0726...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0004_auto_20210417_1900...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0005_update_provider_type_names...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0006_oauthsource_additional_scopes...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0007_oauthsource_oidc_jwks_oauthsource_oidc_jwks_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0007_auto_20201016_1107_squashed_0017_alter_oauth2provider_token_validity...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0008_rename_rsa_key_oauth2provider_signing_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0009_oauth2provider_verification_keys_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0010_alter_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0011_oauth2provider_jwks_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0012_remove_oauth2provider_verification_keys...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0013_devicetoken...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0014_alter_refreshtoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0015_accesstoken_auth_time_authorizationcode_auth_time_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0016_alter_refreshtoken_token...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0017_accesstoken_session_id_authorizationcode_session_id_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0018_alter_accesstoken_expires_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0019_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0020_remove_accesstoken_authentik_p_token_4bc870_idx_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0021_oauth2provider_encryption_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0022_remove_accesstoken_session_id_and_more...
authentik           | 
authentik           | 
authentik           | Fetching session keys, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to Authorization Code, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Access Token, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Adding session to OAuth2 Refresh Token, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0023_alter_accesstoken_refreshtoken_use_hash_index...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0024_remove_oauth2provider_redirect_uris_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0025_rename_jwks_sources_oauth2provider_jwt_federation_sources_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_oauth2.0026_alter_accesstoken_session_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0001_squashed_0014_proxy_v2...
authentik           |  OK
authentik           |   Applying authentik_providers_proxy.0015_proxyprovider_receive_header_auth...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0001_squashed_0003_alter_connectiontoken_options_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0004_alter_connectiontoken_expires...
authentik           |  OK
authentik           |   Applying authentik_providers_rac.0005_alter_racpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0002_radiusprovider_mfa_support...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0003_radiusproviderpropertymapping...
authentik           |  OK
authentik           |   Applying authentik_providers_radius.0004_alter_radiusproviderpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0007_samlprovider_verification_kp...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0008_auto_20201112_1036...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0009_auto_20201112_2016...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0010_auto_20201230_2112...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0011_samlprovider_name_id_mapping...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0012_managed...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0013_samlprovider_default_relay_state...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0014_alter_samlprovider_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0015_alter_samlpropertymapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_saml.0016_samlprovider_encryption_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0007_scimgroup_scim_id_scimuser_scim_id_and_more...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM users, this might take a couple of minutes...
authentik           | 
authentik           | 
authentik           | Fixing primary key for SCIM groups, this might take a couple of minutes...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0008_rename_scimgroup_scimprovidergroup_and_more...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0009_alter_scimmapping_options...
authentik           |  OK
authentik           |   Applying authentik_providers_scim.0010_scimprovider_verify_certificates...
authentik           |  OK
authentik           |   Applying authentik_rbac.0004_alter_systempermission_options...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_kerberos.0002_kerberossource_kadmin_type...
authentik           |  OK
authentik           |   Applying authentik_sources_ldap.0006_rename_ldappropertymapping_ldapsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_oauth.0008_groupoauthsourceconnection_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0002_auto_20210505_1717...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0003_alter_plexsource_plex_token...
authentik           |  OK
authentik           |   Applying authentik_sources_plex.0004_groupplexsourceconnection_plexsourcepropertymapping_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0001_squashed_0009_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0010_samlsource_pre_authentication_flow...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0011_auto_20210324_0736...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0012_usersamlsourceconnection...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0013_samlsource_verification_kp_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0014_alter_samlsource_digest_algorithm_and_more...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0015_groupsamlsourceconnection_samlsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0016_samlsource_encryption_kp...
authentik           |  OK
authentik           |   Applying authentik_sources_saml.0017_fix_x509subjectname...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_sources_scim.0002_scimsourcepropertymapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0002_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0003_duodevice_last_t...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0004_authenticatorduostage_admin_integration_key_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0005_authenticatorduostage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_duo.0006_duodevice_created_duodevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_endpoint_gdtc.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0001_squashed_0004_auto_20211014_0936...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0002_alter_authenticatorsmsstage_from_number...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0003_smsdevice_last_used_on...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0004_authenticatorsmsstage_verify_only_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0005_authenticatorsmsstage_mapping...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0006_authenticatorsmsstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_sms.0007_smsdevice_created_smsdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0002_otpstaticstage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0003_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0004_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0005_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0006_authenticatorstaticstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0007_authenticatorstaticstage_token_length_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0009_throttling...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_static.0010_staticdevice_created_staticdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0002_auto_20200701_1900...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0003_otptimestage_configure_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0004_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0005_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0006_default_setup_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0007_authenticatortotpstage_friendly_name...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0008_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0009_auto_20190420_0723...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0010_alter_totpdevice_key...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_totp.0011_totpdevice_created_totpdevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0001_squashed_0011_webauthndevice_aaguid...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0002_auto_20210216_0838...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0003_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0004_auto_20210301_0949...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0005_authenticatorvalidatestage_configuration_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0006_auto_20210301_1757...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0007_auto_20210403_0927...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0008_alter_authenticatorvalidatestage_device_classes...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0009_default_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0010_remove_authenticatorvalidatestage_configuration_stage_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0011_authenticatorvalidatestage_last_auth_threshold...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0012_authenticatorvalidatestage_webauthn_user_verification...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_validate.0013_authenticatorvalidatestage_webauthn_allowed_device_types...
authentik           |  OK
authentik           |   Applying authentik_stages_authenticator_webauthn.0012_webauthndevice_created_webauthndevice_last_updated_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0002_captchastage_api_url_captchastage_js_url_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0003_captchastage_error_on_invalid_score_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_captcha.0004_captchastage_interactive...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0002_auto_20200720_0941...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0003_auto_20200924_1403...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0004_alter_userconsent_unique_together_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0005_alter_consentstage_mode...
authentik           |  OK
authentik           |   Applying authentik_stages_consent.0006_alter_userconsent_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_deny.0002_denystage_deny_message...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_dummy.0002_dummystage_throw_error...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0002_emailstage_use_global_settings...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0003_auto_20210404_1054...
authentik           |  OK
authentik           |   Applying authentik_stages_email.0004_emailstage_activate_user_on_success...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0002_passwordstage_change_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0003_passwordstage_failed_attempts_before_cancel...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0004_auto_20200925_1057...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0005_auto_20210402_2221...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0002_auto_20200530_2204_squashed_0013_identificationstage_passwordless_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0014_identificationstage_pretend...
authentik           |  OK
authentik           |   Applying authentik_stages_identification.0015_identificationstage_captcha_stage...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0001_squashed_0006_invitation_name...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0007_invitation_flow...
authentik           |  OK
authentik           |   Applying authentik_stages_invitation.0008_alter_invitation_expires...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0006_passwordchange_rename...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0007_app_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0008_replace_inbuilt...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0009_passwordstage_allow_show_password...
authentik           |  OK
authentik           |   Applying authentik_stages_password.0010_alter_passwordstage_backends...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0008_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0009_prompt_name...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0010_alter_prompt_placeholder_alter_prompt_type...
authentik           |  OK
authentik           |   Applying authentik_stages_prompt.0011_prompt_initial_value_prompt_initial_value_expression_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_redirect.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_source.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_delete.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0002_userloginstage_session_duration...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0003_session_duration_delta...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0004_userloginstage_terminate_other_sessions...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0005_userloginstage_remember_me_offset...
authentik           |  OK
authentik           |   Applying authentik_stages_user_login.0006_userloginstage_geoip_binding_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_logout.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0001_initial...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0002_auto_20200918_1653...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0003_userwritestage_create_users_as_inactive...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0004_userwritestage_create_users_group...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0005_userwritestage_user_path_template...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0006_userwritestage_can_create_users...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0007_remove_userwritestage_can_create_users_and_more...
authentik           |  OK
authentik           |   Applying authentik_stages_user_write.0008_userwritestage_user_type...
authentik           |  OK
authentik           |   Applying authentik_tenants.0003_alter_tenant_default_token_duration...
authentik           |  OK
authentik           |   Applying authentik_tenants.0004_tenant_impersonation_require_reason...
authentik           |  OK
authentik           |   Applying sessions.0001_initial...
authentik           |  OK
authentik           | System check identified no issues (4 silenced).
authentik           | {"domain_url": null, "event": "releasing database lock", "level": "info", "logger": "lifecycle.migrate", "pid": 18, "schema_name": "public", "timestamp": "2025-01-18T05:06:21.437837"}
authentik           | {"event": "Starting gunicorn 23.0.0", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5352387}
authentik           | {"event": "Listening at: unix:/dev/shm/authentik-core.sock (18)", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5357366}
authentik           | {"event": "Using worker: lifecycle.worker.DjangoUvicornWorker", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5357742}
authentik           | {"event": "Booting worker with pid: 76", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5404963}
authentik           | {"event": "Booting worker with pid: 77", "level": "info", "logger": "gunicorn.error", "timestamp": 1737176781.5705762}
authentik           | {"auth_via": "unauthenticated", "domain_url": "localhost", "event": "/-/health/live/", "host": "localhost:8000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "255.255.255.255", "request_id": "91031223a9ad4ae3a373324ae2bc88c6", "runtime": 13, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:22.318272", "user": "", "user_agent": "goauthentik.io/router/healthcheck"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "b4371d9d35ea411799e73e79af2eae8f", "runtime": 13, "schema_name": "public", "scheme": "http", "status": 403, "timestamp": "2025-01-18T05:06:22.341350", "user": "", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"error":"403 Forbidden","event":"Failed to fetch outpost configuration, retrying in 3 seconds","level":"error","logger":"authentik.outpost.ak-api-controller","timestamp":"2025-01-18T05:06:22Z"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "3b118f08d1fc49baa1c7b5d04a73f752", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:23.819775"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "4dd64da42cfd42ae8fff00933b364333", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.242577"}
authentik           | {"domain_url": null, "event": "New outpost saved, ensuring initial token and user are created", "level": "info", "logger": "authentik.outposts.signals", "pid": 76, "schema_name": "public", "timestamp": "2025-01-18T05:06:24.249293"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "6c10715b576343728d23d2b242a32ec5", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.278844"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "9449bfe48cd04c8f94aff57cf165ef79", "task_name": "authentik.outposts.tasks.outpost_post_save", "timestamp": "2025-01-18T05:06:24.285232"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "b23c1366f7b440d9a919289fa7e2bdff", "task_name": "authentik.blueprints.v1.tasks.blueprints_discovery", "timestamp": "2025-01-18T05:06:24.291908"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "9dc85e56ae444382954d83ad253c5d9f", "task_name": "authentik.blueprints.v1.tasks.clear_failed_blueprints", "timestamp": "2025-01-18T05:06:24.292629"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "b1812b6f152049ce82d3964f6426eea1", "task_name": "authentik.core.tasks.clean_expired_models", "timestamp": "2025-01-18T05:06:24.334496"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "ab90a331e3f04e02a7566e45e5bd6730", "task_name": "authentik.core.tasks.clean_temporary_users", "timestamp": "2025-01-18T05:06:24.335986"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "6ae2039eaacc4606b6b50c3e7b5cf174", "task_name": "authentik.enterprise.tasks.enterprise_update_usage", "timestamp": "2025-01-18T05:06:24.337342"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "e58ca1ecfd8d4fbe8e9776a88264045d", "task_name": "authentik.stages.authenticator_webauthn.tasks.webauthn_mds_import", "timestamp": "2025-01-18T05:06:24.338882"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "cc4a63158f9840448512c5c55f0a407f", "task_name": "authentik.crypto.tasks.certificate_discovery", "timestamp": "2025-01-18T05:06:24.340275"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "ddaae92ba8d24bce834c8a2c8ea75564", "task_name": "authentik.admin.tasks.update_latest_version", "timestamp": "2025-01-18T05:06:24.341751"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "68ba9ceef5594ab38dfd107b12f6753d", "task_name": "authentik.blueprints.v1.tasks.blueprints_discovery", "timestamp": "2025-01-18T05:06:24.343643"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "40621db519684051a9dc020c3f0ab15f", "task_name": "authentik.outposts.tasks.outpost_service_connection_monitor", "timestamp": "2025-01-18T05:06:24.345088"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "d81726eb3af047118956134444a80ea8", "task_name": "authentik.outposts.tasks.outpost_token_ensurer", "timestamp": "2025-01-18T05:06:24.346387"}
authentik           | {"domain_url": null, "event": "Task published", "level": "info", "logger": "authentik.root.celery", "pid": 76, "schema_name": "public", "task_id": "54823535f4594390bc3a2c47daf018cd", "task_name": "authentik.events.tasks.notification_cleanup", "timestamp": "2025-01-18T05:06:24.348956"}
authentik           | {"domain_url": null, "event": "authentik Core Worker finished starting", "level": "info", "logger": "authentik.root.signals", "pid": 76, "schema_name": "public", "timestamp": "2025-01-18T05:06:24.349151", "took_s": 2.802407}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "8ef40f68c0784a25b87ed842f46f22cd", "runtime": 32, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.384952", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/root/config/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "1fab68f6f78743b1af4d764ef06e93a2", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.409164", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"domain_url": null, "event": "/ws/outpost/1a2812d4-f65c-4197-881d-0bb066054b86/", "level": "info", "logger": "authentik.asgi", "pid": 77, "remote": "127.0.0.1", "schema_name": "public", "scheme": "ws", "timestamp": "2025-01-18T05:06:25.411078", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"Successfully connected websocket","level":"info","logger":"authentik.outpost.ak-ws","outpost":"1a2812d4-f65c-4197-881d-0bb066054b86","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"event":"Starting Brand TLS Checker","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"event":"updating brand certificates","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/core/brands/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "4b7afe743cd24ec2a452c92d4a075bea", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.595200", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/instances/", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "5ae87c736cec491d85b6121f766cf59f", "runtime": 26, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.730112", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"Starting authentik outpost","hash":"tagged","level":"info","logger":"authentik.outpost","timestamp":"2025-01-18T05:06:25Z","version":"2024.12.2"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/outposts/proxy/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "86693c5d7dce47a29111b3f52003b0a1", "runtime": 25, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.765354", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"event":"updating brand certificates","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:06:25Z"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/core/brands/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "127.0.0.1", "request_id": "cfd98b49dc7e4dbe9f8df5e9d0da6881", "runtime": 14, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:06:25.789866", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "3c1bfa7e95794c2bad864a4147af4efd", "runtime": 25, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:07:12.245086", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "95cee270120240dab083c8084efbdcdf", "runtime": 18, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:12.286057", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/theme-dark.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.296","scheme":"http","size":10945,"status":200,"timestamp":"2025-01-18T05:07:12Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/authentik.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.359","scheme":"http","size":3526,"status":200,"timestamp":"2025-01-18T05:07:12Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/patternfly.min.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"4.439","scheme":"http","size":0,"status":200,"timestamp":"2025-01-18T05:07:12Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/if/admin/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "f13c37a4713e4d93a9e7fce86991447e", "runtime": 20, "schema_name": "public", "scheme": "https", "status": 200, "timestamp": "2025-01-18T05:07:27.446898", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-7AOZD5GQ.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.144","scheme":"http","size":10871,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-Q5HBE575.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.593","scheme":"http","size":55571,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-XJRVUY6X.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.244","scheme":"http","size":12003,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-OX3BUOI2.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.233","scheme":"http","size":19899,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-Y6Y2XBNK.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.540","scheme":"http","size":1098,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-SBMFQ5EF.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"2.988","scheme":"http","size":186040,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/static/dist/admin/chunk-T7FM7PLJ.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"7.377","scheme":"http","size":501361,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/core/brands/current/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "007622e47e0b46ec91de99a3ee6c34be", "runtime": 16, "schema_name": "public", "scheme": "https", "status": 200, "timestamp": "2025-01-18T05:07:27.602415", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/root/config/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "4c99437d0e90454eb3be1489a9d8429e", "runtime": 16, "schema_name": "public", "scheme": "https", "status": 200, "timestamp": "2025-01-18T05:07:27.602978", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"domain_url": null, "event": "/ws/client/", "level": "info", "logger": "authentik.asgi", "pid": 77, "remote": "192.168.1.1", "schema_name": "public", "scheme": "ws", "timestamp": "2025-01-18T05:07:27.611562", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/core/users/me/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "18ddd45e37144b248cf8b3ddfc37c171", "runtime": 15, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.680929", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/enterprise/license/summary/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "f036eed8e8eb40a68d408a2a36bbb0ae", "runtime": 20, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.685083", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/core/brands/current/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "5c40a8dbdd444297a969b0bd6563e329", "runtime": 21, "schema_name": "public", "scheme": "https", "status": 200, "timestamp": "2025-01-18T05:07:27.685708", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/root/config/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "00c99e7105c9480c906a9bac20f145c0", "runtime": 20, "schema_name": "public", "scheme": "https", "status": 200, "timestamp": "2025-01-18T05:07:27.686123", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/version/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "ad26f9349cdb43438bbd4038ac1920e9", "runtime": 17, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.686925", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/version/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "db8411d577704b64bafc2b66b16d19ba", "runtime": 18, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.687515", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/version/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "ea335f9571544b6e954b2807fd365831", "runtime": 15, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.766162", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/outposts/instances/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "3d54d9adcb1d42719004821f34fa57ef", "runtime": 14, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.767211", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/events/events/top_per_user/?action=authorize_application&top_n=11", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "583e91c614cf421f808aaf83e946e505", "runtime": 19, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.779236", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/metrics/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "5f8a73737c1d4ffc8e2e138e23104cc8", "runtime": 21, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.779439", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/providers/scim/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "29407fcaf3224565b97143a4a9b5667e", "runtime": 19, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.780718", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/system/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "83fe1cbf098545c197cedbdcc791a03a", "runtime": 23, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.781520", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/workers/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "6fc12f6c015f4081a68eb4b72dbff9d1", "runtime": 23, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.781849", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/admin/system/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "f61113f7e8474f1a9cca53af8c667339", "runtime": 22, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.782311", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"event":"/if/admin/assets/fonts/overpass-webfont/overpass-bold.woff2","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"192.168.1.1","runtime":"0.145","scheme":"http","size":34752,"status":200,"timestamp":"2025-01-18T05:07:27Z","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/events/notifications/?ordering=-created&page_size=1&seen=false&user=-1", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "7431e594e56a47f3a1967d12aa3bf4aa", "runtime": 9, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.851122", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/events/events/?ordering=-created&page=1&page_size=6", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "42859f93373f4efba8ad9b0f2c17bdb8", "runtime": 10, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.851675", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/api/v3/events/notifications/?ordering=-created&seen=false&user=-1", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "9e91f2eefc8f451381030ce6eea6d0d2", "runtime": 10, "schema_name": "public", "scheme": "https", "status": 403, "timestamp": "2025-01-18T05:07:27.852242", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=%2Fif%2Fadmin%2F%23%2Fadministration%2Foverview", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "192.168.1.1", "request_id": "abdcd0b6a42c4bea985272943facb4c9", "runtime": 30, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:27.871032", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "9ca5986214c2423cb716b5994134c562", "runtime": 6, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:07:47.121839", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "5c036847282a4eebb37dae209bbdde53", "runtime": 10, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:47.151137", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "0a5dd9c68acf42b1a8b48c7267785502", "runtime": 6, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:07:50.066770", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "8b825a2e154842b59a00f6cfb9039802", "runtime": 9, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:50.092758", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "a2679748969647028ac7a758a1093629", "runtime": 6, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:07:50.817910", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "8c44f2213d9a4296982d5ac9c3e7885d", "runtime": 9, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:50.843493", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "805cb46b72ae4ac68b58494d3507b3cb", "runtime": 6, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:07:51.349499", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 77, "remote": "192.168.1.1", "request_id": "0e93945f6c274ca3a578e551674620eb", "runtime": 9, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:07:51.375983", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "14.152.91.159", "request_id": "74c122a766244a619acaab272e650f3d", "runtime": 8, "schema_name": "public", "scheme": "https", "status": 302, "timestamp": "2025-01-18T05:08:41.996830", "user": "", "user_agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"auth_via": "unauthenticated", "domain_url": "login.apsjado.com", "event": "/flows/-/default/authentication/?next=/", "host": "login.apsjado.com", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "14.152.91.159", "request_id": "97d8bd38c3e642eb863e14809c47824e", "runtime": 10, "schema_name": "public", "scheme": "https", "status": 404, "timestamp": "2025-01-18T05:08:42.291743", "user": "", "user_agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/authentik.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.441","scheme":"http","size":3526,"status":200,"timestamp":"2025-01-18T05:08:42Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/custom.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.549","scheme":"http","size":24,"status":200,"timestamp":"2025-01-18T05:08:42Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/standalone/loading/index-2024.12.2.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"4.684","scheme":"http","size":315636,"status":200,"timestamp":"2025-01-18T05:08:42Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/poly-2024.12.2.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"10.170","scheme":"http","size":469446,"status":200,"timestamp":"2025-01-18T05:08:42Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/patternfly.min.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"16.650","scheme":"http","size":1421960,"status":200,"timestamp":"2025-01-18T05:08:42Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/assets/icons/icon_left_brand.svg","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.332","scheme":"http","size":4861,"status":200,"timestamp":"2025-01-18T05:08:43Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/theme-dark.css","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.068","scheme":"http","size":10945,"status":200,"timestamp":"2025-01-18T05:08:43Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/assets/images/flow_background.jpg","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"50.924","scheme":"http","size":791017,"status":200,"timestamp":"2025-01-18T05:08:43Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/standalone/loading/chunk-LTEQ7OUJ.js","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.150","scheme":"http","size":259,"status":200,"timestamp":"2025-01-18T05:08:43Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/assets/fonts/RedHatDisplay/RedHatDisplay-Medium.woff2","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.269","scheme":"http","size":28661,"status":200,"timestamp":"2025-01-18T05:08:44Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"/static/dist/assets/fonts/RedHatText/RedHatText-Regular.woff2","host":"login.apsjado.com","level":"info","logger":"authentik.router","method":"GET","remote":"14.152.91.159","runtime":"0.355","scheme":"http","size":28169,"status":200,"timestamp":"2025-01-18T05:08:44Z","user_agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36 MicroMessenger/7.0.1"}
authentik           | {"event":"updating brand certificates","level":"info","logger":"authentik.router.brand_tls","timestamp":"2025-01-18T05:09:25Z"}
authentik           | {"auth_via": "secret_key", "domain_url": "0.0.0.0", "event": "/api/v3/core/brands/?page=1&page_size=100", "host": "0.0.0.0:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 76, "remote": "127.0.0.1", "request_id": "4f6d4c8af07d4ac794fd459e70811fc5", "runtime": 15, "schema_name": "public", "scheme": "http", "status": 200, "timestamp": "2025-01-18T05:09:25.605180", "user": "ak-outpost-1a2812d4f65c4197881d0bb066054b86", "user_agent": "goauthentik.io/outpost/2024.12.2"}
^Ccanceled
ashwin@ubuntu-server:~/traefik$ docker compose down
docker compose up -d
docker compose logs -f
[+] Running 5/5
 ✔ Container authentik_redis     Removed                                                                                                        0.4s 
 ✔ Container traefik             Removed                                                                                                       10.3s 
 ✔ Container authentik           Removed                                                                                                        0.3s 
 ✔ Container authentik_postgres  Removed                                                                                                        2.5s 
 ✔ Network traefik_traefik-net   Removed                                                                                                        0.2s 
[+] Running 5/5
 ✔ Network traefik_traefik-net   Created                                                                                                        0.1s 
 ✔ Container authentik_postgres  Started                                                                                                        0.6s 
 ✔ Container authentik           Started                                                                                                        0.6s 
 ✔ Container authentik_redis     Started                                                                                                        0.5s 
 ✔ Container traefik             Started                                                                                                        0.5s 
authentik_postgres  | The files belonging to this database system will be owned by user "postgres".
authentik_postgres  | This user must also own the server process.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | The database cluster will be initialized with locale "en_US.utf8".
authentik_postgres  | The default database encoding has accordingly been set to "UTF8".
authentik_postgres  | The default text search configuration will be set to "english".
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Data page checksums are disabled.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | fixing permissions on existing directory /var/lib/postgresql/data ... ok
authentik_postgres  | creating subdirectories ... ok
authentik_postgres  | selecting dynamic shared memory implementation ... posix
authentik_postgres  | selecting default max_connections ... 100
authentik_postgres  | selecting default shared_buffers ... 128MB
authentik_postgres  | selecting default time zone ... UTC
authentik_redis     | 1:C 18 Jan 2025 05:09:47.906 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
authentik_redis     | 1:C 18 Jan 2025 05:09:47.906 # Redis version=6.2.17, bits=64, commit=00000000, modified=0, pid=1, just started
authentik_redis     | 1:C 18 Jan 2025 05:09:47.906 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
authentik_redis     | 1:M 18 Jan 2025 05:09:47.906 * monotonic clock: POSIX clock_gettime
authentik_redis     | 1:M 18 Jan 2025 05:09:47.906 * Running mode=standalone, port=6379.
authentik_redis     | 1:M 18 Jan 2025 05:09:47.906 # Server initialized
authentik_redis     | 1:M 18 Jan 2025 05:09:47.906 # WARNING Memory overcommit must be enabled! Without it, a background save or replication may fail under low memory condition. Being disabled, it can can also cause failures without low memory condition, see https://github.com/jemalloc/jemalloc/issues/1328. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
authentik_redis     | 1:M 18 Jan 2025 05:09:47.907 * Ready to accept connections
authentik_postgres  | creating configuration files ... ok
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176988.1045527, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176988.104785, "count": 11}
authentik_postgres  | running bootstrap script ... ok
authentik_postgres  | sh: locale: not found
authentik_postgres  | 2025-01-18 05:09:48.314 UTC [35] WARNING:  no usable system locales were found
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176988.400903}
authentik_postgres  | performing post-bootstrap initialization ... ok
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176989.4027448}
authentik_postgres  | syncing data to disk ... ok
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | Success. You can now start the database server using:
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  |     pg_ctl -D /var/lib/postgresql/data -l logfile start
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | initdb: warning: enabling "trust" authentication for local connections
authentik_postgres  | You can change this by editing pg_hba.conf or using the option -A, or
authentik_postgres  | --auth-local and --auth-host, the next time you run initdb.
authentik_postgres  | waiting for server to start....2025-01-18 05:09:49.496 UTC [41] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:09:49.501 UTC [41] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:09:49.518 UTC [42] LOG:  database system was shut down at 2025-01-18 05:09:48 UTC
authentik_postgres  | 2025-01-18 05:09:49.525 UTC [41] LOG:  database system is ready to accept connections
authentik_postgres  |  done
authentik_postgres  | server started
authentik_postgres  | CREATE DATABASE
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | /usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | waiting for server to shut down....2025-01-18 05:09:49.917 UTC [41] LOG:  received fast shutdown request
authentik_postgres  | 2025-01-18 05:09:49.924 UTC [41] LOG:  aborting any active transactions
authentik_postgres  | 2025-01-18 05:09:49.925 UTC [41] LOG:  background worker "logical replication launcher" (PID 48) exited with exit code 1
authentik_postgres  | 2025-01-18 05:09:49.925 UTC [43] LOG:  shutting down
authentik_postgres  | 2025-01-18 05:09:49.969 UTC [41] LOG:  database system is shut down
authentik_postgres  |  done
authentik_postgres  | server stopped
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | PostgreSQL init process complete; ready for start up.
authentik_postgres  | 
authentik_postgres  | 
authentik_postgres  | 2025-01-18 05:09:50.040 UTC [1] LOG:  starting PostgreSQL 14.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit
authentik_postgres  | 2025-01-18 05:09:50.040 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
authentik_postgres  | 2025-01-18 05:09:50.040 UTC [1] LOG:  listening on IPv6 address "::", port 5432
authentik_postgres  | 2025-01-18 05:09:50.050 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
authentik_postgres  | 2025-01-18 05:09:50.062 UTC [57] LOG:  database system was shut down at 2025-01-18 05:09:49 UTC
authentik_postgres  | 2025-01-18 05:09:50.069 UTC [1] LOG:  database system is ready to accept connections
authentik           | {"event": "PostgreSQL connection failed, retrying... (connection failed: connection to server at \"172.21.0.4\", port 5432 failed: Connection refused\n\tIs the server running on that host and accepting TCP/IP connections?)", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176990.4034903}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176990.4138987}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176990.4145145}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176990.4145794}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737176991.3528707, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176991.353308, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176991.3546536}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3551924, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3555348, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3573053, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.357858, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.358514, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3588135, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3591197, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3596227, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3603656, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3607488, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.361701, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.362711, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.363047, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3634686, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.3652306, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176991.365731, "path": "authentik.sources.oauth.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:51.694221"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:51.694838"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.712371"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.712658"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.721914"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.722137"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.722690"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.740246"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.759087"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.759545"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.760044"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.766527"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.766855"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.767168"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.767414"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.768779"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.769424"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.770015"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.771157"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.771524"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.775138"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.777045"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.785381"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.785685"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.786052"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.786406"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.786680"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.811465"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.811597"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.812727"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.812781"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.813042"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.813339"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.813727"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.813939"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.814247"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.814449"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.817418"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.817646"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:52.817694"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 0
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176993.435871, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176993.4360783, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176993.719317}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176993.724985}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176993.7255297}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176993.7255664}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737176994.6235387, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176994.6239583, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176994.625524}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6260402, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6267104, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6283808, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6292114, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6298761, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6302772, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.630674, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6309068, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6320705, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.632089, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6326532, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6329641, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6338, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6346107, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6353521, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176994.6357398, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:54.957894"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:54.958506"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.935144"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.935409"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.945225"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.945585"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.946411"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.965523"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.985076"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.985547"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.986067"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.992740"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.993087"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.993411"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.993672"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.995078"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.995759"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.996375"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.997536"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:55.997934"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.001606"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.003555"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.012123"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.012436"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.012828"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.013217"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.013506"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.039283"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.039414"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.040589"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.040648"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.040913"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.041203"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.041592"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.041807"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.042115"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.042315"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.045201"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.045421"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:56.045467"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176996.709798, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176996.7100086, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.0038128}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.0094745}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.0100615}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.010131}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737176997.9008098, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.9012413, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737176997.9027953}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9033084, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.904597, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9058173, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9059775, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9076662, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9081454, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9088874, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9095018, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9098063, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9102159, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9105613, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9109259, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9118106, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9121335, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.91264, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737176997.9129782, "path": "authentik.admin.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:58.240032"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:58.240643"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.211791"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.212057"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.221845"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.222166"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.222936"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.241715"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.261043"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.261522"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.262034"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.268721"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.269060"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.269379"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.269639"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.271003"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.271658"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.272237"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.273380"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.273758"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.277399"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.279310"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.287661"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.287965"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.288336"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.288703"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.288978"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.313837"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.313966"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.315114"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.315167"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.315435"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.315728"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.316116"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.316324"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.316645"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.316846"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.319679"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.319898"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:09:59.319943"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177000.2064495, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177000.206672, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177000.5096107}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177000.5154808}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177000.5161934}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177000.5162385}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737177001.410619, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177001.411046, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177001.4126315}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4131305, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4133532, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.414441, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4156418, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.416095, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.416634, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4179935, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.418745, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4190404, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4194047, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4198244, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4205546, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4209454, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4221172, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.4229674, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177001.423378, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:01.745328"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:01.745931"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.709641"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.709920"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.719186"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.719420"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.719993"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.737491"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.756298"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.756766"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.757259"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.763749"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.764075"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.764392"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.764645"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.766017"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.766674"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.767250"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.768391"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.768766"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.772412"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.774335"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.782747"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.783046"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.783410"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.783775"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.784047"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.809356"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.809487"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.810623"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.810679"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.810944"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.811235"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.811634"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.811846"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.812156"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.812357"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.815243"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.815462"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:02.815511"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177004.0908449, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177004.0910594, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177004.3905497}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177004.3965657}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177004.3972151}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177004.397255}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737177005.2865222, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177005.2869384, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177005.288503}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2890182, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2894359, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2902827, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2913623, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2918818, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.292379, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.292896, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.293091, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2936711, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2940176, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2943544, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2952414, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.295504, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.296832, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2979062, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177005.2986932, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:05.615487"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:05.616093"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.577131"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.577398"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.587142"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.587479"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.588241"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.607000"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.626697"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.627172"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.627699"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.634503"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.634847"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.635173"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.635426"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.636827"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.637488"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.638090"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.639258"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.639650"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.643374"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.645339"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.653883"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.654190"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.654564"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.654941"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.655217"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.680338"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.680469"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.681605"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.681666"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.681937"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.682227"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.682619"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.682834"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.683145"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.683346"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.686182"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.686401"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:06.686452"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177008.7155635, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177008.7158234, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.0117452}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.0176203}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.0182521}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.0182915}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737177009.911627, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.9120615, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177009.9136372}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.91415, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.91467, "path": "authentik.blueprints.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9150362, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.915339, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9158607, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9162524, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9168177, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9184144, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9187715, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.919817, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9205046, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9208074, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9215662, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.922658, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9233496, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177009.9238636, "path": "authentik.providers.scim.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:10.253245"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:10.253962"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.224087"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.224368"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.234169"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.234533"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.235325"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.254278"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.273646"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.274116"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.274621"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.281252"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.281593"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.281922"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.282171"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.283541"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.284187"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.284783"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.285928"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.286297"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.289934"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.291852"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.300253"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.300554"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.300928"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.301289"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.301560"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.326558"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.326694"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.327840"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.327894"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.328164"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.328457"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.328859"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.329072"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.329387"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.329589"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.332433"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.332661"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:11.332708"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1
authentik           | {"event": "Loaded config", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177014.9868557, "file": "/authentik/lib/default.yml"}
authentik           | {"event": "Loaded environment variables", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177014.9870617, "count": 11}
authentik           | {"event": "Starting authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177015.285721}
authentik           | {"event": "PostgreSQL connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177015.291456}
authentik           | {"event": "Redis Connection successful", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177015.2920995}
authentik           | {"event": "Finished authentik bootstrap", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177015.2921596}
authentik           | {"event": "Failed to parse config as int", "level": "warning", "logger": "authentik.lib.config", "timestamp": 1737177016.1903152, "path": "postgresql.conn_max_age", "exc": "int() argument must be a string, a bytes-like object or a real number, not 'type'"}
authentik           | {"event": "Booting authentik", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177016.1907656, "version": "2024.12.2"}
authentik           | {"event": "Enabled authentik enterprise", "level": "info", "logger": "authentik.lib.config", "timestamp": 1737177016.1923344}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.192847, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.193275, "path": "authentik.enterprise.providers.microsoft_entra.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1939483, "path": "authentik.sources.kerberos.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.194713, "path": "authentik.sources.plex.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1953378, "path": "authentik.crypto.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1957154, "path": "authentik.enterprise.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1970012, "path": "authentik.sources.ldap.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1976547, "path": "authentik.sources.oauth.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.1981099, "path": "authentik.admin.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.198532, "path": "authentik.outposts.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.199056, "path": "authentik.enterprise.providers.google_workspace.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.200302, "path": "authentik.providers.scim.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.200758, "path": "authentik.stages.authenticator_webauthn.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.2017193, "path": "authentik.events.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.201914, "path": "authentik.stages.authenticator_totp.settings"}
authentik           | {"event": "Loaded app settings", "level": "debug", "logger": "authentik.lib.config", "timestamp": 1737177016.2023036, "path": "authentik.blueprints.settings"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-ASN.mmdb", "last_write": 1736444074.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:16.523658"}
authentik           | {"domain_url": null, "event": "Loaded MMDB database", "file": "/geoip/GeoLite2-City.mmdb", "last_write": 1736444073.0, "level": "info", "logger": "authentik.events.context_processors.mmdb", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:16.524277"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.checks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.499510"}
authentik           | {"app_name": "authentik.tenants", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.tenants.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.499797"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.509140"}
authentik           | {"app_name": "authentik.admin", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.admin.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.509364"}
authentik           | {"app_name": "authentik.crypto", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.crypto.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.509926"}
authentik           | {"app_name": "authentik.flows", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.flows.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.529203"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.548312"}
authentik           | {"app_name": "authentik.outposts", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.outposts.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.548791"}
authentik           | {"app_name": "authentik.policies.reputation", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.reputation.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.549301"}
authentik           | {"app_name": "authentik.policies", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.policies.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.555850"}
authentik           | {"app_name": "authentik.providers.oauth2", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.oauth2.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.556188"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.556516"}
authentik           | {"app_name": "authentik.providers.proxy", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.proxy.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.556781"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.558161"}
authentik           | {"app_name": "authentik.providers.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.providers.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.558827"}
authentik           | {"app_name": "authentik.rbac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.rbac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.559409"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.560556"}
authentik           | {"app_name": "authentik.sources.kerberos", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.kerberos.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.560939"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.564579"}
authentik           | {"app_name": "authentik.sources.ldap", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.ldap.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.566493"}
authentik           | {"app_name": "authentik.sources.oauth", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.oauth.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.574846"}
authentik           | {"app_name": "authentik.sources.saml", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.saml.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.575158"}
authentik           | {"app_name": "authentik.sources.scim", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.sources.scim.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.575537"}
authentik           | {"app_name": "authentik.stages.authenticator_duo", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_duo.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.575914"}
authentik           | {"app_name": "authentik.stages.authenticator_static", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_static.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.576194"}
authentik           | {"app_name": "authentik.stages.authenticator_webauthn", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.authenticator_webauthn.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.601150"}
authentik           | {"app_name": "authentik.stages.email", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.stages.email.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.601284"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.602450"}
authentik           | {"app_name": "authentik.core", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.core.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.602505"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.602790"}
authentik           | {"app_name": "authentik.enterprise", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.603109"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.603510"}
authentik           | {"app_name": "authentik.enterprise.providers.google_workspace", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.google_workspace.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.603728"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.604044"}
authentik           | {"app_name": "authentik.enterprise.providers.microsoft_entra", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.microsoft_entra.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.604246"}
authentik           | {"app_name": "authentik.enterprise.providers.rac", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.enterprise.providers.rac.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.607073"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.tasks", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.607290"}
authentik           | {"app_name": "authentik.events", "domain_url": null, "event": "Imported related module", "level": "info", "logger": "authentik.blueprints.apps", "module": "authentik.events.signals", "pid": 7, "schema_name": "public", "timestamp": "2025-01-18T05:10:17.607335"}
authentik           | Unknown command: 'server+worker'. Did you mean runworker?
authentik           | Type 'manage.py help' for usage.
authentik exited with code 1

version: "3.3"

networks:
  traefik-net:
    external: false

services:
  ##########################################
  # Traefik
  ##########################################
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    networks:
      - traefik-net

    ports:
      - "80:80"     # HTTP
      - "443:443"   # HTTPS

    # We'll store Traefik config in the same folder as this docker-compose.yml
    volumes:
      # Traefik File-based config (if you use traefik.yml)
      - "./traefik.yml:/traefik.yml:ro"

      # ACME (Let's Encrypt) certificate file
      - "./acme.json:/letsencrypt/acme.json"

      # Docker socket (read-only) so Traefik can detect container labels
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

    command:
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"

      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt (ACME) settings
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"

    # No labels here for the dashboard domain, unless you want to expose it.
    # If you do, you can add your domain rule for the dashboard.

  ##########################################
  # Authentik
  ##########################################
  authentik:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik
    restart: unless-stopped
    command: "server+worker"
    networks:
      - traefik-net

    # If you want to access it directly on the host (optional):
    # ports:
    #   - "127.0.0.1:9000:9000"

    labels:
      # Enable Traefik for this service
      - "traefik.enable=true"

      # Route domain login.apsjado.com to the Authentik container
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"

      # Authentik container listens on port 9000, so direct traffic there
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"

    environment:

      AUTHENTIK_SECRET_KEY: "3PqLoxRxB6B7oCGw9MLWSRWU7BhNhbktqa1i5wJgn46K8klPUyu5"
      # Make sure your domain here matches your external URL
      AUTHENTIK_HOST: "https://login.apsjado.com"

      # Database configuration (PostgreSQL)
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik

      # Redis configuration
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"

      # BOOTSTRAP an admin user
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"

      # Email configuration (optional but recommended)
#      AUTHENTIK_EMAIL__HOST: smtp.yourprovider.com
#      AUTHENTIK_EMAIL__PORT: "587"
#      AUTHENTIK_EMAIL__USERNAME: your_smtp_user
#      AUTHENTIK_EMAIL__PASSWORD: your_smtp_pass
#      AUTHENTIK_EMAIL__USE_TLS: "True"

  ##########################################
  # PostgreSQL
  ##########################################
  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    restart: unless-stopped
    networks:
      - traefik-net
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: your_db_password

  ##########################################
  # Redis
  ##########################################
  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped
    networks:
      - traefik-net


Skip to content
Navigation Menu

    goauthentik

    authentik

Code
Issues 618
Pull requests 124
Discussions
Actions
Security 18

    Insights

Authentik not showing intial user signup #4183
Closed
Closed
Authentik not showing intial user signup
#4183
@amitavaghosh1
Description
amitavaghosh1
opened on Dec 8, 2022 · edited by amitavaghosh1

Describe the bug
A clear and concise description of what the bug is.

When I tried to access, localhost:9000 or http://localhost:9000/if/flow/initial-setup/ It redirects to http://localhost:9000/flows/-/default/authentication/?next=/ And shows a webpage saying. Not Found

To Reproduce
Steps to reproduce the behavior:

    docker prune exsisting volumes and images. docker container prune; docker image prune; docker volume prune
    set the authentik secret, db username password in .env
    do docker-compose up
    access the http://localhost:9000/if/flow/initial-setup/

Expected behavior
Show the default signup page

Screenshots

Logs

server_1      | {"auth_via": "unauthenticated", "event": "/-/health/ready/", "host": "localhost:9000", "level": "info", "logger": "authentik.asgi", "method": "HEAD", "pid": 23, "remote": "127.0.0.1", "request_id": "0b05a58a3f5a49d3a2bcfe3954dfe6c5", "runtime": 14, "scheme": "http", "status": 204, "timestamp": "2022-12-08T08:02:33.468877", "user": "", "user_agent": "goauthentik.io lifecycle Healthcheck"}
server_1      | {"auth_via": "unauthenticated", "event": "/if/flow/initial-setup/", "host": "localhost:9000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 23, "remote": "172.26.0.1", "request_id": "afd7146497974f449b397caa9345dc76", "runtime": 29, "scheme": "http", "status": 404, "timestamp": "2022-12-08T08:02:39.818211", "user": "", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0"}
server_1      | {"event": "Not Found: /if/flow/initial-setup/", "level": "warning", "logger": "django.request", "timestamp": 1670486559.8202548}
server_1      | {"auth_via": "unauthenticated", "event": "/-/health/live/", "host": "localhost:8000", "level": "info", "logger": "authentik.asgi", "method": "GET", "pid": 23, "remote": "127.0.0.1", "request_id": "0c48202ee11d4c269aa179b84b40aa6a", "runtime": 17, "scheme": "http", "status": 204, "timestamp": "2022-12-08T08:02:43.120408", "user": "", "user_agent": "goauthentik.io/proxy/healthcheck"}

Version and Deployment (please complete the following information):

    authentik version: [2022.11.1]
    Deployment: [docker-compose]

Additional context

Also there is no documentation on what is Configuration Stages. The documentation is so bad, its so difficult to understand as a begineer.

ANyway, here is the. docker compose I am using

---
version: '3.4'

services:
  postgresql:
    image: postgres:13-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      start_period: 20s
      interval: 30s
      retries: 5
      timeout: 5s
    volumes:
      - database:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${PG_PASS:-authentik}
      - POSTGRES_USER=${PG_USER:-authentik_dev_user}
      - POSTGRES_DB=${PG_DB:-authentik_dev}
    env_file:
      - .env
    ports:
      - "5432:5432"
  redis:
    image: redis:alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      start_period: 20s
      interval: 30s
      retries: 5
      timeout: 3s
    ports:
      - "6379:6379"
  server:
    image: ${AUTHENTIK_IMAGE:-ghcr.io/goauthentik/server}:${AUTHENTIK_TAG:-2022.11.1}
    restart: unless-stopped
    command: server
    environment:
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: ${PG_USER:-authentik_dev_user}
      AUTHENTIK_POSTGRESQL__NAME: ${PG_DB:-authentik_dev}
      AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS:-authentik}
    volumes:
      - ./media:/media
      - ./custom-templates:/templates
    env_file:
      - .env
    ports:
      - "0.0.0.0:${AUTHENTIK_PORT_HTTP:-9000}:9000"
      - "0.0.0.0:${AUTHENTIK_PORT_HTTPS:-9443}:9443"
  # worker:
    # image: ${AUTHENTIK_IMAGE:-ghcr.io/goauthentik/server}:${AUTHENTIK_TAG:-2022.11.1}
    # restart: unless-stopped
    # command: worker
    # environment:
      # AUTHENTIK_REDIS__HOST: redis
      # AUTHENTIK_POSTGRESQL__HOST: postgresql
      # AUTHENTIK_POSTGRESQL__USER: ${PG_USER:-authentik_dev_user}
      # AUTHENTIK_POSTGRESQL__NAME: ${PG_DB:-authentik_dev}
      # AUTHENTIK_POSTGRESQL__PASSWORD: ${PG_PASS:-authentik}
    # user: root
    # volumes:
      # - ./media:/media
      # - ./certs:/certs
      # - /var/run/docker.sock:/var/run/docker.sock
      # - ./custom-templates:/templates
    # env_file:
      # - .env
  # geoipupdate:
    # image: "maxmindinc/geoipupdate:latest"
    # volumes:
      # - "geoip:/usr/share/GeoIP"
    # environment:
      # GEOIPUPDATE_EDITION_IDS: "GeoLite2-City"
      # GEOIPUPDATE_FREQUENCY: "8"
    # env_file:
      # - .env

volumes:
  database:
    driver: local
  # geoip:
    # driver: local

Activity
amitavaghosh1
added
bugSomething isn't working
on Dec 8, 2022
simonszu
simonszu commented on Dec 14, 2022
simonszu
on Dec 14, 2022

I have the same problem. Not very sure how to proceed from here.
BeryJu
BeryJu commented on Dec 14, 2022
BeryJu
on Dec 14, 2022
Member

The worker container needs to be running as it creates all the default objects
simonszu
simonszu commented on Dec 14, 2022
simonszu
on Dec 14, 2022

Good to know. I had the worker running, but it failed to connect to the PgSQL. I fixed the connection, and now its working for me :)
kmanwar89
kmanwar89 commented on Dec 15, 2022
kmanwar89
on Dec 15, 2022 · edited by kmanwar89

    Good to know. I had the worker running, but it failed to connect to the PgSQL. I fixed the connection, and now its working for me :)

As someone who is currently facing this issue, would you mind sharing what the fix was? To add, I am facing this issue while using the 2022.10.1 version. I have the docker-compose file copied verbatim from the GitHub page, and can reproduce this issue on two different machines, both of which are hosting dozens of other services.
simonszu
simonszu commented on Dec 16, 2022
simonszu
on Dec 16, 2022

@kmanwar89 Have a look at the output of the logs of the worker. In my case i have Postgres installed in a native way without containers to have only one server running for several applications. I have an additional /etc/hosts config added to the dockerfile to let the containers access its host via the FQDN "host.docker.internal" and set the Postgres host in the config to that value. However, i forgot to add this additional host config to the server and the worker, so the server was connecting to postgres just fine, but the worker had the problem "host not found".

However, this applies to my special situation. As i said, please have a look at the logs of your workers and check what their problem is.
BeryJu
mentioned this on Dec 26, 2022

    Cannot reach to the admin signup page in authentik #4288

amitavaghosh1
amitavaghosh1 commented on Dec 26, 2022
amitavaghosh1
on Dec 26, 2022
Author

Ok, so the older docker-compose file doesn't work with the new docker image. So when I switched the new docker-compose.yaml, it worked alright. I notice that the new compose file, also doesn't use geoip as a service. Coool.

Thanks guys, and sorry for the trouble.
amitavaghosh1
closed this as completedon Dec 26, 2022
amitavaghosh1
amitavaghosh1 commented on Dec 26, 2022
amitavaghosh1
on Dec 26, 2022
Author

@BeryJu could you please help me with setting up a sms based totp sending, which appears after user enters the password?
I am not able to understand how to properly configure the flow. And where from will authentik get the users phone number. need to know where to set it.
ocean-haiyang
ocean-haiyang commented on Jun 16, 2024
ocean-haiyang
on Jun 16, 2024

this fix doesn't work for me
werty1st
werty1st commented on Jun 25, 2024
werty1st
on Jun 25, 2024 · edited by werty1st

I "solved" it by starting with a docker image version from 2023. after the initial setup you can upgrade to the current version. at least something is running now :D
alxlion
alxlion commented on Jul 18, 2024
alxlion
on Jul 18, 2024

I solved it by following these steps: https://docs.goauthentik.io/docs/troubleshooting/login
solidDoWant
mentioned this on Nov 25, 2024

    Out of box blueprints fail to load (according to DB) despite worker reporting SUCCESS #12186

wbywfjptrgmuMJxByvFD
Add a comment
new Comment
Markdown input: edit mode selected.
Remember, contributions to this repository should follow its contributing guidelines, security policy and code of conduct.
Assignees
No one assigned

Labels
bugSomething isn't working
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
@simonszu
@alxlion
@BeryJu
@werty1st
@kmanwar89
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

Authentik not showing intial user signup · Issue #4183 · goauthentik/authentik

#### ChatGPT:
<time datetime="2025-01-18T05:13:50.184Z" title="1/18/2025, 2:13:50 PM">14:13</time>

**TL;DR: Authentik can’t recognize `"server+worker"` as a valid command, causing container restarts.\
To fix it, you must run two containers: one with `command: "server"` and another with `command: "worker"`**—or, as an alternative, run a single “all-in-one” container by setting an environment variable.

---

## Why You’re Seeing “Unknown command: 'server+worker'”

In the **older** Authentik images, you could run a single container with `server+worker`. But in **newer** versions, **each** process (server vs. worker) must run in its **own** container. When Authentik sees `server+worker`, it doesn’t find that as a valid subcommand, so the container exits with:

```
Unknown command: 'server+worker'
Did you mean runworker?
```

---

## 1. Correct Approach: Two Containers

**Recommended** approach is to run **two** Authentik containers, **one** for the main server and **one** for the background worker. For example:

```yaml
version: "3.3"

networks:
  traefik-net:
    external: false

services:
  traefik:
    # ... same as your existing

  # ===============================
  # Authentik SERVER container
  # ===============================
  authentik_server:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik_server
    restart: unless-stopped
    command: "server"  # <–– Only run the server part
    networks:
      - traefik-net
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"
    environment:
      AUTHENTIK_SECRET_KEY: "..."
      AUTHENTIK_HOST: "https://login.apsjado.com"
      # same DB, Redis, etc. environment as before
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"
      # Admin bootstrap user
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"

  # ===============================
  # Authentik WORKER container
  # ===============================
  authentik_worker:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik_worker
    restart: unless-stopped
    command: "worker"  # <–– Only run the background worker
    networks:
      - traefik-net
    environment:
      AUTHENTIK_SECRET_KEY: "..."
      AUTHENTIK_HOST: "https://login.apsjado.com"
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"

  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    # ...

  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    # ...
```

With **both** `authentik_server` and `authentik_worker` running:

- The **server** container handles HTTP requests (web UI, flows).
- The **worker** container applies migrations, processes background tasks, and creates the default flows/objects.

If you only start `server` but **not** `worker`, many crucial tasks (like generating default flows, brand, etc.) do not happen, leading to 404s on `/flows/-/default/authentication/`.

---

## 2. Alternative: “All-in-One” Single Container

If you truly want a single container (like older images), you can do so with an environment variable:

```yaml
authentik:
  image: ghcr.io/goauthentik/server:latest
  # ...
  environment:
    AUTHENTIK_INSTALL_MODE: "all"  # <-- Forces a combined single-process approach
```

This tells Authentik to run both the server and worker processes **inside** a single container. However, keep in mind that the official best practice now is **two containers**—one for server, one for worker.

---

## 3. Why You See 404 on “/flows/-/default/authentication”

Even with your `server` container running, you might get a 404 at:

```
https://login.apsjado.com/flows/-/default/authentication/
```

**Because** the worker never ran to create (or import) the default flows. Once the worker is up, it automatically applies migrations, runs default blueprint tasks, and then the 404 for the main login flow goes away.

---

## 4. That “conn\_max\_age” Warning

You might notice logs about:

```
"Failed to parse config as int" ... "postgresql.conn_max_age"
```

It’s only a **warning**, typically safe to ignore. If you want to remove it, ensure your environment variables do not mistakenly set something like `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE` to a non-integer. By default, that’s not set.

---

## 5. Summary

1. **Remove** `command: "server+worker"`.
2. **Use** two separate containers—**or** set `AUTHENTIK_INSTALL_MODE: "all"` to run everything in one container.
3. **Ensure** your worker container is up, so it can do background tasks and create default flows.

Once you have the worker running, your Authentik instance will auto-create the default login flow, and you’ll no longer get “Not Found” on `flows/-/default/authentication`. You’ll be able to sign in and reach the admin UI.


#### You:
<time datetime="2025-01-18T05:14:20.243Z" title="1/18/2025, 2:14:20 PM">14:14</time>

version: "3.3"

networks:
  traefik-net:
    external: false

services:
  ##########################################
  # Traefik
  ##########################################
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    networks:
      - traefik-net

    ports:
      - "80:80"     # HTTP
      - "443:443"   # HTTPS

    # We'll store Traefik config in the same folder as this docker-compose.yml
    volumes:
      # Traefik File-based config (if you use traefik.yml)
      - "./traefik.yml:/traefik.yml:ro"

      # ACME (Let's Encrypt) certificate file
      - "./acme.json:/letsencrypt/acme.json"

      # Docker socket (read-only) so Traefik can detect container labels
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

    command:
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"

      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt (ACME) settings
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"

    # No labels here for the dashboard domain, unless you want to expose it.
    # If you do, you can add your domain rule for the dashboard.

  # ===============================
    # Authentik SERVER container
    # ===============================
    authentik_server:
      image: ghcr.io/goauthentik/server:latest
      container_name: authentik_server
      restart: unless-stopped
      command: "server"  # <–– Only run the server part
      networks:
        - traefik-net
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
        - "traefik.http.routers.authentik.entrypoints=websecure"
        - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"
        - "traefik.http.services.authentik.loadbalancer.server.port=9000"
      environment:
        AUTHENTIK_SECRET_KEY: "..."
        AUTHENTIK_HOST: "https://login.apsjado.com"
        # same DB, Redis, etc. environment as before
        AUTHENTIK_POSTGRESQL__HOST: postgresql
        AUTHENTIK_POSTGRESQL__USER: authentik
        AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
        AUTHENTIK_POSTGRESQL__NAME: authentik
        AUTHENTIK_REDIS__HOST: redis
        AUTHENTIK_REDIS__PORT: "6379"
        # Admin bootstrap user
        AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
        AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
        AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"
    
    # ===============================
    # Authentik WORKER container
    # ===============================
    authentik_worker:
      image: ghcr.io/goauthentik/server:latest
      container_name: authentik_worker
      restart: unless-stopped
      command: "worker"  # <–– Only run the background worker
      networks:
        - traefik-net
      environment:
        AUTHENTIK_SECRET_KEY: "..."
        AUTHENTIK_HOST: "https://login.apsjado.com"
        AUTHENTIK_POSTGRESQL__HOST: postgresql
        AUTHENTIK_POSTGRESQL__USER: authentik
        AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
        AUTHENTIK_POSTGRESQL__NAME: authentik
        AUTHENTIK_REDIS__HOST: redis
        AUTHENTIK_REDIS__PORT: "6379"
        AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "green.text5235@fastmail.com"
        AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "password"
        AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"
  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    restart: unless-stopped
    networks:
      - traefik-net
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: your_db_password

  ##########################################
  # Redis
  ##########################################
  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped
    networks:
      - traefik-net

#### ChatGPT:
<time datetime="2025-01-18T05:14:50.887Z" title="1/18/2025, 2:14:50 PM">14:14</time>

Below is a **cleaned-up** Docker Compose example that runs **two separate** Authentik containers—one for the **server** and one for the **worker**—behind Traefik. Just copy this as `docker-compose.yml` (adjust environment variables for your passwords and secrets), then run:

```bash
docker compose down
docker compose up -d
```

---

```yaml
version: "3.3"

networks:
  traefik-net:
    external: false

services:
  ##############################################################################
  #                            1) TRAEFIK REVERSE PROXY
  ##############################################################################
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    networks:
      - traefik-net
    ports:
      - "80:80"    # HTTP
      - "443:443"  # HTTPS
    volumes:
      # main Traefik config (if you prefer file-based)
      - "./traefik.yml:/traefik.yml:ro"

      # ACME (Let's Encrypt) certificate storage
      - "./acme.json:/letsencrypt/acme.json"

      # Docker socket (read-only) so Traefik can detect container labels
      - "/var/run/docker.sock:/var/run/docker.sock:ro"

    command:
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"

      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt (ACME)
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=youremail@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"

  ##############################################################################
  #                      2) AUTHENTIK SERVER CONTAINER
  ##############################################################################
  authentik_server:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik_server
    restart: unless-stopped
    command: "server"  # only runs the web server
    networks:
      - traefik-net
    labels:
      # enable Traefik for this container
      - "traefik.enable=true"

      # route https://login.apsjado.com → this container
      - "traefik.http.routers.authentik.rule=Host(`login.apsjado.com`)"
      - "traefik.http.routers.authentik.entrypoints=websecure"
      - "traefik.http.routers.authentik.tls.certresolver=letsencrypt"

      # Traefik → port 9000 in the authentik container
      - "traefik.http.services.authentik.loadbalancer.server.port=9000"

    environment:
      # Required secret key for authentik
      AUTHENTIK_SECRET_KEY: "super-random-secret-key"
      # set to your real domain
      AUTHENTIK_HOST: "https://login.apsjado.com"

      # Database config
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik

      # Redis config
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"

      # Optional admin bootstrap
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "admin@example.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "changeit"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"


  ##############################################################################
  #                      3) AUTHENTIK WORKER CONTAINER
  ##############################################################################
  authentik_worker:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik_worker
    restart: unless-stopped
    command: "worker"  # runs background tasks
    networks:
      - traefik-net
    environment:
      AUTHENTIK_SECRET_KEY: "super-random-secret-key"
      AUTHENTIK_HOST: "https://login.apsjado.com"

      # Same DB config
      AUTHENTIK_POSTGRESQL__HOST: postgresql
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: your_db_password
      AUTHENTIK_POSTGRESQL__NAME: authentik

      # Same Redis config
      AUTHENTIK_REDIS__HOST: redis
      AUTHENTIK_REDIS__PORT: "6379"

      # Admin bootstrap
      AUTHENTIK_BOOTSTRAP_ADMIN_EMAIL: "admin@example.com"
      AUTHENTIK_BOOTSTRAP_ADMIN_PASSWORD: "changeit"
      AUTHENTIK_BOOTSTRAP_ADMIN_USERNAME: "admin"


  ##############################################################################
  #                      4) POSTGRESQL DATABASE
  ##############################################################################
  postgresql:
    image: postgres:14-alpine
    container_name: authentik_postgres
    restart: unless-stopped
    networks:
      - traefik-net
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: your_db_password


  ##############################################################################
  #                            5) REDIS
  ##############################################################################
  redis:
    image: redis:6-alpine
    container_name: authentik_redis
    restart: unless-stopped
    networks:
      - traefik-net
```

### How This Works

1. **Traefik** listens on ports 80/443 and routes `Host(login.apsjado.com)` to the `authentik_server` container’s port 9000.
2. **authentik\_server** runs only the web server.
3. **authentik\_worker** runs the worker process (handles database migrations, blueprint loading, background tasks).
4. **PostgreSQL** provides the database for both the server and worker.
5. **Redis** is used by Authentik for caching and queue tasks.

Once you bring this stack up with `docker compose up -d`, both the server and worker will start. The worker will handle creating default flows/blueprints, and you’ll be able to visit `https://login.apsjado.com` to see Authentik’s login page without the “Not Found” error.


#### You:
<time datetime="2025-01-18T05:18:20.477Z" title="1/18/2025, 2:18:20 PM">14:18</time>

what are the login cred