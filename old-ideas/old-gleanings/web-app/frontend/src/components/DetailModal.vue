<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-96 overflow-y-auto" @click.stop>
      <div class="p-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Gleaning Details</h2>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Title</label>
            <p class="mt-1 text-sm text-gray-900">{{ gleaning.title || 'Untitled' }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">URL</label>
            <a :href="gleaning.url" target="_blank" class="mt-1 text-sm text-blue-600 hover:text-blue-800 break-all">
              {{ gleaning.url }}
            </a>
          </div>
          
          <div v-if="gleaning.description">
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <p class="mt-1 text-sm text-gray-900">{{ gleaning.description }}</p>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Domain</label>
              <p class="mt-1 text-sm text-gray-900">{{ gleaning.domain }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Category</label>
              <p class="mt-1 text-sm text-gray-900">{{ gleaning.category || 'Uncategorized' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Date</label>
              <p class="mt-1 text-sm text-gray-900">{{ gleaning.date }} {{ gleaning.timestamp }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <p class="mt-1 text-sm text-gray-900">{{ gleaning.user_status || 'active' }}</p>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Source File</label>
            <p class="mt-1 text-xs text-gray-600 break-all">{{ gleaning.source_file }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Internal ID</label>
            <p class="mt-1 text-xs font-mono text-gray-600">{{ gleaning.id }}</p>
          </div>
          
          <div v-if="gleaning.created_at" class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Created</label>
              <p class="mt-1 text-xs text-gray-600">{{ formatDate(gleaning.created_at) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Last Modified</label>
              <p class="mt-1 text-xs text-gray-600">{{ formatDate(gleaning.last_modified) }}</p>
            </div>
          </div>
        </div>
        
        <div class="mt-6 flex justify-end">
          <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  gleaning: Object
})

defineEmits(['close'])

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}
</script>