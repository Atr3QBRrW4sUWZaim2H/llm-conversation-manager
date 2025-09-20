#!/bin/bash

# Migration script to consolidate data from existing projects
# This script migrates data from llm-conversation-importer, llm-conversations, and claude-extract

set -e

echo "🔄 LLM Conversation Manager Migration Script"
echo "============================================="

# Change to project directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup.sh first"
    exit 1
fi

# Load environment variables
source .env

echo "📋 Migration Plan:"
echo "1. Migrate data from llm-conversation-importer"
echo "2. Import markdown archive from llm-conversations"
echo "3. Set up claude-extract data (if available)"
echo ""

# Step 1: Migrate from llm-conversation-importer
echo "🔄 Step 1: Migrating from llm-conversation-importer..."

if [ -d "../llm-conversation-importer" ]; then
    echo "📁 Found llm-conversation-importer project"
    
    # Copy files to process
    if [ -d "../llm-conversation-importer/files/to-process" ]; then
        echo "📦 Copying files from llm-conversation-importer/files/to-process..."
        mkdir -p data/to-process
        cp -r ../llm-conversation-importer/files/to-process/* data/to-process/ 2>/dev/null || true
        echo "✅ Files copied to data/to-process/"
    fi
    
    # Import the files
    echo "🔄 Importing ChatGPT and TypingMind conversations..."
    python scripts/import_all.py --input-dir data/to-process --platform all --log-level INFO
    
    # Move processed files
    echo "📁 Moving processed files..."
    mkdir -p data/processed
    mv data/to-process/* data/processed/ 2>/dev/null || true
    
    echo "✅ llm-conversation-importer migration completed"
else
    echo "⚠️  llm-conversation-importer project not found, skipping..."
fi

# Step 2: Import markdown archive
echo ""
echo "🔄 Step 2: Importing markdown archive from llm-conversations..."

if [ -d "../llm-conversations" ]; then
    echo "📁 Found llm-conversations project"
    
    # Run markdown import
    ./scripts/import_markdown.sh ../llm-conversations
    
    echo "✅ llm-conversations migration completed"
else
    echo "⚠️  llm-conversations project not found, skipping..."
fi

# Step 3: Handle claude-extract
echo ""
echo "🔄 Step 3: Handling claude-extract project..."

if [ -d "../claude-extract" ]; then
    echo "📁 Found claude-extract project"
    
    # Check if there's any data to migrate
    if [ -d "../claude-extract/data" ] && [ "$(ls -A ../claude-extract/data)" ]; then
        echo "📦 Found data in claude-extract/data"
        
        # Copy any JSON files
        find ../claude-extract/data -name "*.json" -type f | while read -r file; do
            filename=$(basename "$file")
            cp "$file" "data/to-process/$filename"
            echo "  ✅ Copied: $filename"
        done
        
        # Import Claude conversations
        if [ "$(ls -A data/to-process)" ]; then
            echo "🔄 Importing Claude conversations..."
            python scripts/import_all.py --input-dir data/to-process --platform claude --log-level INFO
            
            # Move processed files
            mv data/to-process/* data/processed/ 2>/dev/null || true
        fi
    else
        echo "⚠️  No data found in claude-extract/data"
    fi
    
    echo "✅ claude-extract migration completed"
else
    echo "⚠️  claude-extract project not found, skipping..."
fi

# Step 4: Run deduplication
echo ""
echo "🔄 Step 4: Running deduplication..."

python -c "
from src.processors.deduplicator import Deduplicator
import logging

logging.basicConfig(level=logging.INFO)
deduplicator = Deduplicator()
stats = deduplicator.run_full_deduplication()
print(f'✅ Deduplication completed: {stats}')
"

# Step 5: Generate final report
echo ""
echo "📊 Migration Summary:"
echo "===================="

python -c "
from src.database.models import Conversation
import json

try:
    stats = Conversation.get_stats()
    print('📈 Final Statistics:')
    for platform, platform_stats in stats.items():
        print(f'  {platform.upper()}:')
        print(f'    Conversations: {platform_stats[\"total_conversations\"]}')
        print(f'    Messages: {platform_stats[\"total_messages\"]}')
        print(f'    Cost: \${platform_stats[\"total_cost\"]:.2f}')
        print(f'    Models: {platform_stats[\"unique_models\"]}')
        print()
except Exception as e:
    print(f'❌ Error getting statistics: {e}')
"

echo ""
echo "🎉 Migration completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start the web interface: streamlit run src/web/streamlit_app.py"
echo "2. Access the application at: http://localhost:8501"
echo "3. Review and organize your conversations"
echo "4. Add tags to categorize conversations"
echo ""
echo "🔧 Management commands:"
echo "• View logs: tail -f logs/import.log"
echo "• Run backup: ./scripts/backup.sh"
echo "• Get stats: python -c \"from src.database.models import Conversation; print(Conversation.get_stats())\""
