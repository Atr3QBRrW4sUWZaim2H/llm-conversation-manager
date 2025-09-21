---
title: Supavisor tenant connection error
source: https://chatgpt.com/c/678d96b1-1cf8-8003-8524-339dcc1e5e7e
---

# Supavisor tenant connection error

#### You:
<time datetime="2025-01-20T00:20:01.554Z" title="1/20/2025, 9:20:01 AM">09:20</time>

connection to server at "192.168.1.200", port 5432 failed: FATAL:  Tenant or user not found

    | 00:19:04.801 request_id=GBw-kBS0XImec90AAA6E region=local [info] Sent 204 in 73µs
supabase-pooler                 | 00:19:05.279 region=local [error] ClientHandler: User requested SSL connection but no downstream cert/key found
supabase-pooler                 | 00:19:05.279 region=local [error] ClientHandler: User not found: "Either external_id or sni_hostname must be provided" {:single, "supabase_admin", nil}
supabase-pooler                 | 00:19:05.279 region=local [warning] client_join is called with a mismatched id: nil
supabase-pooler                 | 00:19:05.279 region=local [warning] ClientHandler: socket closed with reason {:shutdown, :user_not_found}
supabase-analytics              | 
supabase-analytics              | 
supabase-analytics              | 00:19:05.423 [info] All logs logged!
supabase-analytics              | 
supabase-analytics              | 
supabase-analytics              | 00:19:05.423 [info] Logs last second!
supabase-analytics              | 
supabase-analytics              | 
supabase-analytics              | 00:19:05.919 [info] Process metrics!
supabase-pooler                 | 00:19:06.040 region=local [error] ClientHandler: User requested SSL connection but no downstream cert/key found
supabase-pooler                 | 00:19:06.040 region=local [error] ClientHandler: User not found: "Either external_id or sni_hostname must be provided

version: "3.9"

################################################################################
# USAGE:
#   docker compose up
#   docker compose down
################################################################################

services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:20250113-83c9420
    restart: unless-stopped
    healthcheck:
      test:
        [
          "CMD",
          "node",
          "-e",
          "fetch('http://studio:3000/api/profile').then((r) => {if (r.status !== 200) throw new Error(r.status)})"
        ]
      timeout: 10s
      interval: 5s
      retries: 3
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      # Inlined environment values
      STUDIO_PG_META_URL: "http://meta:8080"
      POSTGRES_PASSWORD: "supabase"

      DEFAULT_ORGANIZATION_NAME: "MyOrganization"
      DEFAULT_PROJECT_NAME: "MyProject"
      OPENAI_API_KEY: ""  # or leave blank

      SUPABASE_URL: "http://kong:8000"
      SUPABASE_PUBLIC_URL: "http://localhost:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      AUTH_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      LOGFLARE_PUBLIC_ACCESS_TOKEN: ""
      LOGFLARE_URL: "http://analytics:4000"
      NEXT_PUBLIC_ENABLE_LOGS: "true"
      NEXT_ANALYTICS_BACKEND_PROVIDER: "postgres"
      # Uncomment if using BigQuery for analytics
      # NEXT_ANALYTICS_BACKEND_PROVIDER: "bigquery"

  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    restart: unless-stopped
    entrypoint: bash -c 'eval "echo \"$$(cat ~/temp.yml)\"" > ~/kong.yml && /docker-entrypoint.sh kong docker-start'
    ports:
      - "8000:8000/tcp"   # From KONG_HTTP_PORT=8000
      - "8443:8443/tcp"   # From KONG_HTTPS_PORT=8443
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: "/home/kong/kong.yml"
      KONG_DNS_ORDER: "LAST,A,CNAME"
      KONG_PLUGINS: "request-transformer,cors,key-auth,acl,basic-auth"
      KONG_NGINX_PROXY_PROXY_BUFFER_SIZE: "160k"
      KONG_NGINX_PROXY_PROXY_BUFFERS: "64 160k"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      DASHBOARD_USERNAME: "admin"
      DASHBOARD_PASSWORD: "supabase"
    volumes:
      - "./volumes/api/kong.yml:/home/kong/temp.yml:ro"

  auth:
    container_name: supabase-auth
    image: supabase/gotrue:v2.167.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://localhost:9999/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: "0.0.0.0"
      GOTRUE_API_PORT: "9999"
      API_EXTERNAL_URL: "http://127.0.0.1:8080"  # originally API_EXTERNAL_URL was blank

      GOTRUE_DB_DRIVER: "postgres"
      # => "postgres://supabase_auth_admin:POSTGRES_PASSWORD@POSTGRES_HOST:POSTGRES_PORT/POSTGRES_DB"
      GOTRUE_DB_DATABASE_URL: "postgres://supabase_auth_admin:supabase@db:5432/supabase"

      GOTRUE_SITE_URL: "http://localhost:3000"
      GOTRUE_URI_ALLOW_LIST: "http://localhost:3000"
      GOTRUE_DISABLE_SIGNUP: "false"

      GOTRUE_JWT_ADMIN_ROLES: "service_role"
      GOTRUE_JWT_AUD: "authenticated"
      GOTRUE_JWT_DEFAULT_GROUP_NAME: "authenticated"
      GOTRUE_JWT_EXP: "3600"
      GOTRUE_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
      GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED: "false"
      GOTRUE_MAILER_AUTOCONFIRM: "false"

      # Phone signups
      GOTRUE_EXTERNAL_PHONE_ENABLED: "false"
      GOTRUE_SMS_AUTOCONFIRM: "false"

      # Mailer / SMTP
      GOTRUE_SMTP_ADMIN_EMAIL: "myadmin@example.com"
      GOTRUE_SMTP_HOST: "mail.example.com"
      GOTRUE_SMTP_PORT: "587"
      GOTRUE_SMTP_USER: "my-smtp-user"
      GOTRUE_SMTP_PASS: "my-smtp-password"
      GOTRUE_SMTP_SENDER_NAME: "My App Emailer"
      GOTRUE_MAILER_URLPATHS_INVITE: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_CONFIRMATION: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_RECOVERY: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE: "/auth/v1/verify"

  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:v12.2.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PGRST_DB_URI: "postgres://authenticator:supabase@db:5432/supabase"
      PGRST_DB_SCHEMAS: "public"
      PGRST_DB_ANON_ROLE: "anon"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_DB_USE_LEGACY_GUCS: "false"
      PGRST_APP_SETTINGS_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_APP_SETTINGS_JWT_EXP: "3600"
    command: "postgrest"

  realtime:
    container_name: realtime-dev.supabase-realtime
    image: supabase/realtime:v2.33.70
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    # healthcheck:
    #   test:
    #     [
    #       "CMD",
    #       "curl",
    #       "-sSfL",
    #       "--head",
    #       "-o",
    #       "/dev/null",
    #       "-H",
    #       "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg",
    #       "http://localhost:4000/api/tenants/realtime-dev/health"
    #     ]
    #   timeout: 5s
    #   interval: 5s
    #   retries: 3
    restart: unless-stopped
    environment:
      PORT: "4000"
      DB_HOST: "db"
      DB_PORT: "5432"
      DB_USER: "supabase_admin"
      DB_PASSWORD: "supabase"
      DB_NAME: "supabase"
      DB_AFTER_CONNECT_QUERY: "SET search_path TO _realtime"
      DB_ENC_KEY: "supabaserealtime"
      API_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SECRET_KEY_BASE: "UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq"
      ERL_AFLAGS: "-proto_dist inet_tcp"
      DNS_NODES: "''"
      RLIMIT_NOFILE: "10000"
      APP_NAME: "realtime"
      SEED_SELF_HOST: "true"
      RUN_JANITOR: "true"

  storage:
    container_name: supabase-storage
    image: supabase/storage-api:v1.14.5
    depends_on:
      db:
        condition: service_healthy
      rest:
        condition: service_started
      imgproxy:
        condition: service_started
    healthcheck:
      test:
        ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://storage:5000/status"]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      POSTGREST_URL: "http://rest:3000"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      DATABASE_URL: "postgres://supabase_storage_admin:supabase@db:5432/supabase"
      FILE_SIZE_LIMIT: "52428800"
      STORAGE_BACKEND: "file"
      FILE_STORAGE_BACKEND_PATH: "/var/lib/storage"
      TENANT_ID: "stub"
      REGION: "stub"
      GLOBAL_S3_BUCKET: "stub"
      ENABLE_IMAGE_TRANSFORMATION: "true"
      IMGPROXY_URL: "http://imgproxy:5001"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  imgproxy:
    container_name: supabase-imgproxy
    image: darthsim/imgproxy:v3.8.0
    healthcheck:
      test: ["CMD", "imgproxy", "health"]
      timeout: 5s
      interval: 5s
      retries: 3
    environment:
      IMGPROXY_BIND: ":5001"
      IMGPROXY_LOCAL_FILESYSTEM_ROOT: "/"
      IMGPROXY_USE_ETAG: "true"
      IMGPROXY_ENABLE_WEBP_DETECTION: "true"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:v0.84.2
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PG_META_PORT: "8080"
      PG_META_DB_HOST: "db"
      PG_META_DB_PORT: "5432"
      PG_META_DB_NAME: "supabase"
      PG_META_DB_USER: "supabase_admin"
      PG_META_DB_PASSWORD: "supabase"

  functions:
    container_name: supabase-edge-functions
    image: supabase/edge-runtime:v1.66.4
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      JWT_SECRET: "SFMyNTY.g2gDYQFuBgA8zdCAlAFiAAFRgA.PujAUfyhA9oirQz839ZafEnwITtZZQgKZtB9cpqUA_o"
      SUPABASE_URL: "http://kong:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      SUPABASE_DB_URL: "postgresql://postgres:supabase@db:5432/supabase"
      VERIFY_JWT: "true"
    volumes:
      - "./volumes/functions:/home/deno/functions:Z"
    command:
      - start
      - --main-service
      - /home/deno/functions/main

  analytics:
    container_name: supabase-analytics
    image: supabase/logflare:1.4.0
    healthcheck:
      test: ["CMD", "curl", "http://localhost:4000/health"]
      timeout: 5s
      interval: 5s
      retries: 10
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      LOGFLARE_NODE_HOST: "127.0.0.1:4000"
      DB_USERNAME: "supabase_admin"
      DB_DATABASE: "_supabase"
      DB_HOSTNAME: "db"
      DB_PORT: "5432"
      DB_PASSWORD: "supabase"
      DB_SCHEMA: "_analytics"
      LOGFLARE_PUBLIC_ACCESS_TOKEN: "logflare-api-key"
      LOGFLARE_SINGLE_TENANT: "true"
      LOGFLARE_SUPABASE_MODE: "true"
      LOGFLARE_MIN_CLUSTER_SIZE: "1"

      POSTGRES_BACKEND_URL: "postgresql://supabase_admin:supabase@db:5432/_supabase"
      POSTGRES_BACKEND_SCHEMA: "_analytics"
      LOGFLARE_FEATURE_FLAG_OVERRIDE: "multibackend=true"

      # If using BigQuery:
      # GOOGLE_PROJECT_ID: "my-google-project"
      # GOOGLE_PROJECT_NUMBER: "1234567890"
    ports:
      - "4000:4000"

  db:
    container_name: supabase-db
    image: supabase/postgres:15.8.1.020
    healthcheck:
      test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
    depends_on:
      vector:
        condition: service_healthy
    command:
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
      - -c
      - log_min_messages=fatal
    restart: unless-stopped
    environment:
      POSTGRES_HOST: "/var/run/postgresql"
      PGPORT: "5432"
      POSTGRES_PORT: "5432"
      PGPASSWORD: "supabase"
      POSTGRES_PASSWORD: "supabase"
      PGDATABASE: "supabase"
      POSTGRES_DB: "supabase"
      JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      JWT_EXP: "3600"
    volumes:
      - "./volumes/db/realtime.sql:/docker-entrypoint-initdb.d/migrations/99-realtime.sql:Z"
      - "./volumes/db/webhooks.sql:/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql:Z"
      - "./volumes/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:Z"
      - "./volumes/db/jwt.sql:/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql:Z"
      - "./volumes/db/data:/var/lib/postgresql/data:Z"
      - "./volumes/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:Z"
      - "./volumes/db/logs.sql:/docker-entrypoint-initdb.d/migrations/99-logs.sql:Z"
      - "./volumes/db/pooler.sql:/docker-entrypoint-initdb.d/migrations/99-pooler.sql:Z"
      - "db-config:/etc/postgresql-custom"

  vector:
    container_name: supabase-vector
    image: timberio/vector:0.28.1-alpine
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://vector:9001/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    volumes:
      - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      LOGFLARE_API_KEY: "logflare-api-key"
    command: ["--config", "/etc/vector/vector.yml"]

  supavisor:
    container_name: supabase-pooler
    image: supabase/supavisor:1.1.56
    healthcheck:
      test: ["CMD-SHELL", "curl -sSfL --head -o /dev/null 'http://127.0.0.1:4000/api/health'"]
      interval: 10s
      timeout: 5s
      retries: 5
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    command:
      - /bin/sh
      - -c
      - '/app/bin/migrate && /app/bin/supavisor eval "$(cat /etc/pooler/pooler.exs)" && /app/bin/server'
    ports:
      - "5432:5432"
      - "6543:6543"
    environment:
      - PORT=4000
      - POSTGRES_PORT=5432
      - POSTGRES_DB=supabase
      - POSTGRES_PASSWORD=supabase
      - DATABASE_URL=ecto://supabase_admin:supabase@db:5432/_supabase
      - CLUSTER_POSTGRES=true
      - SECRET_KEY_BASE=UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq
      - VAULT_ENC_KEY=your-encryption-key-32-chars-min
      - API_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg
      - METRICS_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg
      - REGION=local
      - ERL_AFLAGS=-proto_dist inet_tcp
      - POOLER_TENANT_ID=my-tenant
      - POOLER_DEFAULT_POOL_SIZE=10
      - POOLER_MAX_CLIENT_CONN=100
      - POOLER_POOL_MODE=transaction
    volumes:
      - "./volumes/pooler/pooler.exs:/etc/pooler/pooler.exs:ro"

