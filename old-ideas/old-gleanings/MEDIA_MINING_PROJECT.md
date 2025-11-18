---
type:
title: Media Mining System Project Plan
description: "Project plan to extend the gleanings system for extracting and managing movies and books from daily notes, detailing extraction patterns, state management integration, tag-based organization, technical schema, file changes, success criteria, risk mitigation, and timeline. ✷❋✷"
created: 2025-08-23T15:43:50-04:00
modified: 2025-08-23T16:01:14-04:00
project: "[[IDIOSYNTHESIS]]"
tags:
  - to-watch
  - books
  - completed
  - obsidian
  - llms
---

# Media Mining System Project Plan

**Branch**: `media-mining-system`  
**Start Date**: 2025-08-23  
**Goal**: Extend the existing gleanings system to extract and manage movies and books from daily notes

## Project Overview

Enhance the robust gleanings v2 system to include media (movies and books) extraction alongside existing URL extraction. This leverages the existing state management, categorization, and incremental processing architecture while adding new media-specific capabilities.

## Current State Analysis

### Daily Notes Patterns Identified

**Movies:**
- `TOWATCH [[Title (Year)]]` - movies to watch
- `~~TOWATCH~~ [[Title]]` - completed movies (strikethrough)
- `[time] watching [[Title]]` - currently watching
- `[time] finished [[Title]]` - completed movies

**Books:**
- `TOREAD [[Title]]` - books to read
- `TOREAD [[Author]]'s "[[Title]]"` - books with author attribution
- `~~TOREAD~~ [[Title]]` - completed books (strikethrough)
- `![[Title (Book)]]` - embedded book references

**Existing Vault Structure:**
- `Reference/Culture/Movies/Title (Year).md` - Detailed movie notes with metadata (58+ films)
- Film notes contain structured data: director, year, duration, cast, descriptions  
- **Note**: Many movie notes still scattered in other locations (e.g., `L/` directory)
- Potential for cross-referencing daily mentions with existing detailed notes across vault

**Data Volume:**
- 242 daily notes in 2025 (January through August)
- Consistent timestamp and wiki-link formatting
- Status tracking via strikethrough notation

### Existing Gleanings System Architecture

**Strengths to Leverage:**
- JSON state management (`gleanings_state.json`)
- Incremental processing (10-100x performance improvement)
- User preference management (hide/restore/delete)
- YAML-based categorization system (`categories.yaml`)
- Web application for management
- Automatic backup system
- File modification tracking for efficiency

## Implementation Strategy

### Phase 1: Core Media Detection
**Files to Modify:**
- `extraction_functions.py` - Add `extract_media_from_file()` function
- Core extraction patterns for all identified media formats

**Deliverables:**
- Regex patterns for all movie/book reference formats
- Status detection (to-watch, watching, completed, etc.)
- Title/year/author parsing
- Obsidian tag generation for media items
- Integration with existing file processing loop

### Phase 2: State Management Integration
**Files to Modify:**
- `gleanings_state.py` - Extend to handle media items alongside URLs
- `extract_new.py` - Include media extraction in incremental processing
- Data deduplication for media items

**Deliverables:**
- Media items stored in same state file as gleanings
- Incremental processing for media (only changed files)
- User preference support (hide/delete media items)

### Phase 3: Output and Tag-Based Organization
**Files to Modify:**
- `generate_index_v2.py` - Add media sections to output with tag-based grouping
- Output formatting for movies and books

