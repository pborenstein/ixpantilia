#!/usr/bin/env python3
"""
Analyze gleanings patterns and create insights.

This script provides analysis of gleaning patterns including:
- Time-based patterns
- Topic trends
- Domain analysis
- Discovery patterns
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import argparse

def load_gleanings_data(json_file):
    """Load the gleanings data from JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_time_patterns(gleanings):
    """Analyze time-based patterns in gleanings."""
    hours = []
    days_of_week = []
    daily_counts = defaultdict(int)
    
    for gleaning in gleanings:
        timestamp = gleaning['timestamp']
        date = gleaning['date']
        
        # Extract hour from timestamp (format: HH:MM)
        if ':' in timestamp:
            try:
                hour_str = timestamp.split(':')[0]
                # Only process if it looks like a valid hour (1-2 digits)
                if hour_str.isdigit() and 0 <= int(hour_str) <= 23:
                    hour = int(hour_str)
                    hours.append(hour)
            except (ValueError, IndexError):
                # Skip malformed timestamps
                pass
        
        # Count per day
        daily_counts[date] += 1
        
        # Day of week
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
            days_of_week.append(dt.strftime('%A'))
        except:
            pass
    
    hour_counts = Counter(hours)
    dow_counts = Counter(days_of_week)
    
    return {
        'hour_distribution': hour_counts,
        'day_of_week': dow_counts,
        'daily_counts': daily_counts,
        'avg_per_day': len(gleanings) / len(daily_counts) if daily_counts else 0
    }

def analyze_domain_patterns(gleanings):
    """Analyze domain patterns and categorize sources."""
    domains = Counter(g['domain'] for g in gleanings)
    
    # Categorize domains
    domain_categories = {
        'Development': ['github.com', 'stackoverflow.com', 'dev.to', 'medium.com'],
        'Learning': ['en.wikipedia.org', 'en.m.wikipedia.org', 'arxiv.org', 'scholar.google.com'],
        'News/Social': ['news.ycombinator.com', 'reddit.com', 'twitter.com'],
        'Video': ['youtube.com', 'youtu.be', 'm.youtube.com', 'vimeo.com'],
        'Tools': ['claude.ai', 'openai.com', 'anthropic.com'],
        'Academic': ['arxiv.org', 'researchgate.net', 'springer.com']
    }
    
    categorized_domains = defaultdict(list)
    uncategorized = []
    
    for domain, count in domains.items():
        categorized = False
        for category, category_domains in domain_categories.items():
            if domain in category_domains:
                categorized_domains[category].append((domain, count))
                categorized = True
                break
        
        if not categorized:
            uncategorized.append((domain, count))
    
    return {
        'top_domains': domains.most_common(20),
        'categorized': dict(categorized_domains),
        'uncategorized': uncategorized[:10]  # Top 10 uncategorized
    }