volumes:
  db-config:

#### ChatGPT:
<time datetime="2025-01-20T00:21:25.617Z" title="1/20/2025, 9:21:25 AM">09:21</time>

From the container logs:

```
connection to server at "192.168.1.200", port 5432 failed: FATAL:  Tenant or user not found

User requested SSL connection but no downstream cert/key found
ClientHandler: User not found: "Either external_id or sni_hostname must be provided" {:single, "supabase_admin", nil}
```

these errors almost always indicate that:

1. **Supavisor (the new Postgres pooler) is requiring you to specify which “tenant” you want to connect to.**
2. **You are requesting SSL from the client, but have not provided any SSL certs to Supavisor.**

Below is an overview of what is happening and a few options to fix it.

---

## Why Supavisor is complaining about “Tenant or user not found”

Supavisor is multi-tenant by design: it can run multiple “projects” on one pooled Postgres port. It identifies each “tenant” in one of two ways:

1. **SNI (Server Name Indication)** – The hostname you connect with (e.g. `my-tenant.my-custom-domain.com`) must match the `POOLER_TENANT_ID` in your environment.
2. **`external_id`** – Passed in the Postgres connection string as a special option (e.g. `?options=project%3Dmy-tenant`).

In your docker-compose, the `supavisor` service is configured with:

```yaml
environment:
  - POOLER_TENANT_ID=my-tenant
  - CLUSTER_POSTGRES=true
  # ...
```

That means Supavisor will only route connections which specify a tenant matching `my-tenant`. If you try to connect to `localhost` or `192.168.1.200` without any extra “project” information, Supavisor cannot match the tenant and returns `FATAL: Tenant or user not found`.

### How to connect with the correct tenant

To satisfy Supavisor, you have two main options:

#### **Option A: Pass the tenant name in the connection string “options” parameter**

You can provide the “project” name in the Postgres `options` parameter like so:

```bash
psql "postgres://supabase_admin:supabase@127.0.0.1:5432/supabase?sslmode=disable&options=project%3Dmy-tenant"
```

- `project=my-tenant` needs to match your `POOLER_TENANT_ID=my-tenant`
- `sslmode=disable` is added here to avoid the SSL error (see below for more on SSL).
- You can of course replace `127.0.0.1` with your Docker host’s IP, or `localhost`, etc.

If you’re using a GUI client (like pgAdmin or TablePlus), you can often set:

- **Host**: `127.0.0.1` (or wherever you exposed port 5432)
- **Database**: `supabase`
- **Username**: `supabase_admin`
- **Password**: `supabase`
- **SSL Mode**: `Disable` (for now)
- Then find an “Advanced Options” or “Options” field to insert `-c project=my-tenant`

If your GUI doesn’t let you pass an `options` param, you can often manually craft a connection string in the advanced settings.

#### **Option B: Use a hostname matching the tenant (SNI)**

If you prefer to avoid the `options=project%3Dmy-tenant` approach, you can rely on SNI (Server Name Indication) to supply the tenant ID. For example, if your `POOLER_TENANT_ID` is `my-tenant`, then connecting to something like:

```
my-tenant.localhost
```

would pass that hostname as the SNI server name, letting Supavisor identify the tenant as `my-tenant`. But for that to work locally:

1. You would need an `/etc/hosts` entry mapping `my-tenant.localhost` → `127.0.0.1` (or your Docker bridge IP).
2. Your client would need to request SSL, because SNI is part of the TLS handshake. (This also implies you’d need to set up SSL certs inside the `supavisor` container—otherwise you’ll still get the “User requested SSL connection but no downstream cert/key found” error.)

That’s more complicated for a purely local setup. Most people end up using the “options” query param approach.

---

## Why you see “User requested SSL connection but no downstream cert/key found”

By default, many Postgres tools (psql, pgAdmin, etc.) default to `sslmode=require` or `sslmode=prefer`—they attempt an SSL handshake before falling back to plaintext.

Supavisor sees the request for SSL but does not have any certificate or key configured (`no downstream cert/key found`). This is expected in a local Docker-based environment unless you explicitly configure supavisor with SSL. If you do not need SSL locally, just disable it on the client side:

```bash
sslmode=disable
```

### Configuring SSL in supavisor (optional)

If you actually want SSL locally, you would need to:

1. Provide a certificate and private key to supavisor (e.g. in `/etc/pooler/tls/`).
2. Set environment variables or config pointing to those cert/key paths.
3. Then connect via SNI-based SSL domain.

For local development, it is usually simpler to set `sslmode=disable`.

---

## Quick fixes

1. **Disable SSL in your connection**\
   Add `?sslmode=disable` (or set `sslmode` to “Disable” in your GUI) so that supavisor doesn’t attempt TLS.

2. **Provide the tenant name**
   - Either add `options=project%3Dmy-tenant` to your connection string.
   - Or set up DNS + SSL for SNI.

### Example psql command

```bash
psql \
  --host=127.0.0.1 \
  --port=5432 \
  --username=supabase_admin \
  --dbname=supabase \
  --no-password \
  --set=sslmode=disable \
  --set=options="-c project=my-tenant"
```

(Or put it all in the `postgres://…` URL.)

---

## Bypassing Supavisor (Single-tenant only)

If you do not need multi-tenant pooling and just want to connect to Postgres as usual, you can skip supavisor altogether:

- Connect directly to the `db` container’s port **inside** Docker Compose (e.g. `db:5432`).
- Or expose the `db` container’s Postgres port on your host. (However, your Compose file currently maps the supavisor container to port 5432, not the `db` container.)
- You could comment out the `supavisor` container or remove the `CLUSTER_POSTGRES=true` logic if you do not need advanced pooling.

That said, the recommended approach in new Supabase stacks is to go through Supavisor.

---

## Summary

- **The “Tenant or user not found”** error is because Supavisor requires you to indicate you are connecting to `POOLER_TENANT_ID = my-tenant`, typically via either:
  1. `?options=project%3Dmy-tenant`, **or**
  2. Using a hostname that matches `my-tenant` (SNI + SSL).
- **“User requested SSL connection but no downstream cert/key found”** means your client is asking for SSL, but you don’t have SSL configured in supavisor. You can fix this by setting `sslmode=disable` on the client side for local dev.

Once you include the correct tenant name and adjust your SSL mode, you should be able to connect without errors.


#### You:
<time datetime="2025-01-20T00:22:23.209Z" title="1/20/2025, 9:22:23 AM">09:22</time>

can i disable project checking

#### ChatGPT:
<time datetime="2025-01-20T00:22:50.528Z" title="1/20/2025, 9:22:50 AM">09:22</time>

Yes, you can effectively disable “project” (tenant) checking by running Supavisor in **single-tenant** mode or by removing it altogether. By default, the new Supavisor container is set up for multi-tenant (cluster) mode, which requires a `POOLER_TENANT_ID` for every connection. Below are your options to turn that off.

---

## 1. Set Supavisor to Single-Tenant Mode

If you want to keep using Supavisor’s connection pooling (but only for one project), you can disable multi-tenant checks by removing or changing these environment variables:

```yaml
# Remove or comment out these lines in the supavisor environment:
- CLUSTER_POSTGRES=true
- POOLER_TENANT_ID=my-tenant
```

You can either remove them entirely or set `CLUSTER_POSTGRES=false`. For example:

```yaml
supavisor:
  image: supabase/supavisor:1.1.56
  environment:
    # CLUSTER_POSTGRES: "false"  # or just remove it
    # POOLER_TENANT_ID: ""       # or remove this line
    # ...
```

In single-tenant mode, Supavisor does **not** require a tenant ID. You should then be able to connect like a normal Postgres instance:

```bash
psql "postgres://supabase_admin:supabase@127.0.0.1:5432/supabase?sslmode=disable"
```

(Adjust host and password as needed.)

---

## 2. Bypass/Remove Supavisor Entirely

If you don’t need connection pooling at all, you can just expose the Postgres port **directly** from the `db` container. For instance, in your `docker-compose.yml`:

```yaml
db:
  container_name: supabase-db
  image: supabase/postgres:15.8.1.020
  ports:
    - "5432:5432"
  # ...
```

Then you can connect directly to the database container without going through Supavisor:

```bash
psql "postgres://postgres:supabase@127.0.0.1:5432/supabase"
```

---

## 3. Continue Using Multi-Tenant (If You Actually Need It)

If you **do** want multi-tenant capabilities, then you must provide a tenant ID with either:

1. **Query param**: `?options=project%3Dmy-tenant`
2. **SNI**: Connect via a hostname matching your `POOLER_TENANT_ID`.

But if that’s not your use case, disabling multi-tenant (single-tenant mode or removing Supavisor) is simpler.


#### You:
<time datetime="2025-01-20T00:23:34.294Z" title="1/20/2025, 9:23:34 AM">09:23</time>

i don't need multitennant or any high perf features. let's simplify this by not using connection pooling

#### ChatGPT:
<time datetime="2025-01-20T00:23:53.328Z" title="1/20/2025, 9:23:53 AM">09:23</time>

Below is a minimal way to **bypass Supavisor** and connect directly to Postgres, without multi-tenancy or connection pooling. This greatly simplifies your local Supabase setup if you don’t need those advanced features.

---

## 1. Remove the `supavisor` service

In your `docker-compose.yml`, **comment out** (or remove) the entire `supavisor:` block:

```yaml
# supavisor:
#   container_name: supabase-pooler
#   image: supabase/supavisor:1.1.56
#   ...
#   ports:
#     - "5432:5432"
#     - "6543:6543"
#   environment:
#     - CLUSTER_POSTGRES=true
#     ...
#   volumes:
#     - "./volumes/pooler/pooler.exs:/etc/pooler/pooler.exs:ro"
```

By removing it, you won’t have a separate connection pooling layer anymore.

---

## 2. Expose port 5432 **directly** from the `db` service

Right now, your `db` container does not expose port 5432. In the original compose, 5432 is taken by Supavisor. You can re-map it directly to `db`:

```yaml
db:
  container_name: supabase-db
  image: supabase/postgres:15.8.1.020
  restart: unless-stopped
  ports:
    - "5432:5432"        # <- Add this line
  environment:
    POSTGRES_PASSWORD: "supabase"
    ...
  volumes:
    - "./volumes/db/data:/var/lib/postgresql/data:Z"
    ...
```

With that, Docker will forward host port 5432 straight into the `db` container.

---

## 3. Connect directly to Postgres

Now you can connect from your host machine (or from other containers) using the usual Postgres credentials. For example, with `psql`:

```bash
psql "postgres://postgres:supabase@127.0.0.1:5432/supabase"
```

By default, the `supabase/postgres` image creates:

- **Database**: `supabase`
- **Username**: `postgres`
- **Password**: `supabase` (set by `POSTGRES_PASSWORD`)

> **Tip**: If you get any SSL-related errors (rare in this direct setup), you can always append `?sslmode=disable` to your connection string, but usually the default “prefer” works fine directly on 127.0.0.1.

---

## 4. (Optional) Remove references to Supavisor config

- If you have any `.sql` migrations referencing Supavisor (like `pooler.sql` in the `docker-entrypoint-initdb.d` folder), remove or ignore them since you are no longer using it.
- You may also remove `CLUSTER_POSTGRES=true` or `POOLER_TENANT_ID` env vars from anywhere else, if they exist.

---

### That’s it!

With these changes, you get a straightforward single Postgres container, without the overhead or complexity of Supavisor. You can still use the rest of the Supabase stack (Auth, REST, Storage, Realtime, etc.) as normal—just remember everything now talks to Postgres at `db:5432` internally, or `localhost:5432` externally.


#### You:
<time datetime="2025-01-20T00:29:38.045Z" title="1/20/2025, 9:29:38 AM">09:29</time>

revise my docker file to remove any connection pooling and make any other improvements.
---
version: "3.9"

################################################################################
# USAGE:
#   docker compose up
#   docker compose down
################################################################################

