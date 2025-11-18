<template>
  <div class="date-range-picker">
    <div class="flex items-center justify-between mb-2">
      <label class="text-xs font-medium text-gray-700">Date Range</label>
      <button 
        @click="clearDates"
        class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
      >
        Clear
      </button>
    </div>
    
    <!-- Quick Presets -->
    <div class="flex flex-wrap gap-1 mb-2">
      <button
        v-for="preset in datePresets.slice(0, 3)"
        :key="preset.label"
        @click="applyPreset(preset)"
        class="px-2 py-1 rounded text-xs border transition-colors"
        :class="{ 
          'bg-blue-600 text-white border-blue-600': isPresetActive(preset),
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-50': !isPresetActive(preset)
        }"
      >
        {{ preset.label.replace(' Days', 'd').replace('Last ', '') }}
      </button>
    </div>

    <!-- Custom Date Inputs -->
    <div class="grid grid-cols-1 gap-2">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">After</label>
        <input
          v-model="localAfterDate"
          type="date"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          @change="emitChange"
        />
      </div>
      
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Before</label>
        <input
          v-model="localBeforeDate"
          type="date"
          class="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          @change="emitChange"
        />
      </div>
    </div>

    <!-- Selected Range Display -->
    <div v-if="hasDateRange" class="mt-2 text-xs text-gray-500">
      <span v-if="localAfterDate && localBeforeDate">
        {{ formatDate(localAfterDate) }} - {{ formatDate(localBeforeDate) }}
      </span>
      <span v-else-if="localAfterDate">
        After {{ formatDate(localAfterDate) }}
      </span>
      <span v-else-if="localBeforeDate">
        Before {{ formatDate(localBeforeDate) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  afterDate: {
    type: String,
    default: ''
  },
  beforeDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:afterDate', 'update:beforeDate'])

const localAfterDate = ref(props.afterDate)
const localBeforeDate = ref(props.beforeDate)

// Date presets
const datePresets = [
  {
    label: 'Last 7 Days',
    afterDate: () => formatDateForInput(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)),
    beforeDate: () => ''
  },
  {
    label: 'Last 30 Days',
    afterDate: () => formatDateForInput(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)),
    beforeDate: () => ''
  },
  {
    label: 'Last 90 Days',
    afterDate: () => formatDateForInput(new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)),
    beforeDate: () => ''
  },
  {
    label: 'This Year',
    afterDate: () => `${new Date().getFullYear()}-01-01`,
    beforeDate: () => ''
  },
  {
    label: 'Last Year',
    afterDate: () => `${new Date().getFullYear() - 1}-01-01`,
    beforeDate: () => `${new Date().getFullYear() - 1}-12-31`
  }
]

const hasDateRange = computed(() => {
  return localAfterDate.value || localBeforeDate.value
})

// Watch for external changes
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

const formatDateForInput = (date) => {
  return date.toISOString().split('T')[0]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  })
}

const applyPreset = (preset) => {
  localAfterDate.value = preset.afterDate()
  localBeforeDate.value = preset.beforeDate()
  emitChange()
}

const isPresetActive = (preset) => {
  const presetAfter = preset.afterDate()
  const presetBefore = preset.beforeDate()
  
  return localAfterDate.value === presetAfter && localBeforeDate.value === presetBefore
}

const clearDates = () => {
  localAfterDate.value = ''
  localBeforeDate.value = ''
  emitChange()
}

const emitChange = () => {
  emit('update:afterDate', localAfterDate.value)
  emit('update:beforeDate', localBeforeDate.value)
}
</script>

<style scoped>
.date-range-picker {
  @apply min-w-0;
}
</style>