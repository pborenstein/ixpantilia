#!/usr/bin/env python3
"""
State-Aware Gleanings Index Generator

Enhanced index generator that works with the state management system:
- Respects user preferences (hidden/deleted items)
- Shows only active gleanings by default
- Includes management tips and statistics
- Backward compatible with existing index format
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import argparse

# Import the state management system
from gleanings_state import create_state_manager

def format_gleaning_entry(gleaning, include_date=True):
    """Format a single gleaning entry for markdown output."""
    title = gleaning['title']
    url = gleaning['url']
    domain = gleaning['domain']
    timestamp = gleaning['timestamp']
    description = gleaning['description']
    date = gleaning['date']
    
    # Create the main link
    entry = f"- [{title}]({url})"
    
    if include_date:
        entry += f" | {date} [{timestamp}]"
    else:
        entry += f" [{timestamp}]"
    
    # Add description if available
    if description.strip():
        desc_clean = description.replace('\n', ' ').strip()
        if len(desc_clean) > 150:
            desc_clean = desc_clean[:150] + "..."
        entry += f"\n  > {desc_clean}"
    
    # Add domain if it's not obvious from the title
    if domain and domain not in title.lower():
        entry += f"\n  > *{domain}*"
    
    return entry

def format_media_entry(media_item, include_date=True):
    """Format a single media entry for markdown output."""
    title = media_item['title']
    media_type = media_item['type']
    status = media_item['status']
    date = media_item['date']
    timestamp = media_item.get('timestamp', 'unknown')
    year = media_item.get('year', '')
    author = media_item.get('author', '')
    description = media_item.get('description', '')
    tags = media_item.get('tags', [])
    
    # Create the main entry
    if year:
        display_title = f"{title} ({year})"
    else:
        display_title = title
    
    # Format as wiki link for Obsidian compatibility
    entry = f"- **[[{display_title}]]**"
    
    # Add status badge (context-aware based on media type)
    if media_type == 'movie':
        status_badge = {
            'to-watch': 'To Watch',
            'watching': 'Watching', 
            'completed': 'Watched',
            'referenced': 'Referenced'
        }
    elif media_type == 'book':
        status_badge = {
            'to-read': 'To Read',
            'reading': 'Reading',
            'completed': 'Read',
            'referenced': 'Referenced'
        }
    elif media_type == 'music':
        status_badge = {
            'to-listen': 'To Listen',
            'listening': 'Listening',
            'completed': 'Listened',
            'referenced': 'Referenced'
        }
    else:
        status_badge = {
            'completed': 'Completed',
            'referenced': 'Referenced'
        }
    
    badge = status_badge.get(status, status.replace('-', ' ').title())
    entry += f" - {badge}"
    
    if include_date:
        entry += f" | {date}"
        if timestamp != 'unknown':
            entry += f" [{timestamp}]"
    
    # Add author for books
    if author:
        entry += f"\n  > Author: {author}"
    
    # Add description if available and not just author info
    if description.strip() and not description.startswith('Author:'):
        desc_clean = description.replace('\n', ' ').strip()
        if len(desc_clean) > 100:
            desc_clean = desc_clean[:100] + "..."
        entry += f"\n  > {desc_clean}"
    
    # Add tags
    if tags:
        tags_str = " ".join(tags)
        entry += f"\n  > Tags: {tags_str}"
    
    return entry

def generate_index_content(state_manager, include_management_info=True):
    """Generate the complete index content."""
    # Get active gleanings and media
    gleanings = state_manager.get_all_gleanings(include_hidden=False, include_deleted=False)
    media_items = state_manager.get_all_media(include_hidden=False, include_deleted=False)
    
    if not gleanings and not media_items:
        return "# Gleanings Index\n\nNo active gleanings or media found.\n"
    
    # Get statistics
    stats = state_manager.get_statistics()
    
    content = []
    content.append("# Gleanings Index")
    content.append("")
    content.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    content.append(f"*Total active gleanings: {len(gleanings)} | Media items: {len(media_items)}*")
    
    if include_management_info:
        content.append("")
        content.append("**Management**: Use `python manage_gleanings.py` to hide/delete unwanted items")
        
        # Show stats if there are hidden/deleted items
        hidden_count = stats['status_breakdown'].get('hidden', 0)
        deleted_count = stats['status_breakdown'].get('deleted', 0)
        if hidden_count > 0 or deleted_count > 0:
            content.append(f"**Hidden**: {hidden_count} | **Deleted**: {deleted_count}")
    
    content.append("")
    content.append("---")
    content.append("")
    
    # Organize by category
    by_category = defaultdict(list)
    for gleaning in gleanings:
        category = gleaning.get('category', 'Miscellaneous')
        by_category[category].append(gleaning)
    
    # Sort categories by count (descending)
    sorted_categories = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Generate category sections
    content.append("## By Category")
    content.append("")
    
    for category, cat_gleanings in sorted_categories:
        content.append(f"### {category} ({len(cat_gleanings)})")
        content.append("")
        
        # Sort by date (newest first)
        cat_gleanings.sort(key=lambda x: (x.get('date', ''), x.get('timestamp', '')), reverse=True)
        
        for gleaning in cat_gleanings:
            content.append(format_gleaning_entry(gleaning, include_date=True))
            content.append("")
    
    content.append("---")
    content.append("")
    
    # Recent gleanings section
    content.append("## Recent Gleanings")
    content.append("")
    
    # Get last 30 gleanings
    recent_gleanings = sorted(gleanings, key=lambda x: (x.get('date', ''), x.get('timestamp', '')), reverse=True)[:30]
    
    for gleaning in recent_gleanings:
        content.append(format_gleaning_entry(gleaning, include_date=True))
        content.append("")
    
    content.append("---")
    content.append("")
    
    # Top domains section
    content.append("## Top Domains")
    content.append("")
    
    domain_counts = Counter(g.get('domain', 'unknown') for g in gleanings)
    top_domains = domain_counts.most_common(15)
    
    for domain, count in top_domains:
        content.append(f"- **{domain}**: {count} gleanings")
    
    content.append("")
    content.append("---")
    content.append("")
    
    # Media sections
    if media_items:
        content.append("# Media")
        content.append("")
        
        # Organize media by type and status
        media_by_type = defaultdict(lambda: defaultdict(list))
        for media in media_items:
            media_type = media.get('type', 'unknown').title()
            status = media.get('status', 'unknown')
            media_by_type[media_type][status].append(media)
        
        # Generate sections for each media type
        for media_type in sorted(media_by_type.keys()):
            type_media = media_by_type[media_type]
            total_count = sum(len(status_items) for status_items in type_media.values())
            
            content.append(f"## {media_type}s ({total_count})")
            content.append("")
            
            # Order statuses logically
            status_order = ['to-watch', 'to-read', 'to-listen', 'watching', 'reading', 'listening', 'completed', 'referenced']
            ordered_statuses = []
            
            # Add existing statuses in preferred order
            for status in status_order:
                if status in type_media:
                    ordered_statuses.append(status)
            
            # Add any other statuses not in the standard order
            for status in type_media.keys():
                if status not in ordered_statuses:
                    ordered_statuses.append(status)
            
            for status in ordered_statuses:
                status_items = type_media[status]
                if status_items:
                    status_title = {
                        'to-watch': 'To Watch',
                        'watching': 'Currently Watching',
                        'completed': 'Completed',
                        'to-read': 'To Read',
                        'reading': 'Currently Reading',
                        'to-listen': 'To Listen',
                        'listening': 'Currently Listening',
                        'referenced': 'Referenced'
                    }.get(status, status.replace('-', ' ').title())
                    
                    content.append(f"### {status_title} ({len(status_items)})")
                    content.append("")
                    
                    # Sort by date (newest first)
                    status_items.sort(key=lambda x: (x.get('date', ''), x.get('title', '')), reverse=True)
                    
                    for media in status_items:
                        content.append(format_media_entry(media, include_date=True))
                        content.append("")
                    
        content.append("---")
        content.append("")
    
    # Monthly breakdown
    content.append("## Monthly Breakdown")
    content.append("")
    
    monthly_counts = defaultdict(int)
    for gleaning in gleanings:
        date_str = gleaning.get('date', '')
        if date_str and len(date_str) >= 7:  # YYYY-MM format
            month_key = date_str[:7]
            monthly_counts[month_key] += 1
    
    sorted_months = sorted(monthly_counts.items(), reverse=True)
    for month, count in sorted_months:
        content.append(f"- **{month}**: {count} gleanings")
    
    return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(description='Generate state-aware gleanings index')
    parser.add_argument('--state-file', default='gleanings_state.json',
                       help='State file path')
    parser.add_argument('--output', default='Gleanings Index.md',
                       help='Output markdown file')
    parser.add_argument('--no-management-info', action='store_true',
                       help='Exclude management information from index')
    
    args = parser.parse_args()
    
    try:
        # Create state manager
        state_manager = create_state_manager(args.state_file)
        
        # Generate index content
        content = generate_index_content(
            state_manager, 
            include_management_info=not args.no_management_info
        )
        
        # Write to file
        output_path = Path(__file__).parent / args.output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"SUCCESS: Generated state-aware index: {output_path}")
        
        # Show statistics
        stats = state_manager.get_statistics()
        print(f"STATS: Active gleanings: {stats['status_breakdown'].get('active', 0)}")
        print(f"STATS: Hidden gleanings: {stats['status_breakdown'].get('hidden', 0)}")
        print(f"STATS: Deleted gleanings: {stats['status_breakdown'].get('deleted', 0)}")
        
    except Exception as e:
        print(f"ERROR: Error generating index: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())