services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:20250113-83c9420
    restart: unless-stopped
    healthcheck:
      test:
        [
          "CMD",
          "node",
          "-e",
          "fetch('http://studio:3000/api/profile').then((r) => {if (r.status !== 200) throw new Error(r.status)})"
        ]
      timeout: 10s
      interval: 5s
      retries: 3
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      # Inlined environment values
      STUDIO_PG_META_URL: "http://meta:8080"
      POSTGRES_PASSWORD: "supabase"

      DEFAULT_ORGANIZATION_NAME: "MyOrganization"
      DEFAULT_PROJECT_NAME: "MyProject"
      OPENAI_API_KEY: ""  # or leave blank

      SUPABASE_URL: "http://kong:8000"
      SUPABASE_PUBLIC_URL: "http://localhost:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      AUTH_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      LOGFLARE_PUBLIC_ACCESS_TOKEN: ""
      LOGFLARE_URL: "http://analytics:4000"
      NEXT_PUBLIC_ENABLE_LOGS: "true"
      NEXT_ANALYTICS_BACKEND_PROVIDER: "postgres"
      # Uncomment if using BigQuery for analytics
      # NEXT_ANALYTICS_BACKEND_PROVIDER: "bigquery"

  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    restart: unless-stopped
    entrypoint: bash -c 'eval "echo \"$$(cat ~/temp.yml)\"" > ~/kong.yml && /docker-entrypoint.sh kong docker-start'
    ports:
      - "8000:8000/tcp"   # From KONG_HTTP_PORT=8000
      - "8443:8443/tcp"   # From KONG_HTTPS_PORT=8443
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: "/home/kong/kong.yml"
      KONG_DNS_ORDER: "LAST,A,CNAME"
      KONG_PLUGINS: "request-transformer,cors,key-auth,acl,basic-auth"
      KONG_NGINX_PROXY_PROXY_BUFFER_SIZE: "160k"
      KONG_NGINX_PROXY_PROXY_BUFFERS: "64 160k"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      DASHBOARD_USERNAME: "admin"
      DASHBOARD_PASSWORD: "supabase"
    volumes:
      - "./volumes/api/kong.yml:/home/kong/temp.yml:ro"

  auth:
    container_name: supabase-auth
    image: supabase/gotrue:v2.167.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://localhost:9999/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: "0.0.0.0"
      GOTRUE_API_PORT: "9999"
      API_EXTERNAL_URL: "http://127.0.0.1:8080"  # originally API_EXTERNAL_URL was blank

      GOTRUE_DB_DRIVER: "postgres"
      # => "postgres://supabase_auth_admin:POSTGRES_PASSWORD@POSTGRES_HOST:POSTGRES_PORT/POSTGRES_DB"
      GOTRUE_DB_DATABASE_URL: "postgres://supabase_auth_admin:supabase@db:5432/supabase"

      GOTRUE_SITE_URL: "http://localhost:3000"
      GOTRUE_URI_ALLOW_LIST: "http://localhost:3000"
      GOTRUE_DISABLE_SIGNUP: "false"

      GOTRUE_JWT_ADMIN_ROLES: "service_role"
      GOTRUE_JWT_AUD: "authenticated"
      GOTRUE_JWT_DEFAULT_GROUP_NAME: "authenticated"
      GOTRUE_JWT_EXP: "3600"
      GOTRUE_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
      GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED: "false"
      GOTRUE_MAILER_AUTOCONFIRM: "false"

      # Phone signups
      GOTRUE_EXTERNAL_PHONE_ENABLED: "false"
      GOTRUE_SMS_AUTOCONFIRM: "false"

      # Mailer / SMTP
      GOTRUE_SMTP_ADMIN_EMAIL: "myadmin@example.com"
      GOTRUE_SMTP_HOST: "mail.example.com"
      GOTRUE_SMTP_PORT: "587"
      GOTRUE_SMTP_USER: "my-smtp-user"
      GOTRUE_SMTP_PASS: "my-smtp-password"
      GOTRUE_SMTP_SENDER_NAME: "My App Emailer"
      GOTRUE_MAILER_URLPATHS_INVITE: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_CONFIRMATION: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_RECOVERY: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE: "/auth/v1/verify"

  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:v12.2.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PGRST_DB_URI: "postgres://authenticator:supabase@db:5432/supabase"
      PGRST_DB_SCHEMAS: "public"
      PGRST_DB_ANON_ROLE: "anon"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_DB_USE_LEGACY_GUCS: "false"
      PGRST_APP_SETTINGS_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_APP_SETTINGS_JWT_EXP: "3600"
    command: "postgrest"

  realtime:
    container_name: realtime-dev.supabase-realtime
    image: supabase/realtime:v2.33.70
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    # healthcheck:
    #   test:
    #     [
    #       "CMD",
    #       "curl",
    #       "-sSfL",
    #       "--head",
    #       "-o",
    #       "/dev/null",
    #       "-H",
    #       "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg",
    #       "http://localhost:4000/api/tenants/realtime-dev/health"
    #     ]
    #   timeout: 5s
    #   interval: 5s
    #   retries: 3
    restart: unless-stopped
    environment:
      PORT: "4000"
      DB_HOST: "db"
      DB_PORT: "5432"
      DB_USER: "supabase_admin"
      DB_PASSWORD: "supabase"
      DB_NAME: "supabase"
      DB_AFTER_CONNECT_QUERY: "SET search_path TO _realtime"
      DB_ENC_KEY: "supabaserealtime"
      API_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SECRET_KEY_BASE: "UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq"
      ERL_AFLAGS: "-proto_dist inet_tcp"
      DNS_NODES: "''"
      RLIMIT_NOFILE: "10000"
      APP_NAME: "realtime"
      SEED_SELF_HOST: "true"
      RUN_JANITOR: "true"

  storage:
    container_name: supabase-storage
    image: supabase/storage-api:v1.14.5
    depends_on:
      db:
        condition: service_healthy
      rest:
        condition: service_started
      imgproxy:
        condition: service_started
    healthcheck:
      test:
        ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://storage:5000/status"]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      POSTGREST_URL: "http://rest:3000"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      DATABASE_URL: "postgres://supabase_storage_admin:supabase@db:5432/supabase"
      FILE_SIZE_LIMIT: "52428800"
      STORAGE_BACKEND: "file"
      FILE_STORAGE_BACKEND_PATH: "/var/lib/storage"
      TENANT_ID: "stub"
      REGION: "stub"
      GLOBAL_S3_BUCKET: "stub"
      ENABLE_IMAGE_TRANSFORMATION: "true"
      IMGPROXY_URL: "http://imgproxy:5001"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  imgproxy:
    container_name: supabase-imgproxy
    image: darthsim/imgproxy:v3.8.0
    healthcheck:
      test: ["CMD", "imgproxy", "health"]
      timeout: 5s
      interval: 5s
      retries: 3
    environment:
      IMGPROXY_BIND: ":5001"
      IMGPROXY_LOCAL_FILESYSTEM_ROOT: "/"
      IMGPROXY_USE_ETAG: "true"
      IMGPROXY_ENABLE_WEBP_DETECTION: "true"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:v0.84.2
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PG_META_PORT: "8080"
      PG_META_DB_HOST: "db"
      PG_META_DB_PORT: "5432"
      PG_META_DB_NAME: "supabase"
      PG_META_DB_USER: "supabase_admin"
      PG_META_DB_PASSWORD: "supabase"

  functions:
    container_name: supabase-edge-functions
    image: supabase/edge-runtime:v1.66.4
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      JWT_SECRET: "SFMyNTY.g2gDYQFuBgA8zdCAlAFiAAFRgA.PujAUfyhA9oirQz839ZafEnwITtZZQgKZtB9cpqUA_o"
      SUPABASE_URL: "http://kong:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      SUPABASE_DB_URL: "postgresql://postgres:supabase@db:5432/supabase"
      VERIFY_JWT: "true"
    volumes:
      - "./volumes/functions:/home/deno/functions:Z"
    command:
      - start
      - --main-service
      - /home/deno/functions/main

  analytics:
    container_name: supabase-analytics
    image: supabase/logflare:1.4.0
    healthcheck:
      test: ["CMD", "curl", "http://localhost:4000/health"]
      timeout: 5s
      interval: 5s
      retries: 10
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      LOGFLARE_NODE_HOST: "127.0.0.1:4000"
      DB_USERNAME: "supabase_admin"
      DB_DATABASE: "_supabase"
      DB_HOSTNAME: "db"
      DB_PORT: "5432"
      DB_PASSWORD: "supabase"
      DB_SCHEMA: "_analytics"
      LOGFLARE_PUBLIC_ACCESS_TOKEN: "logflare-api-key"
      LOGFLARE_SINGLE_TENANT: "true"
      LOGFLARE_SUPABASE_MODE: "true"
      LOGFLARE_MIN_CLUSTER_SIZE: "1"

      POSTGRES_BACKEND_URL: "postgresql://supabase_admin:supabase@db:5432/_supabase"
      POSTGRES_BACKEND_SCHEMA: "_analytics"
      LOGFLARE_FEATURE_FLAG_OVERRIDE: "multibackend=true"

      # If using BigQuery:
      # GOOGLE_PROJECT_ID: "my-google-project"
      # GOOGLE_PROJECT_NUMBER: "1234567890"
    ports:
      - "4000:4000"

  db:
    container_name: supabase-db
    image: supabase/postgres:15.8.1.020
    healthcheck:
      test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
    depends_on:
      vector:
        condition: service_healthy
    command:
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
      - -c
      - log_min_messages=fatal
    restart: unless-stopped
    environment:
      POSTGRES_HOST: "/var/run/postgresql"
      PGPORT: "5432"
      POSTGRES_PORT: "5432"
      PGPASSWORD: "supabase"
      POSTGRES_PASSWORD: "supabase"
      PGDATABASE: "supabase"
      POSTGRES_DB: "supabase"
      JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      JWT_EXP: "3600"
    volumes:
      - "./volumes/db/realtime.sql:/docker-entrypoint-initdb.d/migrations/99-realtime.sql:Z"
      - "./volumes/db/webhooks.sql:/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql:Z"
      - "./volumes/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:Z"
      - "./volumes/db/jwt.sql:/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql:Z"
      - "./volumes/db/data:/var/lib/postgresql/data:Z"
      - "./volumes/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:Z"
      - "./volumes/db/logs.sql:/docker-entrypoint-initdb.d/migrations/99-logs.sql:Z"
      - "./volumes/db/pooler.sql:/docker-entrypoint-initdb.d/migrations/99-pooler.sql:Z"
      - "db-config:/etc/postgresql-custom"

  vector:
    container_name: supabase-vector
    image: timberio/vector:0.28.1-alpine
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://vector:9001/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    volumes:
      - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      LOGFLARE_API_KEY: "logflare-api-key"
    command: ["--config", "/etc/vector/vector.yml"]

  supavisor:
    container_name: supabase-pooler
    image: supabase/supavisor:1.1.56
    healthcheck:
      test: ["CMD-SHELL", "curl -sSfL --head -o /dev/null 'http://127.0.0.1:4000/api/health'"]
      interval: 10s
      timeout: 5s
      retries: 5
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    command:
      - /bin/sh
      - -c
      - '/app/bin/migrate && /app/bin/supavisor eval "$(cat /etc/pooler/pooler.exs)" && /app/bin/server'
    ports:
      - "5432:5432"
      - "6543:6543"
    environment:
      - PORT=4000
      - POSTGRES_PORT=5432
      - POSTGRES_DB=supabase
      - POSTGRES_PASSWORD=supabase
      - DATABASE_URL=ecto://supabase_admin:supabase@db:5432/_supabase
      - CLUSTER_POSTGRES=true
      - SECRET_KEY_BASE=UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq
      - VAULT_ENC_KEY=your-encryption-key-32-chars-min
      - API_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg
      - METRICS_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg
      - REGION=local
      - ERL_AFLAGS=-proto_dist inet_tcp
      - POOLER_TENANT_ID=my-tenant
      - POOLER_DEFAULT_POOL_SIZE=10
      - POOLER_MAX_CLIENT_CONN=100
      - POOLER_POOL_MODE=transaction
    volumes:
      - "./volumes/pooler/pooler.exs:/etc/pooler/pooler.exs:ro"

volumes:
  db-config:

#### ChatGPT:
<time datetime="2025-01-20T00:32:18.317Z" title="1/20/2025, 9:32:18 AM">09:32</time>

Below is a **revised** `docker-compose.yml` that:

1. **Removes the `supavisor` service** (the connection pooling layer).
2. **Exposes port 5432 directly on the `db` container** so other services (and your host) can connect to Postgres normally.
3. **Removes references to pooling** such as `pooler.sql`.

All other services remain the same. This way, you have a simpler local Supabase stack without multi-tenant or connection pooling features.

