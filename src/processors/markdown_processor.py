"""
Markdown conversation processor for importing markdown archives.
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import frontmatter

from ..database.models import Conversation
from ..importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class MarkdownProcessor(BaseImporter):
    """Processor for markdown conversation archives."""
    
    def __init__(self):
        super().__init__("markdown")
    
    def is_valid_file(self, filename: str) -> bool:
        """Check if file is a valid markdown file."""
        return filename.lower().endswith('.md')
    
    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse markdown file and extract conversation data."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            post = frontmatter.loads(content)
            
            # Extract metadata
            metadata = post.metadata
            content_text = post.content
            
            # Parse conversation structure
            conversation_data = self.parse_conversation_content(content_text, metadata, filepath)
            
            return [conversation_data] if conversation_data else []
            
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return []
    
    def parse_conversation_content(self, content: str, metadata: Dict[str, Any], filepath: str) -> Optional[Dict[str, Any]]:
        """Parse conversation content from markdown."""
        # Extract title from metadata or filename
        title = metadata.get('title', '')
        if not title:
            # Extract from filename
            filename = os.path.basename(filepath)
            title = os.path.splitext(filename)[0]
            # Clean up title
            title = re.sub(r'^ChatGPT-', '', title)
            title = re.sub(r'^Claude-', '', title)
            title = re.sub(r'^GPT-', '', title)
            title = title.replace('_', ' ').replace('-', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
        
        # Extract source URL if available
        source = metadata.get('source', '')
        if not source:
            source = f"markdown_{os.path.basename(filepath)}"
        
        # Parse messages from content
        messages = self.extract_messages(content)
        
        # Determine platform from filename or metadata
        platform = self.determine_platform(filepath, metadata)
        
        # Extract timestamps
        create_time = self.parse_timestamp(metadata.get('date') or metadata.get('created_at'))
        if not create_time:
            # Try to extract from filename
            create_time = self.extract_date_from_filename(filepath)
        
        # Create conversation data
        conversation_data = {
            'title': title,
            'source': source,
            'platform': platform,
            'create_time': create_time.isoformat() if create_time else None,
            'datemodified': create_time.isoformat() if create_time else None,
            'messages': messages,
            'metadata': metadata,
            'file_path': filepath,
            'content': content
        }
        
        return conversation_data
    
    def extract_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extract messages from markdown content."""
        messages = []
        
        # Split content into sections
        sections = re.split(r'\n(?=####|###|##|#)', content)
        
        current_message = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if this is a user message
            if section.startswith('#### You:') or section.startswith('### You:') or section.startswith('## You:'):
                if current_message:
                    messages.append(current_message)
                
                # Extract user message
                content_text = re.sub(r'^#### You:\s*', '', section, flags=re.MULTILINE)
                content_text = re.sub(r'^### You:\s*', '', content_text, flags=re.MULTILINE)
                content_text = re.sub(r'^## You:\s*', '', content_text, flags=re.MULTILINE)
                
                # Extract timestamp if present
                timestamp_match = re.search(r'<time datetime="([^"]+)"', content_text)
                timestamp = None
                if timestamp_match:
                    timestamp = self.parse_timestamp(timestamp_match.group(1))
                    content_text = re.sub(r'<time[^>]*>', '', content_text)
                
                current_message = {
                    'role': 'user',
                    'content': content_text.strip(),
                    'timestamp': timestamp.isoformat() if timestamp else None
                }
            
            # Check if this is an assistant message
            elif section.startswith('#### Assistant:') or section.startswith('### Assistant:') or section.startswith('## Assistant:'):
                if current_message:
                    messages.append(current_message)
                
                # Extract assistant message
                content_text = re.sub(r'^#### Assistant:\s*', '', section, flags=re.MULTILINE)
                content_text = re.sub(r'^### Assistant:\s*', '', content_text, flags=re.MULTILINE)
                content_text = re.sub(r'^## Assistant:\s*', '', content_text, flags=re.MULTILINE)
                
                current_message = {
                    'role': 'assistant',
                    'content': content_text.strip(),
                    'timestamp': None
                }
            
            # Check if this is a ChatGPT response
            elif section.startswith('#### ChatGPT:') or section.startswith('### ChatGPT:') or section.startswith('## ChatGPT:'):
                if current_message:
                    messages.append(current_message)
                
                # Extract ChatGPT message
                content_text = re.sub(r'^#### ChatGPT:\s*', '', section, flags=re.MULTILINE)
                content_text = re.sub(r'^### ChatGPT:\s*', '', content_text, flags=re.MULTILINE)
                content_text = re.sub(r'^## ChatGPT:\s*', '', content_text, flags=re.MULTILINE)
                
                current_message = {
                    'role': 'assistant',
                    'content': content_text.strip(),
                    'timestamp': None
                }
            
            # Check if this is a Claude response
            elif section.startswith('#### Claude:') or section.startswith('### Claude:') or section.startswith('## Claude:'):
                if current_message:
                    messages.append(current_message)
                
                # Extract Claude message
                content_text = re.sub(r'^#### Claude:\s*', '', section, flags=re.MULTILINE)
                content_text = re.sub(r'^### Claude:\s*', '', content_text, flags=re.MULTILINE)
                content_text = re.sub(r'^## Claude:\s*', '', content_text, flags=re.MULTILINE)
                
                current_message = {
                    'role': 'assistant',
                    'content': content_text.strip(),
                    'timestamp': None
                }
            
            # If we have a current message, append content to it
            elif current_message:
                current_message['content'] += '\n\n' + section
        
        # Add the last message
        if current_message:
            messages.append(current_message)
        
        return messages
    
    def determine_platform(self, filepath: str, metadata: Dict[str, Any]) -> str:
        """Determine platform from filename or metadata."""
        filename = os.path.basename(filepath).lower()
        
        if 'chatgpt' in filename or 'gpt' in filename:
            return 'chatgpt'
        elif 'claude' in filename:
            return 'claude'
        elif 'typingmind' in filename:
            return 'typingmind'
        else:
            # Check metadata
            source = metadata.get('source', '').lower()
            if 'chatgpt' in source or 'openai' in source:
                return 'chatgpt'
            elif 'claude' in source or 'anthropic' in source:
                return 'claude'
            elif 'typingmind' in source:
                return 'typingmind'
            else:
                return 'markdown'
    
    def extract_date_from_filename(self, filepath: str) -> Optional[datetime]:
        """Extract date from filename if present."""
        filename = os.path.basename(filepath)
        
        # Look for date patterns in filename
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{4}_\d{2}_\d{2})',  # YYYY_MM_DD
            r'(\d{8})',  # YYYYMMDD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1).replace('_', '-')
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
        
        return None
    
    def extract_preview(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """Extract preview from markdown conversation."""
        messages = data.get('messages', [])
        if messages:
            first_message = messages[0]
            content = first_message.get('content', '')
            if content:
                # Clean up markdown formatting
                content = re.sub(r'#+\s*', '', content)  # Remove headers
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove bold
                content = re.sub(r'\*(.*?)\*', r'\1', content)  # Remove italic
                content = re.sub(r'`(.*?)`', r'\1', content)  # Remove code
                content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Remove links
                
                return content[:max_length] + ('...' if len(content) > max_length else '')
        
        # Fallback to title
        title = data.get('title', '')
        if title:
            return title[:max_length] + ('...' if len(title) > max_length else '')
        
        return "No preview available"
    
    def calculate_cost(self, data: Dict[str, Any]) -> float:
        """Calculate cost for markdown conversation (not available)."""
        return 0.0
    
    def extract_model_info(self, data: Dict[str, Any]) -> tuple[str, str]:
        """Extract model information from markdown data."""
        platform = data.get('platform', 'markdown')
        
        if platform == 'chatgpt':
            return 'gpt-4', 'GPT-4'
        elif platform == 'claude':
            return 'claude-3-opus', 'Claude 3 Opus'
        elif platform == 'typingmind':
            return 'typingmind', 'TypingMind'
        else:
            return 'unknown', 'Unknown Model'
    
    def count_messages(self, data: Dict[str, Any]) -> int:
        """Count messages in markdown conversation."""
        messages = data.get('messages', [])
        return len(messages) if isinstance(messages, list) else 0
    
    def create_conversation(self, data: Dict[str, Any], source: str) -> 'Conversation':
        """Create conversation with markdown-specific processing."""
        # Extract title
        title = data.get('title', f"Markdown Conversation {source}")
        
        # Extract timestamps
        create_time = self.parse_timestamp(data.get('create_time'))
        datemodified = self.parse_timestamp(data.get('datemodified'))
        
        # Extract model info
        model_id, model_name = self.extract_model_info(data)
        
        # Count messages
        num_messages = self.count_messages(data)
        
        # Extract preview
        preview = self.extract_preview(data)
        
        # Get file path
        file_path = data.get('file_path', '')
        
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
            synced_at=create_time,
            file_path=file_path
        )
        
        return conversation