def load_categories_config(config_path=None):
    """Load categories configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent / 'categories.yaml'
    
    try:
        # Import the simple parser from extraction_functions
        from extraction_functions import simple_yaml_parse
        config = simple_yaml_parse(config_path)
        return config
    except Exception as e:
        print(f"Warning: Could not load categories config from {config_path}: {e}")
        return None

def analyze_content_trends(gleanings):
    """Analyze content trends and keywords with improved filtering."""
    # Load stop words from config
    config = load_categories_config()
    config_stop_words = set(config.get('stop_words', [])) if config else set()
    
    # Additional technical stop words
    tech_stop_words = {
        'https', 'http', 'www', 'com', 'org', 'net', 'github', 'page', 'site', 
        'link', 'url', 'file', 'files', 'data', 'information', 'content', 'text',
        'create', 'created', 'creating', 'build', 'built', 'make', 'made', 'making',
        'used', 'using', 'user', 'users', 'work', 'working', 'works', 'simple',
        'easy', 'quick', 'fast', 'best', 'better', 'great', 'good', 'nice',
        'feature', 'features', 'support', 'supports', 'available', 'free',
        'open', 'source', 'project', 'projects', 'version', 'versions',
        'install', 'installation', 'setup', 'configure', 'configuration'
    }
    
    # Combine all stop words
    all_stop_words = config_stop_words | tech_stop_words
    
    # Extract keywords from titles and descriptions by category
    category_keywords = defaultdict(list)
    all_keywords = []
    
    for gleaning in gleanings:
        # Combine title, description for keyword extraction
        text = (gleaning.get('title', '') + ' ' + gleaning.get('description', '')).lower()
        category = gleaning.get('category', 'Unknown')
        
        # Extract meaningful words (3+ chars, not stop words)
        words = re.findall(r'\b[a-z]{3,}\b', text)
        filtered_words = [w for w in words if w not in all_stop_words and len(w) >= 3]
        
        category_keywords[category].extend(filtered_words)
        all_keywords.extend(filtered_words)
    
    # Count overall keywords
    keyword_counts = Counter(all_keywords)
    
    # Count keywords by category
    category_keyword_counts = {}
    for category, words in category_keywords.items():
        category_keyword_counts[category] = Counter(words).most_common(10)
    
    # Extract technical concepts and themes
    technical_themes = analyze_technical_themes(gleanings)
    
    return {
        'top_keywords': keyword_counts.most_common(20),
        'category_keywords': category_keyword_counts,
        'technical_themes': technical_themes,
        'total_unique_words': len(keyword_counts),
        'stop_words_filtered': len(all_stop_words)
    }

def analyze_technical_themes(gleanings):
    """Analyze specific technical themes and concepts."""
    themes = {
        'AI/ML Concepts': ['transformer', 'neural', 'embedding', 'model', 'training', 'inference', 'llm', 'gpt', 'claude', 'anthropic', 'openai', 'mcp'],
        'Programming Languages': ['python', 'javascript', 'typescript', 'rust', 'go', 'java', 'cpp', 'ruby', 'php', 'swift'],
        'Web Technologies': ['react', 'vue', 'angular', 'nodejs', 'express', 'nextjs', 'css', 'html', 'bootstrap', 'tailwind'],
        'Development Tools': ['docker', 'kubernetes', 'git', 'github', 'vscode', 'webpack', 'babel', 'eslint', 'prettier'],
        'Cloud & Infrastructure': ['aws', 'azure', 'gcp', 'serverless', 'microservices', 'api', 'rest', 'graphql'],
        'Knowledge Management': ['obsidian', 'notion', 'roam', 'logseq', 'zettelkasten', 'pkm', 'markdown', 'notes']
    }
    
    theme_counts = {}
    all_text = ' '.join([
        (gleaning.get('title', '') + ' ' + gleaning.get('description', '')).lower() 
        for gleaning in gleanings
    ])
    
    for theme_name, keywords in themes.items():
        count = sum(all_text.count(keyword) for keyword in keywords)
        if count > 0:
            theme_counts[theme_name] = count
    
    return sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

def monthly_summary(gleanings):
    """Create monthly summaries."""
    monthly_data = defaultdict(lambda: {
        'count': 0,
        'categories': defaultdict(int),
        'top_domains': defaultdict(int),
        'highlights': []
    })
    
    for gleaning in gleanings:
        date = gleaning['date']
        year_month = date[:7]  # YYYY-MM
        
        monthly_data[year_month]['count'] += 1
        monthly_data[year_month]['categories'][gleaning['category']] += 1
        monthly_data[year_month]['top_domains'][gleaning['domain']] += 1
        
        # Collect interesting items (those with longer descriptions)
        if len(gleaning['description']) > 100:
            monthly_data[year_month]['highlights'].append(gleaning)
    
    return monthly_data

def generate_analysis_report(gleanings):
    """Generate a comprehensive analysis report."""
    time_patterns = analyze_time_patterns(gleanings)
    domain_patterns = analyze_domain_patterns(gleanings)
    content_trends = analyze_content_trends(gleanings)
    monthly_data = monthly_summary(gleanings)
    
    report = f"""# Gleanings Analysis Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## Summary Statistics

