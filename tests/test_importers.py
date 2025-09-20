"""
Tests for conversation importers.
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch

from src.importers import ChatGPTImporter, TypingMindImporter, ClaudeImporter
from src.processors import MarkdownProcessor


class TestChatGPTImporter:
    """Test ChatGPT importer."""
    
    def test_is_valid_file(self):
        """Test file validation."""
        importer = ChatGPTImporter()
        assert importer.is_valid_file("test.json")
        assert not importer.is_valid_file("test.txt")
        assert not importer.is_valid_file("test.md")
    
    def test_parse_file(self):
        """Test file parsing."""
        importer = ChatGPTImporter()
        
        # Test with temporary file
        test_data = [
            {
                "title": "Test Conversation",
                "create_time": "2024-01-01T00:00:00Z",
                "mapping": {
                    "1": {
                        "message": {
                            "author": {"role": "user"},
                            "content": {"parts": ["Hello"]}
                        }
                    }
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            result = importer.parse_file(temp_file)
            assert len(result) == 1
            assert result[0]["title"] == "Test Conversation"
        finally:
            os.unlink(temp_file)


class TestTypingMindImporter:
    """Test TypingMind importer."""
    
    def test_is_valid_file(self):
        """Test file validation."""
        importer = TypingMindImporter()
        assert importer.is_valid_file("test.json")
        assert not importer.is_valid_file("test.txt")
    
    def test_parse_file(self):
        """Test file parsing."""
        importer = TypingMindImporter()
        
        test_data = {
            "data": {
                "chats": [
                    {
                        "chatTitle": "Test Chat",
                        "messages": [{"content": "Hello"}],
                        "tokenUsage": {"totalCostUSD": 0.01}
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            result = importer.parse_file(temp_file)
            assert len(result) == 1
            assert result[0]["chatTitle"] == "Test Chat"
        finally:
            os.unlink(temp_file)


class TestClaudeImporter:
    """Test Claude importer."""
    
    def test_is_valid_file(self):
        """Test file validation."""
        importer = ClaudeImporter()
        assert importer.is_valid_file("test.json")
        assert not importer.is_valid_file("test.txt")
    
    def test_parse_file(self):
        """Test file parsing."""
        importer = ClaudeImporter()
        
        test_data = [
            {
                "title": "Test Claude Chat",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            result = importer.parse_file(temp_file)
            assert len(result) == 1
            assert result[0]["title"] == "Test Claude Chat"
        finally:
            os.unlink(temp_file)


class TestMarkdownProcessor:
    """Test Markdown processor."""
    
    def test_is_valid_file(self):
        """Test file validation."""
        processor = MarkdownProcessor()
        assert processor.is_valid_file("test.md")
        assert not processor.is_valid_file("test.txt")
        assert not processor.is_valid_file("test.json")
    
    def test_parse_file(self):
        """Test file parsing."""
        processor = MarkdownProcessor()
        
        test_content = """---
title: Test Markdown Chat
source: https://example.com
---

#### You:
Hello, how are you?

#### Assistant:
I'm doing well, thank you for asking!
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            result = processor.parse_file(temp_file)
            assert len(result) == 1
            assert result[0]["title"] == "Test Markdown Chat"
            assert len(result[0]["messages"]) == 2
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
