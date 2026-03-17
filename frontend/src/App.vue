<!-- App.vue -->
<template>
  <div>
   <OnuRegView :agreement="agreement" />
  </div>
</template>

<script setup>
import OnuRegView from '@/views/OnuRegView.vue'

defineProps({
  agreement: String
})
</script>