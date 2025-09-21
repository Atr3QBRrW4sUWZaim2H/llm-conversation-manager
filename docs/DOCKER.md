# Docker Setup for LLM Conversation Manager

This document provides instructions for running the LLM Conversation Manager using Docker Compose.

## Quick Start

1. **Clone and navigate to the project**:
   ```bash
   git clone <repository-url>
   cd llm-conversation-manager
   ```

2. **Copy environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings (optional)
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Web Interface: http://localhost:8501
   - Database: localhost:5432
   - pgAdmin (optional): http://localhost:5050

## Services

### Main Application (`app`)
- **Port**: 8501
- **Image**: Built from local Dockerfile
- **Dependencies**: PostgreSQL database
- **Volumes**: 
  - `./data` → `/app/data` (conversation data)
  - `./logs` → `/app/logs` (application logs)
  - `./backups` → `/app/backups` (database backups)
  - `./config` → `/app/config` (read-only configuration)

### PostgreSQL Database (`postgres`)
- **Port**: 5432
- **Image**: postgres:15-alpine
- **Database**: conversations
- **User**: conversation_user
- **Password**: conversation_password
- **Volumes**: 
  - `postgres_data` (persistent database storage)
  - `./config/database_schema.sql` (initialization script)

### pgAdmin (Optional)
- **Port**: 5050
- **Image**: dpage/pgadmin4:latest
- **Email**: admin@example.com
- **Password**: admin_password
- **Profile**: admin (use `--profile admin` to include)

## Environment Variables

The application uses the following environment variables (configured in docker-compose.yml):

### Database Configuration
- `DB_HOST`: postgres
- `DB_PORT`: 5432
- `DB_NAME`: conversations
- `DB_USER`: conversation_user
- `DB_PASSWORD`: conversation_password

### Streamlit Configuration
- `STREAMLIT_SERVER_PORT`: 8501
- `STREAMLIT_SERVER_ADDRESS`: 0.0.0.0
- `STREAMLIT_SERVER_HEADLESS`: true
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS`: false

### Optional Configuration
- `CLAUDE_COOKIE`: For Claude imports
- `USER_AGENT`: For web scraping
- `IMGUR_BEARER`: For image uploads
- `GIST_PAT`: For GitHub gist uploads

## Common Commands

### Start services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
```

### Stop services
```bash
docker-compose down
```

### Rebuild and restart
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access database
```bash
# Using docker-compose
docker-compose exec postgres psql -U conversation_user -d conversations

# Or connect from host
psql -h localhost -p 5432 -U conversation_user -d conversations
```

### Backup database
```bash
docker-compose exec postgres pg_dump -U conversation_user conversations > backup.sql
```

### Restore database
```bash
docker-compose exec -T postgres psql -U conversation_user -d conversations < backup.sql
```

## Data Persistence

- **Database data**: Stored in Docker volume `postgres_data`
- **Application data**: Stored in `./data` directory
- **Logs**: Stored in `./logs` directory
- **Backups**: Stored in `./backups` directory

## Troubleshooting

### Service won't start
1. Check logs: `docker-compose logs <service-name>`
2. Verify ports aren't in use: `netstat -tulpn | grep :8501`
3. Check disk space: `df -h`

### Database connection issues
1. Ensure PostgreSQL is healthy: `docker-compose ps`
2. Check database logs: `docker-compose logs postgres`
3. Verify environment variables in docker-compose.yml

### Application not accessible
1. Check if app container is running: `docker-compose ps`
2. Verify port mapping: `docker-compose port app 8501`
3. Check application logs: `docker-compose logs app`

### Reset everything
```bash
docker-compose down -v  # Removes volumes
docker-compose build --no-cache
docker-compose up -d
```

## Production Considerations

For production deployment:

1. **Change default passwords** in docker-compose.yml
2. **Use environment files** for sensitive data
3. **Configure proper networking** and security
4. **Set up regular backups**
5. **Monitor resource usage**
6. **Use Docker secrets** for sensitive data

## Development

For development with live code changes:

```bash
# Mount source code for live reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  app:
    volumes:
      - ./src:/app/src
    environment:
      - PYTHONUNBUFFERED=1
```