```yaml
version: "3.9"

services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:20250113-83c9420
    restart: unless-stopped
    healthcheck:
      test:
        [
          "CMD",
          "node",
          "-e",
          "fetch('http://studio:3000/api/profile').then((r) => {if (r.status !== 200) throw new Error(r.status)})"
        ]
      timeout: 10s
      interval: 5s
      retries: 3
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      # Inlined environment values
      STUDIO_PG_META_URL: "http://meta:8080"
      POSTGRES_PASSWORD: "supabase"

      DEFAULT_ORGANIZATION_NAME: "MyOrganization"
      DEFAULT_PROJECT_NAME: "MyProject"
      OPENAI_API_KEY: ""  # or leave blank

      SUPABASE_URL: "http://kong:8000"
      SUPABASE_PUBLIC_URL: "http://localhost:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      AUTH_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      LOGFLARE_PUBLIC_ACCESS_TOKEN: ""
      LOGFLARE_URL: "http://analytics:4000"
      NEXT_PUBLIC_ENABLE_LOGS: "true"
      NEXT_ANALYTICS_BACKEND_PROVIDER: "postgres"
      # Uncomment if using BigQuery for analytics
      # NEXT_ANALYTICS_BACKEND_PROVIDER: "bigquery"

  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    restart: unless-stopped
    entrypoint: bash -c 'eval "echo \"$$(cat ~/temp.yml)\"" > ~/kong.yml && /docker-entrypoint.sh kong docker-start'
    ports:
      - "8000:8000/tcp"   # From KONG_HTTP_PORT=8000
      - "8443:8443/tcp"   # From KONG_HTTPS_PORT=8443
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: "/home/kong/kong.yml"
      KONG_DNS_ORDER: "LAST,A,CNAME"
      KONG_PLUGINS: "request-transformer,cors,key-auth,acl,basic-auth"
      KONG_NGINX_PROXY_PROXY_BUFFER_SIZE: "160k"
      KONG_NGINX_PROXY_PROXY_BUFFERS: "64 160k"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      DASHBOARD_USERNAME: "admin"
      DASHBOARD_PASSWORD: "supabase"
    volumes:
      - "./volumes/api/kong.yml:/home/kong/temp.yml:ro"

  auth:
    container_name: supabase-auth
    image: supabase/gotrue:v2.167.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://localhost:9999/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: "0.0.0.0"
      GOTRUE_API_PORT: "9999"
      API_EXTERNAL_URL: "http://127.0.0.1:8080"  # originally blank

      GOTRUE_DB_DRIVER: "postgres"
      GOTRUE_DB_DATABASE_URL: "postgres://supabase_auth_admin:supabase@db:5432/supabase"

      GOTRUE_SITE_URL: "http://localhost:3000"
      GOTRUE_URI_ALLOW_LIST: "http://localhost:3000"
      GOTRUE_DISABLE_SIGNUP: "false"

      GOTRUE_JWT_ADMIN_ROLES: "service_role"
      GOTRUE_JWT_AUD: "authenticated"
      GOTRUE_JWT_DEFAULT_GROUP_NAME: "authenticated"
      GOTRUE_JWT_EXP: "3600"
      GOTRUE_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
      GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED: "false"
      GOTRUE_MAILER_AUTOCONFIRM: "false"

      # Phone signups
      GOTRUE_EXTERNAL_PHONE_ENABLED: "false"
      GOTRUE_SMS_AUTOCONFIRM: "false"

      # Mailer / SMTP
      GOTRUE_SMTP_ADMIN_EMAIL: "myadmin@example.com"
      GOTRUE_SMTP_HOST: "mail.example.com"
      GOTRUE_SMTP_PORT: "587"
      GOTRUE_SMTP_USER: "my-smtp-user"
      GOTRUE_SMTP_PASS: "my-smtp-password"
      GOTRUE_SMTP_SENDER_NAME: "My App Emailer"
      GOTRUE_MAILER_URLPATHS_INVITE: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_CONFIRMATION: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_RECOVERY: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE: "/auth/v1/verify"

  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:v12.2.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PGRST_DB_URI: "postgres://authenticator:supabase@db:5432/supabase"
      PGRST_DB_SCHEMAS: "public"
      PGRST_DB_ANON_ROLE: "anon"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_DB_USE_LEGACY_GUCS: "false"
      PGRST_APP_SETTINGS_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_APP_SETTINGS_JWT_EXP: "3600"
    command: "postgrest"

  realtime:
    container_name: realtime-dev.supabase-realtime
    image: supabase/realtime:v2.33.70
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PORT: "4000"
      DB_HOST: "db"
      DB_PORT: "5432"
      DB_USER: "supabase_admin"
      DB_PASSWORD: "supabase"
      DB_NAME: "supabase"
      DB_AFTER_CONNECT_QUERY: "SET search_path TO _realtime"
      DB_ENC_KEY: "supabaserealtime"
      API_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SECRET_KEY_BASE: "UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq"
      ERL_AFLAGS: "-proto_dist inet_tcp"
      DNS_NODES: "''"
      RLIMIT_NOFILE: "10000"
      APP_NAME: "realtime"
      SEED_SELF_HOST: "true"
      RUN_JANITOR: "true"

  storage:
    container_name: supabase-storage
    image: supabase/storage-api:v1.14.5
    depends_on:
      db:
        condition: service_healthy
      rest:
        condition: service_started
      imgproxy:
        condition: service_started
    healthcheck:
      test:
        ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://storage:5000/status"]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      POSTGREST_URL: "http://rest:3000"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      DATABASE_URL: "postgres://supabase_storage_admin:supabase@db:5432/supabase"
      FILE_SIZE_LIMIT: "52428800"
      STORAGE_BACKEND: "file"
      FILE_STORAGE_BACKEND_PATH: "/var/lib/storage"
      TENANT_ID: "stub"
      REGION: "stub"
      GLOBAL_S3_BUCKET: "stub"
      ENABLE_IMAGE_TRANSFORMATION: "true"
      IMGPROXY_URL: "http://imgproxy:5001"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  imgproxy:
    container_name: supabase-imgproxy
    image: darthsim/imgproxy:v3.8.0
    healthcheck:
      test: ["CMD", "imgproxy", "health"]
      timeout: 5s
      interval: 5s
      retries: 3
    environment:
      IMGPROXY_BIND: ":5001"
      IMGPROXY_LOCAL_FILESYSTEM_ROOT: "/"
      IMGPROXY_USE_ETAG: "true"
      IMGPROXY_ENABLE_WEBP_DETECTION: "true"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:v0.84.2
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PG_META_PORT: "8080"
      PG_META_DB_HOST: "db"
      PG_META_DB_PORT: "5432"
      PG_META_DB_NAME: "supabase"
      PG_META_DB_USER: "supabase_admin"
      PG_META_DB_PASSWORD: "supabase"

  functions:
    container_name: supabase-edge-functions
    image: supabase/edge-runtime:v1.66.4
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      JWT_SECRET: "SFMyNTY.g2gDYQFuBgA8zdCAlAFiAAFRgA.PujAUfyhA9oirQz839ZafEnwITtZZQgKZtB9cpqUA_o"
      SUPABASE_URL: "http://kong:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      SUPABASE_DB_URL: "postgresql://postgres:supabase@db:5432/supabase"
      VERIFY_JWT: "true"
    volumes:
      - "./volumes/functions:/home/deno/functions:Z"
    command:
      - start
      - --main-service
      - /home/deno/functions/main

  analytics:
    container_name: supabase-analytics
    image: supabase/logflare:1.4.0
    healthcheck:
      test: ["CMD", "curl", "http://localhost:4000/health"]
      timeout: 5s
      interval: 5s
      retries: 10
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      LOGFLARE_NODE_HOST: "127.0.0.1:4000"
      DB_USERNAME: "supabase_admin"
      DB_DATABASE: "_supabase"
      DB_HOSTNAME: "db"
      DB_PORT: "5432"
      DB_PASSWORD: "supabase"
      DB_SCHEMA: "_analytics"
      LOGFLARE_PUBLIC_ACCESS_TOKEN: "logflare-api-key"
      LOGFLARE_SINGLE_TENANT: "true"
      LOGFLARE_SUPABASE_MODE: "true"
      LOGFLARE_MIN_CLUSTER_SIZE: "1"

      POSTGRES_BACKEND_URL: "postgresql://supabase_admin:supabase@db:5432/_supabase"
      POSTGRES_BACKEND_SCHEMA: "_analytics"
      LOGFLARE_FEATURE_FLAG_OVERRIDE: "multibackend=true"

      # If using BigQuery:
      # GOOGLE_PROJECT_ID: "my-google-project"
      # GOOGLE_PROJECT_NUMBER: "1234567890"
    ports:
      - "4000:4000"

  db:
    container_name: supabase-db
    image: supabase/postgres:15.8.1.020
    healthcheck:
      test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
    depends_on:
      vector:
        condition: service_healthy
    command:
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
      - -c
      - log_min_messages=fatal
    restart: unless-stopped
    ports:
      - "5432:5432"  # <--- Directly expose Postgres port on the host
    environment:
      POSTGRES_HOST: "/var/run/postgresql"
      PGPORT: "5432"
      POSTGRES_PORT: "5432"
      PGPASSWORD: "supabase"
      POSTGRES_PASSWORD: "supabase"
      PGDATABASE: "supabase"
      POSTGRES_DB: "supabase"
      JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      JWT_EXP: "3600"
    volumes:
      - "./volumes/db/realtime.sql:/docker-entrypoint-initdb.d/migrations/99-realtime.sql:Z"
      - "./volumes/db/webhooks.sql:/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql:Z"
      - "./volumes/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:Z"
      - "./volumes/db/jwt.sql:/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql:Z"
      - "./volumes/db/data:/var/lib/postgresql/data:Z"
      - "./volumes/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:Z"
      - "./volumes/db/logs.sql:/docker-entrypoint-initdb.d/migrations/99-logs.sql:Z"
      # REMOVE pooler.sql reference:
      # - "./volumes/db/pooler.sql:/docker-entrypoint-initdb.d/migrations/99-pooler.sql:Z"
      - "db-config:/etc/postgresql-custom"

  vector:
    container_name: supabase-vector
    image: timberio/vector:0.28.1-alpine
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://vector:9001/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    volumes:
      - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      LOGFLARE_API_KEY: "logflare-api-key"
    command: ["--config", "/etc/vector/vector.yml"]

# REMOVE the supavisor service entirely:
# supavisor:
#   container_name: supabase-pooler
#   ...

volumes:
  db-config:
```

### Key changes:

1. **Removed `supavisor`**: The entire `supavisor` service block is commented out (you can delete it if you want). This removes all connection pooling logic.
2. **Removed `pooler.sql`**: The `db` service no longer loads `pooler.sql`.
3. **Exposed Postgres on 5432**: The `db` container now has:
   ```yaml
   ports:
     - "5432:5432"
   ```
   so you can connect directly from your host or from other containers at `localhost:5432` (or wherever Docker is running).

With this setup, there’s no multi-tenant or cluster pooling overhead—just a straightforward single Postgres instance for your local Supabase stack.


#### You:
<time datetime="2025-01-20T00:36:57.522Z" title="1/20/2025, 9:36:57 AM">09:36</time>

ashwin@ubuntu-server:~/supabase/docker$ docker ps
CONTAINER ID   IMAGE                               COMMAND                  CREATED         STATUS                     PORTS                                       NAMES
24cf4c48348f   supabase/postgres:15.8.1.020        "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes (unhealthy)   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   supabase-db
0fdad8f49664   darthsim/imgproxy:v3.8.0            "imgproxy"               2 minutes ago   Up 2 minutes (healthy)     8080/tcp                                    supabase-imgproxy
2f4142f99b4a   timberio/vector:0.28.1-alpine       "/usr/local/bin/vect…"   2 minutes ago   Up 2 minutes (healthy)                                                 supabase-vector
1a8cf7285d91   ghcr.io/goauthentik/server:latest   "dumb-init -- ak wor…"   42 hours ago    Up 3 hours (healthy)                                                   authentik_worker
0d028d8b521a   postgres:14-alpine                  "docker-entrypoint.s…"   42 hours ago    Up 3 hours                 5432/tcp                                    authentik_postgres
dee666c898b3   ghcr.io/goauthentik/server:latest   "dumb-init -- ak ser…"   42 hours ago    Up 3 hours (healthy)                                                   authentik_server
9638fe1eface   redis:6-alpine                      "docker-entrypoint.s…"   42 hours ago    Up 3 hours                 6379/tcp                                    authentik_redis
030052732b1d   ghcr.io/goauthentik/server:latest   "dumb-init -- ak ser…"   43 hours ago    Up 3 hours (healthy)                                                   authentik
4eac5f2e4174   redis:alpine                        "docker-entrypoint.s…"   2 days ago      Up 3 hours                 6379/tcp                                    outline_redis
ashwin@ubuntu-server:~/supabase/docker$ docker compose logs -f supabase-db
no such service: supabase-db
ashwin@ubuntu-server:~/supabase/docker$ docker compose logs -f supabase
no such service: supabase
ashwin@ubuntu-server:~/supabase/docker$ docker compose logs -f 24cf4c48348f
no such service: 24cf4c48348f
ashwin@ubuntu-server:~/supabase/docker$ 

#### ChatGPT:
<time datetime="2025-01-20T00:37:10.302Z" title="1/20/2025, 9:37:10 AM">09:37</time>



#### You:
<time datetime="2025-01-20T00:46:47.001Z" title="1/20/2025, 9:46:47 AM">09:46</time>

p: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector  | 2025-01-20T00:39:31.292504Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Internal log [Retrying after error.] has been rate limited 1 times.
supabase-vector  | 2025-01-20T00:39:31.292506Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-vector  | 2025-01-20T00:39:41.300540Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector  | 2025-01-20T00:39:41.300575Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true

---
version: "3.9"

