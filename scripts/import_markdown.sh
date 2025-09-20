#!/bin/bash

# Markdown Archive Import Script
# Imports markdown conversations from the llm-conversations project

set -e

echo "📚 Importing Markdown Archive..."

# Change to project directory
cd "$(dirname "$0")/.."

# Check if source directory is provided
SOURCE_DIR="${1:-../llm-conversations}"
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    echo "Usage: $0 [source_directory]"
    echo "Example: $0 ../llm-conversations"
    exit 1
fi

echo "📁 Source directory: $SOURCE_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run setup.sh first"
    exit 1
fi

# Load environment variables
source .env

# Create markdown archive directory
mkdir -p data/markdown-archive

echo "📋 Copying markdown files to archive directory..."
find "$SOURCE_DIR" -name "*.md" -type f | while read -r file; do
    filename=$(basename "$file")
    cp "$file" "data/markdown-archive/$filename"
    echo "  ✅ Copied: $filename"
done

echo "🔄 Processing markdown files..."
python -c "
from src.processors.markdown_processor import MarkdownProcessor
import os

processor = MarkdownProcessor()
stats = processor.import_directory('data/markdown-archive')

print(f'✅ Import completed:')
print(f'   Processed: {stats[\"processed\"]} files')
print(f'   Failed: {stats[\"failed\"]} files')
print(f'   Total: {stats[\"total\"]} files')
"

echo ""
echo "🎉 Markdown import completed!"
echo ""
echo "📊 Next steps:"
echo "1. View imported conversations in the web interface"
echo "2. Run deduplication if needed"
echo "3. Add tags to organize conversations"
