import express from 'express'
import cors from 'cors'
import ogs from 'open-graph-scraper'
import { GleaningsDataManager } from '../shared/gleanings-data.js'

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors())
app.use(express.json())

// Initialize data manager
const dataManager = new GleaningsDataManager()

// Simple in-memory cache for thumbnails
const thumbnailCache = new Map()

// Routes

// Get all gleanings with optional filtering
app.get('/api/gleanings', (req, res) => {
  try {
    const { status, category, search, sort = 'date_desc', domain, page = 1, limit = 50 } = req.query
    
    const filters = {
      status: status || 'all',
      category: category || 'all',
      search: search || '',
      sort: sort || 'date_desc',
      domain: domain || 'all'
    }
    
    const allGleanings = dataManager.getAllGleanings(filters)
    
    // Pagination
    const pageNum = parseInt(page)
    const limitNum = parseInt(limit)
    const startIndex = (pageNum - 1) * limitNum
    const endIndex = startIndex + limitNum
    
    const paginatedGleanings = allGleanings.slice(startIndex, endIndex)
    
    res.json({
      gleanings: paginatedGleanings,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total: allGleanings.length,
        pages: Math.ceil(allGleanings.length / limitNum)
      }
    })
  } catch (error) {
    console.error('Error fetching gleanings:', error)
    res.status(500).json({ error: 'Failed to fetch gleanings' })
  }
})

// Bulk operations (must come before parameterized routes)
app.patch('/api/gleanings/bulk', (req, res) => {
  try {
    const { ids, status, reason } = req.body
    
    if (!Array.isArray(ids) || !['active', 'hidden'].includes(status)) {
      return res.status(400).json({ error: 'Invalid request data' })
    }
    
    const results = []
    for (const id of ids) {
      const result = dataManager.updateGleaningStatus(id, status, reason)
      results.push({ id, ...result })
    }
    
    const successCount = results.filter(r => r.success).length
    res.json({ 
      success: true, 
      processed: results.length,
      successful: successCount,
      results 
    })
  } catch (error) {
    console.error('Error in bulk operation:', error)
    res.status(500).json({ error: 'Failed to perform bulk operation' })
  }
})

// Bulk category update
app.patch('/api/gleanings/bulk/category', (req, res) => {
  try {
    const { ids, category } = req.body
    console.log('Bulk request:', { ids, category })
    
    if (!Array.isArray(ids) || !category) {
      return res.status(400).json({ error: 'Invalid request data' })
    }
    
    const results = []
    for (const id of ids) {
      console.log('Processing ID:', id, typeof id)
      const result = dataManager.updateGleaningCategory(id, category)
      console.log('Result:', result)
      results.push({ id, ...result })
    }
    
    const successCount = results.filter(r => r.success).length
    res.json({ 
      success: true, 
      processed: results.length,
      successful: successCount,
      results 
    })
  } catch (error) {
    console.error('Error in bulk category update:', error)
    res.status(500).json({ error: 'Failed to perform bulk category update' })
  }
})

// Update gleaning status
app.patch('/api/gleanings/:id/status', (req, res) => {
  try {
    const { id } = req.params
    const { status, reason } = req.body
    
    if (!['active', 'hidden'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' })
    }
    
    const result = dataManager.updateGleaningStatus(id, status, reason)
    
    if (result.success) {
      res.json({ success: true, gleaning: result.gleaning })
    } else {
      res.status(404).json({ error: result.error })
    }
  } catch (error) {
    console.error('Error updating gleaning:', error)
    res.status(500).json({ error: 'Failed to update gleaning' })
  }
})

// Update gleaning category
app.patch('/api/gleanings/:id/category', (req, res) => {
  try {
    const { id } = req.params
    const { category } = req.body
    
    const result = dataManager.updateGleaningCategory(id, category)
    
    if (result.success) {
      res.json({ success: true, gleaning: result.gleaning })
    } else {
      res.status(404).json({ error: result.error })
    }
  } catch (error) {
    console.error('Error updating category:', error)
    res.status(500).json({ error: 'Failed to update category' })
  }
})

// Get system statistics
app.get('/api/gleanings/stats', (req, res) => {
  try {
    const stats = dataManager.getStats()
    res.json(stats)
  } catch (error) {
    console.error('Error fetching stats:', error)
    res.status(500).json({ error: 'Failed to fetch statistics' })
  }
})

// Get available categories
app.get('/api/categories', (req, res) => {
  try {
    const categoriesData = dataManager.loadCategories()
    const categories = Object.keys(categoriesData.categories || {})
    res.json({ categories })
  } catch (error) {
    console.error('Error fetching categories:', error)
    res.status(500).json({ error: 'Failed to fetch categories' })
  }
})


// Get thumbnail for a URL
app.get('/api/thumbnail', async (req, res) => {
  try {
    const { url } = req.query
    
    if (!url) {
      return res.status(400).json({ error: 'URL parameter is required' })
    }

    // Check cache first
    if (thumbnailCache.has(url)) {
      return res.json(thumbnailCache.get(url))
    }

    // Try Open Graph extraction first
    try {
      const { result } = await ogs({ url })
      
      if (result.ogImage && result.ogImage.length > 0) {
        const imageUrl = result.ogImage[0].url
        // Make sure we return absolute URLs
        const absoluteImageUrl = imageUrl.startsWith('http') 
          ? imageUrl 
          : new URL(imageUrl, url).toString()
        
        const thumbnailData = { 
          thumbnail: absoluteImageUrl,
          source: 'opengraph',
          title: result.ogTitle || '',
          description: result.ogDescription || ''
        }
        
        // Cache the result
        thumbnailCache.set(url, thumbnailData)
        
        return res.json(thumbnailData)
      }
    } catch (ogError) {
      console.log('Open Graph extraction failed:', ogError.message)
    }

    // Fallback to Eleventy screenshot service (public, no auth required)
    const screenshotUrl = `https://v1.screenshot.11ty.dev/${encodeURIComponent(url)}/small/`
    
    const thumbnailData = {
      thumbnail: screenshotUrl,
      source: 'screenshot',
      title: '',
      description: ''
    }
    
    // Cache the result
    thumbnailCache.set(url, thumbnailData)
    
    return res.json(thumbnailData)
    
  } catch (error) {
    console.error('Error generating thumbnail:', error)
    res.status(500).json({ error: 'Failed to generate thumbnail' })
  }
})

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({ error: 'Something went wrong!' })
})

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Gleanings API server running on port ${PORT}`)
  console.log(`Health check: http://localhost:${PORT}/api/health`)
  console.log(`Network access: http://ningal.local:${PORT}/api/health`)
})