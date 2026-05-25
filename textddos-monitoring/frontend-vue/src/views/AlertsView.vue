<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-white mb-2">Cảnh Báo & Sự Cố</h2>
      <p class="text-slate-400">Danh sách các cuộc tấn công realtime</p>
    </div>

    <AlertList />
  </div>
</template>

<script setup>
import AlertList from '../components/AlertList.vue'
import Chart from 'chart.js/auto';
</script>
