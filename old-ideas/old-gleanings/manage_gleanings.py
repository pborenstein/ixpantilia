#!/usr/bin/env python3
"""
Gleanings Management Interface

Interactive command-line interface for managing gleanings:
- Hide/show gleanings
- Delete/restore gleanings  
- Bulk operations by domain or category
- Search and filter operations
- Undo capability
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime

# Import the state management system
from gleanings_state import create_state_manager

class GleaningsManager:
    """Interactive manager for gleaning operations."""
    
    def __init__(self, state_file: str = "gleanings_state.json"):
        self.state = create_state_manager(state_file)
        
    def search_gleanings(self, query: str, include_hidden: bool = False, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Search gleanings by title, description, URL, or domain."""
        all_gleanings = self.state.get_all_gleanings(include_hidden=include_hidden, include_deleted=include_deleted)
        query_lower = query.lower()
        
        matching = []
        for gleaning in all_gleanings:
            # Search in multiple fields
            searchable_text = " ".join([
                gleaning.get('title', ''),
                gleaning.get('description', ''),
                gleaning.get('url', ''),
                gleaning.get('domain', ''),
                gleaning.get('category', '')
            ]).lower()
            
            if query_lower in searchable_text:
                matching.append(gleaning)
        
        return matching
    
    def list_gleanings(self, filter_by: str = None, filter_value: str = None, 
                      include_hidden: bool = False, include_deleted: bool = False,
                      limit: int = None) -> List[Dict[str, Any]]:
        """List gleanings with optional filtering."""
        if filter_by == "domain" and filter_value:
            gleanings = self.state.get_gleanings_by_domain(filter_value, include_hidden=include_hidden)
        elif filter_by == "category" and filter_value:
            gleanings = self.state.get_gleanings_by_category(filter_value, include_hidden=include_hidden)
        else:
            gleanings = self.state.get_all_gleanings(include_hidden=include_hidden, include_deleted=include_deleted)
        
        if limit:
            gleanings = gleanings[:limit]
            
        return gleanings
    
    def display_gleanings(self, gleanings: List[Dict[str, Any]], show_ids: bool = True, 
                         show_status: bool = True) -> None:
        """Display gleanings in a readable format."""
        if not gleanings:
            print("No gleanings found.")
            return
        
        for i, gleaning in enumerate(gleanings, 1):
            # Status indicator
            status = gleaning.get('user_status', 'active')
            status_icon = {
                'active': '[A]',
                'hidden': '[H]',
                'deleted': '[D]',
                'favorited': '[F]'
            }.get(status, '[?]')
            
            # Format output
            title = gleaning.get('title', 'No title')[:80]
            domain = gleaning.get('domain', 'unknown')
            date = gleaning.get('date', 'unknown')
            
            print(f"{i:3d}. {status_icon if show_status else ''} {title}")
            print(f"     {domain} | {date}")
            
            if show_ids:
                print(f"     ID: {gleaning.get('id', 'unknown')}")
            
            # Show description if available and not too long
            desc = gleaning.get('description', '').strip()
            if desc and len(desc) < 100:
                print(f"     > {desc}")
            
            print()
    
    def get_gleanings_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get gleanings by their IDs."""
        gleanings = []
        for gleaning_id in ids:
            gleaning = self.state.get_gleaning(gleaning_id)
            if gleaning:
                gleanings.append(gleaning)
        return gleanings
    
    def hide_gleanings_interactive(self, ids: List[str], reason: str = "") -> None:
        """Hide gleanings with confirmation."""
        gleanings = self.get_gleanings_by_ids(ids)
        
        if not gleanings:
            print("No valid gleanings found with those IDs.")
            return
        
        print(f"\nAbout to hide {len(gleanings)} gleaning(s):")
        self.display_gleanings(gleanings, show_ids=False, show_status=False)
        
        if not reason:
            reason = input("Reason for hiding (optional): ").strip()
        
        confirm = input(f"Hide these {len(gleanings)} gleanings? (y/N): ").strip().lower()
        if confirm == 'y':
            count = self.state.hide_gleanings(ids, reason)
            self.state.save_state()
            print(f"SUCCESS: Hidden {count} gleanings")
        else:
            print("CANCELLED: Operation cancelled")
    
    def delete_gleanings_interactive(self, ids: List[str], reason: str = "") -> None:
        """Delete gleanings with confirmation."""
        gleanings = self.get_gleanings_by_ids(ids)
        
        if not gleanings:
            print("No valid gleanings found with those IDs.")
            return
        
        print(f"\nAbout to mark {len(gleanings)} gleaning(s) as deleted:")
        self.display_gleanings(gleanings, show_ids=False, show_status=False)
        
        if not reason:
            reason = input("Reason for deleting (optional): ").strip()
        
        confirm = input(f"Delete these {len(gleanings)} gleanings? (y/N): ").strip().lower()
        if confirm == 'y':
            count = self.state.delete_gleanings(ids, reason)
            self.state.save_state()
            print(f"SUCCESS: Deleted {count} gleanings")
        else:
            print("CANCELLED: Operation cancelled")
    
    def restore_gleanings_interactive(self, ids: List[str], reason: str = "") -> None:
        """Restore gleanings with confirmation."""
        gleanings = self.get_gleanings_by_ids(ids)
        
        if not gleanings:
            print("No valid gleanings found with those IDs.")
            return
        
        print(f"\nAbout to restore {len(gleanings)} gleaning(s):")
        self.display_gleanings(gleanings, show_ids=False, show_status=True)
        
        if not reason:
            reason = input("Reason for restoring (optional): ").strip()
        
        confirm = input(f"Restore these {len(gleanings)} gleanings? (y/N): ").strip().lower()
        if confirm == 'y':
            count = self.state.restore_gleanings(ids, reason)
            self.state.save_state()
            print(f"SUCCESS: Restored {count} gleanings")
        else:
            print("CANCELLED: Operation cancelled")
    
    def bulk_operations_menu(self) -> None:
        """Interactive menu for bulk operations."""
        print("\nBulk Operations")
        print("1. Hide all gleanings from a domain")
        print("2. Hide all gleanings from a category") 
        print("3. Delete all gleanings from a domain")
        print("4. Delete all gleanings from a category")
        print("5. Restore hidden gleanings from a domain")
        print("6. Restore hidden gleanings from a category")
        print("0. Back to main menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            domain = input("Domain to hide from: ").strip()
            gleanings = self.state.get_gleanings_by_domain(domain)
            if gleanings:
                ids = [g['id'] for g in gleanings if g.get('user_status') == 'active']
                if ids:
                    self.hide_gleanings_interactive(ids, f"Bulk hide from domain: {domain}")
                else:
                    print("No active gleanings found for that domain.")
            else:
                print("No gleanings found for that domain.")
        
        elif choice == '2':
            category = input("Category to hide from: ").strip()
            gleanings = self.state.get_gleanings_by_category(category)
            if gleanings:
                ids = [g['id'] for g in gleanings if g.get('user_status') == 'active']
                if ids:
                    self.hide_gleanings_interactive(ids, f"Bulk hide from category: {category}")
                else:
                    print("No active gleanings found for that category.")
            else:
                print("No gleanings found for that category.")
        
        elif choice == '3':
            domain = input("Domain to delete from: ").strip()
            gleanings = self.state.get_gleanings_by_domain(domain)
            if gleanings:
                ids = [g['id'] for g in gleanings if g.get('user_status') in ['active', 'hidden']]
                if ids:
                    self.delete_gleanings_interactive(ids, f"Bulk delete from domain: {domain}")
                else:
                    print("No active/hidden gleanings found for that domain.")
            else:
                print("No gleanings found for that domain.")
        
        # Add more bulk operations as needed...
        
        elif choice == '0':
            return
        else:
            print("Invalid choice.")
    
    def show_statistics(self) -> None:
        """Display comprehensive statistics."""
        stats = self.state.get_statistics()
        
        print("\nGleanings Statistics")
        print("=" * 30)
        print(f"Total gleanings: {stats['total_gleanings']}")
        print(f"Last updated: {stats['last_updated']}")
        print(f"Tracked files: {stats['tracked_files']}")
        
        print("\nStatus Breakdown:")
        for status, count in stats['status_breakdown'].items():
            print(f"  {status}: {count}")
        
        print("\nTop Categories:")
        for category, count in list(stats['category_breakdown'].items())[:10]:
            print(f"  {category}: {count}")
        
        print("\nTop Domains:")
        for domain, count in list(stats['top_domains'].items())[:10]:
            print(f"  {domain}: {count}")
    
    def interactive_menu(self) -> None:
        """Main interactive menu."""
        while True:
            print("\nGleanings Manager")
            print("=" * 30)
            print("1. List active gleanings")
            print("2. List hidden gleanings")
            print("3. List deleted gleanings")
            print("4. Search gleanings")
            print("5. Hide gleanings by ID")
            print("6. Delete gleanings by ID")
            print("7. Restore gleanings by ID")
            print("8. Bulk operations")
            print("9. Show statistics")
            print("0. Exit")
            
            choice = input("\nChoice: ").strip()
            
            try:
                if choice == '1':
                    gleanings = self.list_gleanings(limit=20)
                    print(f"\nActive Gleanings (showing first 20)")
                    self.display_gleanings(gleanings)
                
                elif choice == '2':
                    gleanings = self.list_gleanings(include_hidden=True, limit=20)
                    hidden = [g for g in gleanings if g.get('user_status') == 'hidden']
                    print(f"\nHidden Gleanings (showing first 20)")
                    self.display_gleanings(hidden)
                
                elif choice == '3':
                    gleanings = self.list_gleanings(include_deleted=True, limit=20)
                    deleted = [g for g in gleanings if g.get('user_status') == 'deleted']
                    print(f"\nDeleted Gleanings (showing first 20)")
                    self.display_gleanings(deleted)
                
                elif choice == '4':
                    query = input("Search query: ").strip()
                    if query:
                        gleanings = self.search_gleanings(query, include_hidden=True, include_deleted=True)
                        print(f"\nSearch Results for '{query}'")
                        self.display_gleanings(gleanings[:20])  # Limit to 20 results
                
                elif choice == '5':
                    ids_input = input("Enter gleaning IDs (comma-separated): ").strip()
                    if ids_input:
                        ids = [id.strip() for id in ids_input.split(',')]
                        self.hide_gleanings_interactive(ids)
                
                elif choice == '6':
                    ids_input = input("Enter gleaning IDs (comma-separated): ").strip()
                    if ids_input:
                        ids = [id.strip() for id in ids_input.split(',')]
                        self.delete_gleanings_interactive(ids)
                
                elif choice == '7':
                    ids_input = input("Enter gleaning IDs (comma-separated): ").strip()
                    if ids_input:
                        ids = [id.strip() for id in ids_input.split(',')]
                        self.restore_gleanings_interactive(ids)
                
                elif choice == '8':
                    self.bulk_operations_menu()
                
                elif choice == '9':
                    self.show_statistics()
                
                elif choice == '0':
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"ERROR: {e}")

def main():
    parser = argparse.ArgumentParser(description='Manage gleanings interactively')
    parser.add_argument('--state-file', default='gleanings_state.json',
                       help='State file path')
    parser.add_argument('--list', choices=['active', 'hidden', 'deleted', 'all'],
                       help='List gleanings by status')
    parser.add_argument('--search', type=str,
                       help='Search gleanings')
    parser.add_argument('--hide', type=str, nargs='+',
                       help='Hide gleanings by ID')
    parser.add_argument('--delete', type=str, nargs='+',
                       help='Delete gleanings by ID')
    parser.add_argument('--restore', type=str, nargs='+',
                       help='Restore gleanings by ID')
    parser.add_argument('--reason', type=str,
                       help='Reason for the action')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics')
    parser.add_argument('--interactive', action='store_true',
                       help='Launch interactive mode')
    
    args = parser.parse_args()
    
    try:
        manager = GleaningsManager(args.state_file)
        
        # Handle command-line operations
        if args.stats:
            manager.show_statistics()
        
        elif args.list:
            include_hidden = args.list in ['hidden', 'all']
            include_deleted = args.list in ['deleted', 'all']
            gleanings = manager.list_gleanings(include_hidden=include_hidden, include_deleted=include_deleted)
            
            if args.list == 'hidden':
                gleanings = [g for g in gleanings if g.get('user_status') == 'hidden']
            elif args.list == 'deleted':
                gleanings = [g for g in gleanings if g.get('user_status') == 'deleted']
            elif args.list == 'active':
                gleanings = [g for g in gleanings if g.get('user_status') == 'active']
            
            manager.display_gleanings(gleanings)
        
        elif args.search:
            gleanings = manager.search_gleanings(args.search, include_hidden=True, include_deleted=True)
            print(f"Search results for '{args.search}':")
            manager.display_gleanings(gleanings)
        
        elif args.hide:
            manager.hide_gleanings_interactive(args.hide, args.reason or "")
        
        elif args.delete:
            manager.delete_gleanings_interactive(args.delete, args.reason or "")
        
        elif args.restore:
            manager.restore_gleanings_interactive(args.restore, args.reason or "")
        
        else:
            # Default to interactive mode
            manager.interactive_menu()
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()