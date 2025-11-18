<template>
  <div class="filter-panel">
    <!-- Panel Header -->
    <div class="flex items-center justify-between py-2">
      <div class="flex items-center gap-2">
        <h3 class="text-sm font-medium text-gray-800">Advanced Filters</h3>
        <span v-if="activeFiltersCount > 0" class="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
          {{ activeFiltersCount }}
        </span>
      </div>
      <button
        @click="togglePanel"
        class="text-gray-400 hover:text-gray-600 p-1 rounded"
        :title="isPanelOpen ? 'Collapse filters' : 'Expand filters'"
      >
        <svg 
          class="w-4 h-4 transition-transform duration-200"
          :class="{ 'rotate-180': isPanelOpen }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- Panel Content -->
    <div 
      v-show="isPanelOpen"
      class="filter-panel-content"
      :class="{ 'panel-open': isPanelOpen }"
    >
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 py-3">
        <!-- Category Filter -->
        <div class="filter-section">
          <CategoryMultiSelect
            :available-categories="availableCategories"
            :category-counts="categoryCounts"
            :selected-categories="selectedCategories"
            @update:selected-categories="updateSelectedCategories"
          />
        </div>

        <!-- Domain Filter -->
        <div class="filter-section">
          <DomainQuickSelect
            :domain-counts="domainCounts"
            :selected-domains="selectedDomains"
            @update:selected-domains="updateSelectedDomains"
          />
        </div>

        <!-- Date Range Filter -->
        <div class="filter-section">
          <DateRangePicker
            :after-date="afterDate"
            :before-date="beforeDate"
            @update:after-date="updateAfterDate"
            @update:before-date="updateBeforeDate"
          />
        </div>
      </div>

      <!-- Panel Actions -->
      <div class="flex justify-between items-center pt-3 border-t border-gray-200">
        <div class="text-xs text-gray-500">
          <span v-if="activeFiltersCount > 0">
            {{ activeFiltersCount }} advanced {{ activeFiltersCount === 1 ? 'filter' : 'filters' }}
          </span>
          <span v-else>No advanced filters</span>
        </div>
        
        <div class="flex gap-2">
          <button
            @click="clearAllFilters"
            class="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-100 border border-gray-200 rounded hover:bg-gray-200 transition-colors"
            :disabled="activeFiltersCount === 0"
          >
            Clear
          </button>
          <button
            @click="applyFilters"
            class="px-3 py-1 text-xs font-medium text-white bg-blue-600 border border-transparent rounded hover:bg-blue-700 transition-colors"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import CategoryMultiSelect from './CategoryMultiSelect.vue'
import DomainQuickSelect from './DomainQuickSelect.vue'
import DateRangePicker from './DateRangePicker.vue'

const props = defineProps({
  // Panel state
  initiallyOpen: {
    type: Boolean,
    default: false
  },
  
  // Category data
  availableCategories: {
    type: Array,
    required: true
  },
  categoryCounts: {
    type: Object,
    required: true
  },
  selectedCategories: {
    type: Array,
    default: () => []
  },
  
  // Domain data
  domainCounts: {
    type: Object,
    required: true
  },
  selectedDomains: {
    type: Array,
    default: () => []
  },
  
  // Date data
  afterDate: {
    type: String,
    default: ''
  },
  beforeDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  'update:selectedCategories',
  'update:selectedDomains', 
  'update:afterDate',
  'update:beforeDate',
  'apply-filters',
  'clear-filters'
])

const isPanelOpen = ref(props.initiallyOpen)

// Filter state
const localSelectedCategories = ref([...props.selectedCategories])
const localSelectedDomains = ref([...props.selectedDomains])
const localAfterDate = ref(props.afterDate)
const localBeforeDate = ref(props.beforeDate)

// Computed properties
const activeFiltersCount = computed(() => {
  let count = 0
  if (localSelectedCategories.value.length > 0) count++
  if (localSelectedDomains.value.length > 0) count++
  if (localAfterDate.value) count++
  if (localBeforeDate.value) count++
  return count
})

// Watch for external changes
watch(
  () => props.selectedCategories,
  (newSelection) => {
    localSelectedCategories.value = [...newSelection]
  },
  { immediate: true, deep: true }
)

watch(
  () => props.selectedDomains,
  (newSelection) => {
    localSelectedDomains.value = [...newSelection]
  },
  { immediate: true, deep: true }
)

watch(
  () => props.afterDate,
  (newDate) => {
    localAfterDate.value = newDate
  },
  { immediate: true }
)

watch(
  () => props.beforeDate,
  (newDate) => {
    localBeforeDate.value = newDate
  },
  { immediate: true }
)

// Methods
const togglePanel = () => {
  isPanelOpen.value = !isPanelOpen.value
}

const updateSelectedCategories = (categories) => {
  localSelectedCategories.value = categories
  emit('update:selectedCategories', categories)
}

const updateSelectedDomains = (domains) => {
  localSelectedDomains.value = domains
  emit('update:selectedDomains', domains)
}

const updateAfterDate = (date) => {
  localAfterDate.value = date
  emit('update:afterDate', date)
}

const updateBeforeDate = (date) => {
  localBeforeDate.value = date
  emit('update:beforeDate', date)
}

const applyFilters = () => {
  emit('apply-filters')
}

const clearAllFilters = () => {
  localSelectedCategories.value = []
  localSelectedDomains.value = []
  localAfterDate.value = ''
  localBeforeDate.value = ''
  
  emit('update:selectedCategories', [])
  emit('update:selectedDomains', [])
  emit('update:afterDate', '')
  emit('update:beforeDate', '')
  emit('clear-filters')
}
</script>

<style scoped>
.filter-panel {
  @apply bg-gray-50 border border-gray-200 rounded p-3 mb-4;
}

.filter-panel-content {
  @apply transition-all duration-200 ease-in-out;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
}

.filter-panel-content.panel-open {
  max-height: 500px;
  opacity: 1;
}

.filter-section {
  @apply bg-white p-3 rounded border border-gray-100;
}

@media (max-width: 1024px) {
  .filter-panel-content {
    max-height: none;
  }
  
  .filter-section {
    @apply mb-3;
  }
}
</style>