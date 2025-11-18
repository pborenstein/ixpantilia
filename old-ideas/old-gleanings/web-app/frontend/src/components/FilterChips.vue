<template>
  <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mt-4 mb-2">
    <!-- Domain Filter Chips -->
    <template v-if="activeFilters.domain && activeFilters.domain !== 'all'">
      <div 
        v-if="Array.isArray(activeFilters.domain)"
        v-for="domain in activeFilters.domain"
        :key="domain"
        class="filter-chip"
      >
        <span class="chip-icon">🌐</span>
        <span>{{ domain }}</span>
        <button 
          @click="removeSpecificFilter('domain', domain)"
          class="chip-remove"
          title="Remove this domain filter"
        >
          ×
        </button>
      </div>
      <div 
        v-else
        class="filter-chip"
      >
        <span class="chip-icon">🌐</span>
        <span>{{ activeFilters.domain }}</span>
        <button 
          @click="removeFilter('domain')"
          class="chip-remove"
          title="Remove domain filter"
        >
          ×
        </button>
      </div>
    </template>

    <!-- Status Filter Chip -->
    <div 
      v-if="activeFilters.status && activeFilters.status !== 'all'"
      class="filter-chip"
    >
      <span class="chip-icon">{{ statusIcon(activeFilters.status) }}</span>
      <span>{{ activeFilters.status }}</span>
      <button 
        @click="removeFilter('status')"
        class="chip-remove"
        title="Remove status filter"
      >
        ×
      </button>
    </div>

    <!-- Category Filter Chips -->
    <template v-if="activeFilters.category && activeFilters.category !== 'all'">
      <div 
        v-if="Array.isArray(activeFilters.category)"
        v-for="category in activeFilters.category"
        :key="category"
        class="filter-chip"
      >
        <span class="chip-icon">🏷️</span>
        <span>{{ category }}</span>
        <button 
          @click="removeSpecificFilter('category', category)"
          class="chip-remove"
          title="Remove this category filter"
        >
          ×
        </button>
      </div>
      <div 
        v-else
        class="filter-chip"
      >
        <span class="chip-icon">🏷️</span>
        <span>{{ activeFilters.category }}</span>
        <button 
          @click="removeFilter('category')"
          class="chip-remove"
          title="Remove category filter"
        >
          ×
        </button>
      </div>
    </template>

    <!-- Date Range Filter Chips -->
    <div 
      v-if="activeFilters.before"
      class="filter-chip"
    >
      <span class="chip-icon">📅</span>
      <span>before {{ activeFilters.before }}</span>
      <button 
        @click="removeFilter('before')"
        class="chip-remove"
        title="Remove before date filter"
      >
        ×
      </button>
    </div>

    <div 
      v-if="activeFilters.after"
      class="filter-chip"
    >
      <span class="chip-icon">📅</span>
      <span>after {{ activeFilters.after }}</span>
      <button 
        @click="removeFilter('after')"
        class="chip-remove"
        title="Remove after date filter"
      >
        ×
      </button>
    </div>

    <!-- Text Search Filter Chip -->
    <div 
      v-if="activeFilters.text"
      class="filter-chip"
    >
      <span class="chip-icon">🔍</span>
      <span>"{{ activeFilters.text }}"</span>
      <button 
        @click="removeFilter('text')"
        class="chip-remove"
        title="Remove text search"
      >
        ×
      </button>
    </div>

    <!-- Clear All Button -->
    <button 
      @click="clearAllFilters"
      class="clear-all-btn"
      title="Clear all filters"
    >
      Clear All
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { parseSearchQuery, buildSearchQuery } from '../../../shared/search-parser.js'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-filters'])

// Parse current filters to extract operators and text
const activeFilters = computed(() => {
  const result = {
    domain: props.filters.domain,
    status: props.filters.status,
    category: props.filters.category
  }
  
  // Parse search query for operators and text
  if (props.filters.search) {
    const parsed = parseSearchQuery(props.filters.search)
    Object.assign(result, parsed.operators)
    if (parsed.text) {
      result.text = parsed.text
    }
  }
  
  return result
})

// Check if there are any active filters
const hasActiveFilters = computed(() => {
  return Object.entries(activeFilters.value).some(([key, value]) => {
    return value && value !== 'all' && value !== ''
  })
})

// Get appropriate icon for status
const statusIcon = (status) => {
  switch (status) {
    case 'active': return '✅'
    case 'hidden': return '🔒'
    default: return '📋'
  }
}

// Remove specific filter
const removeFilter = (filterType) => {
  const newFilters = { ...props.filters }
  
  if (['domain', 'status', 'category'].includes(filterType)) {
    // Remove dropdown filters
    newFilters[filterType] = 'all'
  } else if (['before', 'after', 'text'].includes(filterType)) {
    // Remove search operators
    const parsed = parseSearchQuery(props.filters.search || '')
    const operators = { ...parsed.operators }
    
    if (filterType === 'text') {
      // Remove text, keep operators
      newFilters.search = buildSearchQuery(operators, '')
    } else {
      // Remove specific operator
      delete operators[filterType]
      newFilters.search = buildSearchQuery(operators, parsed.text)
    }
  }
  
  emit('update-filters', newFilters)
}

// Remove specific item from multi-select filter
const removeSpecificFilter = (filterType, valueToRemove) => {
  const newFilters = { ...props.filters }
  const parsed = parseSearchQuery(props.filters.search || '')
  const operators = { ...parsed.operators }
  
  if (operators[filterType] && Array.isArray(operators[filterType])) {
    // Remove specific value from array
    const updatedArray = operators[filterType].filter(value => value !== valueToRemove)
    
    if (updatedArray.length === 0) {
      // If array is empty, remove the operator entirely
      delete operators[filterType]
    } else if (updatedArray.length === 1) {
      // If only one item left, convert back to string
      operators[filterType] = updatedArray[0]
    } else {
      // Keep as array
      operators[filterType] = updatedArray
    }
    
    newFilters.search = buildSearchQuery(operators, parsed.text)
  }
  
  emit('update-filters', newFilters)
}

// Clear all filters
const clearAllFilters = () => {
  emit('update-filters', {
    status: 'all',
    category: 'all',
    search: '',
    sort: props.filters.sort || 'date_desc',
    domain: 'all'
  })
}
</script>

<style scoped>
.filter-chip {
  @apply inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs border border-blue-200;
}

.chip-icon {
  @apply text-xs;
}

.chip-remove {
  @apply ml-1 text-blue-600 hover:text-blue-800 hover:bg-blue-200 rounded w-4 h-4 flex items-center justify-center text-xs font-bold transition-colors;
}

.clear-all-btn {
  @apply inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs border border-gray-200 hover:bg-gray-200 transition-colors;
}
</style>