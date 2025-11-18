<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg transition-opacity duration-200"
      :class="{ 'opacity-0': !loaded, 'opacity-100': loaded }"
      :style="popupStyle"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <div class="p-3 max-w-sm">
        <!-- Thumbnail -->
        <div v-if="thumbnailData" class="mb-3">
          <img 
            :src="thumbnailData.thumbnail" 
            :alt="gleaning.title"
            class="w-full h-32 object-cover rounded border"
            @error="handleImageError"
            @load="handleImageLoad"
          />
          <div v-if="thumbnailData.source" class="text-xs text-gray-400 mt-1">
            {{ thumbnailData.source === 'opengraph' ? 'Preview' : 'Screenshot' }}
          </div>
        </div>
        
        <!-- Loading thumbnail -->
        <div v-else-if="loadingThumbnail" class="mb-3">
          <div class="w-full h-32 bg-gray-100 rounded border flex items-center justify-center">
            <div class="animate-spin w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          </div>
        </div>
        
        <!-- Thumbnail failed - show rich fallback -->
        <div v-else-if="thumbnailError" class="mb-3">
          <div class="w-full h-32 bg-gradient-to-br from-blue-50 to-indigo-100 rounded border flex flex-col items-center justify-center p-4 text-center">
            <!-- Favicon -->
            <img 
              :src="faviconUrl" 
              :alt="gleaning.domain"
              class="w-8 h-8 mb-2 rounded"
              @error="hideFavicon"
              v-if="showFavicon"
            />
            
            <!-- Domain and URL info -->
            <div class="text-sm font-medium text-gray-700 mb-1">
              {{ gleaning.domain }}
            </div>
            <div class="text-xs text-gray-500 truncate max-w-full">
              {{ shortUrl }}
            </div>
            
            <!-- Visual indicator -->
            <div class="mt-2 flex items-center text-xs text-gray-400">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0 9c-1.657 0-3-4.03-3-9s1.343-9 3-9m0 9c1.657 0 3 4.03 3 9s-1.343 9-3-9"></path>
              </svg>
              Live site
            </div>
          </div>
        </div>
        
        <!-- Content -->
        <div class="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
          {{ gleaning.title || 'Untitled' }}
        </div>
        <div v-if="gleaning.description" class="text-xs text-gray-600 mb-2 line-clamp-3">
          {{ gleaning.description }}
        </div>
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span class="truncate">{{ gleaning.domain }}</span>
          <span class="ml-2 px-2 py-1 bg-gray-100 rounded">{{ gleaning.category || 'Uncategorized' }}</span>
        </div>
        
        <!-- Click to open -->
        <div class="mt-2 text-xs text-blue-600 cursor-pointer hover:text-blue-800" @click="openUrl">
          Click to open →
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  gleaning: Object,
  targetElement: Object,
  visible: Boolean
})

const emit = defineEmits(['close', 'cancel-close'])

const loaded = ref(true)
const thumbnailData = ref(null)
const loadingThumbnail = ref(false)
const thumbnailError = ref(false)
const showFavicon = ref(true)

// Calculate popup position relative to target element
const popupStyle = computed(() => {
  if (!props.targetElement) {
    return { left: '100px', top: '100px' }
  }
  
  const rect = props.targetElement.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // Popup dimensions - larger for thumbnail
  const popupWidth = 320
  const popupHeight = 280
  
  // Calculate position (try to show to the right, fallback to left)
  let left = rect.right + 10
  let top = rect.top
  
  // Check if popup would overflow viewport horizontally
  if (left + popupWidth > viewportWidth) {
    left = rect.left - popupWidth - 10
  }
  
  // Check if popup would overflow viewport vertically
  if (top + popupHeight > viewportHeight) {
    top = viewportHeight - popupHeight - 10
  }
  
  // Ensure popup doesn't go off-screen
  left = Math.max(10, left)
  top = Math.max(10, top)
  
  return {
    left: `${left}px`,
    top: `${top}px`,
    width: 'auto',
    height: 'auto'
  }
})

// Generate favicon URL
const faviconUrl = computed(() => {
  if (!props.gleaning?.url) return ''
  try {
    const url = new URL(props.gleaning.url)
    return `https://www.google.com/s2/favicons?domain=${url.hostname}&sz=32`
  } catch {
    return ''
  }
})

// Create a shortened URL for display
const shortUrl = computed(() => {
  if (!props.gleaning?.url) return ''
  try {
    const url = new URL(props.gleaning.url)
    let path = url.pathname
    if (path.length > 30) {
      path = path.substring(0, 27) + '...'
    }
    return url.hostname + path
  } catch {
    return props.gleaning.url.substring(0, 40) + '...'
  }
})

const fetchThumbnail = async () => {
  if (!props.gleaning?.url) return
  
  loadingThumbnail.value = true
  thumbnailError.value = false
  
  try {
    const response = await fetch(`/api/thumbnail?url=${encodeURIComponent(props.gleaning.url)}`)
    if (response.ok) {
      const data = await response.json()
      thumbnailData.value = data
    } else {
      thumbnailError.value = true
    }
  } catch (error) {
    console.error('Failed to fetch thumbnail:', error)
    thumbnailError.value = true
  } finally {
    loadingThumbnail.value = false
  }
}

const handleImageError = () => {
  thumbnailError.value = true
  thumbnailData.value = null
}

const handleImageLoad = () => {
  // Image loaded successfully
}

const hideFavicon = () => {
  showFavicon.value = false
}

const handleMouseEnter = () => {
  // Cancel any pending close when mouse enters popup
  emit('cancel-close')
}

const handleMouseLeave = () => {
  // Close immediately when leaving popup
  emit('close')
}

const openUrl = () => {
  if (props.gleaning?.url) {
    window.open(props.gleaning.url, '_blank', 'noopener,noreferrer')
  }
  emit('close')
}

// Watch for visibility changes to fetch thumbnail
watch(() => props.visible, (newVisible) => {
  if (newVisible && !thumbnailData.value && !loadingThumbnail.value) {
    fetchThumbnail()
  }
})

// Fetch thumbnail on mount if visible
onMounted(() => {
  if (props.visible) {
    fetchThumbnail()
  }
})
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