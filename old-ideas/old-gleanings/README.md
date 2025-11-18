# Gleanings System v2

An intelligent content management system for extracting, organizing, and curating links from your daily notes.

## Prerequisites

- Python 3.8+ 
- [uv](https://docs.astral.sh/uv/) package manager
- No external dependencies (PyYAML dependency has been removed)

## Setup

```bash
# Install dependencies and create virtual environment
uv sync
```

That's it! The `uv sync` command automatically creates a virtual environment and installs any dependencies.

## Quick Start

### 1. Test the system
```bash
# Show current statistics
uv run extract_new.py --stats
```

### 2. Regular Usage
```bash
# Fast incremental update (only processes changed files)
uv run update_gleanings_v2.py

# Interactive management
uv run manage_gleanings.py

# View statistics
uv run extract_new.py --stats
```

## Core Features

### Performance
- Incremental processing - only processes modified files
- 10-100x faster than legacy system
- Smart file tracking prevents unnecessary work

### User Control
- Hide unwanted items without losing data
- Bulk operations by domain or category
- Persistent preferences across updates
- Undo capability for all actions

### Organization
- Auto-categorization with 12+ categories
- Domain-based grouping 
- Search and filtering
- Statistics and breakdowns

## Main Commands

| Command | Purpose | Speed |
|---------|---------|-------|
| `uv run update_gleanings_v2.py` | Complete update pipeline | Fast |
| `uv run extract_new.py` | Extract new/changed gleanings | Fast |
| `uv run manage_gleanings.py` | Hide/restore/search gleanings | Instant |
| `uv run extract_new.py --stats` | Show system statistics | Instant |

## Files Overview

### Core System
- `gleanings_state.py` - State management engine
- `extract_new.py` - Incremental extraction
- `manage_gleanings.py` - User management interface
- `update_gleanings_v2.py` - Main orchestration script
- `generate_index_v2.py` - State-aware index generator

### Configuration
- `categories.yaml` - Categorization rules
- `gleanings_state.json` - System state and user preferences

### Generated Output
- `Gleanings Index.md` - Curated index (excludes hidden items)
- `Gleanings Analysis.md` - Statistics and insights

### Legacy Files
- `_attic/` - Legacy v1 files (for reference only)

## Usage Patterns

### Daily Workflow
1. Add links to your daily notes as usual
2. Run `uv run update_gleanings_v2.py` (processes only new content)
3. Browse the updated `Gleanings Index.md`

### Curation Workflow
1. Run `uv run manage_gleanings.py --stats` to see what's new
2. Use interactive mode to hide unwanted domains/categories
3. Run `uv run update_gleanings_v2.py` to regenerate clean index

### Bulk Management
1. `uv run manage_gleanings.py` → Interactive menu
2. Choose "Bulk operations"
3. Hide entire domains or categories at once

## Performance Comparison

| Operation | v1 (Legacy) | v2 (Current) | Improvement |
|-----------|-------------|--------------|-------------|
| Full processing | 2-5 minutes | 0.1s | 1000x faster |
| Incremental update | 2-5 minutes | 0.0s | ∞ faster |
| User customization | Lost on update | Persistent | ∞ better |

## Advanced Usage

### Force full reprocessing
```bash
uv run update_gleanings_v2.py --force-all
```

### Search across all content
```bash
uv run manage_gleanings.py --search "machine learning"
```

### Hide specific items
```bash
uv run manage_gleanings.py --hide abc123 def456
```

### View hidden items
```bash
uv run manage_gleanings.py --list hidden
```

## Migration from v1

The system automatically detects and migrates legacy `gleanings_data.json` files. Your existing workflow continues to work, but you gain:

- Dramatic performance improvements
- User curation capabilities  
- Enhanced organization and statistics
- Persistent preferences

Legacy files are preserved in `_attic/` directory for reference.

## Documentation

- `docs/manage-gleanings.md` - Detailed user management guide
- `docs/phase-2-report.md` - Complete implementation documentation
- `docs/tagging-implementation.md` - Tagging system implementation
- `docs/web-app-readme.md` - Web application documentation
- `docs/web-app-sorting-issues.md` - Debugging notes for sorting problems
- `categories.yaml` - Categorization configuration reference