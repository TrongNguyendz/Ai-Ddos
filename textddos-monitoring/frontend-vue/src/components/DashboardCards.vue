<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- Total Flows Card -->
    <div class="card-hover">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-slate-400 text-sm">Tổng Flows</p>
          <p class="text-3xl font-bold text-white mt-2">{{ totalFlows }}</p>
          <p class="text-xs text-slate-400 mt-2">+{{ recentFlows }} trong phút này</p>
        </div>
        <div class="w-16 h-16 bg-blue-900/30 rounded-full flex items-center justify-center text-3xl">📊</div>
      </div>
    </div>

    <!-- Attack Flows Card -->
    <div class="card-hover border-red-700/50">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-slate-400 text-sm">Attack Flows</p>
          <p class="text-3xl font-bold text-red-400 mt-2">{{ attackFlows }}</p>
          <p class="text-xs text-slate-400 mt-2">{{ attackPercentage }}% tổng số</p>
        </div>
        <div class="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center text-3xl animate-pulse-custom">🔴</div>
      </div>
    </div>

    <!-- Normal Flows Card -->
    <div class="card-hover border-green-700/50">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-slate-400 text-sm">Normal Flows</p>
          <p class="text-3xl font-bold text-green-400 mt-2">{{ normalFlows }}</p>
          <p class="text-xs text-slate-400 mt-2">{{ (100 - parseFloat(attackPercentage)).toFixed(2) }}% tổng số</p>
        </div>
        <div class="w-16 h-16 bg-green-900/30 rounded-full flex items-center justify-center text-3xl">✓</div>
      </div>
    </div>

    <!-- Attack Percentage Gauge -->
    <div class="card-hover">
      <div class="flex flex-col items-center justify-center h-full">
        <div class="relative w-32 h-32">
          <svg class="w-full h-full" viewBox="0 0 120 120">
            <!-- Background circle -->
            <circle cx="60" cy="60" r="50" fill="none" stroke="#334155" stroke-width="8" />
            <!-- Progress circle -->
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              :stroke="gaugeColor"
              stroke-width="8"
              stroke-dasharray="314"
              :stroke-dashoffset="314 - (314 * attackPercentage / 100)"
              stroke-linecap="round"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl font-bold text-white">{{ attackPercentage }}%</span>
          </div>
        </div>
        <p class="text-slate-400 text-sm mt-4">Tỷ lệ Tấn công</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted,nextTick } from 'vue'
import { useFlowStore } from '../stores'
import Chart from 'chart.js/auto';


const flowStore = ref([])
const totalFlows = computed(() => flowStore.value.totalFlows)
const attackFlows = computed(() => flowStore.value.attackFlows)
const normalFlows = computed(() => flowStore.value.normalFlows)
// const attackPercentage = computed(() => flowStore.value.attackPercentage)
const recentFlows = computed(() => Math.floor(Math.random() * 50) + 10)
import { getTotalFlows } from '../composables/dashboad'


const gettotalFlowsv = async () => {
  try {
    const data = await getTotalFlows()
    console.log('Dashboard stats:', data)
    flowStore.value.totalFlows = data.total_flows
    flowStore.value.attackFlows = data.attack_flows
    flowStore.value.normalFlows = data.normal_flows
  } catch (error) {
    console.error('Error fetching dashboard stats:', error)
  }
}


const attackPercentage = computed(() => {
  const total = flowStore.value.totalFlows
  const attack = flowStore.value.attackFlows
  if (total === 0) return 0
  return ((attack / total) * 100).toFixed(2)
})  



const gaugeColor = computed(() => {
  const pct = parseFloat(attackPercentage.value)
  if (pct > 70) return '#ef4444'
  if (pct > 40) return '#f59e0b'
  return '#10b981'
})

onMounted(() => {
  gettotalFlowsv()
  const interval = setInterval(gettotalFlowsv, 5000) // Cập nhật mỗi 5 giây
  onUnmounted(() => clearInterval(interval))
})

</script>
