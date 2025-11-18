#!/usr/bin/env python3
"""
Gleanings Extraction Functions

Core functions for extracting gleanings from daily notes.
Extracted from legacy _attic/extract_gleanings.py to support current system.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse


def simple_yaml_parse(file_path):
    """Simple YAML parser for basic nested structures with list support."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    result = {}
    current_section = None
    current_subsection = None
    current_list_key = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        # Count leading spaces for nesting level
        indent = len(line) - len(line.lstrip())
        
        # Handle list items (lines starting with -)
        if stripped.startswith('- '):
            list_item = stripped[2:].strip()
            if current_section and current_subsection and current_list_key:
                # We're in a list under a subsection
                if isinstance(result[current_section], dict) and isinstance(result[current_section].get(current_subsection), dict):
                    if current_list_key not in result[current_section][current_subsection]:
                        result[current_section][current_subsection][current_list_key] = []
                    result[current_section][current_subsection][current_list_key].append(list_item)
            continue
            
        # Handle key-value pairs
        if ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if indent == 0:  # Top level
                current_section = key
                current_subsection = None
                current_list_key = None
                if value:
                    result[current_section] = value
                else:
                    result[current_section] = {}
            elif indent <= 2 and current_section:  # Second level
                current_subsection = key
                current_list_key = None
                if value:
                    if isinstance(result[current_section], dict):
                        # Try to parse as number if it's just digits
                        if value.isdigit():
                            result[current_section][current_subsection] = int(value)
                        elif value.replace('.', '').isdigit() and value.count('.') == 1:
                            # Handle decimal numbers
                            result[current_section][current_subsection] = float(value)
                        else:
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            result[current_section][current_subsection] = value
                else:
                    # Empty value means either a dict or list will follow
                    if isinstance(result[current_section], dict):
                        result[current_section][current_subsection] = {}
            elif indent > 2 and current_section and current_subsection:  # Third level
                current_list_key = key
                if isinstance(result[current_section], dict) and isinstance(result[current_section].get(current_subsection), dict):
                    if value:
                        # Try to parse as number or keep as string
                        if value.isdigit():
                            result[current_section][current_subsection][key] = int(value)
                        elif value.replace('.', '').isdigit() and value.count('.') == 1:
                            # Handle decimal numbers
                            result[current_section][current_subsection][key] = float(value)
                        else:
                            result[current_section][current_subsection][key] = value
                    else:
                        # No value means a list will follow
                        result[current_section][current_subsection][key] = []
    
    return result


