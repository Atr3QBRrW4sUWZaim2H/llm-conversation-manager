#!/bin/bash

# LLM Conversation Manager Deployment Script
# Deploys the service with health checks

set -e

echo "🚀 Deploying LLM Conversation Manager..."

# Change to project directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from config/env.example"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD not set in .env file"
    exit 1
fi

echo "🔍 Checking dependencies..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed or not in PATH"
    exit 1
fi

echo "✅ Dependencies verified"

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

echo "🏥 Performing health checks..."

# Test database connection
if python -c "
from src.database.connection import get_db_connection
db = get_db_connection()
if db.test_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
    exit(1)
"; then
    echo "✅ Database connection verified"
else
    echo "❌ Database connection failed"
    exit 1
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Service Status:"
echo "   ✅ Database: Connected"
echo "   ✅ Dependencies: Installed"
echo "   ✅ Schema: Created"
echo ""
echo "📋 Next steps:"
echo "1. Import data:"
echo "   - Place JSON files in data/to-process/"
echo "   - Run importers: python -m src.importers.chatgpt_importer --input-dir data/to-process/"
echo ""
echo "2. Start web interface:"
echo "   streamlit run src/web/streamlit_app.py"
echo ""
echo "3. Access the application:"
echo "   - Web interface: http://localhost:8501"
echo ""
echo "🔧 Management commands:"
echo "   • View logs: tail -f logs/conversation_manager.log"
echo "   • Run deduplication: python -c \"from src.processors.deduplicator import Deduplicator; Deduplicator().run_full_deduplication()\""
echo "   • Get stats: python -c \"from src.database.models import Conversation; print(Conversation.get_stats())\""
