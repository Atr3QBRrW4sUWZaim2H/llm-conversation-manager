"""
Database models for LLM Conversation Manager.
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from psycopg2.extras import RealDictCursor

from .connection import get_db_connection

logger = logging.getLogger(__name__)


@dataclass
class Conversation:
    """Conversation model."""
    
    id: Optional[int] = None
    title: str = ""
    source: str = ""
    platform: str = ""
    create_time: Optional[datetime] = None
    datemodified: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None
    cost: float = 0.0
    model_id: Optional[str] = None
    model_name: Optional[str] = None
    num_messages: int = 0
    chat_title: str = ""
    preview: str = ""
    synced_at: Optional[datetime] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create Conversation from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'platform': self.platform,
            'create_time': self.create_time,
            'datemodified': self.datemodified,
            'data': self.data,
            'cost': self.cost,
            'model_id': self.model_id,
            'model_name': self.model_name,
            'num_messages': self.num_messages,
            'chat_title': self.chat_title,
            'preview': self.preview,
            'synced_at': self.synced_at,
            'file_path': self.file_path,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self) -> int:
        """Save conversation to database."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            if self.id is None:
                # Insert new conversation
                cursor.execute("""
                    INSERT INTO conversations (
                        title, source, platform, create_time, datemodified, data,
                        cost, model_id, model_name, num_messages, chat_title,
                        preview, synced_at, file_path
                    ) VALUES (
                        %(title)s, %(source)s, %(platform)s, %(create_time)s, %(datemodified)s, %(data)s,
                        %(cost)s, %(model_id)s, %(model_name)s, %(num_messages)s, %(chat_title)s,
                        %(preview)s, %(synced_at)s, %(file_path)s
                    ) ON CONFLICT (title, source, platform)
                    DO UPDATE SET
                        datemodified = EXCLUDED.datemodified,
                        create_time = EXCLUDED.create_time,
                        data = EXCLUDED.data,
                        cost = EXCLUDED.cost,
                        model_id = EXCLUDED.model_id,
                        model_name = EXCLUDED.model_name,
                        num_messages = EXCLUDED.num_messages,
                        chat_title = EXCLUDED.chat_title,
                        preview = EXCLUDED.preview,
                        synced_at = EXCLUDED.synced_at,
                        file_path = EXCLUDED.file_path
                    WHERE conversations.datemodified < EXCLUDED.datemodified
                    RETURNING id;
                """, self.to_dict())
                
                result = cursor.fetchone()
                if result:
                    self.id = result['id']
                    logger.info(f"Upserted conversation ID {self.id}")
                else:
                    logger.info("No update needed (datemodified not newer)")
            else:
                # Update existing conversation
                cursor.execute("""
                    UPDATE conversations SET
                        title = %(title)s,
                        source = %(source)s,
                        platform = %(platform)s,
                        create_time = %(create_time)s,
                        datemodified = %(datemodified)s,
                        data = %(data)s,
                        cost = %(cost)s,
                        model_id = %(model_id)s,
                        model_name = %(model_name)s,
                        num_messages = %(num_messages)s,
                        chat_title = %(chat_title)s,
                        preview = %(preview)s,
                        synced_at = %(synced_at)s,
                        file_path = %(file_path)s
                    WHERE id = %(id)s
                """, self.to_dict())
                
                logger.info(f"Updated conversation ID {self.id}")
        
        return self.id
    
    @classmethod
    def get_by_id(cls, conversation_id: int) -> Optional['Conversation']:
        """Get conversation by ID."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
            result = cursor.fetchone()
            
            if result:
                return cls.from_dict(dict(result))
            return None
    
    @classmethod
    def search(cls, query: str = "", platform: Optional[str] = None, 
               model: Optional[str] = None, limit: int = 50, offset: int = 0) -> List['Conversation']:
        """Search conversations."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM search_conversations(%s, %s, %s, %s, %s)
            """, (query, platform, model, limit, offset))
            
            results = cursor.fetchall()
            return [cls.from_dict(dict(row)) for row in results]
    
    @classmethod
    def get_by_platform(cls, platform: str, limit: int = 50) -> List['Conversation']:
        """Get conversations by platform."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE platform = %s 
                ORDER BY create_time DESC 
                LIMIT %s
            """, (platform, limit))
            
            results = cursor.fetchall()
            return [cls.from_dict(dict(row)) for row in results]
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get conversation statistics."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM conversation_summary")
            results = cursor.fetchall()
            
            stats = {}
            for row in results:
                platform = row['platform']
                stats[platform] = {
                    'total_conversations': row['total_conversations'],
                    'total_messages': row['total_messages'],
                    'total_cost': float(row['total_cost']) if row['total_cost'] else 0.0,
                    'avg_cost': float(row['avg_cost']) if row['avg_cost'] else 0.0,
                    'earliest_conversation': row['earliest_conversation'],
                    'latest_conversation': row['latest_conversation'],
                    'unique_models': row['unique_models']
                }
            
            return stats
    
    def get_artifacts(self) -> List['Artifact']:
        """Get artifacts for this conversation."""
        if not self.id:
            return []
        
        return Artifact.get_by_conversation_id(self.id)


@dataclass
class Artifact:
    """Artifact model."""
    
    id: Optional[int] = None
    conversation_id: Optional[int] = None
    artifact_type: str = ""
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """Create Artifact from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'artifact_type': self.artifact_type,
            'title': self.title,
            'content': self.content,
            'file_path': self.file_path,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def save(self) -> int:
        """Save artifact to database."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            if self.id is None:
                cursor.execute("""
                    INSERT INTO artifacts (
                        conversation_id, artifact_type, title, content, file_path, metadata
                    ) VALUES (
                        %(conversation_id)s, %(artifact_type)s, %(title)s, %(content)s, %(file_path)s, %(metadata)s
                    ) RETURNING id;
                """, self.to_dict())
                
                result = cursor.fetchone()
                self.id = result['id']
                logger.info(f"Created artifact ID {self.id}")
            else:
                cursor.execute("""
                    UPDATE artifacts SET
                        conversation_id = %(conversation_id)s,
                        artifact_type = %(artifact_type)s,
                        title = %(title)s,
                        content = %(content)s,
                        file_path = %(file_path)s,
                        metadata = %(metadata)s
                    WHERE id = %(id)s
                """, self.to_dict())
                
                logger.info(f"Updated artifact ID {self.id}")
        
        return self.id
    
    @classmethod
    def get_by_conversation_id(cls, conversation_id: int) -> List['Artifact']:
        """Get artifacts by conversation ID."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM artifacts 
                WHERE conversation_id = %s 
                ORDER BY created_at ASC
            """, (conversation_id,))
            
            results = cursor.fetchall()
            return [cls.from_dict(dict(row)) for row in results]


@dataclass
class Tag:
    """Tag model."""
    
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    color: str = "#007bff"
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """Create Tag from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at
        }
    
    def save(self) -> int:
        """Save tag to database."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            if self.id is None:
                cursor.execute("""
                    INSERT INTO tags (name, description, color)
                    VALUES (%(name)s, %(description)s, %(color)s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id;
                """, self.to_dict())
                
                result = cursor.fetchone()
                if result:
                    self.id = result['id']
                    logger.info(f"Created tag ID {self.id}")
                else:
                    # Tag already exists, get its ID
                    cursor.execute("SELECT id FROM tags WHERE name = %s", (self.name,))
                    result = cursor.fetchone()
                    self.id = result['id']
                    logger.info(f"Found existing tag ID {self.id}")
            else:
                cursor.execute("""
                    UPDATE tags SET
                        name = %(name)s,
                        description = %(description)s,
                        color = %(color)s
                    WHERE id = %(id)s
                """, self.to_dict())
                
                logger.info(f"Updated tag ID {self.id}")
        
        return self.id
    
    @classmethod
    def get_all(cls) -> List['Tag']:
        """Get all tags."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM tags ORDER BY name")
            results = cursor.fetchall()
            return [cls.from_dict(dict(row)) for row in results]


@dataclass
class ConversationTag:
    """Conversation-Tag relationship model."""
    
    conversation_id: int
    tag_id: int
    
    def save(self):
        """Save conversation-tag relationship."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO conversation_tags (conversation_id, tag_id)
                VALUES (%(conversation_id)s, %(tag_id)s)
                ON CONFLICT (conversation_id, tag_id) DO NOTHING
            """, self.to_dict())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'conversation_id': self.conversation_id,
            'tag_id': self.tag_id
        }
    
    @classmethod
    def remove(cls, conversation_id: int, tag_id: int):
        """Remove conversation-tag relationship."""
        db = get_db_connection()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM conversation_tags 
                WHERE conversation_id = %s AND tag_id = %s
            """, (conversation_id, tag_id))
