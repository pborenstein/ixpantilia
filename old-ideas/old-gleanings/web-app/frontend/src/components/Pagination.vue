<template>
  <div class="flex items-center justify-between">
    <div class="text-sm text-gray-700">
      Showing {{ startItem }} to {{ endItem }} of {{ pagination.total }} results
    </div>
    
    <div class="flex items-center gap-2">
      <!-- Previous button -->
      <button 
        @click="$emit('page-change', pagination.page - 1)"
        :disabled="pagination.page <= 1"
        class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>
      
      <!-- Page numbers -->
      <div class="flex gap-1">
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="$emit('page-change', page)"
          class="w-10 h-10 rounded-md text-sm font-medium transition-colors"
          :class="page === pagination.page 
            ? 'bg-blue-600 text-white' 
            : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'"
        >
          {{ page }}
        </button>
      </div>
      
      <!-- Next button -->
      <button 
        @click="$emit('page-change', pagination.page + 1)"
        :disabled="pagination.page >= pagination.pages"
        class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pagination: Object
})

defineEmits(['page-change'])

const startItem = computed(() => {
  return (props.pagination.page - 1) * props.pagination.limit + 1
})

const endItem = computed(() => {
  return Math.min(props.pagination.page * props.pagination.limit, props.pagination.total)
})

const visiblePages = computed(() => {
  const current = props.pagination.page
  const total = props.pagination.pages
  const range = 2 // Show 2 pages on each side of current
  
  let start = Math.max(1, current - range)
  let end = Math.min(total, current + range)
  
  // Adjust if we're near the beginning or end
  if (end - start < range * 2) {
    if (start === 1) {
      end = Math.min(total, start + range * 2)
    } else if (end === total) {
      start = Math.max(1, end - range * 2)
    }
  }
  
  const pages = []
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})
</script>