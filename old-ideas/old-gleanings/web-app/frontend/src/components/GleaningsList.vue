<template>
  <div>
    <!-- Selection Info -->
    <div class="bg-gray-100 rounded p-3 mb-4 flex items-center justify-between">
      <span class="text-sm text-gray-700">
        {{ selectedIds.length > 0 ? `${selectedIds.length} selected` : `${gleanings.length} items shown` }}
      </span>
      <div v-if="selectedIds.length > 0" class="flex gap-2 items-center">
        <button @click="bulkAction('active')" class="text-xs px-3 py-1 bg-emerald-600 text-white rounded hover:bg-emerald-700">Make Active</button>
        <button @click="bulkAction('hidden')" class="text-xs px-3 py-1 bg-slate-600 text-white rounded hover:bg-slate-700">Hide</button>
        <div class="flex items-center gap-1">
          <select 
            :value="selectedCategory" 
            class="text-xs px-2 py-1 border rounded"
            @change="handleCategoryChange"
          >
            <option value="">Set Category...</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
          <button 
            @click="bulkSetCategory" 
            :disabled="!selectedCategory"
            class="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            Set
          </button>
        </div>
        <button @click="clearSelection" class="text-xs px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-gray-500">Loading gleanings...</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card text-center py-8 bg-red-50 border-red-200">
      <div class="text-red-600 font-medium">{{ error }}</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="gleanings.length === 0" class="card text-center py-8">
      <div class="text-gray-500">No gleanings found</div>
    </div>

    <!-- Gleanings Grid -->
    <div v-else class="grid gap-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
      <GleaningCard
        v-for="gleaning in gleanings"
        :key="gleaning.id"
        :gleaning="gleaning"
        :selected="selectedIds.includes(gleaning.id)"
        @update-status="$emit('update-status', $event.id, $event.status, $event.reason)"
        @toggle-selection="toggleSelection"
        @view-details="viewDetails"
        @edit-category="editCategory"
        @domain-sort="$emit('domain-sort', $event)"
      />
    </div>

    <!-- Pagination -->
    <Pagination
      v-if="pagination.pages > 1"
      :pagination="pagination"
      @page-change="$emit('page-change', $event)"
      class="mt-8"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import GleaningCard from './GleaningCard.vue'
import Pagination from './Pagination.vue'

const props = defineProps({
  gleanings: Array,
  loading: Boolean,
  error: String,
  pagination: Object,
  categories: Array,
  selectedIds: Array,
  selectedCategory: String
})

const emit = defineEmits(['update-status', 'bulk-update', 'bulk-set-category', 'toggle-selection', 'clear-selection', 'update-category-selection', 'page-change', 'view-details', 'edit-category', 'domain-sort'])

const toggleSelection = (id) => {
  emit('toggle-selection', id)
}

const clearSelection = () => {
  emit('clear-selection')
}

const bulkAction = async (status) => {
  if (props.selectedIds.length === 0) return
  
  const reason = prompt(`Reason for ${status} (optional):`) || ''
  
  try {
    emit('bulk-update', props.selectedIds, status, reason)
  } catch (error) {
    alert(`Bulk operation failed: ${error.message}`)
  }
}

const viewDetails = (gleaning) => {
  emit('view-details', gleaning)
}

const editCategory = (gleaning) => {
  emit('edit-category', gleaning)
}

const handleCategoryChange = (event) => {
  emit('update-category-selection', event.target.value)
}

const bulkSetCategory = async () => {
  if (props.selectedIds.length === 0 || !props.selectedCategory) return
  
  emit('bulk-set-category', props.selectedIds, props.selectedCategory)
}
</script>