def load_categories_config(config_path=None):
    """Load categories configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent / 'categories.yaml'
    
    try:
        config = simple_yaml_parse(config_path)
        return config
    except Exception as e:
        print(f"Warning: Could not load categories config from {config_path}: {e}")
        print("Falling back to basic categorization")
        return None


def categorize_gleaning_with_config(gleaning, config):
    """Categorize a gleaning using the configuration file with confidence scoring."""
    if not config:
        return categorize_gleaning_fallback(gleaning)
    
    domain = gleaning['domain'].lower()
    title = gleaning['title'].lower()
    description = gleaning['description'].lower()
    url = gleaning['url'].lower()
    
    # Combine all text for keyword matching
    all_text = f"{title} {description} {url}"
    
    # Store matches with confidence scores
    category_scores = {}
    
    # Sort categories by priority (highest first)
    categories = config.get('categories', {})
    sorted_categories = sorted(categories.items(), 
                             key=lambda x: x[1].get('priority', 0), reverse=True)
    
    for category_name, category_info in sorted_categories:
        score = 0
        matches = []
        domain_matches = []
        keyword_matches = []
        
        # Check domain matches (higher weight)
        domains = category_info.get('domains', [])
        for domain_pattern in domains:
            if domain_pattern.lower() in domain:
                score += 3
                domain_matches.append(domain_pattern)
                matches.append(f"domain:{domain_pattern}")
        
        # Check keyword matches in all text
        keywords = category_info.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in all_text:
                score += 1
                keyword_matches.append(keyword)
                matches.append(f"keyword:{keyword}")
        
        # Only add to scores if we have matches
        if score > 0:
            total_possible = len(domains) * 3 + len(keywords)
            confidence = min(score / max(total_possible * 0.1, 1), 1.0)  # Cap at 100%
            
            category_scores[category_name] = {
                'score': score,
                'confidence': confidence,
                'domain_matches': domain_matches,
                'keyword_matches': keyword_matches,
                'matches': matches
            }
    
    # Return the category with the highest score
    if category_scores:
        best_category = max(category_scores.keys(), key=lambda k: category_scores[k]['score'])
        confidence_threshold = config.get('analysis', {}).get('confidence_threshold', 0.1)
        
        if category_scores[best_category]['confidence'] >= confidence_threshold:
            return best_category
    
    # Fallback to Miscellaneous if no good matches
    return 'Miscellaneous'


def categorize_gleaning_fallback(gleaning):
    """Fallback categorization for when config file is not available."""
    domain = gleaning['domain'].lower()
    title = gleaning['title'].lower()
    description = gleaning['description'].lower()
    
    # Basic fallback rules
    if 'github.com' in domain or 'code' in title + description:
        return 'Tech/Development'
    elif any(term in title + description for term in ['ai', 'llm', 'claude', 'gpt']):
        return 'AI/LLM'
    elif 'wikipedia.org' in domain:
        return 'Reference/Wikipedia'
    elif any(term in domain for term in ['youtube.com', 'm.youtube.com']):
        return 'Video/YouTube'
    else:
        return 'Miscellaneous'


def extract_gleanings_from_file(file_path):
    """Extract gleanings section from a single daily note file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    # Extract the date from filename
    filename = Path(file_path).stem
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if not date_match:
        print(f"Could not extract date from filename: {filename}")
        return []
    
    date_str = date_match.group(1)
    
    # Find the Gleanings section
    gleanings_pattern = r'## Gleanings\s*\n(.*?)(?=\n##|\n---|\Z)'
    gleanings_match = re.search(gleanings_pattern, content, re.DOTALL)
    
    if not gleanings_match:
        return []
    
    gleanings_content = gleanings_match.group(1)
    
    # Extract individual gleaning items
    # Support multiple patterns:
    # - [title](url) [timestamp] description
    # - [title](url) - description [timestamp]
    # - * [title](url) [timestamp] description
    # - naked URLs: https://example.com
    # - minimal formatting: - https://example.com
    patterns = [
        r'[-*] \[(.*?)\]\((.*?)\)\s*\[([^\]]+)\](.*?)(?=\n[-*] |\n\n|\Z)',  # Main pattern
        r'[-*] \[(.*?)\]\((.*?)\)\s*-\s*(.*?)\[([^\]]+)\]',  # Alt pattern with dash
        r'[-*] \[(.*?)\]\((.*?)\)(?:\s*\[([^\]]+)\])?\s*(.*?)(?=\n[-*] |\n\n|\Z)',  # Optional timestamp
        r'[-*] (https?://[^\s]+)(?:\s*\[([^\]]+)\])?\s*(.*?)(?=\n[-*] |\n\n|\Z)',  # Bullet + naked URL
        r'^(https?://[^\s]+)(?:\s*\[([^\]]+)\])?\s*(.*?)(?=\n|\Z)'  # Naked URL (line start)
    ]
    
    gleanings = []
    
    # Try each pattern and collect all matches (don't break after first match)
    for pattern_idx, pattern in enumerate(patterns):
        matches = list(re.finditer(pattern, gleanings_content, re.DOTALL | re.MULTILINE))
        for match in matches:
            groups = match.groups()
            
            # Handle different pattern types
            if pattern_idx <= 2:  # Traditional markdown link patterns
                title = groups[0].strip() if groups[0] else ''
                url = groups[1].strip() if groups[1] else ''
                
                # Handle different group arrangements based on pattern
                if len(groups) == 4 and groups[2] and ':' in groups[2]:  # timestamp in group 3
                    timestamp = groups[2].strip()
                    description = groups[3].strip() if groups[3] else ''
                elif len(groups) == 4:  # description then timestamp
                    description = groups[2].strip() if groups[2] else ''
                    timestamp = groups[3].strip() if groups[3] else ''
                else:
                    timestamp = groups[2].strip() if len(groups) > 2 and groups[2] else 'unknown'
                    description = groups[3].strip() if len(groups) > 3 and groups[3] else ''
            
            else:  # Naked URL patterns (patterns 3 and 4)
                url = groups[0].strip() if groups[0] else ''
                # Try to extract title from URL or use URL as title
                title = url
                try:
                    parsed = urlparse(url)
                    if parsed.netloc:
                        title = parsed.netloc + (parsed.path[:30] + '...' if len(parsed.path) > 30 else parsed.path)
                except:
                    title = url[:50] + '...' if len(url) > 50 else url
                
                # Handle timestamp and description for naked URLs
                timestamp = groups[1].strip() if len(groups) > 1 and groups[1] else 'unknown'
                description = groups[2].strip() if len(groups) > 2 and groups[2] else ''
            
            # Clean up description - remove leading > characters and whitespace
            description_lines = []
            for line in description.split('\n'):
                cleaned_line = line.strip()
                if cleaned_line.startswith('>'):
                    cleaned_line = cleaned_line[1:].strip()
                if cleaned_line:
                    description_lines.append(cleaned_line)
            
            description = '\n'.join(description_lines)
            
            # Extract domain from URL
            try:
                domain = urlparse(url).netloc
                if not domain:  # Empty netloc
                    domain = "unknown"
            except Exception as e:
                print(f"  Warning: Error parsing URL {url}: {e}")
                domain = "unknown"
            
            # Skip if no URL found
            if not url:
                continue
            
            # Skip duplicates (same URL from same date)
            url_key = f"{url}:{date_str}"
            if not hasattr(extract_gleanings_from_file, '_seen_urls'):
                extract_gleanings_from_file._seen_urls = set()
            if url_key in extract_gleanings_from_file._seen_urls:
                continue
            extract_gleanings_from_file._seen_urls.add(url_key)
            
            gleaning = {
                'title': title,
                'url': url,
                'domain': domain,
                'timestamp': timestamp,
                'description': description,
                'date': date_str,
                'source_file': str(file_path)
            }
            
            gleanings.append(gleaning)
    
    return gleanings


