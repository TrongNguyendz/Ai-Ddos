<template>
  <div>
    <div class="space-y-6">
      <div>
        <h2 class="text-2xl font-bold text-white mb-2">Quản Lý Alerts</h2>
        <p class="text-slate-400">Danh sách các cảnh báo bảo mật</p>
      </div>

      <!-- Header Actions -->
      <div class="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
        <div class="flex-1 max-w-md">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Tìm kiếm IP, rule hoặc mô tả..."
            class="input-field w-full"
            @keyup.enter="fetchAlerts"
          />
        </div>

        <div class="flex gap-3">
          <button @click="fetchAlerts" class="btn btn-ghost flex items-center gap-2">
            🔄 Làm mới
          </button>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="card p-4">
          <div class="text-slate-400 text-sm">Tổng Alerts</div>
          <div class="text-3xl font-bold text-white mt-1">{{ alerts.length }}</div>
        </div>
        <div class="card p-4">
          <div class="text-slate-400 text-sm">AI Detection</div>
          <div class="text-3xl font-bold text-purple-400 mt-1">{{ aiAlerts }}</div>
        </div>
        <div class="card p-4">
          <div class="text-slate-400 text-sm">Đã Block</div>
          <div class="text-3xl font-bold text-red-400 mt-1">{{ blockedAlerts }}</div>
        </div>
        <div class="card p-4">
          <div class="text-slate-400 text-sm">Severity High</div>
          <div class="text-3xl font-bold text-orange-400 mt-1">{{ highSeverity }}</div>
        </div>
      </div>

      <!-- Table -->
      <div class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-700 sticky top-0">
              <tr>
                <th class="px-4 py-3 text-left text-slate-300">Timestamp</th>
                <th class="px-4 py-3 text-left text-slate-300">Source IP</th>
                <th class="px-4 py-3 text-left text-slate-300">Title</th>
                <th class="px-4 py-3 text-left text-slate-300">Severity</th>
                <th class="px-4 py-3 text-left text-slate-300">Pktrate</th>
                <th class="px-4 py-3 text-left text-slate-300">Confidence</th>
                <th class="px-4 py-3 text-center text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading" class="text-center py-12">
                <td colspan="7" class="text-slate-400">Đang tải dữ liệu...</td>
              </tr>
              <tr v-else-if="filteredAlerts.length === 0" class="text-center py-12">
                <td colspan="7" class="text-slate-400">Không tìm thấy alert nào</td>
              </tr>
              <tr
                v-for="alert in filteredAlerts"
                :key="alert.id || alert._id || alert.timestamp + alert.src_ip"
                class="border-b border-slate-700 hover:bg-slate-700/50 transition-colors"
              >
                <td class="px-4 py-4 text-slate-400 text-xs">{{ formatDate(alert.timestamp) }}</td>
                <td class="px-4 py-4 font-mono text-orange-400">{{ alert.src_ip }}</td>
                <td class="px-4 py-4 text-slate-300">{{ alert.title }}</td>
                <td class="px-4 py-4">
                  <span :class="getSeverityClass(alert.severity)" class="badge">
                    {{ alert.severity?.toUpperCase() }}
                  </span>
                </td>
                <td class="px-4 py-4 text-slate-300">{{ alert.pktrate?.toFixed(2) }}</td>
                <td class="px-4 py-4 text-slate-300">{{ (alert.confidence * 100).toFixed(1) }}%</td>
                <td class="px-4 py-4 text-center">
                  <button
                    @click="handleToggleBlock(alert)"
                    :class="alert.is_blocked 
                      ? 'bg-emerald-600 hover:bg-emerald-700' 
                      : 'bg-red-600 hover:bg-red-700'"
                    class="px-5 py-1.5 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-1 mx-auto"
                  >
                    {{ alert.is_blocked ? '✅ Bỏ chặn' : '🚫 Chặn IP' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAlerts, toggleBlock } from '../composables/alerts'

const alerts = ref([])
const searchQuery = ref('')
const loading = ref(false)

// Computed
const filteredAlerts = computed(() => {
  if (!searchQuery.value) return alerts.value
  const q = searchQuery.value.toLowerCase()
  return alerts.value.filter(item =>
    item.src_ip?.toLowerCase().includes(q) ||
    item.title?.toLowerCase().includes(q) ||
    item.description?.toLowerCase().includes(q)
  )
})

const aiAlerts = computed(() => alerts.value.filter(a => a.is_ai).length)
const blockedAlerts = computed(() => alerts.value.filter(a => a.is_blocked).length)
const highSeverity = computed(() => alerts.value.filter(a => a.severity === 'high').length)

// Methods
const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('vi-VN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const getSeverityClass = (severity) => {
  if (severity === 'high') return 'bg-red-500/20 text-red-400'
  if (severity === 'medium') return 'bg-yellow-500/20 text-yellow-400'
  return 'bg-blue-500/20 text-blue-400'
}

const fetchAlerts = async () => {
  loading.value = true
  try {
    const data = await getAlerts()
    alerts.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Lỗi fetch alerts:', error)
    window.alert('Không thể tải danh sách alerts!')
  } finally {
    loading.value = false
  }
}

const handleToggleBlock = async (alert) => {
  const alertId = alert.id || alert._id
  if (!alertId) {
    window.alert('Không tìm thấy ID của alert!')
    return
  }

  const action = alert.is_blocked ? 'bỏ chặn' : 'chặn'
  if (!confirm(`Bạn có chắc muốn ${action} IP ${alert.src_ip}?`)) return

  try {
    const result = await toggleBlock(alertId)
    window.alert(result.message || `Đã ${action} IP thành công`)
    await fetchAlerts() // Refresh danh sách
  } catch (error) {
    console.error(error)
    window.alert('Thao tác thất bại. Vui lòng thử lại!')
  }
}

onMounted(fetchAlerts)
</script>

<style scoped>
.input-field {
  @apply bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500;
}
.badge {
  @apply px-3 py-1 rounded-full text-xs font-medium;
}
</style>