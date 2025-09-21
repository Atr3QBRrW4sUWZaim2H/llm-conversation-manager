# Scripts Directory

This directory contains utility scripts for the LLM Conversation Manager project.

## Available Scripts

### Setup and Deployment
- **`setup.sh`** - Initial project setup and environment configuration
- **`deploy.sh`** - Deployment script for production environments

### Data Management
- **`import_all.py`** - Import all conversation data from various sources
- **`import_markdown.sh`** - Import markdown conversation files
- **`migrate_from_existing.sh`** - Migrate data from existing systems

### Testing and Validation
- **`test_consolidation.py`** - Test data consolidation processes

### Backup and Maintenance
- **`backup.sh`** - Create database and data backups

## Usage

Most scripts can be run directly from the project root:

```bash
# Setup the project
./scripts/setup.sh

# Import all data
python scripts/import_all.py

# Create backup
./scripts/backup.sh
```

## Requirements

- Python 3.11+
- Required Python packages (see `requirements.txt`)
- Appropriate permissions for file operations
- Database access (for scripts that interact with the database)

## Notes

- Always review scripts before running them in production
- Some scripts may require environment variables to be set
- Check individual script documentation for specific requirements