services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:20250113-83c9420
    restart: unless-stopped
    healthcheck:
      test:
        [
          "CMD",
          "node",
          "-e",
          "fetch('http://studio:3000/api/profile').then((r) => {if (r.status !== 200) throw new Error(r.status)})"
        ]
      timeout: 10s
      interval: 5s
      retries: 3
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      # Inlined environment values
      STUDIO_PG_META_URL: "http://meta:8080"
      POSTGRES_PASSWORD: "supabase"

      DEFAULT_ORGANIZATION_NAME: "MyOrganization"
      DEFAULT_PROJECT_NAME: "MyProject"
      OPENAI_API_KEY: ""  # or leave blank

      SUPABASE_URL: "http://kong:8000"
      SUPABASE_PUBLIC_URL: "http://localhost:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      AUTH_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      LOGFLARE_PUBLIC_ACCESS_TOKEN: ""
      LOGFLARE_URL: "http://analytics:4000"
      NEXT_PUBLIC_ENABLE_LOGS: "true"
      NEXT_ANALYTICS_BACKEND_PROVIDER: "postgres"
      # Uncomment if using BigQuery for analytics
      # NEXT_ANALYTICS_BACKEND_PROVIDER: "bigquery"

  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    restart: unless-stopped
    entrypoint: bash -c 'eval "echo \"$$(cat ~/temp.yml)\"" > ~/kong.yml && /docker-entrypoint.sh kong docker-start'
    ports:
      - "8000:8000/tcp"   # From KONG_HTTP_PORT=8000
      - "8443:8443/tcp"   # From KONG_HTTPS_PORT=8443
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: "/home/kong/kong.yml"
      KONG_DNS_ORDER: "LAST,A,CNAME"
      KONG_PLUGINS: "request-transformer,cors,key-auth,acl,basic-auth"
      KONG_NGINX_PROXY_PROXY_BUFFER_SIZE: "160k"
      KONG_NGINX_PROXY_PROXY_BUFFERS: "64 160k"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      DASHBOARD_USERNAME: "admin"
      DASHBOARD_PASSWORD: "supabase"
    volumes:
      - "./volumes/api/kong.yml:/home/kong/temp.yml:ro"

  auth:
    container_name: supabase-auth
    image: supabase/gotrue:v2.167.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://localhost:9999/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: "0.0.0.0"
      GOTRUE_API_PORT: "9999"
      API_EXTERNAL_URL: "http://127.0.0.1:8080"  # originally blank

      GOTRUE_DB_DRIVER: "postgres"
      GOTRUE_DB_DATABASE_URL: "postgres://supabase_auth_admin:supabase@db:5432/supabase"

      GOTRUE_SITE_URL: "http://localhost:3000"
      GOTRUE_URI_ALLOW_LIST: "http://localhost:3000"
      GOTRUE_DISABLE_SIGNUP: "false"

      GOTRUE_JWT_ADMIN_ROLES: "service_role"
      GOTRUE_JWT_AUD: "authenticated"
      GOTRUE_JWT_DEFAULT_GROUP_NAME: "authenticated"
      GOTRUE_JWT_EXP: "3600"
      GOTRUE_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
      GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED: "false"
      GOTRUE_MAILER_AUTOCONFIRM: "false"

      # Phone signups
      GOTRUE_EXTERNAL_PHONE_ENABLED: "false"
      GOTRUE_SMS_AUTOCONFIRM: "false"

      # Mailer / SMTP
      GOTRUE_SMTP_ADMIN_EMAIL: "myadmin@example.com"
      GOTRUE_SMTP_HOST: "mail.example.com"
      GOTRUE_SMTP_PORT: "587"
      GOTRUE_SMTP_USER: "my-smtp-user"
      GOTRUE_SMTP_PASS: "my-smtp-password"
      GOTRUE_SMTP_SENDER_NAME: "My App Emailer"
      GOTRUE_MAILER_URLPATHS_INVITE: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_CONFIRMATION: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_RECOVERY: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE: "/auth/v1/verify"

  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:v12.2.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PGRST_DB_URI: "postgres://authenticator:supabase@db:5432/supabase"
      PGRST_DB_SCHEMAS: "public"
      PGRST_DB_ANON_ROLE: "anon"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_DB_USE_LEGACY_GUCS: "false"
      PGRST_APP_SETTINGS_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_APP_SETTINGS_JWT_EXP: "3600"
    command: "postgrest"

  realtime:
    container_name: realtime-dev.supabase-realtime
    image: supabase/realtime:v2.33.70
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PORT: "4000"
      DB_HOST: "db"
      DB_PORT: "5432"
      DB_USER: "supabase_admin"
      DB_PASSWORD: "supabase"
      DB_NAME: "supabase"
      DB_AFTER_CONNECT_QUERY: "SET search_path TO _realtime"
      DB_ENC_KEY: "supabaserealtime"
      API_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SECRET_KEY_BASE: "UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq"
      ERL_AFLAGS: "-proto_dist inet_tcp"
      DNS_NODES: "''"
      RLIMIT_NOFILE: "10000"
      APP_NAME: "realtime"
      SEED_SELF_HOST: "true"
      RUN_JANITOR: "true"

  storage:
    container_name: supabase-storage
    image: supabase/storage-api:v1.14.5
    depends_on:
      db:
        condition: service_healthy
      rest:
        condition: service_started
      imgproxy:
        condition: service_started
    healthcheck:
      test:
        ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://storage:5000/status"]
      timeout: 5s
      interval: 5s
      retries: 3
    restart: unless-stopped
    environment:
      ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      POSTGREST_URL: "http://rest:3000"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      DATABASE_URL: "postgres://supabase_storage_admin:supabase@db:5432/supabase"
      FILE_SIZE_LIMIT: "52428800"
      STORAGE_BACKEND: "file"
      FILE_STORAGE_BACKEND_PATH: "/var/lib/storage"
      TENANT_ID: "stub"
      REGION: "stub"
      GLOBAL_S3_BUCKET: "stub"
      ENABLE_IMAGE_TRANSFORMATION: "true"
      IMGPROXY_URL: "http://imgproxy:5001"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  imgproxy:
    container_name: supabase-imgproxy
    image: darthsim/imgproxy:v3.8.0
    healthcheck:
      test: ["CMD", "imgproxy", "health"]
      timeout: 5s
      interval: 5s
      retries: 3
    environment:
      IMGPROXY_BIND: ":5001"
      IMGPROXY_LOCAL_FILESYSTEM_ROOT: "/"
      IMGPROXY_USE_ETAG: "true"
      IMGPROXY_ENABLE_WEBP_DETECTION: "true"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:v0.84.2
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PG_META_PORT: "8080"
      PG_META_DB_HOST: "db"
      PG_META_DB_PORT: "5432"
      PG_META_DB_NAME: "supabase"
      PG_META_DB_USER: "supabase_admin"
      PG_META_DB_PASSWORD: "supabase"

  functions:
    container_name: supabase-edge-functions
    image: supabase/edge-runtime:v1.66.4
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      JWT_SECRET: "SFMyNTY.g2gDYQFuBgA8zdCAlAFiAAFRgA.PujAUfyhA9oirQz839ZafEnwITtZZQgKZtB9cpqUA_o"
      SUPABASE_URL: "http://kong:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      SUPABASE_DB_URL: "postgresql://postgres:supabase@db:5432/supabase"
      VERIFY_JWT: "true"
    volumes:
      - "./volumes/functions:/home/deno/functions:Z"
    command:
      - start
      - --main-service
      - /home/deno/functions/main

  analytics:
    container_name: supabase-analytics
    image: supabase/logflare:1.4.0
    healthcheck:
      test: ["CMD", "curl", "http://localhost:4000/health"]
      timeout: 5s
      interval: 5s
      retries: 10
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      LOGFLARE_NODE_HOST: "0.0.0.0:4000"
      DB_USERNAME: "supabase_admin"
      DB_DATABASE: "_supabase"
      DB_HOSTNAME: "db"
      DB_PORT: "5432"
      DB_PASSWORD: "supabase"
      DB_SCHEMA: "_analytics"
      LOGFLARE_PUBLIC_ACCESS_TOKEN: "logflare-api-key"
      LOGFLARE_SINGLE_TENANT: "true"
      LOGFLARE_SUPABASE_MODE: "true"
      LOGFLARE_MIN_CLUSTER_SIZE: "1"

      POSTGRES_BACKEND_URL: "postgresql://supabase_admin:supabase@db:5432/_supabase"
      POSTGRES_BACKEND_SCHEMA: "_analytics"
      LOGFLARE_FEATURE_FLAG_OVERRIDE: "multibackend=true"

      # If using BigQuery:
      # GOOGLE_PROJECT_ID: "my-google-project"
      # GOOGLE_PROJECT_NUMBER: "1234567890"
    ports:
      - "4000:4000"

  db:
    container_name: supabase-db
    image: supabase/postgres:15.8.1.020
    healthcheck:
      test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 10
    depends_on:
      vector:
        condition: service_healthy
    command:
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
      - -c
      - log_min_messages=fatal
    restart: unless-stopped
    ports:
      - "5432:5432"  # <--- Directly expose Postgres port on the host
    environment:
      POSTGRES_HOST: "/var/run/postgresql"
      PGPORT: "5432"
      POSTGRES_PORT: "5432"
      PGPASSWORD: "supabase"
      POSTGRES_PASSWORD: "supabase"
      PGDATABASE: "supabase"
      POSTGRES_DB: "supabase"
      JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      JWT_EXP: "3600"
    volumes:
      - "./volumes/db/realtime.sql:/docker-entrypoint-initdb.d/migrations/99-realtime.sql:Z"
      - "./volumes/db/webhooks.sql:/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql:Z"
      - "./volumes/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:Z"
      - "./volumes/db/jwt.sql:/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql:Z"
      - "./volumes/db/data:/var/lib/postgresql/data:Z"
      - "./volumes/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:Z"
      - "./volumes/db/logs.sql:/docker-entrypoint-initdb.d/migrations/99-logs.sql:Z"
      # REMOVE pooler.sql reference:
      # - "./volumes/db/pooler.sql:/docker-entrypoint-initdb.d/migrations/99-pooler.sql:Z"
      - "db-config:/etc/postgresql-custom"

  vector:
    container_name: supabase-vector
    image: timberio/vector:0.28.1-alpine
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "--no-verbose",
          "--tries=1",
          "--spider",
          "http://vector:9001/health"
        ]
      timeout: 5s
      interval: 5s
      retries: 3
    volumes:
      - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      LOGFLARE_API_KEY: "logflare-api-key"
    command: ["--config", "/etc/vector/vector.yml"]

# REMOVE the supavisor service entirely:
# supavisor:
#   container_name: supabase-pooler
#   ...

volumes:
  db-config:


#### ChatGPT:
<time datetime="2025-01-20T00:47:44.814Z" title="1/20/2025, 9:47:44 AM">09:47</time>

It’s a **DNS resolution error** inside the `vector` container. Essentially, Vector is trying to POST logs to Logflare (the “analytics” service), but the hostname it’s using cannot be resolved from inside Docker. That’s why you see errors like:

```
HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again
```

Below are the usual causes and how to fix them.

---

## 1. Make sure Vector’s config points to the correct Docker service name

Inside Docker Compose, containers resolve each other by **service name**, not by “localhost” or container name. For example, if your service is:

```yaml
services:
  analytics:
    container_name: supabase-analytics
    ...
    ports:
      - "4000:4000"
```

then **inside** Docker, the hostname is simply `analytics` (the service key), on port `4000`. In other words, to reach that container from the `vector` container, you’d use:

```
http://analytics:4000
```

**Common mistake:** If your config says something like `0.0.0.0:4000`, `localhost:4000`, or `127.0.0.1:4000`, that only works **inside** the analytics container itself (or on the host machine if you mapped the port). But from the separate `vector` container, that address won’t work.

### Where to change this

You likely have a Vector config file (e.g. `./volumes/logs/vector.yml`) referencing a host like `0.0.0.0:4000` or `localhost:4000`. Change that to `analytics:4000` (matching your Docker service name). For example, in `vector.yml` you might see:

```yaml
[sinks.logflare_db]
type = "http"
inputs = ["some_source"]
uri = "http://0.0.0.0:4000/logs"   # WRONG
```

Change to:

```yaml
uri = "http://analytics:4000/logs" # CORRECT
```

If you’re passing this via environment variables, similarly update:

```yaml
# In your analytics or vector environment:
LOGFLARE_NODE_HOST=analytics:4000
```

---

## 2. Confirm the service name is indeed “analytics”

By default, the snippet shows:

```yaml
services:
  analytics:
    container_name: supabase-analytics
    ...
```

So the Docker DNS hostname is **`analytics`**. The container name (`supabase-analytics`) does not matter for Docker DNS. If you removed or renamed that service, or if the service key is different, use that name instead.

---

## 3. (Optional) Remove the analytics+vector stack if you don’t need logs

If you do not need Logflare analytics, you can remove or comment out the `analytics` and `vector` services entirely. This will eliminate the DNS errors.

---

## Summary

1. **Check your Vector config** (or environment variables) and replace any references to `0.0.0.0`, `localhost`, or `127.0.0.1` with the actual **service name** (`analytics`) inside Docker Compose.
2. Ensure the port is `4000` (the internal port for Logflare in your Compose).
3. Rebuild or restart your containers:
   ```bash
   docker compose up --build -d
   ```
4. Vector should now be able to resolve `analytics` and send logs successfully.


#### You:
<time datetime="2025-01-20T00:51:01.273Z" title="1/20/2025, 9:51:01 AM">09:51</time>

dependency failed to start: container supabase-db is unhealthy
2025-01-20T00:49:32.548718Z  INFO vector::app: Internal log rate limit configured. internal_log_rate_secs=10
2025-01-20T00:49:32.548833Z  INFO vector::app: Log level is enabled. level="vector=info,codec=info,vrl=info,file_source=info,tower_limit=trace,rdkafka=info,buffers=info,lapin=info,kube=info"
2025-01-20T00:49:32.548889Z  INFO vector::app: Loading configs. paths=["/etc/vector/vector.yml"]
2025-01-20T00:49:32.563016Z  WARN vector::config::loading: Transform "router._unmatched" has no consumers
2025-01-20T00:49:32.563751Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Capturing logs from now on. now=2025-01-20T00:49:32.563714595+00:00
2025-01-20T00:49:32.563790Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Listening to docker log events.
2025-01-20T00:49:32.644175Z  INFO vector::topology::running: Running healthchecks.
2025-01-20T00:49:32.644232Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644249Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644254Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644257Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644260Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644265Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644268Z  INFO vector::topology::builder: Healthcheck passed.
2025-01-20T00:49:32.644367Z  INFO vector: Vector has started. debug="false" version="0.28.1" arch="x86_64" revision="ff15924 2023-03-06"
2025-01-20T00:49:32.645848Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Excluded self container. id=e4e6c23bff57194610ff03d8658faab18c016d358a2a9f0a643417e19a389c12
2025-01-20T00:49:32.646296Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=4eac5f2e417495b98371f3a664a4a9cc20efac54e86a8950fd72a3d1e6c9bef3

#### ChatGPT:
<time datetime="2025-01-20T00:51:25.333Z" title="1/20/2025, 9:51:25 AM">09:51</time>

