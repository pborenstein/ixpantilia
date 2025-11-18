import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'
import { parseSearchQuery, validateOperators } from './search-parser.js'

export class GleaningsDataManager {
  constructor() {
    // Resolve paths relative to the gleanings directory (parent of web-app)
    const currentDir = path.dirname(decodeURIComponent(new URL(import.meta.url).pathname))
    const gleaningsDir = path.resolve(currentDir, '..', '..')
    this.stateFile = path.join(gleaningsDir, 'gleanings_state.json')
    this.categoriesFile = path.join(gleaningsDir, 'categories.yaml')
  }

  loadState() {
    try {
      const data = fs.readFileSync(this.stateFile, 'utf8')
      return JSON.parse(data)
    } catch (error) {
      console.error('Error loading state:', error)
      return { gleanings: {}, version: '2.0' }
    }
  }

  saveState(state) {
    try {
      // Create backup
      this.createBackup()
      
      // Update timestamp
      state.last_updated = new Date().toISOString()
      
      fs.writeFileSync(this.stateFile, JSON.stringify(state, null, 2))
      return true
    } catch (error) {
      console.error('Error saving state:', error)
      return false
    }
  }

  createBackup() {
    try {
      const backupDir = path.join(path.dirname(this.stateFile), 'backups')
      if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true })
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15)
      const backupFile = path.join(backupDir, `gleanings_state_${timestamp}.json`)
      
      if (fs.existsSync(this.stateFile)) {
        fs.copyFileSync(this.stateFile, backupFile)
      }
    } catch (error) {
      console.error('Error creating backup:', error)
    }
  }

  loadCategories() {
    try {
      const data = fs.readFileSync(this.categoriesFile, 'utf8')
      return yaml.load(data)
    } catch (error) {
      console.error('Error loading categories:', error)
      return { categories: {} }
    }
  }

  getAllGleanings(filters = {}) {
    const state = this.loadState()
    let gleanings = Object.values(state.gleanings || {})
    
    // Parse search query for operators
    let searchOperators = {}
    let searchText = ''
    
    if (filters.search) {
      const parsed = parseSearchQuery(filters.search)
      const validated = validateOperators(parsed.operators)
      searchOperators = validated.operators
      searchText = parsed.text
    }
    
    // Apply filters
    gleanings = gleanings.filter(gleaning => {
      // Status filter (from both dropdown and search operators)
      const statusFilter = searchOperators.status || filters.status
      if (statusFilter && statusFilter !== 'all') {
        const userStatus = gleaning.user_status || 'active'
        if (statusFilter === 'active' && userStatus !== 'active') return false
        if (statusFilter === 'hidden' && userStatus !== 'hidden') return false
      }
      
      // Category filter (from both dropdown and search operators)
      const categoryFilter = searchOperators.category || filters.category
      if (categoryFilter && categoryFilter !== 'all') {
        if (Array.isArray(categoryFilter)) {
          // Multi-category filtering
          if (!categoryFilter.includes(gleaning.category)) return false
        } else {
          // Single category filtering
          if (gleaning.category !== categoryFilter) return false
        }
      }
      
      // Domain filter (from both dropdown and search operators)
      const domainFilter = searchOperators.domain || filters.domain
      if (domainFilter && domainFilter !== 'all') {
        if (Array.isArray(domainFilter)) {
          // Multi-domain filtering
          if (!domainFilter.includes(gleaning.domain)) return false
        } else {
          // Single domain filtering
          if (gleaning.domain !== domainFilter) return false
        }
      }
      
      // Date range filters
      if (searchOperators.before) {
        const gleaningDate = gleaning.date || '1970-01-01'
        if (gleaningDate >= searchOperators.before) return false
      }
      
      if (searchOperators.after) {
        const gleaningDate = gleaning.date || '1970-01-01'
        if (gleaningDate <= searchOperators.after) return false
      }
      
      // Text search filter (search remaining text after operators are extracted)
      if (searchText) {
        const searchTerm = searchText.toLowerCase()
        const searchableText = [
          gleaning.title || '',
          gleaning.description || '',
          gleaning.url || '',
          gleaning.domain || '',
          gleaning.category || ''
        ].join(' ').toLowerCase()
        
        if (!searchableText.includes(searchTerm)) return false
      }
      
      return true
    })
    
    // Apply sorting (default to date_desc if no sort specified)
    const sortOption = filters.sort || 'date_desc'
    const [field, order] = sortOption.split('_')
    const ascending = order === 'asc'
    
    if (field && order) {
      gleanings.sort((a, b) => {
        let valueA, valueB
        
        switch (field) {
          case 'date':
            // Sort by date + timestamp for precise ordering
            try {
              const dateA = a.date || '1970-01-01'
              const timeA = a.timestamp || '00:00'
              const dateB = b.date || '1970-01-01'
              const timeB = b.timestamp || '00:00'
              
              // Clean and normalize timestamps - fix corrupted data
              const cleanTimeA = timeA === 'unknown' || !timeA || !timeA.includes(':') || timeA.includes(']') || timeA.includes('[') ? '00:00' : timeA.trim()
              const cleanTimeB = timeB === 'unknown' || !timeB || !timeB.includes(':') || timeB.includes(']') || timeB.includes('[') ? '00:00' : timeB.trim()
              
              // Ensure timestamp has seconds (HH:MM -> HH:MM:00)
              const timeAFull = cleanTimeA.includes(':') && cleanTimeA.split(':').length === 2 ? `${cleanTimeA}:00` : '00:00:00'
              const timeBFull = cleanTimeB.includes(':') && cleanTimeB.split(':').length === 2 ? `${cleanTimeB}:00` : '00:00:00'
              
              // Create ISO date strings for reliable parsing
              const isoA = `${dateA}T${timeAFull}`
              const isoB = `${dateB}T${timeBFull}`
              
              valueA = new Date(isoA).getTime()
              valueB = new Date(isoB).getTime()
              
              // Critical fix: Handle NaN values properly to prevent sort corruption
              if (isNaN(valueA) && isNaN(valueB)) {
                // Both invalid, fall back to string comparison
                valueA = dateA
                valueB = dateB
              } else if (isNaN(valueA)) {
                // A is invalid, B is valid - A should be treated as very old
                valueA = 0
              } else if (isNaN(valueB)) {
                // B is invalid, A is valid - B should be treated as very old
                valueB = 0
              }
              // If both are valid numbers, use them as-is
              
            } catch (error) {
              // Fallback to string comparison
              valueA = a.date || ''
              valueB = b.date || ''
            }
            break
          case 'title':
            valueA = (a.title || '').toLowerCase()
            valueB = (b.title || '').toLowerCase()
            break
          case 'domain':
            valueA = (a.domain || '').toLowerCase()
            valueB = (b.domain || '').toLowerCase()
            break
          case 'category':
            valueA = (a.category || '').toLowerCase()
            valueB = (b.category || '').toLowerCase()
            break
          default:
            return 0
        }
        
        if (valueA < valueB) return ascending ? -1 : 1
        if (valueA > valueB) return ascending ? 1 : -1
        return 0
      })
    }
    
    return gleanings
  }

  updateGleaningStatus(id, status, reason = '') {
    const state = this.loadState()
    
    if (!state.gleanings[id]) {
      return { success: false, error: 'Gleaning not found' }
    }
    
    // Update gleaning status
    state.gleanings[id].user_status = status
    state.gleanings[id].last_modified = new Date().toISOString()
    
    // Record user action
    if (!state.user_actions) {
      state.user_actions = {}
    }
    
    state.user_actions[id] = {
      action: status,
      timestamp: new Date().toISOString(),
      reason: reason
    }
    
    const success = this.saveState(state)
    return { success, gleaning: state.gleanings[id] }
  }

  updateGleaningCategory(id, category) {
    const state = this.loadState()
    
    console.log('updateGleaningCategory called with:', { id, type: typeof id, category })
    console.log('Available IDs sample:', Object.keys(state.gleanings || {}).slice(0, 3))
    
    if (!state.gleanings[id]) {
      console.log('Gleaning not found for ID:', id, 'Type:', typeof id)
      return { success: false, error: 'Gleaning not found' }
    }
    
    // Update gleaning category
    state.gleanings[id].category = category || ''
    state.gleanings[id].last_modified = new Date().toISOString()
    
    // Record user action
    if (!state.user_actions) {
      state.user_actions = {}
    }
    
    state.user_actions[id] = {
      action: 'category_update',
      timestamp: new Date().toISOString(),
      reason: `Changed category to: ${category || 'Uncategorized'}`
    }
    
    const success = this.saveState(state)
    return { success, gleaning: state.gleanings[id] }
  }

  getStats() {
    const state = this.loadState()
    const gleanings = Object.values(state.gleanings || {})
    
    const stats = {
      total: gleanings.length,
      active: 0,
      hidden: 0,
      categories: {},
      domains: {}
    }
    
    gleanings.forEach(gleaning => {
      const status = gleaning.user_status || 'active'
      stats[status]++
      
      // Category stats
      const category = gleaning.category || 'Uncategorized'
      stats.categories[category] = (stats.categories[category] || 0) + 1
      
      // Domain stats  
      const domain = gleaning.domain || 'Unknown'
      stats.domains[domain] = (stats.domains[domain] || 0) + 1
    })
    
    return stats
  }
}