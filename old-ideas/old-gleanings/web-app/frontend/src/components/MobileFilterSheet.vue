<template>
  <div>
    <!-- Mobile Filter Trigger Button -->
    <button
      @click="openSheet"
      class="fixed bottom-6 right-6 z-40 lg:hidden bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 transition-all"
      :class="{ 'bg-blue-700': hasActiveFilters }"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
      </svg>
      <span v-if="activeFilterCount > 0" class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
        {{ activeFilterCount }}
      </span>
    </button>

    <!-- Bottom Sheet Overlay -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 lg:hidden"
      @click="closeSheet"
    >
      <div class="absolute inset-0 bg-black bg-opacity-50 transition-opacity"></div>
    </div>

    <!-- Bottom Sheet -->
    <div
      v-if="isOpen"
      class="fixed bottom-0 left-0 right-0 z-50 lg:hidden bg-white rounded-t-xl shadow-xl transform transition-transform duration-300"
      :class="{ 'translate-y-0': isOpen, 'translate-y-full': !isOpen }"
      @click.stop
    >
      <!-- Sheet Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <div class="flex items-center gap-3">
          <h2 class="text-lg font-semibold text-gray-900">Filters</h2>
          <span v-if="activeFilterCount > 0" class="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full">
            {{ activeFilterCount }} active
          </span>
        </div>
        <button
          @click="closeSheet"
          class="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Sheet Content -->
      <div class="max-h-96 overflow-y-auto">
        <!-- Quick Actions -->
        <div class="p-4 border-b border-gray-100">
          <div class="flex gap-2">
            <button
              @click="clearAllFilters"
              class="flex-1 px-4 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              :disabled="activeFilterCount === 0"
            >
              Clear All
            </button>
            <button
              @click="applyAndClose"
              class="flex-1 px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        <!-- Filter Sections -->
        <div class="space-y-0">
          <!-- Status Filter -->
          <div class="p-4 border-b border-gray-100">
            <label class="block text-sm font-medium text-gray-700 mb-3">Status</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                @click="updateStatus('all')"
                class="filter-option-button"
                :class="{ 'filter-option-active': localFilters.status === 'all', 'filter-option-inactive': localFilters.status !== 'all' }"
              >
                All
              </button>
              <button
                @click="updateStatus('active')"
                class="filter-option-button"
                :class="{ 'filter-option-active': localFilters.status === 'active', 'filter-option-inactive': localFilters.status !== 'active' }"
              >
                Active
              </button>
              <button
                @click="updateStatus('hidden')"
                class="filter-option-button"
                :class="{ 'filter-option-active': localFilters.status === 'hidden', 'filter-option-inactive': localFilters.status !== 'hidden' }"
              >
                Hidden
              </button>
            </div>
          </div>

          <!-- Categories -->
          <div class="p-4 border-b border-gray-100">
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm font-medium text-gray-700">Categories</label>
              <button
                @click="clearCategories"
                class="text-xs text-blue-600 hover:text-blue-800"
                v-if="selectedCategories.length > 0"
              >
                Clear ({{ selectedCategories.length }})
              </button>
            </div>
            
            <div class="grid grid-cols-2 gap-2">
              <label
                v-for="category in availableCategories"
                :key="category"
                class="mobile-checkbox-label"
              >
                <input
                  type="checkbox"
                  :checked="selectedCategories.includes(category)"
                  @change="toggleCategory(category)"
                  class="mobile-checkbox"
                />
                <div class="mobile-checkbox-content">
                  <span class="text-sm font-medium">{{ category }}</span>
                  <span class="text-xs text-gray-500">({{ categoryCounts[category] || 0 }})</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Domains -->
          <div class="p-4 border-b border-gray-100">
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm font-medium text-gray-700">Domains</label>
              <button
                @click="clearDomains"
                class="text-xs text-blue-600 hover:text-blue-800"
                v-if="selectedDomains.length > 0"
              >
                Clear ({{ selectedDomains.length }})
              </button>
            </div>
            
            <!-- Popular domains as chips -->
            <div class="mb-3">
              <div class="text-xs text-gray-500 mb-2">Popular</div>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="domain in topDomains.slice(0, 6)"
                  :key="domain.name"
                  @click="toggleDomain(domain.name)"
                  class="mobile-domain-chip"
                  :class="{ 'mobile-domain-chip-active': selectedDomains.includes(domain.name), 'mobile-domain-chip-inactive': !selectedDomains.includes(domain.name) }"
                >
                  <span class="font-medium">{{ domain.name.split('.')[0] }}</span>
                  <span class="text-xs opacity-75">({{ domain.count }})</span>
                </button>
              </div>
            </div>
            
            <!-- Show more toggle -->
            <button
              @click="showAllDomains = !showAllDomains"
              class="text-sm text-blue-600 hover:text-blue-800 font-medium w-full text-left"
              v-if="allDomains.length > 6"
            >
              {{ showAllDomains ? 'Show Less' : `Show All (${allDomains.length - 6} more)` }}
            </button>
            
            <!-- All domains list -->
            <div v-if="showAllDomains && allDomains.length > 6" class="mt-3 max-h-32 overflow-y-auto">
              <div class="space-y-1">
                <label
                  v-for="domain in allDomains.slice(6)"
                  :key="domain.name"
                  class="mobile-checkbox-label-compact"
                >
                  <input
                    type="checkbox"
                    :checked="selectedDomains.includes(domain.name)"
                    @change="toggleDomain(domain.name)"
                    class="mobile-checkbox-small"
                  />
                  <div class="flex-1 flex items-center justify-between min-w-0">
                    <span class="text-sm truncate">{{ domain.name }}</span>
                    <span class="text-xs text-gray-500 ml-2">({{ domain.count }})</span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Date Range -->
          <div class="p-4">
            <label class="block text-sm font-medium text-gray-700 mb-3">Date Range</label>
            
            <!-- Quick presets -->
            <div class="grid grid-cols-3 gap-2 mb-4">
              <button
                v-for="preset in datePresets"
                :key="preset.label"
                @click="applyDatePreset(preset)"
                class="mobile-date-preset"
                :class="{ 'mobile-date-preset-active': isDatePresetActive(preset), 'mobile-date-preset-inactive': !isDatePresetActive(preset) }"
              >
                {{ preset.label }}
              </button>
            </div>
            
            <!-- Custom date inputs -->
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">After</label>
                <input
                  v-model="afterDate"
                  type="date"
                  class="mobile-date-input"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Before</label>
                <input
                  v-model="beforeDate"
                  type="date"
                  class="mobile-date-input"
                />
              </div>
            </div>
            
            <!-- Clear dates -->
            <button
              v-if="afterDate || beforeDate"
              @click="clearDates"
              class="mt-3 text-sm text-blue-600 hover:text-blue-800"
            >
              Clear Dates
            </button>
          </div>
        </div>
      </div>

      <!-- Bottom Actions -->
      <div class="p-4 border-t border-gray-200 bg-gray-50">
        <div class="flex gap-3">
          <button
            @click="closeSheet"
            class="flex-1 px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="applyAndClose"
            class="flex-1 px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Apply & Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { buildSearchQuery } from '../../../shared/search-parser.js'

