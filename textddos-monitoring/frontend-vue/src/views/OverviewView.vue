<template>
  <div class="space-y-8">
    <!-- Statistics Cards -->
    <section>
      <DashboardCards />
    </section>

    <!-- Charts and Tables -->
    <section>
      <TrafficChart />
    </section>
  </div>
</template>

<script setup>
import DashboardCards from '../components/DashboardCards.vue'
import TrafficChart from '../components/TrafficChart.vue'
import Chart from 'chart.js/auto';
</script>
