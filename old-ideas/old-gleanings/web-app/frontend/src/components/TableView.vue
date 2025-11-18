<template>
  <div class="bg-white rounded border border-gray-200 overflow-hidden">
    <!-- Selection Info -->
    <div class="bg-gray-100 px-4 py-3 flex items-center justify-between border-b">
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

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <!-- Header -->
        <thead class="bg-gray-50">
          <tr>
            <th class="w-8 px-3 py-2">
              <input 
                type="checkbox" 
                :checked="allSelected"
                @change="toggleAllSelection"
              />
            </th>
            <th class="text-left px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Date</th>
            <th class="text-left px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Title</th>
            <th class="text-left px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Domain</th>
            <th class="text-left px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Category</th>
            <th class="text-left px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
            <th class="w-16 px-3 py-2 text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="divide-y divide-gray-200">
          <tr 
            v-for="gleaning in gleanings" 
            :key="gleaning.id"
            class="hover:bg-gray-50"
            :class="{
              'bg-blue-50': selectedIds.includes(gleaning.id),
              'opacity-60': gleaning.user_status === 'hidden'
            }"
          >
            <!-- Checkbox -->
            <td class="px-3 py-2">
              <input 
                type="checkbox" 
                :checked="selectedIds.includes(gleaning.id)"
                @change="toggleSelection(gleaning.id)"
              />
            </td>

            <!-- Date -->
            <td class="px-3 py-2 text-sm text-gray-900 font-mono">
              <div>{{ gleaning.date }}</div>
              <div class="text-xs text-gray-500">{{ gleaning.timestamp }}</div>
            </td>

            <!-- Title -->
            <td class="px-3 py-2 max-w-xs">
              <a 
                ref="titleLink"
                :href="gleaning.url" 
                target="_blank" 
                class="text-sm text-blue-600 hover:text-blue-800 hover:underline line-clamp-2"
                @click.prevent="handleTitleClick(gleaning)"
                @mouseenter="handleTitleHover($event, gleaning)"
                @mouseleave="handleTitleLeave"
              >
                {{ gleaning.title || 'Untitled' }}
              </a>
              <div v-if="gleaning.description" class="text-xs text-gray-500 mt-1 line-clamp-1">
                {{ gleaning.description }}
              </div>
            </td>

            <!-- Domain -->
            <td class="px-3 py-2 text-sm">
              <button 
                @click="handleDomainClick(gleaning.domain)"
                class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer"
                title="Click to filter by this domain"
              >
                {{ gleaning.domain }}
              </button>
            </td>

            <!-- Category -->
            <td class="px-3 py-2">
              <button 
                @click="$emit('edit-category', gleaning)"
                class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                title="Click to edit category"
              >
                {{ gleaning.category || 'Uncategorized' }}
              </button>
            </td>

            <!-- Status -->
            <td class="px-3 py-2">
              <span 
                class="inline-flex px-2 py-1 text-xs font-medium rounded"
                :class="statusClasses(gleaning.user_status)"
              >
                {{ gleaning.user_status || 'active' }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-3 py-2">
              <div class="flex gap-1">
                <button 
                  v-if="gleaning.user_status !== 'active'"
                  @click="updateStatus(gleaning.id, 'active')"
                  class="text-xs px-2 py-1 bg-emerald-600 text-white rounded hover:bg-emerald-700"
                  title="Make Active"
                >
                  A
                </button>
                <button 
                  v-if="gleaning.user_status !== 'hidden'"
                  @click="updateStatus(gleaning.id, 'hidden')"
                  class="text-xs px-2 py-1 bg-slate-600 text-white rounded hover:bg-slate-700"
                  title="Hide"
                >
                  H
                </button>
                <button 
                  @click="$emit('view-details', gleaning)"
                  class="text-xs px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                  title="View Details"
                >
                  •••
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <Pagination
      v-if="pagination.pages > 1"
      :pagination="pagination"
      @page-change="$emit('page-change', $event)"
      class="border-t"
    />
  </div>
  
  <!-- Preview Popup -->
  <PreviewPopup
    v-if="showPreview"
    :gleaning="selectedGleaning"
    :target-element="titleLinkElement"
    :visible="showPreview"
    @close="handlePreviewClose"
    @cancel-close="cancelClose"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import Pagination from './Pagination.vue'
import PreviewPopup from './PreviewPopup.vue'

const props = defineProps({
  gleanings: Array,
  loading: Boolean,
  error: String,
  pagination: Object,
  categories: Array,
  selectedIds: Array,
  selectedCategory: String
})

const emit = defineEmits(['update-status', 'bulk-update', 'bulk-set-category', 'toggle-selection', 'toggle-all-selection', 'clear-selection', 'update-category-selection', 'page-change', 'view-details', 'edit-category', 'domain-sort'])

// Preview functionality
const showPreview = ref(false)
const selectedGleaning = ref(null)
const titleLinkElement = ref(null)
const hoverTimeout = ref(null)
const leaveTimeout = ref(null)

const allSelected = computed(() => {
  return props.gleanings.length > 0 && props.selectedIds.length === props.gleanings.length
})

const statusClasses = (status) => {
  const userStatus = status || 'active'
  return {
    'bg-emerald-100 text-emerald-800': userStatus === 'active',
    'bg-slate-100 text-slate-800': userStatus === 'hidden'
  }
}

const toggleSelection = (id) => {
  emit('toggle-selection', id)
}

const toggleAllSelection = () => {
  emit('toggle-all-selection')
}

const clearSelection = () => {
  emit('clear-selection')
}

const updateStatus = (id, status) => {
  const reason = prompt(`Reason for ${status} (optional):`) || ''
  emit('update-status', id, status, reason)
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

const handleCategoryChange = (event) => {
  emit('update-category-selection', event.target.value)
}

const bulkSetCategory = async () => {
  if (props.selectedIds.length === 0 || !props.selectedCategory) return
  
  try {
    emit('bulk-set-category', props.selectedIds, props.selectedCategory)
  } catch (error) {
    alert(`Bulk category update failed: ${error.message}`)
  }
}

// Preview functionality methods
const handleTitleHover = (event, gleaning) => {
  // Store the actual target element for positioning
  titleLinkElement.value = event.target
  selectedGleaning.value = gleaning
  
  // Debounce hover to prevent rapid firing
  clearTimeout(hoverTimeout.value)
  hoverTimeout.value = setTimeout(() => {
    showPreview.value = true
  }, 300) // 300ms delay
}

const handleTitleLeave = () => {
  clearTimeout(hoverTimeout.value)
  // Add a longer delay to allow moving to popup
  leaveTimeout.value = setTimeout(() => {
    if (!showPreview.value) return // Already closed
    showPreview.value = false
  }, 300)
}

const handleTitleClick = (gleaning) => {
  // Close preview and open URL
  showPreview.value = false
  if (gleaning?.url) {
    window.open(gleaning.url, '_blank', 'noopener,noreferrer')
  }
}

const handlePreviewClose = () => {
  clearTimeout(leaveTimeout.value)
  showPreview.value = false
}

const cancelClose = () => {
  clearTimeout(leaveTimeout.value)
}

// Domain sorting
const handleDomainClick = (domain) => {
  emit('domain-sort', domain)
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>