def find_daily_notes(base_path):
    """Find all daily note files in the 2025 directory."""
    daily_notes = []
    base_path = Path(base_path)
    
    # The base_path should already point to Daily/2025
    if not base_path.exists():
        print(f"Path not found: {base_path}")
        return daily_notes
    
    # Find all month directories (format: NN-MonthName)
    for month_dir in base_path.glob("*-*"):
        if month_dir.is_dir():
            # Find all daily note files in this month
            for note_file in month_dir.glob("2025-*.md"):
                daily_notes.append(note_file)
    
    return sorted(daily_notes)


def extract_media_from_file(file_path):
    """Extract movies and books from a single daily note file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    # Extract the date from filename
    filename = Path(file_path).stem
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    if not date_match:
        print(f"Could not extract date from filename: {filename}")
        return []
    
    date_str = date_match.group(1)
    media_items = []
    
    # Define patterns for different media reference formats
    patterns = [
        # TOWATCH [[Movie Title (Year)]] or ~~TOWATCH~~ [[Movie Title]]
        (r'(?:^|\n)[-*]?\s*(~~)?TOWATCH(~~)?\s*\[\[([^[\]]+?)\]\]', 'movie', 'towatch'),
        
        # TOREAD [[Book Title]] or TOREAD [[Author]]'s "[[Book Title]]" or ~~TOREAD~~ [[Book]]
        (r'(?:^|\n)[-*]?\s*(~~)?TOREAD(~~)?\s*(?:\[\[([^[\]]+?)\]\]\'s\s*")??\[\[([^[\]]+?)\]\]', 'book', 'toread'),
        
        # [timestamp] watching [[Movie Title]] or [timestamp] ~~watching~~ [[Movie Title]] or bare watching [[Movie Title]]
        (r'(?:\[([^\]]+)\]\s+)?(~~)?watching(~~)?\s*\[\[([^[\]]+?)\]\]', 'movie', 'watching'),
        
        # [timestamp] finished [[Movie/Book Title]] or [timestamp] ~~finished~~ [[Title]]
        (r'\[([^\]]+)\]\s+(~~)?finished(~~)?\s*\[\[([^[\]]+?)\]\]', 'auto', 'finished'),
        
        # ![[Book Title (Book)]] or ![[Movie Title]] - embedded references (exclude section links with #)
        (r'!\[\[([^[\]#]+?)\]\]', 'auto', 'referenced'),
    ]
    
    for pattern, media_type, action_type in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            groups = match.groups()
            
            # Determine if action was completed (strikethrough)
            is_completed = False
            if len(groups) >= 2 and groups[0] == '~~' and groups[1] == '~~':
                is_completed = True
            
            # Extract components based on pattern type
            if action_type == 'towatch':
                title = groups[2].strip() if groups[2] else ''
                timestamp = 'unknown'
                author = ''
                
            elif action_type == 'toread':
                author = groups[2].strip() if groups[2] else ''
                title = groups[3].strip() if groups[3] else groups[2].strip() if groups[2] else ''
                timestamp = 'unknown'
                # Clean up title - remove (Book) suffix if present
                title = title.replace('(Book)', '').strip()
                
            elif action_type == 'watching':
                timestamp = groups[0].strip() if groups[0] else 'unknown'
                title = groups[3].strip() if groups[3] else ''
                author = ''
                is_completed = groups[1] == '~~' and groups[2] == '~~'
                
            elif action_type == 'finished':
                timestamp = groups[0].strip() if groups[0] else 'unknown'
                title = groups[3].strip() if groups[3] else ''
                author = ''
                is_completed = True  # 'finished' always means completed
                
            elif action_type == 'referenced':
                title = groups[0].strip() if groups[0] else ''
                timestamp = 'unknown'
                author = ''
            
            # Skip empty titles
            if not title:
                continue
            
            # Auto-detect media type if needed
            if media_type == 'auto':
                if '(Book)' in title or action_type == 'toread':
                    media_type = 'book'
                    title = title.replace('(Book)', '').strip()
                else:
                    media_type = 'movie'
            
            # Extract year from movie titles like "Movie Title (1995)"
            year = ''
            year_match = re.search(r'\((\d{4})\)$', title)
            if year_match:
                year = year_match.group(1)
                title = title[:year_match.start()].strip()
            
            # Determine status
            if action_type == 'towatch':
                status = 'completed' if is_completed else 'to-watch'
            elif action_type == 'toread':
                status = 'completed' if is_completed else 'to-read'
            elif action_type == 'watching':
                status = 'completed' if is_completed else 'watching'
            elif action_type == 'finished':
                status = 'completed'
            elif action_type == 'referenced':
                status = 'referenced'
            else:
                status = 'unknown'
            
            # Generate tags
            tags = [f"#{media_type}"]
            
            # Add year and decade tags if available
            if year:
                tags.append(f"#{year}")
                decade = f"{year[:3]}0s"
                tags.append(f"#{decade}")
            
            # Add author info to description for books
            description = ''
            if media_type == 'book' and author:
                description = f"Author: {author}"
            
            # Create unique ID for deduplication
            media_key = f"{title.lower()}:{date_str}:{media_type}"
            if not hasattr(extract_media_from_file, '_seen_media'):
                extract_media_from_file._seen_media = set()
            if media_key in extract_media_from_file._seen_media:
                continue
            extract_media_from_file._seen_media.add(media_key)
            
            media_item = {
                'title': title,
                'year': year,
                'author': author,
                'type': media_type,
                'status': status,
                'timestamp': timestamp,
                'description': description,
                'date': date_str,
                'source_file': str(file_path),
                'tags': tags
            }
            
            media_items.append(media_item)
    
    return media_items


def generate_media_tags(media_item):
    """Generate appropriate Obsidian tags for a media item."""
    tags = [f"#{media_item['type']}"]
    
    # Add year and decade if available
    if media_item.get('year'):
        year = media_item['year']
        tags.append(f"#{year}")
        if len(year) == 4:
            decade = f"{year[:3]}0s"
            tags.append(f"#{decade}")
    
    # Could add more contextual tags here based on title/description analysis
    # e.g., #criterion, #netflix, #documentary, etc.
    
    return tags