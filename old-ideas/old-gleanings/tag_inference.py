#!/usr/bin/env python3
"""
Tag Inference Engine for Gleanings

This module provides intelligent tag assignment for gleanings based on:
- Existing vault tags (excluding structural tags)
- Content analysis of titles and descriptions
- Domain-based inference
- Temporal context from daily notes
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
import logging
import subprocess

# Configure logging
logger = logging.getLogger(__name__)

class TagInferenceEngine:
    """Intelligent tag assignment for gleanings using vault content analysis."""
    
    # Structural tags to exclude from content tagging
    EXCLUDED_TAGS = {
        'clippings', 'daily', 'notebook', 'fragments', 'info', 
        'readme', 'license', 'usage', 'benchmarks', 'options',
        'dispatcherrequestoptions-callback', 'dispatcherdispatchoptions-handler',
        'dispatcherconnectoptions-callback', 'sharesheet'
    }
    
    # Domain-based tag mappings
    DOMAIN_TAG_MAPPING = {
        'github.com': ['llms', 'obsidian', 'writing'],
        'gist.github.com': ['llms', 'obsidian'],
        'anthropic.com': ['llms'],
        'claude.ai': ['llms'],
        'openai.com': ['llms'],
        'huggingface.co': ['llms'],
        'arxiv.org': ['llms', 'culture', 'history'],
        'obsidian.md': ['obsidian'],
        'reddit.com': ['culture'],
        'wikipedia.org': ['culture', 'history', 'judaism'],
        'en.wikipedia.org': ['culture', 'history', 'judaism'],
        'en.m.wikipedia.org': ['culture', 'history', 'judaism'],
        'youtube.com': ['culture'],
        'medium.com': ['writing', 'culture'],
        'substack.com': ['writing', 'culture']
    }
    
    # Keyword-based tag mappings
    KEYWORD_TAG_MAPPING = {
        'llms': [
            'ai', 'artificial intelligence', 'machine learning', 'gpt', 'claude', 
            'openai', 'anthropic', 'llm', 'language model', 'chatbot', 'neural',
            'transformer', 'embeddings', 'semantic', 'nlp', 'prompt engineering'
        ],
        'judaism': [
            'jewish', 'judaism', 'torah', 'talmud', 'rabbi', 'synagogue', 'kosher',
            'shabbat', 'passover', 'yom kippur', 'rosh hashanah', 'hanukkah',
            'israel', 'hebrew', 'yiddish', 'zion', 'diaspora', 'antisemitism'
        ],
        'obsidian': [
            'obsidian', 'vault', 'markdown', 'zettelkasten', 'pkm', 'note-taking',
            'knowledge management', 'second brain', 'linked notes', 'backlinks',
            'graph view', 'dataview', 'templater'
        ],
        'culture': [
            'film', 'movie', 'cinema', 'literature', 'book', 'novel', 'art',
            'music', 'poetry', 'theater', 'cultural', 'society', 'social'
        ],
        'writing': [
            'writing', 'author', 'writer', 'publish', 'editor', 'manuscript',
            'draft', 'prose', 'narrative', 'story', 'essay', 'blog', 'article'
        ],
        'history': [
            'history', 'historical', 'ancient', 'medieval', 'renaissance',
            'revolution', 'war', 'empire', 'civilization', 'archaeology'
        ],
        'identity': [
            'identity', 'gender', 'race', 'ethnicity', 'sexuality', 'queer',
            'transgender', 'feminist', 'diversity', 'inclusion', 'minority'
        ],
        'parenting': [
            'parent', 'parenting', 'children', 'child', 'family', 'kids',
            'motherhood', 'fatherhood', 'baby', 'toddler', 'education'
        ],
        'neurotype': [
            'adhd', 'autism', 'neurodivergent', 'neurodiversity', 'neurotype',
            'anxiety', 'depression', 'mental health', 'therapy', 'psychology'
        ],
        'workplace': [
            'work', 'job', 'career', 'employment', 'office', 'remote work',
            'productivity', 'management', 'leadership', 'business', 'startup'
        ]
    }
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tag_frequencies = {}
        self.content_tags = self._load_filtered_vault_tags()
        
    def _load_filtered_vault_tags(self) -> Set[str]:
        """Load content tags from vault, excluding structural ones."""
        try:
            # Use the tag extractor to get vault tags
            tag_extractor_path = self.vault_path / ".tools" / "tag-extractor"
            if not tag_extractor_path.exists():
                logger.warning("Tag extractor not found, using fallback tag list")
                return self._get_fallback_tags()
            
            # Run tag extractor and parse output
            result = subprocess.run(
                ["uv", "run", "main.py", str(self.vault_path), "--format", "txt"],
                cwd=tag_extractor_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Tag extractor failed: {result.stderr}")
                return self._get_fallback_tags()
            
            # Parse tag frequencies from output
            content_tags = set()
            for line in result.stdout.split('\n'):
                if ' (' in line and ' files)' in line:
                    tag_match = re.match(r'^([^(]+) \((\d+) files\)', line.strip())
                    if tag_match:
                        tag_name = tag_match.group(1).strip()
                        frequency = int(tag_match.group(2))
                        
                        # Skip structural tags and low-frequency tags
                        if (tag_name not in self.EXCLUDED_TAGS and 
                            frequency >= 3 and 
                            len(tag_name) > 2):
                            content_tags.add(tag_name)
                            self.tag_frequencies[tag_name] = frequency
            
            logger.info(f"Loaded {len(content_tags)} content tags from vault")
            return content_tags
            
        except Exception as e:
            logger.error(f"Error loading vault tags: {e}")
            return self._get_fallback_tags()
    
    def _get_fallback_tags(self) -> Set[str]:
        """Fallback tag list if vault extraction fails."""
        return {
            'llms', 'judaism', 'culture', 'obsidian', 'writing', 'history', 
            'identity', 'parenting', 'neurotype', 'workplace', 'religion',
            'dictated', 'gil', 'api'
        }
    
    def infer_tags(self, gleaning: Dict[str, Any]) -> List[str]:
        """
        Infer relevant tags for a gleaning based on multiple criteria.
        
        Args:
            gleaning: Dictionary containing gleaning data
            
        Returns:
            List of inferred tags (max 5)
        """
        inferred_tags = set()
        
        # Extract text for analysis
        title = gleaning.get('title', '').lower()
        description = gleaning.get('description', '').lower()
        url = gleaning.get('url', '').lower()
        domain = gleaning.get('domain', '').lower()
        
        # 1. Domain-based inference
        domain_tags = self._infer_from_domain(domain)
        inferred_tags.update(domain_tags)
        
        # 2. Keyword-based inference
        content_text = f"{title} {description} {url}"
        keyword_tags = self._infer_from_keywords(content_text)
        inferred_tags.update(keyword_tags)
        
        # 3. Temporal context inference
        date = gleaning.get('date')
        if date:
            temporal_tags = self._infer_from_temporal_context(date)
            inferred_tags.update(temporal_tags)
        
        # 4. Filter to only valid vault tags
        valid_tags = inferred_tags.intersection(self.content_tags)
        
        # 5. Sort by frequency and limit to 5 tags
        sorted_tags = sorted(
            valid_tags, 
            key=lambda t: self.tag_frequencies.get(t, 0), 
            reverse=True
        )
        
        return sorted_tags[:5]
    
    def _infer_from_domain(self, domain: str) -> Set[str]:
        """Infer tags based on URL domain."""
        tags = set()
        
        for domain_pattern, domain_tags in self.DOMAIN_TAG_MAPPING.items():
            if domain_pattern in domain:
                tags.update(domain_tags)
        
        return tags
    
    def _infer_from_keywords(self, content_text: str) -> Set[str]:
        """Infer tags based on keyword matching in content."""
        tags = set()
        
        for tag, keywords in self.KEYWORD_TAG_MAPPING.items():
            for keyword in keywords:
                if keyword in content_text:
                    tags.add(tag)
                    break  # Found one keyword for this tag, move to next tag
        
        return tags
    
    def _infer_from_temporal_context(self, gleaning_date: str) -> Set[str]:
        """
        Infer tags based on what was happening around the same time.
        
        Looks at daily notes from ±2 days to find thematic clustering.
        """
        tags = set()
        
        try:
            # Parse the gleaning date
            date_obj = datetime.strptime(gleaning_date, '%Y-%m-%d')
            
            # Check daily notes from ±2 days
            for days_offset in [-2, -1, 0, 1, 2]:
                check_date = date_obj + timedelta(days=days_offset)
                daily_file = self._find_daily_note(check_date)
                
                if daily_file and daily_file.exists():
                    daily_tags = self._extract_tags_from_daily_note(daily_file)
                    # Only add tags that are in our content tags set
                    valid_daily_tags = daily_tags.intersection(self.content_tags)
                    tags.update(valid_daily_tags)
        
        except Exception as e:
            logger.debug(f"Error in temporal context analysis: {e}")
        
        return tags
    
    def _find_daily_note(self, date_obj: datetime) -> Optional[Path]:
        """Find the daily note file for a given date."""
        year = date_obj.year
        month = date_obj.strftime('%m-%B')
        
        # Construct path like: Daily/2025/01-January/2025-01-02-Th.md
        daily_dir = self.vault_path / "Daily" / str(year) / month
        
        # Try different day formats
        day_names = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        day_name = day_names[date_obj.weekday()]
        
        date_str = date_obj.strftime('%Y-%m-%d')
        daily_file = daily_dir / f"{date_str}-{day_name}.md"
        
        return daily_file if daily_file.exists() else None
    
    def _extract_tags_from_daily_note(self, daily_file: Path) -> Set[str]:
        """Extract tags from a daily note's frontmatter and content."""
        tags = set()
        
        try:
            with open(daily_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter tags
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                # Look for tags in YAML format
                tag_match = re.search(r'tags:\s*\n((?:\s*-\s*.+\n)*)', frontmatter)
                if tag_match:
                    tag_lines = tag_match.group(1)
                    for line in tag_lines.split('\n'):
                        if line.strip().startswith('-'):
                            tag = line.strip()[1:].strip()
                            if tag:
                                tags.add(tag)
            
            # Extract inline tags (basic implementation)
            inline_tags = re.findall(r'#([a-zA-Z0-9_-]+)', content)
            tags.update(inline_tags)
            
        except Exception as e:
            logger.debug(f"Error extracting tags from {daily_file}: {e}")
        
        return tags

# Convenience function for use in other modules
def create_tag_inference_engine(vault_path: str = None) -> TagInferenceEngine:
    """Create a tag inference engine instance."""
    if vault_path is None:
        # Default to the vault path relative to this script
        script_dir = Path(__file__).parent
        vault_path = script_dir.parent.parent
    
    return TagInferenceEngine(vault_path)