- **Total gleanings:** {len(gleanings)}
- **Average per day:** {time_patterns['avg_per_day']:.1f}
- **Date range:** {min(g['date'] for g in gleanings)} to {max(g['date'] for g in gleanings)}
- **Unique domains:** {len(domain_patterns['top_domains'])}

## Time Patterns

### Peak Discovery Hours
"""
    
    for hour, count in time_patterns['hour_distribution'].most_common(10):
        percentage = (count / len(gleanings)) * 100
        time_label = f"{hour:02d}:00"
        report += f"- **{time_label}**: {count} items ({percentage:.1f}%)\n"
    
    report += "\n### Day of Week Distribution\n\n"
    
    for day, count in time_patterns['day_of_week'].most_common():
        percentage = (count / len(gleanings)) * 100
        report += f"- **{day}**: {count} items ({percentage:.1f}%)\n"
    
    report += "\n## Domain Analysis\n\n### Top Sources\n\n"
    
    for domain, count in domain_patterns['top_domains'][:15]:
        percentage = (count / len(gleanings)) * 100
        report += f"- **{domain}**: {count} items ({percentage:.1f}%)\n"
    
    report += "\n### Source Categories\n\n"
    
    for category, domains in domain_patterns['categorized'].items():
        if domains:
            total = sum(count for _, count in domains)
            report += f"**{category}**: {total} items\n"
            for domain, count in sorted(domains, key=lambda x: x[1], reverse=True)[:5]:
                report += f"  - {domain}: {count}\n"
            report += "\n"
    
    report += "\n## Content Trends\n\n### Popular Keywords\n\n"
    
    for keyword, count in content_trends['top_keywords'][:20]:
        report += f"- **{keyword}**: {count} mentions\n"
    
    report += "\n## Monthly Breakdown\n\n"
    
    for year_month in sorted(monthly_data.keys(), reverse=True):
        data = monthly_data[year_month]
        year, month = year_month.split('-')
        month_name = datetime.strptime(month, '%m').strftime('%B')
        
        report += f"### {month_name} {year}\n\n"
        report += f"**Total items:** {data['count']}\n\n"
        
        report += "**Top categories:**\n"
        for category, count in Counter(data['categories']).most_common(5):
            report += f"- {category}: {count}\n"
        
        report += "\n**Top domains:**\n"
        for domain, count in Counter(data['top_domains']).most_common(5):
            report += f"- {domain}: {count}\n"
        
        report += "\n---\n\n"
    
    report += f"""## Insights

### Discovery Patterns
- You tend to discover most content during {time_patterns['hour_distribution'].most_common(1)[0][0]:02d}:00 hour
- {time_patterns['day_of_week'].most_common(1)[0][0]} is your most active discovery day
- GitHub is your primary source for technical content ({domain_patterns['top_domains'][0][1]} items)

### Content Focus
- Technical/development content makes up {(sum(1 for g in gleanings if g['category'] in ['Tech/Development', 'AI/LLM']) / len(gleanings) * 100):.1f}% of your gleanings
- Your top keyword "{content_trends['top_keywords'][0][0]}" appears {content_trends['top_keywords'][0][1]} times

---

*This analysis was automatically generated from your daily notes gleanings.*
"""
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Analyze Gleanings Patterns')
    parser.add_argument('--input', default='gleanings_data.json',
                       help='Input JSON file with gleanings data')
    parser.add_argument('--output', default='Gleanings Analysis.md',
                       help='Output analysis report file')
    
    args = parser.parse_args()
    
    # Load the data
    base_dir = Path(__file__).parent
    input_path = base_dir / args.input
    
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return
    
    print(f"Loading gleanings data from: {input_path}")
    gleanings = load_gleanings_data(input_path)
    
    if not gleanings:
        print("No gleanings data found!")
        return
    
    print(f"Analyzing {len(gleanings)} gleanings...")
    
    # Generate analysis
    report = generate_analysis_report(gleanings)
    
    # Save report
    output_path = base_dir / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analysis report saved to: {output_path}")

if __name__ == '__main__':
    main()