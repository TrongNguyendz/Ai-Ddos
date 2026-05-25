<template>
  <div class="space-y-4">
    <!-- Filter -->
    <div class="card">
      <div class="flex space-x-3">
        <select v-model="statusFilter" class="input-field flex-1">
          <option value="">Tất cả Status</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
        <button @click="sortByDate" class="btn btn-ghost">
          📅 Sort by Date
        </button>
      </div>
    </div>

    <!-- Alerts List -->
    <div class="space-y-3">
      <div
        v-for="alert in filteredAlerts"
        :key="alert.id"
        :class="alert.status === 'resolved' ? 'opacity-50' : ''"
        class="card border-l-4"
        :style="{ borderLeftColor: getAlertColor(alert.severity) }"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <span class="text-2xl">{{ getAlertIcon(alert.severity) }}</span>
              <div>
                <h4 class="font-semibold text-white">{{ alert.title }}</h4>
                <p class="text-sm text-slate-400 mt-1">{{ alert.description }}</p>
                <div class="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                  <span>Time: {{ formatTime(alert.timestamp) }}</span>
                  <span>Src IP: <span class="text-orange-400 font-mono">{{ alert.src_ip }}</span></span>
                  <span>pktrate: <span class="text-cyan-400">{{ alert.pktrate }}</span></span>
                  <span>Confidence: <span class="text-yellow-400">{{ (alert.confidence * 100).toFixed(1) }}%</span></span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-col items-end space-y-2">
            <span :class="getStatusBadgeClass(alert.status)" class="badge">
              {{ alert.status }}
            </span>

            <div class="flex space-x-2">
              <button
                @click="blockIP(alert.src_ip)"
                class="btn btn-danger text-xs py-1 px-2"
              >
                🚫 Block
              </button>
              <button
                @click="addToBlacklist(alert.src_ip)"
                class="btn btn-ghost text-xs py-1 px-2"
              >
                📋 Blacklist
              </button>
              <button
                @click="resolveAlert(alert.id)"
                v-if="alert.status !== 'resolved'"
                class="btn btn-success text-xs py-1 px-2"
              >
                ✓ Resolve
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredAlerts.length === 0" class="card text-center py-8 text-slate-400">
        Không có cảnh báo
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAlertStore } from '../stores'

const alertStore = useAlertStore()
const statusFilter = ref('')
const sortDesc = ref(true)

// Mock alerts
const mockAlerts = [
  {
    id: 1,
    title: 'UDP Flood Attack Detected',
    description: 'Massive UDP flood from single source with high packet rate',
    severity: 'critical',
    status: 'new',
    timestamp: Date.now(),
    src_ip: '203.0.113.50',
    pktrate: 8900,
    confidence: 0.98
  },
  {
    id: 2,
    title: 'Syn Flood Attempt',
    description: 'Multiple SYN packets detected on port 80',
    severity: 'high',
    status: 'new',
    timestamp: Date.now() - 60000,
    src_ip: '198.51.100.75',
    pktrate: 4500,
    confidence: 0.92
  },
  {
    id: 3,
    title: 'ICMP Echo Request Storm',
    description: 'High volume of ICMP requests from external network',
    severity: 'medium',
    status: 'acknowledged',
    timestamp: Date.now() - 300000,
    src_ip: '192.0.2.100',
    pktrate: 2300,
    confidence: 0.85
  },
]

mockAlerts.forEach(alert => alertStore.addAlert(alert))

const filteredAlerts = computed(() => {
  let alerts = alertStore.alerts

  if (statusFilter.value) {
    alerts = alerts.filter(a => a.status === statusFilter.value)
  }

  if (sortDesc.value) {
    return alerts.sort((a, b) => b.timestamp - a.timestamp)
  }
  return alerts.sort((a, b) => a.timestamp - b.timestamp)
})

const getAlertIcon = (severity) => {
  const icons = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🟢'
  }
  return icons[severity] || '⚠️'
}

const getAlertColor = (severity) => {
  const colors = {
    critical: '#ef4444',
    high: '#f59e0b',
    medium: '#eab308',
    low: '#10b981'
  }
  return colors[severity] || '#3b82f6'
}

const getStatusBadgeClass = (status) => {
  const classes = {
    new: 'badge-danger',
    acknowledged: 'badge-warning',
    resolved: 'badge-success'
  }
  return classes[status] || ''
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('vi-VN')
}

const blockIP = (ip) => {
  alertStore.blockIP(ip)
  alert(`Đã block IP: ${ip}`)
}

const addToBlacklist = (ip) => {
  alertStore.addToBlacklist(ip)
  alert(`Đã thêm IP vào blacklist: ${ip}`)
}

const resolveAlert = (id) => {
  alertStore.resolveAlert(id)
}

const sortByDate = () => {
  sortDesc.value = !sortDesc.value
}
</script>
