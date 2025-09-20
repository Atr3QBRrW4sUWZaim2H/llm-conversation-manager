"""
Base importer class for all conversation importers.
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from ..database.connection import get_db_connection
from ..database.models import Conversation

logger = logging.getLogger(__name__)


class BaseImporter(ABC):
    """Base class for all conversation importers."""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.db = get_db_connection()
        self.processed_count = 0
        self.failed_count = 0
        
    def sanitize_json(self, data: Any) -> Any:
        """Sanitize JSON data to handle invalid Unicode characters."""
        if isinstance(data, str):
            # Remove or replace invalid Unicode characters
            return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', data)
        elif isinstance(data, dict):
            return {k: self.sanitize_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_json(item) for item in data]
        else:
            return data
    
    def extract_preview(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Extract a preview from conversation data."""
        # Try to find the first user message or content
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list) and messages:
                first_message = messages[0]
                if isinstance(first_message, dict):
                    content = first_message.get('content', '')
                    if content:
                        return content[:max_length] + ('...' if len(content) > max_length else '')
        
        # Fallback to title or description
        title = data.get('title', '') or data.get('chat_title', '')
        if title:
            return title[:max_length] + ('...' if len(title) > max_length else '')
        
        return "No preview available"
    
    def calculate_cost(self, data: Dict[str, Any]) -> float:
        """Calculate conversation cost based on token usage."""
        # Look for token usage information
        if 'tokenUsage' in data:
            token_usage = data['tokenUsage']
            if isinstance(token_usage, dict):
                return float(token_usage.get('totalCostUSD', 0.0))
        
        # Look for cost in other common locations
        cost = data.get('cost', 0.0)
        if isinstance(cost, (int, float)):
            return float(cost)
        
        return 0.0
    
    def extract_model_info(self, data: Dict[str, Any]) -> tuple[str, str]:
        """Extract model ID and name from data."""
        model_id = data.get('model', '') or data.get('model_id', '')
        model_name = data.get('model_name', '') or data.get('modelInfo', {}).get('title', '')
        
        return str(model_id), str(model_name)
    
    def count_messages(self, data: Dict[str, Any]) -> int:
        """Count messages in conversation data."""
        if 'messages' in data:
            messages = data['messages']
            if isinstance(messages, list):
                return len(messages)
        
        return 0
    
    def parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if timestamp is None:
            return None
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                return None
        
        if isinstance(timestamp, str):
            # Try various datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
        
        return None
    
    def create_conversation(self, data: Dict[str, Any], source: str) -> Conversation:
        """Create a Conversation object from raw data."""
        # Sanitize the data
        sanitized_data = self.sanitize_json(data)
        
        # Extract basic information
        title = data.get('title', '') or data.get('chat_title', '') or f"Conversation {source}"
        create_time = self.parse_timestamp(data.get('create_time') or data.get('created_at'))
        datemodified = self.parse_timestamp(data.get('datemodified') or data.get('updated_at') or data.get('modified_at'))
        
        # Extract metadata
        cost = self.calculate_cost(data)
        model_id, model_name = self.extract_model_info(data)
        num_messages = self.count_messages(data)
        preview = self.extract_preview(data)
        
        # Create conversation object
        conversation = Conversation(
            title=title,
            source=source,
            platform=self.platform,
            create_time=create_time,
            datemodified=datemodified or create_time,
            data={"content": sanitized_data},
            cost=cost,
            model_id=model_id,
            model_name=model_name,
            num_messages=num_messages,
            chat_title=title,
            preview=preview,
            synced_at=datetime.now()
        )
        
        return conversation
    
    @abstractmethod
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse a file and return list of conversation data."""
        pass
    
    def import_file(self, filepath: str) -> bool:
        """Import a single file."""
        try:
            logger.info(f"Importing {filepath}")
            
            # Parse the file
            conversations_data = self.parse_file(filepath)
            
            if not conversations_data:
                logger.warning(f"No conversations found in {filepath}")
                return False
            
            # Process each conversation
            for i, data in enumerate(conversations_data):
                try:
                    # Generate source ID
                    source = data.get('id', f"{os.path.basename(filepath)}_{i}")
                    
                    # Create conversation
                    conversation = self.create_conversation(data, source)
                    
                    # Save to database
                    conversation.save()
                    self.processed_count += 1
                    
                    logger.info(f"Processed conversation {i+1}/{len(conversations_data)} from {filepath}")
                    
                except Exception as e:
                    logger.error(f"Failed to process conversation {i+1} from {filepath}: {e}")
                    self.failed_count += 1
                    continue
            
            logger.info(f"Successfully imported {self.processed_count} conversations from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import {filepath}: {e}")
            self.failed_count += 1
            return False
    
    def import_directory(self, directory: str) -> Dict[str, int]:
        """Import all files from a directory."""
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all relevant files
        files = self.find_files(directory)
        
        logger.info(f"Found {len(files)} files to import from {directory}")
        
        # Process each file
        for filepath in files:
            self.import_file(filepath)
        
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'total': len(files)
        }
    
    def find_files(self, directory: str) -> List[str]:
        """Find files to import in directory."""
        files = []
        
        for filename in os.listdir(directory):
            if self.is_valid_file(filename):
                filepath = os.path.join(directory, filename)
                files.append(filepath)
        
        return sorted(files)
    
    @abstractmethod
    def is_valid_file(self, filename: str) -> bool:
        """Check if file is valid for this importer."""
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get import statistics."""
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'total': self.processed_count + self.failed_count
        }
