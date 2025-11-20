#!/usr/bin/env python3
"""
Add title field to existing gleaning frontmatter.

This script updates existing gleanings to include 'title:' in frontmatter
so Synthesis can display proper titles instead of MD5 hash filenames.
"""

import argparse
import json
import re
from pathlib import Path


def extract_h1_title(content: str) -> str:
    """Extract title from H1 heading."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def has_title_in_frontmatter(content: str) -> bool:
    """Check if frontmatter already has title field."""
    frontmatter_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        return re.search(r'^title:', frontmatter, re.MULTILINE) is not None
    return False


def add_title_to_frontmatter(content: str, title: str) -> str:
    """Add title field to frontmatter."""
    # Match frontmatter block
    frontmatter_match = re.match(r'^(---\n)(.+?)(\n---)', content, re.DOTALL)
    if not frontmatter_match:
        print("  WARNING: No frontmatter found")
        return content

    opening = frontmatter_match.group(1)
    frontmatter = frontmatter_match.group(2)
    closing = frontmatter_match.group(3)
    rest_of_content = content[frontmatter_match.end():]

    # Quote title for YAML safety (handles colons, quotes, etc.)
    quoted_title = json.dumps(title)

    # Add title as first field in frontmatter
    new_frontmatter = f"title: {quoted_title}\n{frontmatter}"

    return opening + new_frontmatter + closing + rest_of_content


def process_gleaning(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single gleaning file. Returns True if updated."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has title
    if has_title_in_frontmatter(content):
        return False

    # Extract title from H1
    title = extract_h1_title(content)
    if not title:
        print(f"  WARNING: Could not find H1 title in {file_path.name}")
        return False

    # Add title to frontmatter
    new_content = add_title_to_frontmatter(content, title)

    if dry_run:
        print(f"  [DRY RUN] Would add title: {title}")
        return True

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✓ Added title: {title}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Add title field to gleaning frontmatter")
    parser.add_argument(
        "--vault-path",
        type=Path,
        required=True,
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault_path).expanduser()
    gleanings_dir = vault_path / "L" / "Gleanings"

    if not gleanings_dir.exists():
        print(f"Error: Gleanings directory not found: {gleanings_dir}")
        return 1

    print(f"Processing gleanings in: {gleanings_dir}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Find all gleaning markdown files
    gleaning_files = list(gleanings_dir.glob("*.md"))
    print(f"Found {len(gleaning_files)} gleaning files")
    print()

    updated = 0
    skipped = 0

    for file_path in gleaning_files:
        print(f"Processing: {file_path.name}")
        if process_gleaning(file_path, dry_run=args.dry_run):
            updated += 1
        else:
            skipped += 1

    # Summary
    print()
    print("=" * 60)
    print(f"Complete!")
    print(f"Files {'would be ' if args.dry_run else ''}updated: {updated}")
    print(f"Files skipped (already have title): {skipped}")
    print(f"Total files: {len(gleaning_files)}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
