<template>
    <div class="spinner-container" :class="{ active: isLoading }">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Опитуємо світч...</span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps } from 'vue';
  
  defineProps({
    isLoading: {
      type: Boolean,
      required: true
    }
  });
  </script>
  
  <style scoped>
  .spinner-container {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1050;
  }
  
  .spinner-container.active {
    display: block;
  }
  </style>