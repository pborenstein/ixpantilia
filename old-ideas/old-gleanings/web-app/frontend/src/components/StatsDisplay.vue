<template>
  <div class="flex items-center gap-4 text-sm text-gray-600">
    <div class="flex items-center gap-2">
      <span class="w-3 h-3 bg-emerald-500 rounded-full"></span>
      <span>Active: {{ stats.active || 0 }}</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="w-3 h-3 bg-slate-500 rounded-full"></span>
      <span>Hidden: {{ stats.hidden || 0 }}</span>
    </div>
    <div class="text-gray-800 font-medium">
      Total: {{ stats.total || 0 }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: Object
})
</script>