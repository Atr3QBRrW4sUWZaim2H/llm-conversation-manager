# LLM Conversation Manager

A unified system for importing, storing, and managing chat conversation exports from multiple AI platforms including ChatGPT, Claude, TypingMind, and markdown archives.

## Overview

This repository consolidates three separate projects into a comprehensive conversation management system:

- **Importers**: Handle multiple conversation formats (ChatGPT, TypingMind, Claude, Markdown)
- **Database**: Unified PostgreSQL schema for all conversation types
- **Web Interface**: Streamlit-based explorer with search and filtering
- **Processing**: Deduplication, validation, and metadata extraction

## Features

- **Multi-Platform Support**: ChatGPT, Claude, TypingMind, and Markdown archives
- **Unified Database Schema**: Single PostgreSQL database for all conversation types
- **Rich Metadata**: Cost tracking, model information, message counts, and previews
- **Advanced Search**: Full-text search across all conversations
- **Deduplication**: Automatic detection and removal of duplicate conversations
- **Web Interface**: Modern Streamlit-based explorer
- **Docker Support**: Easy deployment with Docker Compose
- **API Access**: REST API for programmatic access

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd llm-conversation-manager
   cp config/env.example .env
   # Edit .env with your database credentials
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Database**:
   ```bash
   ./scripts/setup.sh
   ```

4. **Import Conversations**:
   ```bash
   # Import from JSON files
   python -m src.importers.chatgpt_importer --input-dir data/to-process/
   
   # Import markdown archive
   python -m src.processors.markdown_processor --input-dir ../llm-conversations/
   ```

5. **Start Web Interface**:
   ```bash
   streamlit run src/web/streamlit_app.py
   ```

## Project Structure

```
llm-conversation-manager/
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── config/
│   ├── database_schema.sql
│   └── env.example
├── src/
│   ├── importers/
│   │   ├── __init__.py
│   │   ├── base_importer.py
│   │   ├── chatgpt_importer.py
│   │   ├── typingmind_importer.py
│   │   └── claude_importer.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── markdown_processor.py
│   │   └── deduplicator.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── models.py
│   ├── web/
│   │   ├── streamlit_app.py
│   │   └── api/
│   │       └── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       └── logging_utils.py
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   ├── backup.sh
│   └── import_markdown.sh
├── data/
│   ├── to-process/
│   ├── processed/
│   ├── failed/
│   └── markdown-archive/
└── tests/
    ├── __init__.py
    └── test_importers.py
```

## Database Schema

The unified schema supports all conversation types:

```sql
-- Main conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    platform TEXT NOT NULL, -- 'chatgpt', 'claude', 'typingmind', 'markdown'
    create_time TIMESTAMP,
    datemodified TIMESTAMP,
    data JSONB,
    cost FLOAT DEFAULT 0.0,
    model_id TEXT,
    model_name TEXT,
    num_messages INTEGER DEFAULT 0,
    chat_title TEXT,
    preview TEXT,
    synced_at TIMESTAMP,
    file_path TEXT, -- For markdown files
    UNIQUE (title, source, platform)
);

-- Artifacts table (for Claude-specific content)
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    artifact_type TEXT,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Usage

### Importing Conversations

```bash
# ChatGPT exports
python -m src.importers.chatgpt_importer --input-dir data/to-process/

# TypingMind exports
python -m src.importers.typingmind_importer --input-dir data/to-process/

# Claude exports
python -m src.importers.claude_importer --input-dir data/to-process/

# Markdown archive
python -m src.processors.markdown_processor --input-dir ../llm-conversations/
```

### Web Interface

Access the web interface at `http://localhost:8501` to:
- Browse all conversations
- Search across platforms
- Filter by model, date, or platform
- View conversation details and artifacts
- Export conversations

### API Access

```python
from src.database.connection import get_db_connection
from src.database.models import Conversation

# Search conversations
conversations = Conversation.search("python programming", platform="chatgpt")

# Get conversation details
conv = Conversation.get_by_id(123)
```

## Configuration

Copy `config/env.example` to `.env` and configure:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=conversations
DB_USER=your_user
DB_PASSWORD=your_password

# Optional: For Claude imports
CLAUDE_COOKIE=your_cookie
USER_AGENT=your_user_agent

# Optional: For image uploads
IMGUR_BEARER=your_imgur_token
GIST_PAT=your_github_token
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Adding New Importers

1. Create a new importer class inheriting from `BaseImporter`
2. Implement the `import_file()` method
3. Add platform-specific metadata extraction
4. Register the importer in the main import script

### Database Migrations

```bash
# Create migration
python -m src.database.migrate create "add_new_column"

# Apply migrations
python -m src.database.migrate up
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### Manual Deployment

```bash
./scripts/deploy.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