**Deliverables:**
- Enhanced `Gleanings Index.md` with Movies and Books sections
- Tag-based organization (#movie,, etc.)
- **Note**: Web application will be rewritten separately - focus on core extraction and markdown output

### Phase 4: Testing and Refinement
**Activities:**
- Test extraction on all 242 daily notes
- Validate status detection accuracy
- Performance testing with incremental updates
- User preference functionality testing

## Technical Design

### Media Data Schema
**Extensible design for movies, books, music, and future media types**

```json
{
  "media_abc123": {
    "type": "movie",
    "title": "How It Ends", 
    "year": "2021",
    "status": "to-watch",
    "first_mentioned": "2025-08-21",
    "timestamp": "unknown",
    "description": "",
    "sources": ["Daily/2025/08-August/2025-08-21-Th.md"],
    "user_action": null,
    "tags": ["#movie", "#2021", "#2020s"],
    "metadata": {
      "director": null,
      "duration": null,
      "existing_note": null
    }
  },
  "media_def456": {
    "type": "book",
    "title": "The Ministry of Special Cases",
    "author": "Nathan Englander",
    "year": "",
    "status": "to-read",
    "first_mentioned": "2025-01-27", 
    "timestamp": "unknown",
    "description": "Author: Nathan Englander",
    "sources": ["Daily/2025/01-January/2025-01-27-Mo.md"],
    "user_action": null,
    "tags": ["#book", "#fiction"],
    "metadata": {
      "publisher": null,
      "pages": null,
      "existing_note": null
    }
  },
  "media_ghi789": {
    "type": "music",
    "title": "Album Name",
    "artist": "Artist Name",
    "year": "2023",
    "status": "to-listen",
    "first_mentioned": "2025-08-23",
    "timestamp": "14:30",
    "description": "",
    "sources": ["Daily/2025/08-August/2025-08-23-Fr.md"],
    "user_action": null,
    "tags": ["#music", "#album", "#2023", "#2020s"],
    "metadata": {
      "genre": null,
      "label": null,
      "existing_note": null
    }
  }
}
```

**Key Design Features:**
- **Extensible `type` field**: Supports movies, books, music, podcasts, etc.
- **Obsidian tags array**: Native tag support for flexible organization and filtering
- **Flexible `metadata` object**: Type-specific fields without schema rigidity
- **`existing_note` tracking**: Links to existing vault notes across directories (`Reference/Culture/Movies/`, `L/`, etc.)
- **Consistent core fields**: All media types share status, sources, timestamps
- **Future-proof**: Easy to add new media types without breaking existing data

### Tag Generation Strategy

**Core Tags (Always Present):**
- Media type: `#movie`, `#book`, `#music`, `#podcast`, `#game`

**Contextual Tags (When Available):**
- Year: `#1995`, `#2021`, `#2023`
- Decade: `#1990s`, `#2020s` (derived from year)
- Format: `#film`, `#tv-series`, `#album`, `#single`, `#audiobook`
- Source: `#criterion`, `#netflix`, `#library` (if mentioned)

**Status Tracking:**
- Status stored in `status` field: `to-watch`, `watching`, `completed`, `to-read`, `referenced`
- Tags focus on content attributes, not status

**Example Tag Collections:**
- Movie: `["#movie", "#1995", "#1990s", "#criterion"]`
- Book: `["#book", "#fiction", "#2021", "#2020s"]`  
- Music: `["#music", "#album", "#2023", "#indie"]`

### Integration Points
1. **State Management**: Media items use same ID/state system as gleanings
2. **File Processing**: Media extraction runs alongside URL extraction
3. **Tag-Based Organization**: Media organized by Obsidian tags rather than categories
4. **Output Generation**: Media sections grouped by status, with tag information displayed
5. **User Management**: Media items support same hide/delete functionality
6. **Vault Integration**: Detect existing notes throughout vault (`Reference/Culture/Movies/`, `L/`, etc.) and link appropriately

## File Structure Changes

```
.tools/gleanings/
├── extraction_functions.py     # Add extract_media_from_file()
├── categories.yaml             # Unchanged - media uses tags instead  
├── gleanings_state.json        # Extended to include media
├── extract_new.py              # Include media in processing
├── generate_index_v2.py        # Add media sections to output
├── Gleanings Index.md          # Include Movies/Books sections
└── MEDIA_MINING_PROJECT.md     # This project plan
```

## Success Criteria

1. **Extraction Accuracy**: Successfully detect and parse all media reference formats
2. **Status Detection**: Correctly identify completion status from markup
3. **Performance**: Maintain incremental processing speed (sub-second updates)
4. **Integration**: Seamless integration with existing gleanings workflow
5. **User Experience**: Media items manageable through existing interfaces
6. **Data Integrity**: No loss of existing gleanings functionality

## Risk Mitigation

1. **Backup Strategy**: Automatic state backups before major changes
2. **Branch Isolation**: All work on separate branch until fully tested
3. **Incremental Development**: Phase-based approach with testing at each step
4. **Fallback Plan**: Preserve existing gleanings functionality if media integration fails

## Timeline Estimate

- **Phase 1**: 2-3 hours (pattern development and testing)
- **Phase 2**: 1-2 hours (state management integration) 
- **Phase 3**: 1-2 hours (output generation and categorization - markdown only, no webapp)
- **Phase 4**: 1 hour (testing and refinement)

**Total Estimate**: 5-8 hours development time

## Next Steps

1. Create comprehensive regex patterns for media detection
2. Test patterns against sample daily notes
3. Implement core extraction function
4. Integrate with existing state management
5. Update output generation
6. Full system testing

---

*This project extends the highly successful gleanings v2 system to provide comprehensive media tracking while maintaining the performance and usability improvements that made the original system so effective.*
