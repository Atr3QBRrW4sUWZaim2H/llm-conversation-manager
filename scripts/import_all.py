#!/usr/bin/env python3
"""
Main import script for LLM Conversation Manager.
Imports conversations from all supported platforms.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.importers import ChatGPTImporter, TypingMindImporter, ClaudeImporter
from src.processors import MarkdownProcessor, Deduplicator
from src.utils.logging_utils import setup_logging

def main():
    """Main import function."""
    parser = argparse.ArgumentParser(description="Import conversations from various platforms")
    parser.add_argument("--input-dir", required=True, help="Input directory containing files to import")
    parser.add_argument("--platform", choices=["chatgpt", "typingmind", "claude", "markdown", "all"], 
                       default="all", help="Platform to import from")
    parser.add_argument("--deduplicate", action="store_true", help="Run deduplication after import")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level, log_file="logs/import.log")
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting import from {args.input_dir} for platform: {args.platform}")
    
    # Check if input directory exists
    if not os.path.exists(args.input_dir):
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    total_stats = {"processed": 0, "failed": 0, "total": 0}
    
    try:
        if args.platform in ["chatgpt", "all"]:
            logger.info("Importing ChatGPT conversations...")
            importer = ChatGPTImporter()
            stats = importer.import_directory(args.input_dir)
            total_stats["processed"] += stats["processed"]
            total_stats["failed"] += stats["failed"]
            total_stats["total"] += stats["total"]
            logger.info(f"ChatGPT import: {stats}")
        
        if args.platform in ["typingmind", "all"]:
            logger.info("Importing TypingMind conversations...")
            importer = TypingMindImporter()
            stats = importer.import_directory(args.input_dir)
            total_stats["processed"] += stats["processed"]
            total_stats["failed"] += stats["failed"]
            total_stats["total"] += stats["total"]
            logger.info(f"TypingMind import: {stats}")
        
        if args.platform in ["claude", "all"]:
            logger.info("Importing Claude conversations...")
            importer = ClaudeImporter()
            stats = importer.import_directory(args.input_dir)
            total_stats["processed"] += stats["processed"]
            total_stats["failed"] += stats["failed"]
            total_stats["total"] += stats["total"]
            logger.info(f"Claude import: {stats}")
        
        if args.platform in ["markdown", "all"]:
            logger.info("Importing Markdown conversations...")
            processor = MarkdownProcessor()
            stats = processor.import_directory(args.input_dir)
            total_stats["processed"] += stats["processed"]
            total_stats["failed"] += stats["failed"]
            total_stats["total"] += stats["total"]
            logger.info(f"Markdown import: {stats}")
        
        logger.info(f"Import completed: {total_stats}")
        
        # Run deduplication if requested
        if args.deduplicate:
            logger.info("Running deduplication...")
            deduplicator = Deduplicator()
            dedup_stats = deduplicator.run_full_deduplication()
            logger.info(f"Deduplication completed: {dedup_stats}")
        
        print(f"\n🎉 Import completed successfully!")
        print(f"📊 Final Statistics:")
        print(f"   Processed: {total_stats['processed']} files")
        print(f"   Failed: {total_stats['failed']} files")
        print(f"   Total: {total_stats['total']} files")
        
        if args.deduplicate:
            print(f"   Duplicates removed: {dedup_stats.get('total_removed', 0)}")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
