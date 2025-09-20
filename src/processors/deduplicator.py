"""
Deduplication utilities for conversations.
"""
import logging
from typing import List, Dict, Any, Tuple
from ..database.connection import get_db_connection

logger = logging.getLogger(__name__)


class Deduplicator:
    """Handles conversation deduplication."""
    
    def __init__(self):
        self.db = get_db_connection()
        self.duplicates_found = 0
        self.duplicates_removed = 0
    
    def find_duplicates(self) -> List[Tuple[str, str, List[int]]]:
        """Find duplicate conversations based on title and content."""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    LOWER(chat_title) AS title_normalized,
                    data,
                    array_agg(id ORDER BY id) AS ids,
                    COUNT(*) AS count
                FROM conversations
                WHERE chat_title IS NOT NULL AND chat_title != ''
                GROUP BY LOWER(chat_title), data
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC;
            """)
            
            duplicates = cursor.fetchall()
            logger.info(f"Found {len(duplicates)} groups of potential duplicates")
            return duplicates
    
    def find_similar_conversations(self, similarity_threshold: float = 0.8) -> List[Tuple[str, str, List[int]]]:
        """Find similar conversations using text similarity."""
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    c1.id as id1,
                    c2.id as id2,
                    c1.chat_title as title1,
                    c2.chat_title as title2,
                    similarity(c1.chat_title, c2.chat_title) as sim
                FROM conversations c1
                JOIN conversations c2 ON c1.id < c2.id
                WHERE c1.chat_title IS NOT NULL 
                AND c2.chat_title IS NOT NULL
                AND similarity(c1.chat_title, c2.chat_title) > %s
                ORDER BY sim DESC;
            """, (similarity_threshold,))
            
            similar_pairs = cursor.fetchall()
            logger.info(f"Found {len(similar_pairs)} pairs of similar conversations")
            return similar_pairs
    
    def remove_duplicates(self, duplicates: List[Tuple[str, str, List[int]]]) -> int:
        """Remove duplicate conversations, keeping the oldest."""
        removed_count = 0
        
        with self.db.get_cursor() as cursor:
            for i, (title_normalized, data_val, ids, count_val) in enumerate(duplicates, 1):
                if not ids or count_val < 2:
                    continue
                
                # Keep the first (oldest) ID, delete the rest
                keep_id = ids[0]
                ids_to_delete = ids[1:]
                
                logger.info(
                    f"[Group {i}] Duplicate group has {count_val} records with title='{title_normalized}'. "
                    f"Keeping ID={keep_id}, Deleting IDs={ids_to_delete}"
                )
                
                # Delete duplicates
                cursor.execute("DELETE FROM conversations WHERE id = ANY(%s);", (ids_to_delete,))
                removed_count += len(ids_to_delete)
        
        self.duplicates_removed = removed_count
        logger.info(f"Successfully removed {removed_count} duplicate records")
        return removed_count
    
    def remove_similar_conversations(self, similar_pairs: List[Tuple[str, str, List[int]]], 
                                   keep_strategy: str = "oldest") -> int:
        """Remove similar conversations based on strategy."""
        removed_count = 0
        processed_ids = set()
        
        with self.db.get_cursor() as cursor:
            for id1, id2, title1, title2, similarity_score in similar_pairs:
                if id1 in processed_ids or id2 in processed_ids:
                    continue
                
                # Get full conversation details
                cursor.execute("SELECT * FROM conversations WHERE id IN (%s, %s) ORDER BY id", (id1, id2))
                conversations = cursor.fetchall()
                
                if len(conversations) != 2:
                    continue
                
                # Choose which to keep based on strategy
                if keep_strategy == "oldest":
                    keep_id = min(id1, id2)
                    remove_id = max(id1, id2)
                elif keep_strategy == "newest":
                    keep_id = max(id1, id2)
                    remove_id = min(id1, id2)
                elif keep_strategy == "longest":
                    # Keep the one with more messages
                    if conversations[0]['num_messages'] >= conversations[1]['num_messages']:
                        keep_id = conversations[0]['id']
                        remove_id = conversations[1]['id']
                    else:
                        keep_id = conversations[1]['id']
                        remove_id = conversations[0]['id']
                else:
                    keep_id = min(id1, id2)
                    remove_id = max(id1, id2)
                
                logger.info(
                    f"Removing similar conversation ID={remove_id} (similarity={similarity_score:.3f}), "
                    f"keeping ID={keep_id}"
                )
                
                # Delete the chosen conversation
                cursor.execute("DELETE FROM conversations WHERE id = %s", (remove_id,))
                removed_count += 1
                processed_ids.add(remove_id)
        
        self.duplicates_removed = removed_count
        logger.info(f"Successfully removed {removed_count} similar conversations")
        return removed_count
    
    def get_duplicate_stats(self) -> Dict[str, int]:
        """Get duplicate statistics."""
        with self.db.get_cursor() as cursor:
            # Count total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            # Count duplicate groups
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT LOWER(chat_title), data
                    FROM conversations
                    WHERE chat_title IS NOT NULL AND chat_title != ''
                    GROUP BY LOWER(chat_title), data
                    HAVING COUNT(*) > 1
                ) as duplicate_groups
            """)
            duplicate_groups = cursor.fetchone()[0]
            
            # Count conversations in duplicate groups
            cursor.execute("""
                SELECT SUM(count) FROM (
                    SELECT COUNT(*) as count
                    FROM conversations
                    WHERE chat_title IS NOT NULL AND chat_title != ''
                    GROUP BY LOWER(chat_title), data
                    HAVING COUNT(*) > 1
                ) as duplicate_counts
            """)
            duplicate_conversations = cursor.fetchone()[0] or 0
            
            return {
                'total_conversations': total_conversations,
                'duplicate_groups': duplicate_groups,
                'duplicate_conversations': duplicate_conversations,
                'unique_conversations': total_conversations - duplicate_conversations + duplicate_groups
            }
    
    def run_full_deduplication(self, similarity_threshold: float = 0.8, 
                             keep_strategy: str = "oldest") -> Dict[str, int]:
        """Run full deduplication process."""
        logger.info("Starting full deduplication process")
        
        # Find and remove exact duplicates
        duplicates = self.find_duplicates()
        exact_removed = self.remove_duplicates(duplicates)
        
        # Find and remove similar conversations
        similar_pairs = self.find_similar_conversations(similarity_threshold)
        similar_removed = self.remove_similar_conversations(similar_pairs, keep_strategy)
        
        # Get final stats
        stats = self.get_duplicate_stats()
        
        logger.info(f"Deduplication completed: {exact_removed} exact duplicates, {similar_removed} similar conversations removed")
        
        return {
            'exact_duplicates_removed': exact_removed,
            'similar_conversations_removed': similar_removed,
            'total_removed': exact_removed + similar_removed,
            'final_stats': stats
        }