When the **`supabase-db`** container is marked “unhealthy,” it usually means that:

1. The database itself failed to start or crashed, **or**
2. The **healthcheck** command is failing.

Below are some troubleshooting steps:

---

## 1. Check the actual Postgres logs

First, see what’s happening **inside** the `supabase-db` container:

```bash
# Check logs for the DB container by ID or name:
docker logs supabase-db
# or
docker logs <CONTAINER_ID>
```

Sometimes, `docker compose logs supabase-db` fails if the service name does not match your Compose project name. Using `docker logs` directly on the container ID is more reliable. You’ll likely see an error message that explains why Postgres cannot start or why the healthcheck is failing.

---

## 2. Confirm the health check command actually exists

Your Compose uses:

```yaml
healthcheck:
  test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
  interval: 5s
  timeout: 5s
  retries: 10
```

But the **`_isready`** command may not exist in the `supabase/postgres` image. Try switching to the standard PostgreSQL tool **`pg_isready`**. For example:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -h localhost"]
  interval: 5s
  timeout: 5s
  retries: 10
```

> If `_isready` is failing with `command not found`, your container will always be “unhealthy,” even if the database itself is running fine.

---

## 3. Look for version or config mismatches

If you’re reusing an old **data volume** from a different Postgres version, sometimes migrations or settings can break startup. Check the logs for errors like “incompatible data directory format.”

Also verify your environment variables (like `POSTGRES_PASSWORD=supabase`) match the roles in the DB.

---

## 4. Start fresh (optional)

If you are just testing locally and don’t mind losing data, try removing the old volumes:

```bash
docker compose down -v
docker compose up -d
```

The `-v` removes named volumes declared in your Compose file, giving you a clean slate. This often fixes leftover DB corruption or mismatch issues.

---

## 5. Summary of fixes

1. **Inspect logs**: `docker logs supabase-db` (or container ID).
2. **Change `_isready` → `pg_isready`** in your healthcheck if `_isready` does not exist.
3. **Remove old volumes** if there are version mismatches.
4. Restart the stack:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

Once the underlying error is fixed or the healthcheck command is corrected, the `supabase-db` container should report as “healthy” again.


#### You:
<time datetime="2025-01-20T00:57:08.819Z" title="1/20/2025, 9:57:08 AM">09:57</time>

 ✔ Network docker_default                    Created                                                                                                                     0.1s 
 ✔ Volume "docker_db-config"                 Created                                                                                                                     0.0s 
 ✔ Container supabase-vector                 Healthy                                                                                                                     6.2s 
 ✔ Container supabase-imgproxy               Started                                                                                                                     0.7s 
 ✘ Container supabase-db                     Error                                                                                                                      56.8s 
 ✔ Container supabase-analytics              Created                                                                                                                     0.1s 
 ✔ Container supabase-rest                   Created                                                                                                                     0.1s 
 ✔ Container supabase-edge-functions         Created                                                                                                                     0.1s 
 ✔ Container realtime-dev.supabase-realtime  Created                                                                                                                     0.1s 
 ✔ Container supabase-kong                   Created                                                                                                                     0.1s 
 ✔ Container supabase-studio                 Created                                                                                                                     0.1s 
 ✔ Container supabase-auth                   Created                                                                                                                     0.1s 
 ✔ Container supabase-meta                   Created                                                                                                                     0.1s 
 ✔ Container supabase-storage                Created                                                                                                                     0.1s 
dependency failed to start: container supabase-db is unhealthy
supabase-db        | 
supabase-db        | 
supabase-db        | PostgreSQL Database directory appears to contain a database; Skipping initialization
supabase-db        | 
supabase-db        | 
supabase-imgproxy  | WARNING [2025-01-20T00:55:30Z] No keys defined, so signature checking is disabled 
supabase-vector    | 2025-01-20T00:55:30.049697Z  INFO vector::app: Internal log rate limit configured. internal_log_rate_secs=10
supabase-vector    | 2025-01-20T00:55:30.049823Z  INFO vector::app: Log level is enabled. level="vector=info,codec=info,vrl=info,file_source=info,tower_limit=trace,rdkafka=info,buffers=info,lapin=info,kube=info"
supabase-vector    | 2025-01-20T00:55:30.049881Z  INFO vector::app: Loading configs. paths=["/etc/vector/vector.yml"]
supabase-imgproxy  | WARNING [2025-01-20T00:55:30Z] No salts defined, so signature checking is disabled 
supabase-imgproxy  | WARNING [2025-01-20T00:55:30Z] Exposing root via IMGPROXY_LOCAL_FILESYSTEM_ROOT is unsafe 
supabase-imgproxy  | INFO    [2025-01-20T00:55:30Z] Starting server at :5001 
supabase-imgproxy  | INFO    [2025-01-20T00:55:35Z] Started /health  request_id=nHS3_7WsoNQ2eBtMP6oGL method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:35Z] Completed in 22.63µs /health  request_id=nHS3_7WsoNQ2eBtMP6oGL method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:40Z] Started /health  request_id=hUAaFF3NWofkpn9o0RDxu method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:40Z] Completed in 37.409µs /health  request_id=hUAaFF3NWofkpn9o0RDxu method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:45Z] Started /health  request_id=VrLua1K-iriFAt-cysBi5 method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:45Z] Completed in 30.35µs /health  request_id=VrLua1K-iriFAt-cysBi5 method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:50Z] Started /health  request_id=6lyo7xBf9pNN-zlLYxZHi method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:50Z] Completed in 52.099µs /health  request_id=6lyo7xBf9pNN-zlLYxZHi method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:55Z] Started /health  request_id=8tUw8FQjrtdrx6ygpp4Y2 method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:55:55Z] Completed in 39.61µs /health  request_id=8tUw8FQjrtdrx6ygpp4Y2 method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:00Z] Started /health  request_id=nrmDL9MNgDACx6H_APiy8 method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:00Z] Completed in 59.02µs /health  request_id=nrmDL9MNgDACx6H_APiy8 method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:05Z] Started /health  request_id=eLgdeaj6TakBGvO7vsOxv method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:05Z] Completed in 37.21µs /health  request_id=eLgdeaj6TakBGvO7vsOxv method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:10Z] Started /health  request_id=QSkKG_SYryE1DKWrNq0zY method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:10Z] Completed in 58.229µs /health  request_id=QSkKG_SYryE1DKWrNq0zY method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:15Z] Started /health  request_id=YniTouwugn59Tds8kuB4o method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:15Z] Completed in 33.64µs /health  request_id=YniTouwugn59Tds8kuB4o method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:20Z] Started /health  request_id=g6idmSEpAXGag9KjmlyD1 method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:20Z] Completed in 44.61µs /health  request_id=g6idmSEpAXGag9KjmlyD1 method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:25Z] Started /health  request_id=teJ2M9bhaA8iI8GUYpVan method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:25Z] Completed in 34.51µs /health  request_id=teJ2M9bhaA8iI8GUYpVan method=GET status=200 client_ip=127.0.0.1
supabase-vector    | 2025-01-20T00:55:30.064040Z  WARN vector::config::loading: Transform "router._unmatched" has no consumers
supabase-vector    | 2025-01-20T00:55:30.064694Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Capturing logs from now on. now=2025-01-20T00:55:30.064654342+00:00
supabase-vector    | 2025-01-20T00:55:30.064732Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Listening to docker log events.
supabase-vector    | 2025-01-20T00:55:30.146462Z  INFO vector::topology::running: Running healthchecks.
supabase-vector    | 2025-01-20T00:55:30.146516Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146528Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146537Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146541Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146545Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146551Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146554Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:55:30.146643Z  INFO vector: Vector has started. debug="false" version="0.28.1" arch="x86_64" revision="ff15924 2023-03-06"
supabase-vector    | 2025-01-20T00:55:30.148223Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Excluded self container. id=ae81b3a0e5ec8739a32b4840c8c5c1e2a69f7db2de7fb94191be8519be5553d9
supabase-vector    | 2025-01-20T00:55:30.148680Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=a2b7aa2d74abb6004a57d91f2f4b7e6adab21f4efc8f8bf31e554d89de032fc1
supabase-vector    | 2025-01-20T00:55:30.148829Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=4eac5f2e417495b98371f3a664a4a9cc20efac54e86a8950fd72a3d1e6c9bef3
supabase-vector    | 2025-01-20T00:55:30.148844Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=030052732b1dee606b56e627e94b09ad70199f718ed270b59306b4f152327d48
supabase-vector    | 2025-01-20T00:55:30.148846Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=9638fe1eface210c86bc715b9365d0a00fe7468f3346bc164667764ed72b9695
supabase-vector    | 2025-01-20T00:55:30.148889Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=0d028d8b521a8a98b5b63a3fb1c05229331a5369b9997949419d0f45a723460a
supabase-vector    | 2025-01-20T00:55:30.148902Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=1a8cf7285d91dcd9b818ce4410ebf45f4cd9c26163d1f4549f8cbb4b87db62a2
supabase-vector    | 2025-01-20T00:55:30.148905Z ERROR source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Received out of order log message. error_type="condition_failed" stage="receiving" container_id="a2b7aa2d74abb6004a57d91f2f4b7e6adab21f4efc8f8bf31e554d89de032fc1" timestamp="2025-01-20T00:55:30.044535303Z" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:55:30.148924Z ERROR source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Internal log [Received out of order log message.] is being rate limited.
supabase-vector    | 2025-01-20T00:55:30.148996Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=dee666c898b3446715ebbd32b071b6cdc433474375ac2ab20ac2dfc5ba587aca
supabase-vector    | 2025-01-20T00:55:30.153711Z  INFO vector::internal_events::api: API server running. address=0.0.0.0:9001 playground=http://0.0.0.0:9001/playground
supabase-vector    | 2025-01-20T00:55:35.774363Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=afec2c0853e18b152c2b35b800b6331adb4213c1ec16f7b227f573dde7f6cd0d
supabase-vector    | 2025-01-20T00:55:35.785049Z ERROR transform{component_kind="transform" component_id=db_logs component_type=remap component_name=db_logs}: vector::internal_events::remap: Mapping failed with event. error="function call error for \"upcase\" at (476:516): expected string, got null" error_type="conversion_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:55:35.785152Z ERROR transform{component_kind="transform" component_id=db_logs component_type=remap component_name=db_logs}: vector::internal_events::remap: Internal log [Mapping failed with event.] is being rate limited.
supabase-vector    | 2025-01-20T00:55:41.792423Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:55:41.792461Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:55:47.800001Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: Internal log [HTTP error.] is being rate limited.
supabase-vector    | 2025-01-20T00:55:47.800029Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Internal log [Retrying after error.] is being rate limited.
supabase-vector    | 2025-01-20T00:55:53.806948Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: Internal log [HTTP error.] has been rate limited 1 times.
supabase-vector    | 2025-01-20T00:55:53.806986Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:55:53.807018Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Internal log [Retrying after error.] has been rate limited 1 times.
supabase-vector    | 2025-01-20T00:55:53.807021Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:00.813676Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: Internal log [HTTP error.] is being rate limited.
supabase-vector    | 2025-01-20T00:56:00.813709Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Internal log [Retrying after error.] is being rate limited.
supabase-vector    | 2025-01-20T00:56:08.820991Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: Internal log [HTTP error.] has been rate limited 1 times.
supabase-vector    | 2025-01-20T00:56:08.821004Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:08.821028Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Internal log [Retrying after error.] has been rate limited 1 times.
supabase-vector    | 2025-01-20T00:56:08.821030Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:18.828967Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:18.829000Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-imgproxy  | INFO    [2025-01-20T00:56:30Z] Started /health  request_id=UgYgn80jKWPsEF26IRCeh method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:30Z] Completed in 62.39µs /health  request_id=UgYgn80jKWPsEF26IRCeh method=GET status=200 client_ip=127.0.0.1
supabase-vector    | 2025-01-20T00:56:31.836813Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:31.836847Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-imgproxy  | INFO    [2025-01-20T00:56:35Z] Started /health  request_id=b2NK8YvOYsZP0Vn6uR0J1 method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:35Z] Completed in 39.08µs /health  request_id=b2NK8YvOYsZP0Vn6uR0J1 method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:40Z] Started /health  request_id=DRZZm-FEsEtfApFspbmbE method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:40Z] Completed in 55.109µs /health  request_id=DRZZm-FEsEtfApFspbmbE method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:45Z] Started /health  request_id=Iln2_RNYEhAQP44J0Mgs- method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:45Z] Completed in 31.27µs /health  request_id=Iln2_RNYEhAQP44J0Mgs- method=GET status=200 client_ip=127.0.0.1
supabase-vector    | 2025-01-20T00:56:46.843562Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}:http: vector::internal_events::http_client: HTTP error. error=error trying to connect: dns error: failed to lookup address information: Try again error_type="request_failed" stage="processing" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:56:46.843594Z  WARN sink{component_kind="sink" component_id=logflare_db component_type=http component_name=logflare_db}:request{request_id=0}: vector::sinks::util::retries: Retrying after error. error=Failed to make HTTP(S) request: error trying to connect: dns error: failed to lookup address information: Try again internal_log_rate_limit=true
supabase-imgproxy  | INFO    [2025-01-20T00:56:50Z] Started /health  request_id=ai963LwfJoq1P0RFisnOs method=GET client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:50Z] Completed in 47.999µs /health  request_id=ai963LwfJoq1P0RFisnOs method=GET status=200 client_ip=127.0.0.1
supabase-imgproxy  | INFO    [2025-01-20T00:56:55Z] Started /health  reques

#### ChatGPT:
<time datetime="2025-01-20T00:57:20.847Z" title="1/20/2025, 9:57:20 AM">09:57</time>

It appears your **`supabase-db`** container is **failing its health check** and therefore being marked as “unhealthy.” This usually happens if either:

1. The **health check command** (`_isready` or `pg_isready`) is failing or missing.
2. There is an **incompatible existing data directory** from a previous Postgres version or a corrupted database.
3. Some **other Postgres startup error** is occurring (e.g. a bad init script).

The logs snippet shows just:

```
PostgreSQL Database directory appears to contain a database; Skipping initialization
```

but no specific error message. That alone doesn’t mean it failed—Postgres typically says this when it sees an existing data directory. You need to see if the health check or the server itself is failing afterward.

Below are recommended steps to troubleshoot and fix:

---

## 1. Check the **full** container logs

Use the **container ID** or name (`supabase-db`) directly:

```bash
docker logs supabase-db
```

(If it scrolls too fast, add `--tail 1000` or `--follow`.)

Look for any lines after `Skipping initialization` that indicate a crash or error. Sometimes you’ll see a “database system is ready to accept connections,” which means Postgres is fine—and then you discover the **health check** is failing. Other times, you’ll see a real error (like “FATAL: could not open directory,” or “incompatible data directory”).

---

## 2. Verify the health check command

Inside your `docker-compose.yml`, look at the `db:` service’s **healthcheck**. If you have something like:

```yaml
healthcheck:
  test: ["CMD-SHELL", "_isready -U postgres -h localhost"]
  interval: 5s
  timeout: 5s
  retries: 10
