<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="$emit('close')">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" @click.stop>
      <div class="p-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-lg font-semibold text-gray-900">Edit Category</h2>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <p class="text-sm text-gray-900 truncate">{{ gleaning.title || 'Untitled' }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Current Category</label>
            <p class="text-sm text-gray-600">{{ gleaning.category || 'Uncategorized' }}</p>
          </div>
          
          <div>
            <label for="new-category" class="block text-sm font-medium text-gray-700 mb-1">New Category</label>
            <select 
              id="new-category"
              v-model="selectedCategory" 
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Uncategorized</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
          
          <div>
            <label for="custom-category" class="block text-sm font-medium text-gray-700 mb-1">Or enter custom category</label>
            <input 
              id="custom-category"
              v-model="customCategory"
              type="text" 
              placeholder="Enter new category name"
              class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div class="mt-6 flex justify-end gap-2">
          <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
            Cancel
          </button>
          <button @click="saveCategory" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  gleaning: Object,
  categories: Array
})

const emit = defineEmits(['close', 'save'])

const selectedCategory = ref(props.gleaning.category || '')
const customCategory = ref('')

const saveCategory = () => {
  const newCategory = customCategory.value.trim() || selectedCategory.value
  emit('save', props.gleaning, newCategory)
}
</script>