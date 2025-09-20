#!/bin/bash

# LLM Conversation Manager Setup Script
# Sets up the database schema and installs dependencies

set -e

echo "🚀 Setting up LLM Conversation Manager..."

# Change to project directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from config/env.example..."
    cp config/env.example .env
    echo "📝 Please edit .env file with your actual database credentials"
    echo "   Then run this script again."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD not set in .env file"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🗄️  Setting up database schema..."
python -c "
from src.database.connection import setup_database
setup_database()
print('✅ Database schema setup completed')
"

echo "📁 Creating necessary directories..."
mkdir -p data/{to-process,processed,failed,markdown-archive}
mkdir -p logs
mkdir -p backups

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Import conversations:"
echo "   - ChatGPT: python -m src.importers.chatgpt_importer --input-dir data/to-process/"
echo "   - TypingMind: python -m src.importers.typingmind_importer --input-dir data/to-process/"
echo "   - Claude: python -m src.importers.claude_importer --input-dir data/to-process/"
echo "   - Markdown: python -m src.processors.markdown_processor --input-dir data/markdown-archive/"
echo ""
echo "2. Start web interface:"
echo "   streamlit run src/web/streamlit_app.py"
echo ""
echo "3. Run deduplication:"
echo "   python -c \"from src.processors.deduplicator import Deduplicator; Deduplicator().run_full_deduplication()\""
echo ""
echo "🔍 Useful queries:"
echo "   - View stats: python -c \"from src.database.models import Conversation; print(Conversation.get_stats())\""
echo "   - Search: python -c \"from src.database.models import Conversation; print(Conversation.search('python'))\""