```

…the `_isready` command may not actually exist in the `supabase/postgres` image. The standard PostgreSQL tool is **`pg_isready`**. So update to:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -h localhost"]
  interval: 5s
  timeout: 5s
  retries: 10
```

Save and do:

```bash
docker compose up -d --build
```

After it pulls or rebuilds, see if `supabase-db` becomes healthy. If `pg_isready` also isn’t found, you can remove or adjust the health check, or exec into the container to confirm which commands exist.

---

## 3. Check for leftover/corrupted volumes (version mismatch)

If your data directory was created under a different Postgres version (or corrupted), it may fail to start or fail a readiness check. If you do not need your old data, you can nuke it and let the container start fresh:

1. Stop and remove containers:
   ```bash
   docker compose down
   ```
2. Remove volumes (careful—this deletes all DB data):
   ```bash
   docker compose down -v
   ```
3. Start fresh:
   ```bash
   docker compose up -d
   ```

If there was a mismatch, that often fixes it.

---

## 4. Look for failing init scripts

If you have custom `.sql` in `docker-entrypoint-initdb.d/`, sometimes a broken script can crash Postgres. Check your logs for errors like “ERROR: syntax error at or near…” or “FATAL: role does not exist.” If you see these, comment out or fix that SQL script.

---

## 5. Temporarily remove the health check

If you suspect it’s simply the **health check** failing but Postgres is actually okay, you can remove/comment it out to confirm:

```yaml
db:
  # ...
  healthcheck:
    # test: ["CMD-SHELL", "pg_isready -U postgres -h localhost"]
    # interval: 5s
    # timeout: 5s
    # retries: 10
```

Then run `docker compose up -d` and see if the container remains “Up” (without “(unhealthy)” status). If so, the database is likely fine, and the health check command was simply not recognized or returning a failure code.

---

## Summary

1. **Check Postgres logs** (`docker logs supabase-db`) after “Skipping initialization” to see if it actually started or crashed.
2. **Fix or remove the health check**: use `pg_isready` instead of `_isready`, or comment out the healthcheck to confirm that’s the issue.
3. **Remove volumes** if there might be a leftover DB from an older version.
4. If you find an actual error in the logs, address that specific cause (e.g. invalid SQL migrations).

Following these steps usually resolves the “container is unhealthy” problem with the `supabase-db` service. Once the DB is healthy, the rest of the services should start normally.


#### You:
<time datetime="2025-01-20T01:01:03.057Z" title="1/20/2025, 10:01:03 AM">10:01</time>

version: "3.9"

services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:20250113-83c9420
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      # Inlined environment values
      STUDIO_PG_META_URL: "http://meta:8080"
      POSTGRES_PASSWORD: "supabase"

      DEFAULT_ORGANIZATION_NAME: "MyOrganization"
      DEFAULT_PROJECT_NAME: "MyProject"
      OPENAI_API_KEY: ""  # or leave blank

      SUPABASE_URL: "http://kong:8000"
      SUPABASE_PUBLIC_URL: "http://localhost:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      AUTH_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      LOGFLARE_PUBLIC_ACCESS_TOKEN: ""
      LOGFLARE_URL: "http://analytics:4000"
      NEXT_PUBLIC_ENABLE_LOGS: "true"
      NEXT_ANALYTICS_BACKEND_PROVIDER: "postgres"
      # Uncomment if using BigQuery for analytics
      # NEXT_ANALYTICS_BACKEND_PROVIDER: "bigquery"

  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    restart: unless-stopped
    entrypoint: bash -c 'eval "echo \"$$(cat ~/temp.yml)\"" > ~/kong.yml && /docker-entrypoint.sh kong docker-start'
    ports:
      - "8000:8000/tcp"   # From KONG_HTTP_PORT=8000
      - "8443:8443/tcp"   # From KONG_HTTPS_PORT=8443
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: "/home/kong/kong.yml"
      KONG_DNS_ORDER: "LAST,A,CNAME"
      KONG_PLUGINS: "request-transformer,cors,key-auth,acl,basic-auth"
      KONG_NGINX_PROXY_PROXY_BUFFER_SIZE: "160k"
      KONG_NGINX_PROXY_PROXY_BUFFERS: "64 160k"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      DASHBOARD_USERNAME: "admin"
      DASHBOARD_PASSWORD: "supabase"
    volumes:
      - "./volumes/api/kong.yml:/home/kong/temp.yml:ro"

  auth:
    container_name: supabase-auth
    image: supabase/gotrue:v2.167.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      GOTRUE_API_HOST: "0.0.0.0"
      GOTRUE_API_PORT: "9999"
      API_EXTERNAL_URL: "http://127.0.0.1:8080"  # originally blank

      GOTRUE_DB_DRIVER: "postgres"
      GOTRUE_DB_DATABASE_URL: "postgres://supabase_auth_admin:supabase@db:5432/supabase"

      GOTRUE_SITE_URL: "http://localhost:3000"
      GOTRUE_URI_ALLOW_LIST: "http://localhost:3000"
      GOTRUE_DISABLE_SIGNUP: "false"

      GOTRUE_JWT_ADMIN_ROLES: "service_role"
      GOTRUE_JWT_AUD: "authenticated"
      GOTRUE_JWT_DEFAULT_GROUP_NAME: "authenticated"
      GOTRUE_JWT_EXP: "3600"
      GOTRUE_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"

      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
      GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED: "false"
      GOTRUE_MAILER_AUTOCONFIRM: "false"

      # Phone signups
      GOTRUE_EXTERNAL_PHONE_ENABLED: "false"
      GOTRUE_SMS_AUTOCONFIRM: "false"

      # Mailer / SMTP
      GOTRUE_SMTP_ADMIN_EMAIL: "myadmin@example.com"
      GOTRUE_SMTP_HOST: "mail.example.com"
      GOTRUE_SMTP_PORT: "587"
      GOTRUE_SMTP_USER: "my-smtp-user"
      GOTRUE_SMTP_PASS: "my-smtp-password"
      GOTRUE_SMTP_SENDER_NAME: "My App Emailer"
      GOTRUE_MAILER_URLPATHS_INVITE: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_CONFIRMATION: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_RECOVERY: "/auth/v1/verify"
      GOTRUE_MAILER_URLPATHS_EMAIL_CHANGE: "/auth/v1/verify"

  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:v12.2.0
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PGRST_DB_URI: "postgres://authenticator:supabase@db:5432/supabase"
      PGRST_DB_SCHEMAS: "public"
      PGRST_DB_ANON_ROLE: "anon"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_DB_USE_LEGACY_GUCS: "false"
      PGRST_APP_SETTINGS_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      PGRST_APP_SETTINGS_JWT_EXP: "3600"
    command: "postgrest"

  realtime:
    container_name: realtime-dev.supabase-realtime
    image: supabase/realtime:v2.33.70
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PORT: "4000"
      DB_HOST: "db"
      DB_PORT: "5432"
      DB_USER: "supabase_admin"
      DB_PASSWORD: "supabase"
      DB_NAME: "supabase"
      DB_AFTER_CONNECT_QUERY: "SET search_path TO _realtime"
      DB_ENC_KEY: "supabaserealtime"
      API_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SECRET_KEY_BASE: "UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq"
      ERL_AFLAGS: "-proto_dist inet_tcp"
      DNS_NODES: "''"
      RLIMIT_NOFILE: "10000"
      APP_NAME: "realtime"
      SEED_SELF_HOST: "true"
      RUN_JANITOR: "true"

  storage:
    container_name: supabase-storage
    image: supabase/storage-api:v1.14.5
    depends_on:
      db:
        condition: service_healthy
      rest:
        condition: service_started
      imgproxy:
        condition: service_started
    restart: unless-stopped
    environment:
      ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SERVICE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      POSTGREST_URL: "http://rest:3000"
      PGRST_JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      DATABASE_URL: "postgres://supabase_storage_admin:supabase@db:5432/supabase"
      FILE_SIZE_LIMIT: "52428800"
      STORAGE_BACKEND: "file"
      FILE_STORAGE_BACKEND_PATH: "/var/lib/storage"
      TENANT_ID: "stub"
      REGION: "stub"
      GLOBAL_S3_BUCKET: "stub"
      ENABLE_IMAGE_TRANSFORMATION: "true"
      IMGPROXY_URL: "http://imgproxy:5001"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  imgproxy:
    container_name: supabase-imgproxy
    image: darthsim/imgproxy:v3.8.0
    environment:
      IMGPROXY_BIND: ":5001"
      IMGPROXY_LOCAL_FILESYSTEM_ROOT: "/"
      IMGPROXY_USE_ETAG: "true"
      IMGPROXY_ENABLE_WEBP_DETECTION: "true"
    volumes:
      - "./volumes/storage:/var/lib/storage:z"

  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:v0.84.2
    depends_on:
      db:
        condition: service_healthy
      analytics:
        condition: service_healthy
    restart: unless-stopped
    environment:
      PG_META_PORT: "8080"
      PG_META_DB_HOST: "db"
      PG_META_DB_PORT: "5432"
      PG_META_DB_NAME: "supabase"
      PG_META_DB_USER: "supabase_admin"
      PG_META_DB_PASSWORD: "supabase"

  functions:
    container_name: supabase-edge-functions
    image: supabase/edge-runtime:v1.66.4
    restart: unless-stopped
    depends_on:
      analytics:
        condition: service_healthy
    environment:
      JWT_SECRET: "SFMyNTY.g2gDYQFuBgA8zdCAlAFiAAFRgA.PujAUfyhA9oirQz839ZafEnwITtZZQgKZtB9cpqUA_o"
      SUPABASE_URL: "http://kong:8000"
      SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3MzcyNzM2MDAsCiAgImV4cCI6IDE4OTUwNDAwMDAKfQ.YdIElwh7eSnAbaTFLDI1vmUagahETgpgXn63ZNzzuPA"
      SUPABASE_DB_URL: "postgresql://postgres:supabase@db:5432/supabase"
      VERIFY_JWT: "true"
    volumes:
      - "./volumes/functions:/home/deno/functions:Z"
    command:
      - start
      - --main-service
      - /home/deno/functions/main

  analytics:
    container_name: supabase-analytics
    image: supabase/logflare:1.4.0
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      LOGFLARE_NODE_HOST: "http://analytics:4000"
      DB_USERNAME: "supabase_admin"
      DB_DATABASE: "_supabase"
      DB_HOSTNAME: "db"
      DB_PORT: "5432"
      DB_PASSWORD: "supabase"
      DB_SCHEMA: "_analytics"
      LOGFLARE_PUBLIC_ACCESS_TOKEN: "logflare-api-key"
      LOGFLARE_SINGLE_TENANT: "true"
      LOGFLARE_SUPABASE_MODE: "true"
      LOGFLARE_MIN_CLUSTER_SIZE: "1"

      POSTGRES_BACKEND_URL: "postgresql://supabase_admin:supabase@db:5432/_supabase"
      POSTGRES_BACKEND_SCHEMA: "_analytics"
      LOGFLARE_FEATURE_FLAG_OVERRIDE: "multibackend=true"

      # If using BigQuery:
      # GOOGLE_PROJECT_ID: "my-google-project"
      # GOOGLE_PROJECT_NUMBER: "1234567890"
    ports:
      - "4000:4000"

  db:
    container_name: supabase-db
    image: supabase/postgres:15.8.1.020
    depends_on:
      vector:
        condition: service_healthy
    command:
      - postgres
      - -c
      - config_file=/etc/postgresql/postgresql.conf
      - -c
      - log_min_messages=fatal
    restart: unless-stopped
    ports:
      - "5432:5432"  # <--- Directly expose Postgres port on the host
    environment:
      POSTGRES_HOST: "/var/run/postgresql"
      PGPORT: "5432"
      POSTGRES_PORT: "5432"
      PGPASSWORD: "supabase"
      POSTGRES_PASSWORD: "supabase"
      PGDATABASE: "supabase"
      POSTGRES_DB: "supabase"
      JWT_SECRET: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzM3MjczNjAwLAogICJleHAiOiAxODk1MDQwMDAwCn0.RW03LirVPN5gFy_mEIquogibKXredfUFlOuuqhs9nOg"
      JWT_EXP: "3600"
    volumes:
      - "./volumes/db/realtime.sql:/docker-entrypoint-initdb.d/migrations/99-realtime.sql:Z"
      - "./volumes/db/webhooks.sql:/docker-entrypoint-initdb.d/init-scripts/98-webhooks.sql:Z"
      - "./volumes/db/roles.sql:/docker-entrypoint-initdb.d/init-scripts/99-roles.sql:Z"
      - "./volumes/db/jwt.sql:/docker-entrypoint-initdb.d/init-scripts/99-jwt.sql:Z"
      - "./volumes/db/data:/var/lib/postgresql/data:Z"
      - "./volumes/db/_supabase.sql:/docker-entrypoint-initdb.d/migrations/97-_supabase.sql:Z"
      - "./volumes/db/logs.sql:/docker-entrypoint-initdb.d/migrations/99-logs.sql:Z"
      # REMOVE pooler.sql reference:
      # - "./volumes/db/pooler.sql:/docker-entrypoint-initdb.d/migrations/99-pooler.sql:Z"
      - "db-config:/etc/postgresql-custom"

  vector:
    container_name: supabase-vector
    image: timberio/vector:0.28.1-alpine
    volumes:
      - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      LOGFLARE_API_KEY: "logflare-api-key"
    command: ["--config", "/etc/vector/vector.yml"]

