<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-white mb-2">Live Flows</h2>
      <p class="text-slate-400">Bảng động với các flow realtime - Tìm kiếm, lọc và theo dõi</p>
    </div>

    <LiveFlowTable />
  </div>
</template>

<script setup>
import LiveFlowTable from '../components/LiveFlowTable.vue'
import Chart from 'chart.js/auto';
</script>
