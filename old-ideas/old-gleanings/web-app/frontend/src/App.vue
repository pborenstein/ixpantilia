<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <h1 class="text-2xl font-bold text-gray-900">Gleanings Manager</h1>
          <StatsDisplay :stats="stats" />
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <FilterBar 
        :filters="filters"
        :categories="categories"
        :available-tags="availableTags"
        :category-counts="stats.categories || {}"
        :domain-counts="stats.domains || {}"
        :loading="loading"
        :view="currentView"
        @update-filters="setFilters"
        @refresh="handleRefresh"
        @view-change="handleViewChange"
      />
      
      <GleaningsList 
        v-if="currentView === 'cards'"
        :gleanings="gleanings"
        :loading="loading"
        :error="error"
        :pagination="pagination"
        :categories="categories"
        :selected-ids="selectedIds"
        :selected-category="selectedCategory"
        @update-status="handleUpdateStatus"
        @bulk-update="handleBulkUpdate"
        @bulk-set-category="handleBulkSetCategory"
        @toggle-selection="toggleSelection"
        @clear-selection="clearSelection"
        @update-category-selection="handleCategorySelection"
        @page-change="setPage"
        @view-details="handleViewDetails"
        @edit-category="handleEditCategory"
        @domain-sort="handleDomainSort"
        @tag-filter="handleTagFilter"
      />
      
      <TableView
        v-else-if="currentView === 'table'"
        :gleanings="gleanings"
        :loading="loading"
        :error="error"
        :pagination="pagination"
        :categories="categories"
        :selected-ids="selectedIds"
        :selected-category="selectedCategory"
        @update-status="handleUpdateStatus"
        @bulk-update="handleBulkUpdate"
        @bulk-set-category="handleBulkSetCategory"
        @toggle-selection="toggleSelection"
        @toggle-all-selection="toggleAllSelection"
        @clear-selection="clearSelection"
        @update-category-selection="handleCategorySelection"
        @page-change="setPage"
        @view-details="handleViewDetails"
        @edit-category="handleEditCategory"
        @domain-sort="handleDomainSort"
        @tag-filter="handleTagFilter"
      />
    </main>

    <!-- Details Modal -->
    <DetailModal 
      v-if="showDetailsModal"
      :gleaning="selectedGleaning"
      @close="showDetailsModal = false"
    />

    <!-- Category Edit Modal -->
    <CategoryEditModal 
      v-if="showCategoryModal"
      :gleaning="selectedGleaning"
      :categories="categories"
      @close="showCategoryModal = false"
      @save="handleCategoryUpdate"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useGleanings } from './composables/useGleanings.js'
import FilterBar from './components/FilterBar.vue'
import GleaningsList from './components/GleaningsList.vue'
import TableView from './components/TableView.vue'
import StatsDisplay from './components/StatsDisplay.vue'
import DetailModal from './components/DetailModal.vue'
import CategoryEditModal from './components/CategoryEditModal.vue'

const {
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
} = useGleanings()

const showDetailsModal = ref(false)
const showCategoryModal = ref(false)
const selectedGleaning = ref(null)
const currentView = ref('table')

// Centralized selection state
const selectedIds = ref([])
const selectedCategory = ref('')

// Selection management functions
const toggleSelection = (id) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const clearSelection = () => {
  selectedIds.value = []
  selectedCategory.value = ''
}

const toggleAllSelection = () => {
  if (selectedIds.value.length === gleanings.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = gleanings.value.map(g => g.id)
  }
}

const handleUpdateStatus = async (id, status, reason) => {
  const result = await updateGleaningStatus(id, status, reason)
  if (result.success) {
    await fetchStats() // Refresh stats
  }
  return result
}

const handleBulkUpdate = async (ids, status, reason) => {
  try {
    const result = await bulkUpdateStatus(ids, status, reason)
    await fetchStats() // Refresh stats
    clearSelection() // Clear selection after successful bulk update
    return result
  } catch (error) {
    throw error
  }
}

const handleBulkSetCategory = async (ids, category) => {
  try {
    const result = await bulkUpdateCategory(ids, category)
    await fetchStats() // Refresh stats
    clearSelection() // Clear selection after successful bulk update
    return result
  } catch (error) {
    alert(`Failed to update categories: ${error.message}`)
    throw error
  }
}

const handleRefresh = async () => {
  await Promise.all([
    fetchGleanings(),
    fetchStats(),
    fetchCategories(),
    fetchTags()
  ])
}

const handleViewDetails = (gleaning) => {
  selectedGleaning.value = gleaning
  showDetailsModal.value = true
}

const handleEditCategory = (gleaning) => {
  selectedGleaning.value = gleaning
  showCategoryModal.value = true
}

const handleCategoryUpdate = async (gleaning, newCategory) => {
  try {
    await updateGleaningCategory(gleaning.id, newCategory)
    showCategoryModal.value = false
    await fetchGleanings() // Refresh list
  } catch (error) {
    alert(`Failed to update category: ${error.message}`)
  }
}

const handleViewChange = (view) => {
  currentView.value = view
}

const handleDomainSort = (domain) => {
  // Filter to show only gleanings from this domain
  setFilters({ domain: domain })
}

const handleTagFilter = (tag) => {
  // Filter to show only gleanings with this tag
  setFilters({ tag: tag })
}

const handleCategorySelection = (category) => {
  selectedCategory.value = category
}

onMounted(async () => {
  await handleRefresh()
})
</script>