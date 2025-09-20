"""
Claude conversation importer.
"""
import json
import os
import logging
from typing import List, Dict, Any

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class ClaudeImporter(BaseImporter):
    """Importer for Claude conversation exports."""
    
    def __init__(self):
        super().__init__("claude")
    
    def is_valid_file(self, filename: str) -> bool:
        """Check if file is a valid Claude export."""
        return filename.lower().endswith('.json')
    
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse Claude export file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Claude exports can have different structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Check for conversations array
                if 'conversations' in data:
                    return data['conversations']
                # Check for nested structure
                elif 'data' in data and isinstance(data['data'], list):
                    return data['data']
                # Single conversation
                else:
                    return [data]
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
        
        return []
    
    def extract_preview(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Extract preview from Claude conversation."""
        # Look for first user message
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list) and messages:
                for message in messages:
                    if isinstance(message, dict) and message.get('role') == 'user':
                        content = message.get('content', '')
                        if content:
                            # Handle different content formats
                            if isinstance(content, list):
                                # Find text content
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'text':
                                        text = item.get('text', '')
                                        if text:
                                            return text[:max_length] + ('...' if len(text) > max_length else '')
                            elif isinstance(content, str):
                                return content[:max_length] + ('...' if len(content) > max_length else '')
        
        # Fallback to title
        title = data.get('title', '') or data.get('name', '')
        if title:
            return title[:max_length] + ('...' if len(title) > max_length else '')
        
        return "No preview available"
    
    def calculate_cost(self, data: Dict[str, Any]) -> float:
        """Calculate cost for Claude conversation."""
        # Look for usage information
        if 'usage' in data:
            usage = data['usage']
            if isinstance(usage, dict):
                # Calculate cost based on tokens (approximate)
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                
                # Claude pricing (approximate, as of 2024)
                input_cost_per_1k = 0.003  # $3 per 1M tokens
                output_cost_per_1k = 0.015  # $15 per 1M tokens
                
                input_cost = (input_tokens / 1000) * input_cost_per_1k
                output_cost = (output_tokens / 1000) * output_cost_per_1k
                
                return input_cost + output_cost
        
        # Look for cost field
        cost = data.get('cost', 0.0)
        if isinstance(cost, (int, float)):
            return float(cost)
        
        return 0.0
    
    def extract_model_info(self, data: Dict[str, Any]) -> tuple[str, str]:
        """Extract model information from Claude data."""
        model_id = data.get('model', '') or data.get('model_id', '')
        model_name = data.get('model_name', '')
        
        # If no model name, generate from model ID
        if not model_name and model_id:
            model_name = model_id.replace('claude-', 'Claude ').replace('-', ' ').title()
        
        return str(model_id), str(model_name)
    
    def count_messages(self, data: Dict[str, Any]) -> int:
        """Count messages in Claude conversation."""
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list):
                return len(messages)
        
        return 0
    
    def extract_artifacts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract artifacts from Claude conversation."""
        artifacts = []
        
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list):
                for i, message in enumerate(messages):
                    if isinstance(message, dict) and message.get('role') == 'assistant':
                        content = message.get('content', [])
                        if isinstance(content, list):
                            for j, item in enumerate(content):
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    # Look for code blocks or other artifacts in text
                                    text = item.get('text', '')
                                    if '```' in text:
                                        # Extract code blocks
                                        import re
                                        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', text, re.DOTALL)
                                        for lang, code in code_blocks:
                                            artifacts.append({
                                                'type': 'code',
                                                'title': f'Code Block {len(artifacts) + 1}',
                                                'content': code,
                                                'metadata': {'language': lang, 'message_index': i, 'content_index': j}
                                            })
        
        return artifacts
    
    def create_conversation(self, data: Dict[str, Any], source: str) -> 'Conversation':
        """Create conversation with Claude-specific processing."""
        from ..database.models import Conversation, Artifact
        
        # Extract title
        title = data.get('title', '') or data.get('name', f"Claude Conversation {source}")
        
        # Extract timestamps
        create_time = self.parse_timestamp(data.get('created_at') or data.get('create_time'))
        datemodified = self.parse_timestamp(data.get('updated_at') or data.get('datemodified'))
        
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
            synced_at=create_time
        )
        
        # Save conversation first to get ID
        conversation.save()
        
        # Extract and save artifacts
        artifacts_data = self.extract_artifacts(data)
        for artifact_data in artifacts_data:
            artifact = Artifact(
                conversation_id=conversation.id,
                artifact_type=artifact_data['type'],
                title=artifact_data['title'],
                content=artifact_data['content'],
                metadata=artifact_data.get('metadata', {})
            )
            artifact.save()
        
        return conversation
