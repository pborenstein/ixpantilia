<template>
  <div class="category-multiselect">
    <div class="flex items-center justify-between mb-2">
      <label class="text-xs font-medium text-gray-700">Categories</label>
      <div class="flex gap-1">
        <button 
          @click="selectAll"
          class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
        >
          All
        </button>
        <button 
          @click="clearAll"
          class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Category Grid -->
    <div class="grid grid-cols-1 gap-1 max-h-48 overflow-y-auto">
      <label 
        v-for="category in categoriesWithCounts" 
        :key="category.name"
        class="flex items-center gap-2 p-1.5 border rounded text-xs hover:bg-gray-50 cursor-pointer transition-colors"
        :class="{ 'border-blue-400 bg-blue-50': selectedCategories.includes(category.name) }"
      >
        <input
          type="checkbox"
          :checked="selectedCategories.includes(category.name)"
          @change="toggleCategory(category.name)"
          class="text-blue-600 rounded border-gray-300 focus:ring-blue-500 w-3 h-3"
        />
        <div class="flex-1 min-w-0 flex items-center justify-between">
          <span class="font-medium text-gray-900 truncate">
            {{ category.name }}
          </span>
          <span class="text-gray-500 ml-1">
            {{ category.count }}
          </span>
        </div>
      </label>
    </div>

    <!-- Selected Count -->
    <div v-if="selectedCategories.length > 0" class="mt-2 text-xs text-gray-500">
      {{ selectedCategories.length }} selected
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  availableCategories: {
    type: Array,
    required: true
  },
  categoryCounts: {
    type: Object,
    default: () => ({})
  },
  selectedCategories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:selectedCategories'])

const selectedCategories = ref([...props.selectedCategories])

// Categories with their counts, sorted by count descending
const categoriesWithCounts = computed(() => {
  return props.availableCategories
    .map(category => ({
      name: category,
      count: props.categoryCounts[category] || 0
    }))
    .sort((a, b) => b.count - a.count)
})

// Watch for external changes
watch(
  () => props.selectedCategories,
  (newSelection) => {
    selectedCategories.value = [...newSelection]
  },
  { immediate: true }
)

// Emit changes
watch(
  selectedCategories,
  (newSelection) => {
    emit('update:selectedCategories', [...newSelection])
  },
  { deep: true }
)

const toggleCategory = (category) => {
  const index = selectedCategories.value.indexOf(category)
  if (index === -1) {
    selectedCategories.value.push(category)
  } else {
    selectedCategories.value.splice(index, 1)
  }
}

const selectAll = () => {
  selectedCategories.value = [...props.availableCategories]
}

const clearAll = () => {
  selectedCategories.value = []
}
</script>

<style scoped>
.category-multiselect {
  @apply min-w-0;
}
</style>