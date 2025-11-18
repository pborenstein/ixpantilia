# Gleanings Web App

A Vue.js web application for managing gleanings with an Express.js backend API. This web interface provides a modern, responsive way to browse, search, filter, and manage your gleanings collection.

## Features

- **Search & Filter**: Powerful search with operators, visual filter chips
- **Browse**: Table and card views with sorting options
- **Manage**: Hide/show, delete/restore gleanings with bulk operations
- **Responsive**: Works on desktop, tablet, and mobile
- **Domain Filtering**: Click domain names to filter by specific sites
- **Advanced Filtering**: Category, status, date range filtering
- **Real-time Stats**: Active, hidden, and total counts

## Quick Start

1. **Install all dependencies:**
```bash
npm run install:all
```

2. **Start development servers:**
```bash
npm run dev
```

This starts both the backend API (port 3001) and frontend dev server (port 5173).

## Project Structure

```
web-app/
├── backend/          # Express.js API server
├── frontend/         # Vue 3 application with Vite
├── shared/           # Common utilities and parsers
├── package.json      # Root package with scripts
└── README.md         # This file
```

### Key Directories

- **`backend/`** - Express.js server, routes, and API logic
- **`frontend/src/`** - Vue.js components, composables, and styles
- **`shared/`** - Search parser and data filtering utilities used by both frontend and backend

## Search System

### Search Operators

The application supports powerful search operators for precise filtering:

```bash
domain:github.com                    # Filter by domain
before:2023-01-01                   # Items before date  
after:2023-01-01                    # Items after date
status:active                       # Filter by status (active/hidden)
category:tech                       # Filter by category
domain:github.com typescript        # Domain + text search
before:2023-01-01 after:2022-01-01  # Date range
```

### Search Features

- **Unified interface**: One search box handles operators + text search
- **Visual feedback**: Filter chips show all active filters
- **Individual removal**: Click × on any chip to remove that filter
- **Override behavior**: Operators override dropdown selections
- **Quoted strings**: Support for `domain:"multi word domain"`
- **Case insensitive**: All operators work regardless of case

### Filter Chips

Active filters appear as removable chips below the search bar:
- **Domain filters** (blue chips)
- **Status filters** (active/hidden)  
- **Category filters**
- **Date range filters** (before/after)
- **Text search** (quoted search terms)
- **Clear All** button to reset everything

## User Interface

### Views

- **Table View** (default): Compact list with sortable columns
- **Card View**: Visual cards with thumbnails and descriptions

### Sorting Options

- Date (newest/oldest)
- Title (A-Z, Z-A)
- Domain (A-Z, Z-A)  
- Category (A-Z, Z-A)

### Domain Filtering

Click any domain name in either view to filter gleanings to that domain only. This enables quick exploration of content from specific sites.

### Bulk Operations

- Select multiple gleanings with checkboxes
- Bulk hide/show or delete operations
- Status updates with optional reasons

## API Endpoints

### Core Endpoints

- `GET /api/gleanings` - List gleanings with filtering and pagination
- `PATCH /api/gleanings/:id/status` - Update gleaning status
- `GET /api/gleanings/stats` - System statistics (active/hidden/total counts)
- `GET /api/categories` - Available categories list

### Query Parameters

**`GET /api/gleanings` supports:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 50)
- `status` - Filter by status (`all`, `active`, `hidden`)
- `category` - Filter by category name
- `domain` - Filter by domain name
- `search` - Text search with operator support
- `sort` - Sort order (`date_desc`, `date_asc`, `title_asc`, etc.)

**Example requests:**
```bash
GET /api/gleanings?domain=github.com&status=active&page=1
GET /api/gleanings?search=domain:github.com+before:2023-01-01+typescript
```

## Architecture

### Search Query Flow

1. User enters search with operators: `domain:github.com typescript`
2. `parseSearchQuery()` in `shared/search-parser.js` extracts:
   - Operators: `{ domain: "github.com" }`
   - Text: `"typescript"`
3. Backend applies filters in `shared/gleanings-data.js`
4. Frontend displays filter chips for active filters
5. Users can remove individual filters via chip × buttons

### Key Components

**Frontend (`frontend/src/components/`):**
- `FilterBar.vue` - Main search and filter interface
- `FilterChips.vue` - Visual display of active filters
- `TableView.vue` - Table display with clickable domains
- `GleaningCard.vue` - Card display with clickable domains
- `GleaningsList.vue` - Card view container

**Backend (`backend/`):**
- `server.js` - Express routes and API endpoints
- `routes/` - API route handlers

**Shared (`shared/`):**
- `search-parser.js` - Search operator parsing utilities
- `gleanings-data.js` - Core filtering and data logic

### Data Integration

The application reads from the existing `gleanings_state.json` file and preserves all functionality of the Python-based gleanings system. Status changes are persisted back to this file.

## Development

### File Structure Details

```
frontend/src/
├── components/       # Vue components
│   ├── FilterBar.vue           # Main filtering interface
│   ├── FilterChips.vue         # Active filter display
│   ├── TableView.vue           # Table view component
│   ├── GleaningCard.vue        # Card component
│   └── GleaningsList.vue       # Card container
├── composables/      # Vue composition functions
│   └── useGleanings.js         # Main data management
└── style.css         # Global styles

backend/
├── server.js         # Main Express server
└── routes/           # API route handlers

shared/
├── search-parser.js  # Search query parsing
└── gleanings-data.js # Data filtering logic
```

### Key Implementation Notes

- **Mobile-responsive**: FilterBar adapts from desktop grid to mobile stack
- **Progressive enhancement**: Advanced features degrade gracefully
- **State management**: Vue composables handle data flow
- **Consistent styling**: Shared CSS classes and Tailwind utilities
- **Error handling**: Graceful degradation for API failures

## Implementation History

### Search Operators System
- Comprehensive search parser supporting domain, date, status, category operators
- Visual filter chips with individual removal capability
- Backward compatible with existing dropdown filters
- Override behavior: operators take precedence over dropdowns

### Domain Filtering System  
- Clickable domain names in both table and card views
- Instant filtering to show only gleanings from clicked domain
- Preserves current sorting while filtering by domain
- Clear visual feedback with hover states and tooltips

### UI/UX Improvements
- Table view set as default for better information density
- Responsive design that works on all screen sizes
- Clean, professional styling with consistent spacing
- Advanced filters available via collapsible panel (desktop) or bottom sheet (mobile)

## Testing

### Backend API Testing
```bash
# Test domain filtering
curl "http://localhost:3001/api/gleanings?domain=github.com"

# Test search operators  
curl "http://localhost:3001/api/gleanings?search=domain:github.com+before:2023-01-01"

# Test stats endpoint
curl "http://localhost:3001/api/gleanings/stats"
```

### Frontend Testing
- Search operators parse correctly and display appropriate chips
- Domain clicking filters correctly in both views
- Filter removal (individual chips and clear all) works
- Responsive design tested on various screen sizes
- Bulk operations function correctly

## Future Enhancements

Potential improvements for future development:

### Search & Filtering
- Operator autocomplete suggestions in search box
- Additional operators (`site:`, `type:`, `tag:`)
- Saved search queries/bookmarks
- Search history with quick recall

### UI/UX  
- Keyboard shortcuts for common operations
- Advanced filter presets (e.g., "This Week", "Favorites")
- Export functionality (CSV, JSON)
- Dark mode support

### Performance
- Virtual scrolling for large datasets
- Search result caching
- Progressive loading/infinite scroll
- Background data refresh

The current implementation provides a solid foundation for all these enhancements while maintaining clean, maintainable code.