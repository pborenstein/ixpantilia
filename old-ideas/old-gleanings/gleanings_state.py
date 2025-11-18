#!/usr/bin/env python3
"""
Gleanings State Management System

This module provides persistent state management for the gleanings system,
including user actions (hide/delete), file modification tracking, and 
incremental processing capabilities.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GleaningsState:
    """Manages persistent state for the gleanings system."""
    
    def __init__(self, state_file: str = "gleanings_state.json"):
        self.state_file = Path(__file__).parent / state_file
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file or create new state structure."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}. Creating new state.")
        
        # Default state structure
        return {
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "gleanings": {},  # id -> gleaning data with state
            "file_tracking": {},  # file_path -> {last_modified, last_processed}
            "user_actions": {},  # id -> {action, timestamp, reason}
            "settings": {
                "auto_hide_duplicates": False,
                "confidence_threshold": 0.1,
                "backup_count": 5
            }
        }
    
    def save_state(self) -> None:
        """Save current state to file."""
        self.state["last_updated"] = datetime.now().isoformat()
        
        # Create backup before saving
        self._create_backup()
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.info(f"State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise
    
    def _create_backup(self) -> None:
        """Create a backup of the current state file."""
        if not self.state_file.exists():
            return
            
        backup_dir = self.state_file.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"gleanings_state_{timestamp}.json"
        
        try:
            import shutil
            shutil.copy2(self.state_file, backup_file)
            
            # Clean up old backups
            backups = sorted(backup_dir.glob("gleanings_state_*.json"))
            max_backups = self.state["settings"]["backup_count"]
            for old_backup in backups[:-max_backups]:
                old_backup.unlink()
                
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
    
    def generate_id(self, gleaning: Dict[str, Any]) -> str:
        """Generate a unique ID for a gleaning based on URL and date."""
        # Use URL + date for uniqueness
        key = f"{gleaning['url']}:{gleaning['date']}"
        return hashlib.md5(key.encode('utf-8')).hexdigest()[:12]
    
    def add_gleaning(self, gleaning: Dict[str, Any]) -> str:
        """Add or update a gleaning in the state."""
        gleaning_id = self.generate_id(gleaning)
        
        # Enhanced gleaning data with state management
        enhanced_gleaning = {
            **gleaning,
            "id": gleaning_id,
            "user_status": "active",  # active, hidden, deleted, favorited
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "processing_state": "new"  # new, updated, unchanged
        }
        
        # Check if gleaning already exists
        if gleaning_id in self.state["gleanings"]:
            existing = self.state["gleanings"][gleaning_id]
            
            # Preserve user status and created_at
            enhanced_gleaning["user_status"] = existing.get("user_status", "active")
            enhanced_gleaning["created_at"] = existing.get("created_at", enhanced_gleaning["created_at"])
            
            # Check if content has changed
            content_fields = ["title", "url", "description", "category", "domain", "tags"]
            has_changed = any(
                existing.get(field) != enhanced_gleaning.get(field) 
                for field in content_fields
            )
            
            enhanced_gleaning["processing_state"] = "updated" if has_changed else "unchanged"
        
        self.state["gleanings"][gleaning_id] = enhanced_gleaning
        return gleaning_id
    
    def get_gleaning(self, gleaning_id: str) -> Optional[Dict[str, Any]]:
        """Get a gleaning by ID."""
        return self.state["gleanings"].get(gleaning_id)
    
    def get_all_gleanings(self, include_hidden: bool = False, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all gleanings, optionally filtering by status."""
        gleanings = []
        
        for gleaning in self.state["gleanings"].values():
            status = gleaning.get("user_status", "active")
            
            if status == "deleted" and not include_deleted:
                continue
            if status == "hidden" and not include_hidden:
                continue
                
            gleanings.append(gleaning)
        
        # Sort by date, then by timestamp
        return sorted(gleanings, key=lambda x: (x.get("date", ""), x.get("timestamp", "")))
    
    def update_user_status(self, gleaning_ids: List[str], status: str, reason: str = "") -> int:
        """Update user status for multiple gleanings."""
        updated_count = 0
        timestamp = datetime.now().isoformat()
        
        for gleaning_id in gleaning_ids:
            if gleaning_id in self.state["gleanings"]:
                old_status = self.state["gleanings"][gleaning_id].get("user_status", "active")
                self.state["gleanings"][gleaning_id]["user_status"] = status
                self.state["gleanings"][gleaning_id]["last_modified"] = timestamp
                
                # Record the user action
                self.state["user_actions"][f"{gleaning_id}_{timestamp}"] = {
                    "gleaning_id": gleaning_id,
                    "action": f"{old_status} -> {status}",
                    "timestamp": timestamp,
                    "reason": reason
                }
                
                updated_count += 1
        
        return updated_count
    
    def hide_gleanings(self, gleaning_ids: List[str], reason: str = "") -> int:
        """Hide gleanings."""
        return self.update_user_status(gleaning_ids, "hidden", reason)
    
    def delete_gleanings(self, gleaning_ids: List[str], reason: str = "") -> int:
        """Mark gleanings as deleted."""
        return self.update_user_status(gleaning_ids, "deleted", reason)
    
    def restore_gleanings(self, gleaning_ids: List[str], reason: str = "") -> int:
        """Restore gleanings to active status."""
        return self.update_user_status(gleaning_ids, "active", reason)
    
    def favorite_gleanings(self, gleaning_ids: List[str], reason: str = "") -> int:
        """Mark gleanings as favorited."""
        return self.update_user_status(gleaning_ids, "favorited", reason)
    
    def get_gleanings_by_domain(self, domain: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all gleanings from a specific domain."""
        all_gleanings = self.get_all_gleanings(include_hidden=include_hidden)
        return [g for g in all_gleanings if g.get("domain", "").lower() == domain.lower()]
    
    def get_gleanings_by_category(self, category: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all gleanings from a specific category."""
        all_gleanings = self.get_all_gleanings(include_hidden=include_hidden)
        return [g for g in all_gleanings if g.get("category", "").lower() == category.lower()]
    
    def get_gleanings_by_tag(self, tag: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all gleanings with a specific tag."""
        all_gleanings = self.get_all_gleanings(include_hidden=include_hidden)
        return [g for g in all_gleanings if tag.lower() in [t.lower() for t in g.get("tags", [])]]
    
    def get_gleanings_by_tags(self, tags: List[str], match_any: bool = True, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        Get all gleanings with specific tags.
        
        Args:
            tags: List of tags to search for
            match_any: If True, match gleanings with any of the tags. If False, match only gleanings with all tags.
            include_hidden: Whether to include hidden gleanings
        """
        all_gleanings = self.get_all_gleanings(include_hidden=include_hidden)
        
        if match_any:
            # Match gleanings that have any of the specified tags
            return [
                g for g in all_gleanings 
                if any(tag.lower() in [t.lower() for t in g.get("tags", [])] for tag in tags)
            ]
        else:
            # Match gleanings that have all of the specified tags
            return [
                g for g in all_gleanings 
                if all(tag.lower() in [t.lower() for t in g.get("tags", [])] for tag in tags)
            ]
    
    def track_file_processing(self, file_path: str, last_modified: float) -> None:
        """Track when a file was last processed."""
        self.state["file_tracking"][str(file_path)] = {
            "last_modified": last_modified,
            "last_processed": datetime.now().isoformat()
        }
    
    def get_modified_files(self, file_paths: List[str]) -> List[str]:
        """Get list of files that have been modified since last processing."""
        modified_files = []
        
        for file_path in file_paths:
            file_path_str = str(file_path)
            
            if not os.path.exists(file_path):
                continue
                
            current_mtime = os.path.getmtime(file_path)
            tracking_info = self.state["file_tracking"].get(file_path_str)
            
            if not tracking_info:
                # Never processed before
                modified_files.append(file_path)
            elif current_mtime > tracking_info["last_modified"]:
                # File has been modified
                modified_files.append(file_path)
        
        return modified_files
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the gleanings."""
        gleanings = self.state["gleanings"].values()
        
        status_counts = {}
        category_counts = {}
        domain_counts = {}
        tag_counts = {}
        processing_state_counts = {}
        
        for gleaning in gleanings:
            # Count by status
            status = gleaning.get("user_status", "active")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by category (only active items)
            if status in ["active", "favorited"]:
                category = gleaning.get("category", "Unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Count by domain
                domain = gleaning.get("domain", "Unknown")
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                
                # Count by tags
                tags = gleaning.get("tags", [])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Count by processing state
            proc_state = gleaning.get("processing_state", "unknown")
            processing_state_counts[proc_state] = processing_state_counts.get(proc_state, 0) + 1
        
        return {
            "total_gleanings": len(gleanings),
            "status_breakdown": status_counts,
            "category_breakdown": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)),
            "top_domains": dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "tag_breakdown": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
            "processing_states": processing_state_counts,
            "last_updated": self.state["last_updated"],
            "tracked_files": len(self.state["file_tracking"])
        }
    
    def migrate_from_legacy(self, legacy_json_file: str) -> int:
        """Migrate data from legacy gleanings_data.json format."""
        legacy_path = Path(__file__).parent / legacy_json_file
        
        if not legacy_path.exists():
            logger.info(f"No legacy file found at {legacy_path}")
            return 0
        
        try:
            with open(legacy_path, 'r', encoding='utf-8') as f:
                legacy_data = json.load(f)
            
            migrated_count = 0
            for gleaning in legacy_data:
                self.add_gleaning(gleaning)
                migrated_count += 1
            
            logger.info(f"Migrated {migrated_count} gleanings from legacy format")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Failed to migrate legacy data: {e}")
            return 0
    
    # Media management methods
    def generate_media_id(self, media_item: Dict[str, Any]) -> str:
        """Generate a unique ID for a media item based on title, type and date."""
        # Use title + type + date for uniqueness
        key = f"{media_item['title'].lower()}:{media_item['type']}:{media_item['date']}"
        return "media_" + hashlib.md5(key.encode('utf-8')).hexdigest()[:10]
    
    def add_media(self, media_item: Dict[str, Any]) -> str:
        """Add or update a media item in the state."""
        media_id = self.generate_media_id(media_item)
        
        # Initialize media section if it doesn't exist
        if "media" not in self.state:
            self.state["media"] = {}
        
        # Enhanced media item with state management
        enhanced_media = {
            **media_item,
            "id": media_id,
            "user_status": "active",  # active, hidden, deleted, favorited
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "processing_state": "new"  # new, updated, unchanged
        }
        
        # Check if media item already exists
        if media_id in self.state["media"]:
            existing = self.state["media"][media_id]
            
            # Preserve user status and created_at
            enhanced_media["user_status"] = existing.get("user_status", "active")
            enhanced_media["created_at"] = existing.get("created_at", enhanced_media["created_at"])
            
            # Check if content has changed
            content_fields = ["title", "year", "author", "status", "description", "tags"]
            has_changed = any(
                existing.get(field) != enhanced_media.get(field) 
                for field in content_fields
            )
            
            enhanced_media["processing_state"] = "updated" if has_changed else "unchanged"
        
        self.state["media"][media_id] = enhanced_media
        return media_id
    
    def get_media(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get a media item by ID."""
        return self.state.get("media", {}).get(media_id)
    
    def get_all_media(self, include_hidden: bool = False, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all media items, optionally filtering by status."""
        media_items = []
        
        for media_item in self.state.get("media", {}).values():
            status = media_item.get("user_status", "active")
            
            if status == "deleted" and not include_deleted:
                continue
            if status == "hidden" and not include_hidden:
                continue
                
            media_items.append(media_item)
        
        # Sort by date, then by title
        return sorted(media_items, key=lambda x: (x.get("date", ""), x.get("title", "")))
    
    def get_media_by_type(self, media_type: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all media items of a specific type (movie, book, music, etc.)."""
        all_media = self.get_all_media(include_hidden=include_hidden)
        return [m for m in all_media if m.get("type", "").lower() == media_type.lower()]
    
    def get_media_by_status(self, status: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all media items with a specific status (to-watch, completed, etc.)."""
        all_media = self.get_all_media(include_hidden=include_hidden)
        return [m for m in all_media if m.get("status", "").lower() == status.lower()]
    
    def get_media_by_tag(self, tag: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """Get all media items with a specific tag."""
        all_media = self.get_all_media(include_hidden=include_hidden)
        return [m for m in all_media if tag.lower() in [t.lower() for t in m.get("tags", [])]]
    
    def update_media_user_status(self, media_ids: List[str], status: str, reason: str = "") -> int:
        """Update user status for multiple media items."""
        updated_count = 0
        timestamp = datetime.now().isoformat()
        
        for media_id in media_ids:
            if media_id in self.state.get("media", {}):
                old_status = self.state["media"][media_id].get("user_status", "active")
                self.state["media"][media_id]["user_status"] = status
                self.state["media"][media_id]["last_modified"] = timestamp
                
                # Record the user action
                self.state["user_actions"][f"{media_id}_{timestamp}"] = {
                    "media_id": media_id,
                    "action": f"{old_status} -> {status}",
                    "timestamp": timestamp,
                    "reason": reason
                }
                
                updated_count += 1
        
        return updated_count
    
    def hide_media(self, media_ids: List[str], reason: str = "") -> int:
        """Hide media items."""
        return self.update_media_user_status(media_ids, "hidden", reason)
    
    def delete_media(self, media_ids: List[str], reason: str = "") -> int:
        """Mark media items as deleted."""
        return self.update_media_user_status(media_ids, "deleted", reason)
    
    def restore_media(self, media_ids: List[str], reason: str = "") -> int:
        """Restore media items to active status."""
        return self.update_media_user_status(media_ids, "active", reason)

def create_state_manager(state_file: str = "gleanings_state.json") -> GleaningsState:
    """Factory function to create a state manager instance."""
    return GleaningsState(state_file)

if __name__ == "__main__":
    # Simple test/demo
    state = create_state_manager()
    
    # Example usage
    sample_gleaning = {
        "title": "Test Article",
        "url": "https://example.com/test",
        "domain": "example.com",
        "timestamp": "12:00",
        "description": "A test article",
        "date": "2025-01-01",
        "source_file": "/path/to/file.md",
        "category": "Test",
        "tags": ["test", "example"]
    }
    
    gleaning_id = state.add_gleaning(sample_gleaning)
    print(f"Added gleaning with ID: {gleaning_id}")
    
    stats = state.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
    
    state.save_state()
    print("State saved successfully")