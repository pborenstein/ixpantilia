<template>
  <div 
    class="bg-white rounded border border-gray-200 p-3 hover:shadow-sm transition-shadow duration-200"
    :class="{
      'ring-2 ring-blue-500': selected,
      'opacity-60': gleaning.user_status === 'hidden'
    }"
  >
    <!-- Header -->
    <div class="flex items-start gap-2 mb-2">
      <input 
        type="checkbox" 
        :checked="selected"
        @change="$emit('toggle-selection', gleaning.id)"
        class="mt-0.5"
      />
      
      <span 
        class="px-2 py-0.5 text-xs font-medium rounded"
        :class="statusClasses"
      >
        {{ statusLetter }}
      </span>
      
      <button 
        @click="$emit('edit-category', gleaning)"
        class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 ml-auto"
        title="Click to edit category"
      >
        {{ gleaning.category || 'Uncategorized' }}
      </button>
      
      <button 
        @click="$emit('view-details', gleaning)"
        class="text-gray-400 hover:text-gray-600 text-sm"
        title="View details"
      >
        •••
      </button>
    </div>

    <!-- Title -->
    <h3 class="font-medium text-gray-900 mb-1 line-clamp-2 text-sm leading-tight">
      <a 
        ref="titleLink"
        :href="gleaning.url" 
        target="_blank" 
        class="hover:text-blue-600 transition-colors"
        @mouseenter="handleTitleHover($event)"
        @mouseleave="handleTitleLeave"
        @click.prevent="handleTitleClick"
      >
        {{ gleaning.title || 'Untitled' }}
      </a>
    </h3>

    <!-- Description -->
    <p v-if="gleaning.description" class="text-xs text-gray-600 mb-2 line-clamp-2">
      {{ gleaning.description }}
    </p>

    <!-- Tags -->
    <div v-if="gleaning.tags && gleaning.tags.length > 0" class="flex flex-wrap gap-1 mb-2">
      <button
        v-for="tag in gleaning.tags"
        :key="tag"
        @click="handleTagClick(tag)"
        class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors cursor-pointer"
        :title="`Filter by tag: ${tag}`"
      >
        #{{ tag }}
      </button>
    </div>

    <!-- Metadata -->
    <div class="text-xs mb-2">
      <button 
        @click="handleDomainClick(gleaning.domain)"
        class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer truncate block"
        title="Click to filter by this domain"
      >
        {{ gleaning.domain }}
      </button>
      <div class="text-gray-500">{{ gleaning.date }} {{ gleaning.timestamp }}</div>
    </div>

    <!-- Actions -->
    <div class="flex gap-1">
      <button 
        v-if="gleaning.user_status !== 'active'"
        @click="updateStatus('active')"
        class="text-xs px-2 py-1 bg-emerald-600 text-white rounded hover:bg-emerald-700"
      >
        Restore
      </button>
      <button 
        v-if="gleaning.user_status !== 'hidden'"
        @click="updateStatus('hidden')"
        class="text-xs px-2 py-1 bg-slate-600 text-white rounded hover:bg-slate-700"
      >
        Hide
      </button>
    </div>
  </div>
  
  <!-- Preview Popup -->
  <PreviewPopup
    v-if="showPreview"
    :gleaning="gleaning"
    :target-element="titleLink"
    :visible="showPreview"
    @close="handlePreviewClose"
    @cancel-close="cancelClose"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import PreviewPopup from './PreviewPopup.vue'

const props = defineProps({
  gleaning: Object,
  selected: Boolean
})

const emit = defineEmits(['update-status', 'toggle-selection', 'view-details', 'edit-category', 'domain-sort', 'tag-filter'])

const titleLink = ref(null)
const showPreview = ref(false)
const hoverTimeout = ref(null)
const leaveTimeout = ref(null)

const statusClasses = computed(() => {
  const status = props.gleaning.user_status || 'active'
  return {
    'bg-emerald-100 text-emerald-800': status === 'active',
    'bg-slate-100 text-slate-800': status === 'hidden'
  }
})

const statusLetter = computed(() => {
  const status = props.gleaning.user_status || 'active'
  return status.charAt(0).toUpperCase()
})

const updateStatus = (status) => {
  const reason = prompt(`Reason for ${status} (optional):`) || ''
  emit('update-status', props.gleaning.id, status, reason)
}

const handleTitleHover = (event) => {
  // Store the actual target element for positioning
  titleLink.value = event.target
  
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

const handleTitleClick = () => {
  // Close preview and open URL
  showPreview.value = false
  if (props.gleaning?.url) {
    window.open(props.gleaning.url, '_blank', 'noopener,noreferrer')
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

// Tag filtering
const handleTagClick = (tag) => {
  emit('tag-filter', tag)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>