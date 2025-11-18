import { ref, reactive } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export function useGleanings() {
  const gleanings = ref([])
  const loading = ref(false)
  const error = ref(null)
  const stats = ref({})
  const categories = ref([])
  const availableTags = ref([])
  
  const pagination = reactive({
    page: 1,
    limit: 50,
    total: 0,
    pages: 0
  })
  
  const filters = reactive({
    status: 'all',
    category: 'all',
    tag: 'all',
    search: '',
    sort: 'date_desc',
    domain: 'all'
  })

  const fetchGleanings = async () => {
    loading.value = true
    error.value = null
    
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...filters
      }
      
      const response = await api.get('/gleanings', { params })
      gleanings.value = response.data.gleanings
      Object.assign(pagination, response.data.pagination)
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch gleanings'
      console.error('Error fetching gleanings:', err)
    } finally {
      loading.value = false
    }
  }

  const updateGleaningStatus = async (id, status, reason = '') => {
    try {
      const response = await api.patch(`/gleanings/${id}/status`, { status, reason })
      
      // Update local state
      const index = gleanings.value.findIndex(g => g.id === id)
      if (index !== -1) {
        gleanings.value[index] = response.data.gleaning
      }
      
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to update gleaning'
      console.error('Error updating gleaning:', err)
      return { success: false, error: message }
    }
  }

  const updateGleaningCategory = async (id, category) => {
    try {
      const response = await api.patch(`/gleanings/${id}/category`, { category })
      
      // Update local state
      const index = gleanings.value.findIndex(g => g.id === id)
      if (index !== -1) {
        gleanings.value[index] = response.data.gleaning
      }
      
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to update category'
      console.error('Error updating category:', err)
      return { success: false, error: message }
    }
  }

  const bulkUpdateStatus = async (ids, status, reason = '') => {
    try {
      const response = await api.patch('/gleanings/bulk', { ids, status, reason })
      
      // Refresh the list to get updated data
      await fetchGleanings()
      
      return response.data
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to perform bulk update'
      console.error('Error in bulk update:', err)
      throw new Error(message)
    }
  }

  const bulkUpdateCategory = async (ids, category) => {
    try {
      const response = await api.patch('/gleanings/bulk/category', { ids, category })
      
      // Refresh the list to get updated data
      await fetchGleanings()
      
      return response.data
    } catch (err) {
      const message = err.response?.data?.error || 'Failed to perform bulk category update'
      console.error('Error in bulk category update:', err)
      throw new Error(message)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/gleanings/stats')
      stats.value = response.data
    } catch (err) {
      console.error('Error fetching stats:', err)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories')
      categories.value = response.data.categories
    } catch (err) {
      console.error('Error fetching categories:', err)
    }
  }

  const fetchTags = async () => {
    try {
      const response = await api.get('/tags')
      availableTags.value = response.data.tags
    } catch (err) {
      console.error('Error fetching tags:', err)
    }
  }

  const setFilters = (newFilters) => {
    Object.assign(filters, newFilters)
    pagination.page = 1 // Reset to first page when filters change
    fetchGleanings()
  }

  const setPage = (page) => {
    pagination.page = page
    fetchGleanings()
  }

  return {
    gleanings,
    loading,
    error,
    stats,
    categories,
    availableTags,
    pagination,
    filters,
    fetchGleanings,
    updateGleaningStatus,
    updateGleaningCategory,
    bulkUpdateStatus,
    bulkUpdateCategory,
    fetchStats,
    fetchCategories,
    fetchTags,
    setFilters,
    setPage
  }
}