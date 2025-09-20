"""
TypingMind conversation importer.
"""
import json
import os
import logging
from typing import List, Dict, Any

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class TypingMindImporter(BaseImporter):
    """Importer for TypingMind conversation exports."""
    
    def __init__(self):
        super().__init__("typingmind")
    
    def is_valid_file(self, filename: str) -> bool:
        """Check if file is a valid TypingMind export."""
        return filename.lower().endswith('.json')
    
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse TypingMind export file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # TypingMind exports have different structures
            if isinstance(data, dict):
                # Check for nested structure with data.chats
                if 'data' in data and isinstance(data['data'], dict) and 'chats' in data['data']:
                    return data['data']['chats']
                
                # Check for wrapper key structure
                for key, value in data.items():
                    if isinstance(value, dict) and 'data' in value and 'chats' in value['data']:
                        return value['data']['chats']
                
                # Direct chats array
                if 'chats' in data:
                    return data['chats']
            
            # If it's a list, treat as direct chat array
            if isinstance(data, list):
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
        
        return []
    
    def extract_preview(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Extract preview from TypingMind conversation."""
        # Look for preview field first
        preview = data.get('preview', '')
        if preview:
            return preview[:max_length] + ('...' if len(preview) > max_length else '')
        
        # Look for first message content
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list) and messages:
                first_message = messages[0]
                if isinstance(first_message, dict):
                    content = first_message.get('content', '')
                    if content:
                        return content[:max_length] + ('...' if len(content) > max_length else '')
        
        # Fallback to title
        title = data.get('chatTitle', '') or data.get('title', '')
        if title:
            return title[:max_length] + ('...' if len(title) > max_length else '')
        
        return "No preview available"
    
    def calculate_cost(self, data: Dict[str, Any]) -> float:
        """Calculate cost for TypingMind conversation."""
        # Look for token usage information
        if 'tokenUsage' in data:
            token_usage = data['tokenUsage']
            if isinstance(token_usage, dict):
                return float(token_usage.get('totalCostUSD', 0.0))
        
        # Look for cost field
        cost = data.get('cost', 0.0)
        if isinstance(cost, (int, float)):
            return float(cost)
        
        return 0.0
    
    def extract_model_info(self, data: Dict[str, Any]) -> tuple[str, str]:
        """Extract model information from TypingMind data."""
        model_id = data.get('model', '')
        model_name = data.get('model_name', '')
        
        # Look in modelInfo if available
        if 'modelInfo' in data and isinstance(data['modelInfo'], dict):
            model_info = data['modelInfo']
            model_id = model_id or model_info.get('id', '')
            model_name = model_name or model_info.get('title', '')
        
        return str(model_id), str(model_name)
    
    def count_messages(self, data: Dict[str, Any]) -> int:
        """Count messages in TypingMind conversation."""
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list):
                return len(messages)
        
        return 0
    
    def create_conversation(self, data: Dict[str, Any], source: str) -> 'Conversation':
        """Create conversation with TypingMind-specific processing."""
        from ..database.models import Conversation
        
        # Extract title
        title = data.get('chatTitle', '') or data.get('title', f"TypingMind Conversation {source}")
        
        # Extract timestamps
        create_time = self.parse_timestamp(data.get('createTime') or data.get('createdAt'))
        datemodified = self.parse_timestamp(data.get('datemodified') or data.get('updatedAt') or data.get('syncedAt'))
        
        # Extract model info
        model_id, model_name = self.extract_model_info(data)
        
        # Count messages
        num_messages = self.count_messages(data)
        
        # Extract preview
        preview = self.extract_preview(data)
        
        # Calculate cost
        cost = self.calculate_cost(data)
        
        # Create conversation
        conversation = Conversation(
            title=title,
            source=source,
            platform=self.platform,
            create_time=create_time,
            datemodified=datemodified or create_time,
            data={"content": self.sanitize_json(data)},
            cost=cost,
            model_id=model_id,
            model_name=model_name,
            num_messages=num_messages,
            chat_title=title,
            preview=preview,
            synced_at=self.parse_timestamp(data.get('syncedAt')) or create_time
        )
        
        return conversation
