# Gleanings Management System

The **Gleanings Management System** is an interactive tool for organizing and curating your collection of saved links from daily notes. Here's how it works:

## What is Gleaning Management?

**Gleanings** are interesting links you save in your daily notes - articles, tools, research papers, videos, etc. The management system lets you:

### Core Actions
- **Hide** - Remove from index but keep in database (for low-quality or irrelevant items)
- **Delete** - Mark as deleted but recoverable (for unwanted duplicates or mistakes)  
- **Restore** - Bring back hidden/deleted items
- **Favorite** - Mark important items (future feature)

### Key Benefits
- **Persistent preferences** - Your hide/delete actions survive system updates
- **No data loss** - Items are never permanently destroyed
- **Bulk operations** - Hide entire domains or categories at once
- **Undo capability** - All actions are reversible with reason tracking

## How to Use

### Interactive Management
```bash
uv run manage_gleanings.py
```
This opens a menu where you can:
- Browse active/hidden/deleted gleanings
- Search across all content
- Hide unwanted items
- Restore previously hidden items
- View statistics and breakdowns

### Command Line Operations
```bash
# Hide specific gleanings by ID
uv run manage_gleanings.py --hide abc123 def456

# List only hidden items
uv run manage_gleanings.py --list hidden

# Search for specific content
uv run manage_gleanings.py --search "machine learning"

# Show system statistics
uv run manage_gleanings.py --stats
```

### Example Workflow
1. **Extract gleanings**: `uv run extract_new.py` (finds new items)
2. **Review collection**: `uv run manage_gleanings.py --stats` 
3. **Hide unwanted domains**: Interactive menu → Bulk operations → Hide from domain
4. **Generate clean index**: `uv run update_gleanings_v2.py` (excludes hidden items)

## Why This Matters

**Before**: Every link you ever saved cluttered your index, with no way to curate without losing data

**After**: You can curate a clean, focused index while preserving everything in the background. Perfect for maintaining a high signal-to-noise ratio in your knowledge system.

The system turns your raw collection of links into a curated knowledge resource you actually want to browse and reference.