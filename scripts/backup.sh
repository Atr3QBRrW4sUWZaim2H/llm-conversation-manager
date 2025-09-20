#!/bin/bash

# LLM Conversation Manager Backup Script
# Creates comprehensive backups of database and files

set -e

echo "💾 LLM Conversation Manager Backup Script"
echo "=========================================="

# Change to project directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found"
    exit 1
fi

# Create backup directory with timestamp
BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backup in: $BACKUP_DIR"

# Database backup
echo "🗄️  Backing up database..."
if command -v pg_dump >/dev/null; then
    pg_dump -h "${DB_HOST:-localhost}" \
            -p "${DB_PORT:-5432}" \
            -U "${DB_USER:-your_user}" \
            -d "${DB_NAME:-conversations}" \
            --no-password \
            --clean \
            --if-exists \
            > "$BACKUP_DIR/database_backup.sql"
    echo "✅ Database backup created"
else
    echo "⚠️  pg_dump not found, skipping database backup"
fi

# File storage backup
echo "📦 Backing up file storage..."
if [ -d "data" ] && [ "$(ls -A data)" ]; then
    tar -czf "$BACKUP_DIR/data_backup.tar.gz" data/
    echo "✅ Data backup created"
fi

if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
    tar -czf "$BACKUP_DIR/logs_backup.tar.gz" logs/
    echo "✅ Logs backup created"
fi

# Configuration backup
echo "⚙️  Backing up configuration..."
tar -czf "$BACKUP_DIR/config_backup.tar.gz" \
    config/ \
    requirements.txt \
    .env 2>/dev/null || true

echo "✅ Configuration backup created"

# Create backup manifest
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.txt" << EOF
LLM Conversation Manager Backup Manifest
=======================================
Backup Date: $(date)
Backup Directory: $BACKUP_DIR

Contents:
$(ls -la "$BACKUP_DIR")

Environment:
- Database Host: ${DB_HOST:-localhost}
- Database Port: ${DB_PORT:-5432}
- Database Name: ${DB_NAME:-conversations}
- Database User: ${DB_USER:-your_user}

System:
- Hostname: $(hostname)
- OS: $(uname -a)
- Python: $(python --version 2>/dev/null || echo "Not available")

Disk Usage:
$(du -sh "$BACKUP_DIR")
EOF

echo "✅ Backup manifest created"

# Cleanup old backups (keep last 7 days)
echo "🧹 Cleaning up old backups..."
find backups/ -name "backup_*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo ""
echo "🎉 Backup completed successfully!"
echo "📊 Backup Details:"
echo "   Location: $BACKUP_DIR"
echo "   Size: $BACKUP_SIZE"
echo "   Files: $(ls -1 "$BACKUP_DIR" | wc -l)"
echo ""
echo "📋 Backup contents:"
ls -la "$BACKUP_DIR"
echo ""
echo "🔧 Restore instructions:"
echo "1. Database: psql -h localhost -U ${DB_USER:-your_user} -d ${DB_NAME:-conversations} < $BACKUP_DIR/database_backup.sql"
echo "2. Files: Extract tar.gz files to respective directories"
echo "3. Config: Copy configuration files back to project root"
echo ""
echo "💡 To automate backups, add to crontab:"
echo "   0 2 * * * cd $(pwd) && ./scripts/backup.sh"