const props = defineProps({
  filters: Object,
  availableCategories: Array,
  categoryCounts: Object,
  domainCounts: Object
})

const emit = defineEmits(['update-filters', 'apply-filters'])

const isOpen = ref(false)
const showAllDomains = ref(false)

// Local filter state
const localFilters = ref({ ...props.filters })
const selectedCategories = ref([])
const selectedDomains = ref([])
const afterDate = ref('')
const beforeDate = ref('')

// Date presets
const datePresets = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '90d', days: 90 }
]

// Computed properties
const allDomains = computed(() => {
  return Object.entries(props.domainCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const topDomains = computed(() => {
  return allDomains.value.slice(0, 10)
})

const activeFilterCount = computed(() => {
  let count = 0
  if (localFilters.value.status !== 'all') count++
  if (selectedCategories.value.length > 0) count++
  if (selectedDomains.value.length > 0) count++
  if (afterDate.value || beforeDate.value) count++
  return count
})

const hasActiveFilters = computed(() => {
  return activeFilterCount.value > 0
})

// Watch for external filter changes
watch(
  () => props.filters,
  (newFilters) => {
    localFilters.value = { ...newFilters }
  },
  { deep: true }
)

// Methods
const openSheet = () => {
  isOpen.value = true
  document.body.style.overflow = 'hidden' // Prevent background scroll
}

const closeSheet = () => {
  isOpen.value = false
  document.body.style.overflow = '' // Restore scroll
  showAllDomains.value = false
}

const updateStatus = (status) => {
  localFilters.value.status = status
}

const toggleCategory = (category) => {
  const index = selectedCategories.value.indexOf(category)
  if (index === -1) {
    selectedCategories.value.push(category)
  } else {
    selectedCategories.value.splice(index, 1)
  }
}

const clearCategories = () => {
  selectedCategories.value = []
}

const toggleDomain = (domain) => {
  const index = selectedDomains.value.indexOf(domain)
  if (index === -1) {
    selectedDomains.value.push(domain)
  } else {
    selectedDomains.value.splice(index, 1)
  }
}

const clearDomains = () => {
  selectedDomains.value = []
}

const applyDatePreset = (preset) => {
  const date = new Date()
  date.setDate(date.getDate() - preset.days)
  afterDate.value = date.toISOString().split('T')[0]
  beforeDate.value = ''
}

const isDatePresetActive = (preset) => {
  if (!afterDate.value || beforeDate.value) return false
  const expectedDate = new Date()
  expectedDate.setDate(expectedDate.getDate() - preset.days)
  return afterDate.value === expectedDate.toISOString().split('T')[0]
}

const clearDates = () => {
  afterDate.value = ''
  beforeDate.value = ''
}

const clearAllFilters = () => {
  localFilters.value = {
    status: 'all',
    category: 'all',
    search: '',
    sort: localFilters.value.sort || 'date_desc',
    domain: 'all'
  }
  selectedCategories.value = []
  selectedDomains.value = []
  afterDate.value = ''
  beforeDate.value = ''
}

const applyAndClose = () => {
  // Build search query with advanced filters
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
  
  // Update search query
  const searchQuery = buildSearchQuery(operators, '')
  
  const finalFilters = {
    ...localFilters.value,
    search: searchQuery,
    category: 'all', // Reset dropdown since using advanced filters
    domain: 'all'    // Reset dropdown since using advanced filters  
  }
  
  emit('update-filters', finalFilters)
  closeSheet()
}
</script>

<style scoped>
.filter-option-button {
  @apply px-3 py-2 rounded-lg text-sm font-medium transition-colors;
}

.filter-option-active {
  @apply bg-blue-600 text-white;
}

.filter-option-inactive {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.mobile-checkbox-label {
  @apply flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors;
}

.mobile-checkbox-label-compact {
  @apply flex items-center p-2 hover:bg-gray-100 cursor-pointer transition-colors rounded;
}

.mobile-checkbox {
  @apply w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 mr-3;
}

.mobile-checkbox-small {
  @apply w-4 h-4 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 mr-2;
}

.mobile-checkbox-content {
  @apply flex flex-col;
}

.mobile-domain-chip {
  @apply px-3 py-2 rounded-lg text-sm border transition-colors flex items-center gap-1;
}

.mobile-domain-chip-active {
  @apply bg-blue-600 text-white border-blue-600;
}

.mobile-domain-chip-inactive {
  @apply bg-white text-gray-700 border-gray-300 hover:bg-gray-50;
}

.mobile-date-preset {
  @apply px-3 py-2 rounded-lg text-sm font-medium border transition-colors;
}

.mobile-date-preset-active {
  @apply bg-blue-600 text-white border-blue-600;
}

.mobile-date-preset-inactive {
  @apply bg-white text-gray-700 border-gray-300 hover:bg-gray-50;
}

.mobile-date-input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
}
</style>