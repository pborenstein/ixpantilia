#!/usr/bin/env python3
"""
Incremental Gleanings Extraction

This script performs incremental extraction of gleanings, only processing files
that have been modified since the last run. Uses the state management system
to track changes and maintain user preferences.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Import the state management system
from gleanings_state import create_state_manager

# Import extraction functions from the new module
from extraction_functions import (
    load_categories_config,
    categorize_gleaning_with_config,
    extract_gleanings_from_file,
    extract_media_from_file,
    find_daily_notes
)

# Import tag inference engine
from tag_inference import create_tag_inference_engine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IncrementalExtractor:
    """Handles incremental extraction of gleanings with state management."""
    
    def __init__(self, state_file: str = "gleanings_state.json"):
        self.state = create_state_manager(state_file)
        self.categories_config = load_categories_config()
        self.tag_engine = None  # Lazy initialization
        self.extracted_count = 0
        self.updated_count = 0
        self.unchanged_count = 0
        self.media_extracted_count = 0
        self.media_updated_count = 0
        self.media_unchanged_count = 0
        
    def categorize_gleaning(self, gleaning):
        """Categorize a gleaning using the config file."""
        return categorize_gleaning_with_config(gleaning, self.categories_config)
    
    def infer_tags(self, gleaning):
        """Infer tags for a gleaning using the tag inference engine."""
        if self.tag_engine is None:
            # Lazy initialization - determine vault path from the script location
            script_dir = Path(__file__).parent
            vault_path = script_dir.parent.parent  # Go up two levels to reach vault root
            try:
                self.tag_engine = create_tag_inference_engine(str(vault_path))
                logger.info("Tag inference engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize tag inference engine: {e}")
                return []
        
        try:
            return self.tag_engine.infer_tags(gleaning)
        except Exception as e:
            logger.warning(f"Error inferring tags for gleaning: {e}")
            return []
    
    def process_file(self, file_path: str) -> int:
        """Process a single file and extract gleanings and media."""
        logger.info(f"Processing: {Path(file_path).name}")
        
        try:
            # Clear the deduplication caches for this run
            if hasattr(extract_gleanings_from_file, '_seen_urls'):
                delattr(extract_gleanings_from_file, '_seen_urls')
            if hasattr(extract_media_from_file, '_seen_media'):
                delattr(extract_media_from_file, '_seen_media')
            
            # Extract both gleanings and media
            gleanings = extract_gleanings_from_file(file_path)
            media_items = extract_media_from_file(file_path)
            
            processed_count = 0
            
            # Process gleanings
            for gleaning in gleanings:
                # Add category
                try:
                    gleaning['category'] = self.categorize_gleaning(gleaning)
                except Exception as e:
                    logger.warning(f"Error categorizing gleaning: {e}")
                    gleaning['category'] = 'Miscellaneous'
                
                # Add tags
                try:
                    gleaning['tags'] = self.infer_tags(gleaning)
                except Exception as e:
                    logger.warning(f"Error inferring tags for gleaning: {e}")
                    gleaning['tags'] = []
                
                # Add to state management
                gleaning_id = self.state.add_gleaning(gleaning)
                
                # Track statistics
                processing_state = self.state.get_gleaning(gleaning_id).get('processing_state', 'new')
                if processing_state == 'new':
                    self.extracted_count += 1
                elif processing_state == 'updated':
                    self.updated_count += 1
                else:
                    self.unchanged_count += 1
                
                processed_count += 1
            
            # Process media items
            for media_item in media_items:
                # Add media item to state management
                media_id = self.state.add_media(media_item)
                
                # Track statistics for media
                processing_state = self.state.get_media(media_id).get('processing_state', 'new')
                if processing_state == 'new':
                    self.media_extracted_count += 1
                elif processing_state == 'updated':
                    self.media_updated_count += 1
                else:
                    self.media_unchanged_count += 1
                
                processed_count += 1
            
            # Track that we've processed this file
            file_mtime = os.path.getmtime(file_path)
            self.state.track_file_processing(file_path, file_mtime)
            
            if processed_count > 0:
                gleaning_count = len(gleanings)
                media_count = len(media_items)
                logger.info(f"  Extracted {gleaning_count} gleanings, {media_count} media items")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return 0
    
    def extract_incremental(self, daily_path: str, force_all: bool = False) -> dict:
        """
        Perform incremental extraction.
        
        Args:
            daily_path: Path to daily notes directory
            force_all: If True, process all files regardless of modification time
        
        Returns:
            Dictionary with extraction statistics
        """
        daily_path = Path(daily_path)
        
        if not daily_path.exists():
            raise ValueError(f"Daily notes path does not exist: {daily_path}")
        
        logger.info(f"Starting incremental extraction from: {daily_path}")
        
        # Find all daily note files
        all_daily_notes = find_daily_notes(daily_path)
        logger.info(f"Found {len(all_daily_notes)} total daily note files")
        
        if force_all:
            files_to_process = [str(f) for f in all_daily_notes]
            logger.info("Force mode: processing all files")
        else:
            # Get only modified files
            files_to_process = self.state.get_modified_files([str(f) for f in all_daily_notes])
            logger.info(f"Found {len(files_to_process)} modified files to process")
        
        if not files_to_process:
            logger.info("No files need processing")
            return {
                "processed_files": 0,
                "total_files": len(all_daily_notes),
                "new_gleanings": 0,
                "updated_gleanings": 0,
                "unchanged_gleanings": 0,
                "execution_time": 0
            }
        
        # Process files
        start_time = datetime.now()
        processed_files = 0
        
        for file_path in files_to_process:
            if self.process_file(file_path) >= 0:  # >= 0 means successful processing
                processed_files += 1
        
        # Save state
        self.state.save_state()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        stats = {
            "processed_files": processed_files,
            "total_files": len(all_daily_notes),
            "new_gleanings": self.extracted_count,
            "updated_gleanings": self.updated_count,
            "unchanged_gleanings": self.unchanged_count,
            "execution_time": execution_time
        }
        
        logger.info(f"Extraction completed in {execution_time:.1f}s")
        logger.info(f"Processed {processed_files}/{len(all_daily_notes)} files")
        logger.info(f"New: {self.extracted_count}, Updated: {self.updated_count}, Unchanged: {self.unchanged_count}")
        
        return stats
    
    def migrate_legacy_data(self, legacy_file: str = "gleanings_data.json") -> int:
        """Migrate data from legacy format if needed."""
        return self.state.migrate_from_legacy(legacy_file)

def main():
    parser = argparse.ArgumentParser(description='Incremental gleanings extraction')
    parser.add_argument('--daily-path', default='Daily/2025',
                       help='Path to daily notes directory')
    parser.add_argument('--state-file', default='gleanings_state.json',
                       help='State file path')
    parser.add_argument('--force-all', action='store_true',
                       help='Process all files, not just modified ones')
    parser.add_argument('--migrate', action='store_true',
                       help='Migrate from legacy gleanings_data.json')
    parser.add_argument('--stats', action='store_true',
                       help='Show current statistics')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Find vault root
    script_dir = Path(__file__).parent
    vault_root = script_dir
    
    while vault_root.parent != vault_root:
        if (vault_root / '.obsidian').exists() or (vault_root / 'CLAUDE.md').exists():
            break
        vault_root = vault_root.parent
    else:
        vault_root = script_dir.parent.parent
    
    daily_path = vault_root / args.daily_path
    
    try:
        extractor = IncrementalExtractor(args.state_file)
        
        # Handle migration if requested
        if args.migrate:
            migrated = extractor.migrate_legacy_data()
            print(f"Migrated {migrated} gleanings from legacy format")
            if migrated > 0:
                extractor.state.save_state()
        
        # Show statistics if requested
        if args.stats:
            stats = extractor.state.get_statistics()
            print("\nCurrent Statistics:")
            print(f"Total gleanings: {stats['total_gleanings']}")
            print(f"Status breakdown: {stats['status_breakdown']}")
            print(f"Tracked files: {stats['tracked_files']}")
            print(f"Last updated: {stats['last_updated']}")
            return
        
        # Perform extraction
        results = extractor.extract_incremental(str(daily_path), args.force_all)
        
        # Print summary
        print("\nIncremental Extraction Complete")
        print("=" * 40)
        print(f"Processed: {results['processed_files']}/{results['total_files']} files")
        print(f"New gleanings: {results['new_gleanings']}")
        print(f"Updated gleanings: {results['updated_gleanings']}")
        print(f"Unchanged gleanings: {results['unchanged_gleanings']}")
        print(f"Execution time: {results['execution_time']:.1f}s")
        
        # Show overall statistics
        state_stats = extractor.state.get_statistics()
        print(f"\nSTATS: Total in system: {state_stats['total_gleanings']} gleanings")
        print(f"Active: {state_stats['status_breakdown'].get('active', 0)}")
        print(f"Hidden: {state_stats['status_breakdown'].get('hidden', 0)}")
        print(f"Deleted: {state_stats['status_breakdown'].get('deleted', 0)}")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()