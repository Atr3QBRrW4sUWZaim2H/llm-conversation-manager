#!/usr/bin/env python3
"""
Test script to verify the consolidation works correctly.
"""
import os
import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_db_connection, setup_database
from src.database.models import Conversation, Artifact, Tag
from src.importers import ChatGPTImporter, TypingMindImporter, ClaudeImporter
from src.processors import MarkdownProcessor, Deduplicator
from src.utils.logging_utils import setup_logging

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    
    try:
        db = get_db_connection()
        if db.test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_database_schema():
    """Test database schema setup."""
    print("🔍 Testing database schema...")
    
    try:
        setup_database()
        print("✅ Database schema setup successful")
        return True
    except Exception as e:
        print(f"❌ Database schema setup error: {e}")
        return False

def test_importers():
    """Test all importers."""
    print("🔍 Testing importers...")
    
    # Create test data
    test_data_dir = tempfile.mkdtemp()
    
    try:
        # Test ChatGPT importer
        print("  Testing ChatGPT importer...")
        chatgpt_data = [
            {
                "title": "Test ChatGPT Conversation",
                "create_time": "2024-01-01T00:00:00Z",
                "mapping": {
                    "1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Hello, how are you?"]},
                            "metadata": {"model_slug": "gpt-4"}
                        }
                    },
                    "2": {
                        "message": {
                            "author": {"role": "assistant"},
                            "content": {"parts": ["I'm doing well, thank you!"]}
                        }
                    }
                }
            }
        ]
        
        with open(os.path.join(test_data_dir, "chatgpt_test.json"), "w") as f:
            json.dump(chatgpt_data, f)
        
        importer = ChatGPTImporter()
        stats = importer.import_directory(test_data_dir)
        print(f"    ChatGPT: {stats}")
        
        # Test TypingMind importer
        print("  Testing TypingMind importer...")
        typingmind_data = {
            "data": {
                "chats": [
                    {
                        "chatTitle": "Test TypingMind Chat",
                        "messages": [
                            {"content": "Hello", "role": "user"},
                            {"content": "Hi there!", "role": "assistant"}
                        ],
                        "tokenUsage": {"totalCostUSD": 0.01},
                        "model": "gpt-4",
                        "modelInfo": {"title": "GPT-4"}
                    }
                ]
            }
        }
        
        with open(os.path.join(test_data_dir, "typingmind_test.json"), "w") as f:
            json.dump(typingmind_data, f)
        
        importer = TypingMindImporter()
        stats = importer.import_directory(test_data_dir)
        print(f"    TypingMind: {stats}")
        
        # Test Claude importer
        print("  Testing Claude importer...")
        claude_data = [
            {
                "title": "Test Claude Chat",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ],
                "usage": {"input_tokens": 10, "output_tokens": 20}
            }
        ]
        
        with open(os.path.join(test_data_dir, "claude_test.json"), "w") as f:
            json.dump(claude_data, f)
        
        importer = ClaudeImporter()
        stats = importer.import_directory(test_data_dir)
        print(f"    Claude: {stats}")
        
        print("✅ All importers tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Importer test error: {e}")
        return False
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_data_dir, ignore_errors=True)

def test_markdown_processor():
    """Test markdown processor."""
    print("🔍 Testing markdown processor...")
    
    test_data_dir = tempfile.mkdtemp()
    
    try:
        # Create test markdown file
        markdown_content = """---
title: Test Markdown Chat
source: https://example.com
---

#### You:
Hello, how are you?

#### Assistant:
I'm doing well, thank you for asking!

#### You:
What can you help me with?

#### Assistant:
I can help you with a wide variety of tasks including answering questions, writing, coding, analysis, and more!
"""
        
        with open(os.path.join(test_data_dir, "test_chat.md"), "w") as f:
            f.write(markdown_content)
        
        processor = MarkdownProcessor()
        stats = processor.import_directory(test_data_dir)
        print(f"    Markdown: {stats}")
        
        print("✅ Markdown processor tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Markdown processor test error: {e}")
        return False
    finally:
        import shutil
        shutil.rmtree(test_data_dir, ignore_errors=True)

def test_deduplication():
    """Test deduplication."""
    print("🔍 Testing deduplication...")
    
    try:
        deduplicator = Deduplicator()
        stats = deduplicator.get_duplicate_stats()
        print(f"    Duplicate stats: {stats}")
        
        # Run deduplication
        dedup_stats = deduplicator.run_full_deduplication()
        print(f"    Deduplication: {dedup_stats}")
        
        print("✅ Deduplication tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Deduplication test error: {e}")
        return False

def test_web_interface():
    """Test web interface components."""
    print("🔍 Testing web interface components...")
    
    try:
        # Test conversation search
        conversations = Conversation.search("test", limit=10)
        print(f"    Found {len(conversations)} conversations")
        
        # Test conversation stats
        stats = Conversation.get_stats()
        print(f"    Stats: {stats}")
        
        # Test conversation retrieval
        if conversations:
            conv = conversations[0]
            artifacts = conv.get_artifacts()
            print(f"    Conversation artifacts: {len(artifacts)}")
        
        print("✅ Web interface components tested successfully")
        return True
        
    except Exception as e:
        print(f"❌ Web interface test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 LLM Conversation Manager Consolidation Test")
    print("===============================================")
    
    # Setup logging
    setup_logging(log_level="INFO")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Schema", test_database_schema),
        ("Importers", test_importers),
        ("Markdown Processor", test_markdown_processor),
        ("Deduplication", test_deduplication),
        ("Web Interface", test_web_interface),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Consolidation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
