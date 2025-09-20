"""
ChatGPT conversation importer.
"""
import json
import os
import logging
from typing import List, Dict, Any

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class ChatGPTImporter(BaseImporter):
    """Importer for ChatGPT conversation exports."""
    
    def __init__(self):
        super().__init__("chatgpt")
    
    def is_valid_file(self, filename: str) -> bool:
        """Check if file is a valid ChatGPT export."""
        return filename.lower().endswith('.json')
    
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse ChatGPT export file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ChatGPT exports are typically a list of conversations
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'conversations' in data:
                return data['conversations']
            else:
                # Single conversation wrapped in an object
                return [data]
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
    
    def extract_preview(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Extract preview from ChatGPT conversation."""
        # ChatGPT conversations have a 'mapping' structure
        if 'mapping' in data:
            mapping = data['mapping']
            if isinstance(mapping, dict):
                # Find the first user message
                for message_id, message_data in mapping.items():
                    if isinstance(message_data, dict) and message_data.get('message'):
                        message = message_data['message']
                        if message.get('author', {}).get('role') == 'user':
                            content = message.get('content', {})
                            if isinstance(content, dict) and 'parts' in content:
                                parts = content['parts']
                                if parts and isinstance(parts[0], str):
                                    return parts[0][:max_length] + ('...' if len(parts[0]) > max_length else '')
        
        # Fallback to title
        title = data.get('title', '')
        if title:
            return title[:max_length] + ('...' if len(title) > max_length else '')
        
        return "No preview available"
    
    def calculate_cost(self, data: Dict[str, Any]) -> float:
        """Calculate cost for ChatGPT conversation."""
        # ChatGPT doesn't typically include cost in exports
        # This would need to be calculated based on token usage if available
        return 0.0
    
    def extract_model_info(self, data: Dict[str, Any]) -> tuple[str, str]:
        """Extract model information from ChatGPT data."""
        # Look for model information in the conversation
        if 'mapping' in data:
            mapping = data['mapping']
            if isinstance(mapping, dict):
                for message_data in mapping.values():
                    if isinstance(message_data, dict) and message_data.get('message'):
                        message = message_data['message']
                        if 'metadata' in message:
                            metadata = message['metadata']
                            model_id = metadata.get('model_slug', '')
                            model_name = metadata.get('model_slug', '').replace('gpt-', 'GPT-').replace('-', ' ')
                            if model_id:
                                return model_id, model_name
        
        return 'unknown', 'Unknown Model'
    
    def count_messages(self, data: Dict[str, Any]) -> int:
        """Count messages in ChatGPT conversation."""
        if 'mapping' in data:
            mapping = data['mapping']
            if isinstance(mapping, dict):
                return len([m for m in mapping.values() if isinstance(m, dict) and m.get('message')])
        
        return 0
    
    def create_conversation(self, data: Dict[str, Any], source: str) -> 'Conversation':
        """Create conversation with ChatGPT-specific processing."""
        from ..database.models import Conversation
        
        # Extract title
        title = data.get('title', f"ChatGPT Conversation {source}")
        
        # Extract timestamps
        create_time = self.parse_timestamp(data.get('create_time'))
        datemodified = self.parse_timestamp(data.get('update_time'))
        
        # Extract model info
        model_id, model_name = self.extract_model_info(data)
        
        # Count messages
        num_messages = self.count_messages(data)
        
        # Extract preview
        preview = self.extract_preview(data)
        
        # Create conversation
        conversation = Conversation(
            title=title,
            source=source,
            platform=self.platform,
            create_time=create_time,
            datemodified=datemodified or create_time,
            data={"content": self.sanitize_json(data)},
            cost=self.calculate_cost(data),
            model_id=model_id,
            model_name=model_name,
            num_messages=num_messages,
            chat_title=title,
            preview=preview,
            synced_at=self.parse_timestamp(data.get('update_time')) or self.parse_timestamp(data.get('create_time'))
        )
        
        return conversation