# REMOVE the supavisor service entirely:
# supavisor:
#   container_name: supabase-pooler
#   ...

volumes:
  db-config:

[+] Running 14/14
 ✔ Network docker_default                    Created                                                                                                                     0.1s 
 ✔ Volume "docker_db-config"                 Created                                                                                                                     0.0s 
 ✘ Container supabase-vector                 Error                                                                                                                       1.2s 
 ✔ Container supabase-imgproxy               Started                                                                                                                     0.7s 
 ✔ Container supabase-db                     Created                                                                                                                     0.1s 
 ✔ Container supabase-analytics              Created                                                                                                                     0.1s 
 ✔ Container supabase-meta                   Created                                                                                                                     0.1s 
 ✔ Container supabase-studio                 Created                                                                                                                     0.1s 
 ✔ Container supabase-kong                   Created                                                                                                                     0.1s 
 ✔ Container supabase-auth                   Created                                                                                                                     0.1s 
 ✔ Container supabase-rest                   Created                                                                                                                     0.1s 
 ✔ Container realtime-dev.supabase-realtime  Created                                                                                                                     0.1s 
 ✔ Container supabase-edge-functions         Created                                                                                                                     0.1s 
 ✔ Container supabase-storage                Created                                                                                                                     0.1s 
dependency failed to start: container supabase-vector has no healthcheck configured
supabase-imgproxy  | WARNING [2025-01-20T00:59:22Z] No keys defined, so signature checking is disabled 
supabase-imgproxy  | WARNING [2025-01-20T00:59:22Z] No salts defined, so signature checking is disabled 
supabase-imgproxy  | WARNING [2025-01-20T00:59:22Z] Exposing root via IMGPROXY_LOCAL_FILESYSTEM_ROOT is unsafe 
supabase-imgproxy  | INFO    [2025-01-20T00:59:22Z] Starting server at :5001 
supabase-vector    | 2025-01-20T00:59:22.240203Z  INFO vector::app: Internal log rate limit configured. internal_log_rate_secs=10
supabase-vector    | 2025-01-20T00:59:22.240335Z  INFO vector::app: Log level is enabled. level="vector=info,codec=info,vrl=info,file_source=info,tower_limit=trace,rdkafka=info,buffers=info,lapin=info,kube=info"
supabase-vector    | 2025-01-20T00:59:22.240398Z  INFO vector::app: Loading configs. paths=["/etc/vector/vector.yml"]
supabase-vector    | 2025-01-20T00:59:22.255249Z  WARN vector::config::loading: Transform "router._unmatched" has no consumers
supabase-vector    | 2025-01-20T00:59:22.256008Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Capturing logs from now on. now=2025-01-20T00:59:22.255970127+00:00
supabase-vector    | 2025-01-20T00:59:22.256047Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Listening to docker log events.
supabase-vector    | 2025-01-20T00:59:22.341269Z  INFO vector::topology::running: Running healthchecks.
supabase-vector    | 2025-01-20T00:59:22.341310Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341318Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341322Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341325Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341328Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341331Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341335Z  INFO vector::topology::builder: Healthcheck passed.
supabase-vector    | 2025-01-20T00:59:22.341430Z  INFO vector: Vector has started. debug="false" version="0.28.1" arch="x86_64" revision="ff15924 2023-03-06"
supabase-vector    | 2025-01-20T00:59:22.343306Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::sources::docker_logs: Excluded self container. id=39165fc53f942d5f09d28fc8100ee1f08afeeed1ca8d173b6953abd45ef2f901
supabase-vector    | 2025-01-20T00:59:22.344073Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=dee666c898b3446715ebbd32b071b6cdc433474375ac2ab20ac2dfc5ba587aca
supabase-vector    | 2025-01-20T00:59:22.344087Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=1deae4d49b7341722cb9689404d7737b93d20083daca945eb8bd5a9dc5c2f530
supabase-vector    | 2025-01-20T00:59:22.344093Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=4eac5f2e417495b98371f3a664a4a9cc20efac54e86a8950fd72a3d1e6c9bef3
supabase-vector    | 2025-01-20T00:59:22.344094Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=1a8cf7285d91dcd9b818ce4410ebf45f4cd9c26163d1f4549f8cbb4b87db62a2
supabase-vector    | 2025-01-20T00:59:22.344117Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=9638fe1eface210c86bc715b9365d0a00fe7468f3346bc164667764ed72b9695
supabase-vector    | 2025-01-20T00:59:22.344143Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=0d028d8b521a8a98b5b63a3fb1c05229331a5369b9997949419d0f45a723460a
supabase-vector    | 2025-01-20T00:59:22.344257Z  INFO source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Started watching for container logs. container_id=030052732b1dee606b56e627e94b09ad70199f718ed270b59306b4f152327d48
supabase-vector    | 2025-01-20T00:59:22.344298Z ERROR source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Received out of order log message. error_type="condition_failed" stage="receiving" container_id="1deae4d49b7341722cb9689404d7737b93d20083daca945eb8bd5a9dc5c2f530" timestamp="2025-01-20T00:59:22.251833576Z" internal_log_rate_limit=true
supabase-vector    | 2025-01-20T00:59:22.344310Z ERROR source{component_kind="source" component_id=docker_host component_type=docker_logs component_name=docker_host}: vector::internal_events::docker_logs: Internal log [Received out of order log message.] is being rate limited.
supabase-vector    | 2025-01-20T00:59:22.348333Z  INFO vector::internal_events::api: API server running. address=0.0.0.0:9001 playground=http://0.0.0.0:9001/playground
ashwin@ubuntu-server:~/supabase/docker$ docker ps
CONTAINER ID   IMAGE                               COMMAND                  CREATED              STATUS                 PORTS      NAMES
1deae4d49b73   darthsim/imgproxy:v3.8.0            "imgproxy"               About a minute ago   Up About a minute      8080/tcp   supabase-imgproxy
39165fc53f94   timberio/vector:0.28.1-alpine       "/usr/local/bin/vect…"   About a minute ago   Up About a minute                 supabase-vector
1a8cf7285d91   ghcr.io/goauthentik/server:latest   "dumb-init -- ak wor…"   43 hours ago         Up 3 hours (healthy)              authentik_worker
0d028d8b521a   postgres:14-alpine                  "docker-entrypoint.s…"   43 hours ago         Up 3 hours             5432/tcp   authentik_postgres
dee666c898b3   ghcr.io/goauthentik/server:latest   "dumb-init -- ak ser…"   43 hours ago         Up 3 hours (healthy)              authentik_server
9638fe1eface   redis:6-alpine                      "docker-entrypoint.s…"   43 hours ago         Up 3 hours             6379/tcp   authentik_redis
030052732b1d   ghcr.io/goauthentik/server:latest   "dumb-init -- ak ser…"   44 hours ago         Up 3 hours (healthy)              authentik
4eac5f2e4174   redis:alpine                        "docker-entrypoint.s…"   2 days ago           Up 3 hours             6379/tcp   outline_redis
ashwin@ubuntu-server:~/supabase/docker$ 

#### ChatGPT:
<time datetime="2025-01-20T01:03:48.619Z" title="1/20/2025, 10:03:48 AM">10:03</time>

It’s failing because your **`db`** service is configured with:

```yaml
depends_on:
  vector:
    condition: service_healthy
```

…but **`vector`** has **no healthcheck** at all. Docker will never mark a container as “healthy” unless it defines (and passes) a healthcheck. So `db` remains stuck waiting for `vector` to become “healthy,” but `vector` is only in “starting” or “unhealthy” states from Docker’s perspective.

---

## Two Ways to Fix

### **Option A: Remove the Health Condition**

If you **don’t really need** `db` to wait for `vector` to be healthy, remove the `condition: service_healthy` line. For example:

```yaml
db:
  depends_on:
    vector:
      condition: service_started
```

Or remove the `depends_on` on `vector` altogether if it’s not truly required.

### **Option B: Add a Healthcheck to Vector**

If you **do** want `db` to wait until `vector` is ready, you need to define a **healthcheck** for the `vector` service. For instance:

```yaml
vector:
  container_name: supabase-vector
  image: timberio/vector:0.28.1-alpine
  healthcheck:
    test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9001/health"]
    interval: 5s
    timeout: 5s
    retries: 3
  volumes:
    - "./volumes/logs/vector.yml:/etc/vector/vector.yml:ro"
    - "/var/run/docker.sock:/var/run/docker.sock:ro"
  environment:
    LOGFLARE_API_KEY: "logflare-api-key"
  command: ["--config", "/etc/vector/vector.yml"]
```

- **`9001/health`** is the port + health path Vector exposes by default (see your logs: `API server running. address=0.0.0.0:9001`).
- This will let Docker check if Vector is up and responding. Once the healthcheck passes, Docker marks the container “healthy,” so `db` (or anything else) will start.

---

## Summary

- You currently have `depends_on: { vector: { condition: service_healthy }}`, but Vector has **no** healthcheck.
- Either remove that condition (simplest) **or** add a healthcheck to Vector if you need `db` to wait for it.


#### You:
<time datetime="2025-01-20T01:15:16.091Z" title="1/20/2025, 10:15:16 AM">10:15</time>

abase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 2025/01/20 01:10:12 [error] 1111#0: *65 connect() failed (111: Connection refused) while connecting to upstream, client: 172.18.0.3, server: kong, request: "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1", upstream: "http://172.18.0.7:4000/api/logs?source_name=postgres.logs&api_key=logflare-api-key", host: "kong:8000"
supabase-kong  | 172.18.0.3 - - [20/Jan/2025:01:10:12 +0000] "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1" 502 75 "-" "Vector/0.28.1 (x86_64-unknown-linux-musl ff15924 2023-03-06)"
supabase-kong  | 172.18.0.3 - - [20/Jan/2025:01:10:13 +0000] "POST /analytics/v1/api/logs?source_name=postgres.logs&api_key=logflare-api-key HTTP/1.1" 200 21 "-" "Vector/0.28.1 (x86_64-unknown-linux-musl ff15924 2023-03-06)"

#### ChatGPT:
<time datetime="2025-01-20T01:17:12.546Z" title="1/20/2025, 10:17:12 AM">10:17</time>

These logs indicate that Kong is **trying to forward log requests** to the Supabase Analytics (Logflare) service, but initially **cannot connect** to it at `172.18.0.7:4000`, resulting in a bunch of `502` errors (“Bad Gateway”). Then, about a second later, it successfully returns a `200` response—which means the analytics service finally responded and Kong was able to reach it.

In other words, Kong is sending logs to Analytics, but Analytics wasn’t ready or listening right at that moment. Once Analytics finished booting (or resolved its own dependencies), Kong’s next attempt worked—hence the `200 OK`.

---

## Why You Saw the Errors

1. **The Analytics container was not yet up** or not fully booted by the time Vector or Kong sent logs to `analytics:4000`.
2. **Kong’s upstream is hard-coded** to forward logs to `analytics:4000`, so it tries repeatedly.
3. Until Analytics is actually listening on port 4000, Kong sees `Connection refused`.

---

## What to Check or Adjust

1. **Ensure the analytics container is actually running and healthy**:
   - `docker ps` should show your `supabase-analytics` container “Up (healthy) …”.
   - `docker compose logs analytics` can confirm it started successfully.

2. **Add a “depends\_on: condition: service\_healthy”** in your Kong or Vector service if you want them to wait for Analytics to be fully healthy before sending logs:

   ```yaml
   kong:
     depends_on:
       analytics:
         condition: service_healthy
   ```

   This only works if your **analytics** service defines a healthcheck, which you already do (`curl http://localhost:4000/health`). That way, Docker will wait for Analytics to be “healthy” before launching Kong.

3. **Ignore if it’s only a startup blip**:
   - Often, a few `connection refused` lines are harmless if the service eventually starts.
   - You can safely ignore these if everything runs fine afterward.

4. **Remove or disable Analytics** if you don’t really need logs:
   - If you don’t need log forwarding, you can remove the analytics + vector config from your Compose to avoid these extra steps.

---

### Summary

The `Connection refused` errors happened because Kong tried to send logs to the Analytics service before it was fully up. It quickly retried and got a `200` response, so everything likely works now. If you prefer to avoid these transient errors, add a healthcheck and `depends_on` logic so Kong waits until Analytics is ready. Otherwise, you can safely ignore the brief 502 errors during startup.
