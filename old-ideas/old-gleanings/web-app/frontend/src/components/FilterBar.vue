<template>
  <div class="card mb-4">
    <!-- Unified Responsive Layout -->
    <div class="space-y-4">
      <!-- Search Row -->
      <div class="mb-3">
        <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
        <input 
          v-model="localFilters.search"
          type="text" 
          placeholder="Search or use operators: domain:github.com" 
          class="input w-full"
          @input="debouncedUpdate"
        />
      </div>
      
      <!-- Filters Row -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
          <select 
            v-model="localFilters.status" 
            class="input w-full"
            @change="() => updateFilters()"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="hidden">Hidden</option>
          </select>
        </div>
        
        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
          <select 
            v-model="localFilters.category" 
            class="input w-full"
            @change="() => updateFilters()"
          >
            <option value="all">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        
        <!-- Tag Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tag</label>
          <select 
            v-model="localFilters.tag" 
            class="input w-full"
            @change="() => updateFilters()"
          >
            <option value="all">All Tags</option>
            <option v-for="tag in availableTags" :key="tag" :value="tag">
              #{{ tag }}
            </option>
          </select>
        </div>
        
        <!-- Sort Options -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Sort</label>
          <select 
            v-model="localFilters.sort" 
            class="input w-full"
            @change="() => updateFilters()"
          >
            <option value="date_desc">Date ↓</option>
            <option value="date_asc">Date ↑</option>
            <option value="title_asc">Title ↑</option>
            <option value="title_desc">Title ↓</option>
            <option value="domain_asc">Domain ↑</option>
            <option value="domain_desc">Domain ↓</option>
            <option value="category_asc">Category ↑</option>
            <option value="category_desc">Category ↓</option>
          </select>
        </div>
        
        <!-- Actions -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Actions</label>
          <div class="flex gap-1">
            <!-- View Toggle -->
            <div class="flex bg-gray-100 rounded border border-gray-300 text-xs">
              <button 
                @click="$emit('view-change', 'cards')"
                class="px-2 py-2 font-medium rounded-l transition-colors"
                :class="view === 'cards' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              >
                Cards
              </button>
              <button 
                @click="$emit('view-change', 'table')"
                class="px-2 py-2 font-medium rounded-r transition-colors"
                :class="view === 'table' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              >
                Table
              </button>
            </div>
            
            <button 
              @click="clearFilters" 
              class="px-2 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
              :disabled="loading"
            >
              Clear
            </button>
            <button 
              @click="$emit('refresh')" 
              class="px-2 py-2 text-xs font-medium text-white bg-blue-600 border border-transparent rounded hover:bg-blue-700 transition-colors"
              :disabled="loading"
            >
              {{ loading ? '...' : 'Refresh' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Filter Chips -->
    <FilterChips 
      :filters="localFilters"
      @update-filters="updateFilters"
    />
    
    <!-- Desktop Advanced Filter Panel -->
    <div class="hidden lg:block">
      <FilterPanel
        :available-categories="categories"
        :category-counts="categoryCounts"
        :domain-counts="domainCounts"
        :selected-categories="selectedCategories"
        :selected-domains="selectedDomains"
        :after-date="afterDate"
        :before-date="beforeDate"
        @update:selected-categories="updateSelectedCategories"
        @update:selected-domains="updateSelectedDomains"
        @update:after-date="updateAfterDate"
        @update:before-date="updateBeforeDate"
        @apply-filters="applyAdvancedFilters"
        @clear-filters="clearAdvancedFilters"
      />
    </div>
    
    <!-- Mobile Filter Sheet for Advanced Filters -->
    <MobileFilterSheet
      :filters="localFilters"
      :available-categories="categories"
      :category-counts="categoryCounts"
      :domain-counts="domainCounts"
      @update-filters="updateFilters"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import FilterChips from './FilterChips.vue'
import FilterPanel from './FilterPanel.vue'
import MobileFilterSheet from './MobileFilterSheet.vue'
import { buildSearchQuery } from '../../../shared/search-parser.js'

const props = defineProps({
  filters: Object,
  categories: Array,
  categoryCounts: Object,
  domainCounts: Object,
  availableTags: Array,
  loading: Boolean,
  view: String
})

const emit = defineEmits(['update-filters', 'refresh', 'view-change'])

const localFilters = ref({ ...props.filters })

// Advanced filter state
const selectedCategories = ref([])
const selectedDomains = ref([])
const afterDate = ref('')
const beforeDate = ref('')

// Debounced search
let searchTimeout = null
const debouncedUpdate = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    updateFilters()
  }, 300)
}

const updateFilters = (newFilters) => {
  if (newFilters) {
    // Called from FilterChips component
    localFilters.value = { ...newFilters }
  }
  emit('update-filters', { ...localFilters.value })
}

const clearFilters = () => {
  localFilters.value = {
    status: 'all',
    category: 'all',
    tag: 'all',
    search: '',
    sort: 'date_desc',
    domain: 'all'
  }
  // Clear advanced filters too
  selectedCategories.value = []
  selectedDomains.value = []
  afterDate.value = ''
  beforeDate.value = ''
  updateFilters()
}

// Advanced filter methods
const updateSelectedCategories = (categories) => {
  selectedCategories.value = categories
}

const updateSelectedDomains = (domains) => {
  selectedDomains.value = domains
}

const updateAfterDate = (date) => {
  afterDate.value = date
}

const updateBeforeDate = (date) => {
  beforeDate.value = date
}

const applyAdvancedFilters = () => {
  // Convert advanced filters to search operators
  const operators = {}
  
  if (selectedCategories.value.length > 0) {
    operators.category = selectedCategories.value.length === 1 
      ? selectedCategories.value[0] 
      : selectedCategories.value
  }
  
  if (selectedDomains.value.length > 0) {
    operators.domain = selectedDomains.value.length === 1 
      ? selectedDomains.value[0] 
      : selectedDomains.value
  }
  
  if (afterDate.value) {
    operators.after = afterDate.value
  }
  
  if (beforeDate.value) {
    operators.before = beforeDate.value
  }
  
  // Build search query with operators
  const searchQuery = buildSearchQuery(operators, '')
  
  // Update local filters
  localFilters.value = {
    ...localFilters.value,
    search: searchQuery,
    category: 'all', // Reset dropdown since using advanced filters
    domain: 'all'    // Reset dropdown since using advanced filters  
  }
  
  updateFilters()
}

const clearAdvancedFilters = () => {
  selectedCategories.value = []
  selectedDomains.value = []
  afterDate.value = ''
  beforeDate.value = ''
  
  // Clear search operators but keep text search
  localFilters.value = {
    ...localFilters.value,
    search: '',
    category: 'all',
    tag: 'all',
    domain: 'all'
  }
  
  updateFilters()
}

// Sync with parent filters
watch(
  () => props.filters,
  (newFilters) => {
    localFilters.value = { ...newFilters }
  },
  { deep: true }
)
</script>

