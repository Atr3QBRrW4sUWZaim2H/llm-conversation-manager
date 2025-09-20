"""
File utilities for LLM Conversation Manager.
"""
import os
import shutil
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory(path: str) -> None:
        """Ensure directory exists, create if it doesn't."""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """Move file from source to destination."""
        try:
            shutil.move(source, destination)
            logger.info(f"Moved {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {source} to {destination}: {e}")
            return False
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """Copy file from source to destination."""
        try:
            shutil.copy2(source, destination)
            logger.info(f"Copied {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy {source} to {destination}: {e}")
            return False
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_extension(filepath: str) -> str:
        """Get file extension."""
        return Path(filepath).suffix.lower()
    
    @staticmethod
    def is_valid_json(filepath: str) -> bool:
        """Check if file is valid JSON."""
        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
    
    @staticmethod
    def is_valid_markdown(filepath: str) -> bool:
        """Check if file is valid markdown."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Basic markdown validation
            return len(content.strip()) > 0
        except UnicodeDecodeError:
            return False
    
    @staticmethod
    def find_files(directory: str, extensions: List[str], recursive: bool = True) -> List[str]:
        """Find files with specific extensions in directory."""
        files = []
        path = Path(directory)
        
        if recursive:
            pattern = f"**/*.{{{','.join(extensions)}}}"
            files = [str(f) for f in path.glob(pattern) if f.is_file()]
        else:
            for ext in extensions:
                pattern = f"*.{ext}"
                files.extend([str(f) for f in path.glob(pattern) if f.is_file()])
        
        return sorted(files)
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe storage."""
        import re
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        return filename
    
    @staticmethod
    def get_file_hash(filepath: str) -> Optional[str]:
        """Get MD5 hash of file."""
        try:
            import hashlib
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to get hash for {filepath}: {e}")
            return None
    
    @staticmethod
    def backup_file(filepath: str, backup_dir: str) -> Optional[str]:
        """Create backup of file."""
        try:
            FileUtils.ensure_directory(backup_dir)
            
            filename = Path(filepath).name
            backup_path = os.path.join(backup_dir, filename)
            
            # Add timestamp if file exists
            counter = 1
            while os.path.exists(backup_path):
                name, ext = os.path.splitext(filename)
                backup_path = os.path.join(backup_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.copy2(filepath, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup {filepath}: {e}")
            return None
