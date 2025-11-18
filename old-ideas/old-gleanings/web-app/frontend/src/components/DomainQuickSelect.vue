<template>
  <div class="domain-quick-select">
    <div class="flex items-center justify-between mb-2">
      <label class="text-xs font-medium text-gray-700">Popular Domains</label>
      <button 
        @click="clearAll"
        class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
      >
        Clear
      </button>
    </div>
    
    <!-- Top Domains as Buttons -->
    <div class="flex flex-wrap gap-1 mb-2">
      <button
        v-for="domain in topDomains.slice(0, 6)"
        :key="domain.name"
        @click="toggleDomain(domain.name)"
        class="px-2 py-1 rounded text-xs border transition-colors"
        :class="{ 
          'bg-blue-600 text-white border-blue-600': selectedDomains.includes(domain.name),
          'bg-white text-gray-700 border-gray-300 hover:bg-gray-50': !selectedDomains.includes(domain.name)
        }"
      >
        <span class="text-xs font-medium">{{ domain.name.split('.')[0] }}</span>
        <span class="text-xs opacity-75 ml-1">({{ domain.count }})</span>
      </button>
    </div>

    <!-- Show More Toggle -->
    <div class="flex items-center justify-between mb-2">
      <button 
        @click="showAll = !showAll"
        class="text-xs text-blue-600 hover:text-blue-800 font-medium"
      >
        {{ showAll ? 'Show Less' : `+${allDomains.length - 6} more` }}
      </button>
    </div>

    <!-- All Domains List (when expanded) -->
    <div v-if="showAll" class="border rounded p-2 bg-gray-50 max-h-40 overflow-y-auto">
      <div class="grid grid-cols-1 gap-1">
        <label 
          v-for="domain in allDomains" 
          :key="domain.name"
          class="flex items-center gap-2 p-1 hover:bg-gray-100 cursor-pointer transition-colors rounded text-xs"
        >
          <input
            type="checkbox"
            :checked="selectedDomains.includes(domain.name)"
            @change="toggleDomain(domain.name)"
            class="text-blue-600 rounded border-gray-300 focus:ring-blue-500 w-3 h-3"
          />
          <div class="flex-1 flex items-center justify-between min-w-0">
            <span class="text-gray-900 truncate">{{ domain.name }}</span>
            <span class="text-gray-500 ml-2">({{ domain.count }})</span>
          </div>
        </label>
      </div>
    </div>

    <!-- Selected Count -->
    <div v-if="selectedDomains.length > 0" class="mt-2 text-xs text-gray-500">
      {{ selectedDomains.length }} selected
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  domainCounts: {
    type: Object,
    required: true
  },
  selectedDomains: {
    type: Array,
    default: () => []
  },
  topCount: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['update:selectedDomains'])

const selectedDomains = ref([...props.selectedDomains])
const showAll = ref(false)

// All domains sorted by count
const allDomains = computed(() => {
  return Object.entries(props.domainCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

// Top domains for quick selection
const topDomains = computed(() => {
  return allDomains.value.slice(0, props.topCount)
})

// Watch for external changes
watch(
  () => props.selectedDomains,
  (newSelection) => {
    selectedDomains.value = [...newSelection]
  },
  { immediate: true }
)

// Emit changes
watch(
  selectedDomains,
  (newSelection) => {
    emit('update:selectedDomains', [...newSelection])
  },
  { deep: true }
)

const toggleDomain = (domain) => {
  const index = selectedDomains.value.indexOf(domain)
  if (index === -1) {
    selectedDomains.value.push(domain)
  } else {
    selectedDomains.value.splice(index, 1)
  }
}

const clearAll = () => {
  selectedDomains.value = []
}
</script>

<style scoped>
.domain-quick-select {
  @apply min-w-0;
}
</style>