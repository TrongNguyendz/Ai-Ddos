<template>
  <div>
    <div class="space-y-6">
      <div>
        <h2 class="text-2xl font-bold text-white mb-2">Quản Lý Danh Sách Đen</h2>
        <p class="text-slate-400">Quản lý các IP bị chặn (Blacklist)</p>
      </div>

    <!-- Header Actions -->
    <div class="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
      <div class="flex-1 max-w-md">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm IP hoặc lý do..."
          class="input-field w-full"
          @keyup.enter="filterBlacklist"
        />
      </div>

      <div class="flex gap-3">
        <button @click="showAddModal = true" class="btn btn-success flex items-center gap-2">
          <span>+</span> Thêm IP vào Blacklist
        </button>
        <button @click="exportBlacklist" class="btn btn-ghost flex items-center gap-2">
          📤 Export
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card p-4">
        <div class="text-slate-400 text-sm">Tổng IP bị chặn</div>
        <div class="text-3xl font-bold text-white mt-1">{{ blacklist.length }}</div>
      </div>
      <div class="card p-4">
        <div class="text-slate-400 text-sm">Chặn thủ công</div>
        <div class="text-3xl font-bold text-blue-400 mt-1">{{ manualBlocked }}</div>
      </div>
      <div class="card p-4">
        <div class="text-slate-400 text-sm">Chặn tự động</div>
        <div class="text-3xl font-bold text-red-400 mt-1">{{ autoBlocked }}</div>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-700 sticky top-0">
            <tr>
              <th class="px-4 py-3 text-left text-slate-300">IP Address</th>
              <th class="px-4 py-3 text-left text-slate-300">Thời gian chặn</th>
              <th class="px-4 py-3 text-left text-slate-300">Lý do</th>
              <th class="px-4 py-3 text-left text-slate-300">Loại</th>
              <th class="px-4 py-3 text-right text-slate-300">Expiry</th>
              <th class="px-4 py-3 text-center text-slate-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredBlacklist.length === 0" class="text-center py-12">
              <td colspan="6" class="text-slate-400">Không tìm thấy IP nào trong danh sách đen</td>
            </tr>
            <tr
              v-for="item in filteredBlacklist"
              :key="item.ip"
              class="border-b border-slate-700 hover:bg-slate-700/50 transition-colors"
            >
              <td class="px-4 py-4 font-mono text-orange-400">{{ item.ip }}</td>
              <td class="px-4 py-4 text-slate-400 text-xs">{{ formatDate(item.blockedAt) }}</td>
              <td class="px-4 py-4">
                <span class="text-slate-300">{{ item.reason }}</span>
              </td>
              <td class="px-4 py-4">
                <span
                  :class="item.type === 'manual' ? 'badge-blue' : 'badge-danger'"
                  class="badge"
                >
                  {{ item.type === 'manual' ? 'Thủ công' : 'Tự động' }}
                </span>
              </td>
              <td class="px-4 py-4 text-right text-sm">
                <span v-if="item.expiry" class="text-amber-400">
                  {{ formatDate(item.expiry) }}
                </span>
                <span v-else class="text-emerald-400">Vĩnh viễn</span>
              </td>
              <td class="px-4 py-4 text-center">
                <button
                  @click="unblockIP(item.ip)"
                  class="px-3 py-1 text-red-400 hover:text-red-300 hover:bg-red-900/30 rounded-md transition-colors text-xs font-medium flex items-center gap-1 mx-auto"
                >
                  🗑️ Gỡ chặn
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-4 border-t border-slate-700 flex items-center justify-between text-sm">
        <div class="text-slate-400">
          Hiển thị {{ filteredBlacklist.length }} / {{ blacklist.length }} IP
        </div>
      </div>
    </div>
  </div>

  <!-- Add IP Modal -->
  <div v-if="showAddModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
    <div class="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md p-6">
      <h3 class="text-xl font-semibold text-white mb-4">Thêm IP vào Blacklist</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-slate-400 text-sm mb-1">Địa chỉ IP</label>
          <input v-model="newBlock.ip" type="text" placeholder="192.168.1.100" class="input-field w-full" />
        </div>

        <div>
          <label class="block text-slate-400 text-sm mb-1">Lý do</label>
          <input v-model="newBlock.reason" type="text" placeholder="Tấn công DDoS, Scan port..." class="input-field w-full" />
        </div>

        <div>
          <label class="block text-slate-400 text-sm mb-1">Thời hạn</label>
          <select v-model="newBlock.duration" class="input-field w-full">
            <option value="permanent">Vĩnh viễn</option>
            <option value="1h">1 giờ</option>
            <option value="6h">6 giờ</option>
            <option value="24h">24 giờ</option>
            <option value="7d">7 ngày</option>
          </select>
        </div>
      </div>

      <div class="flex gap-3 mt-6">
        <button @click="addToBlacklist" class="btn btn-success flex-1">Xác nhận chặn</button>
        <button @click="showAddModal = false" class="btn btn-ghost flex-1">Hủy</button>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlertStore } from '../stores'

const alertStore = useAlertStore()

const blacklist = ref([
  {
    ip: '45.76.123.45',
    blockedAt: '2026-05-17T10:23:00',
    reason: 'Phát hiện tấn công SYN Flood',
    type: 'auto',
    expiry: '2026-05-18T10:23:00'
  },
  {
    ip: '103.214.56.78',
    blockedAt: '2026-05-16T22:15:00',
    reason: 'Quét port hàng loạt',
    type: 'auto',
    expiry: null
  },
  {
    ip: '185.220.101.55',
    blockedAt: '2026-05-17T08:45:00',
    reason: 'Manual block từ admin',
    type: 'manual',
    expiry: '2026-05-24T08:45:00'
  },
  {
    ip: '91.234.67.89',
    blockedAt: '2026-05-15T14:30:00',
    reason: 'Brute force SSH',
    type: 'auto',
    expiry: null
  }
])

const searchQuery = ref('')
const showAddModal = ref(false)
const newBlock = ref({
  ip: '',
  reason: '',
  duration: 'permanent'
})

// Computed
const filteredBlacklist = computed(() => {
  if (!searchQuery.value) return blacklist.value
  
  const q = searchQuery.value.toLowerCase()
  return blacklist.value.filter(item =>
    item.ip.toLowerCase().includes(q) ||
    item.reason.toLowerCase().includes(q)
  )
})

const manualBlocked = computed(() => blacklist.value.filter(i => i.type === 'manual').length)
const autoBlocked = computed(() => blacklist.value.filter(i => i.type === 'auto').length)

// Methods
const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('vi-VN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const addToBlacklist = () => {
  if (!newBlock.value.ip) {
    alert('Vui lòng nhập địa chỉ IP!')
    return
  }

  const expiry = newBlock.value.duration === 'permanent' ? null : 
    new Date(Date.now() + getDurationMs(newBlock.value.duration)).toISOString()

  blacklist.value.unshift({
    ip: newBlock.value.ip,
    blockedAt: new Date().toISOString(),
    reason: newBlock.value.reason || 'Chặn thủ công bởi admin',
    type: 'manual',
    expiry
  })

  alertStore.addNotification({
    type: 'success',
    message: `Đã chặn IP ${newBlock.value.ip}`
  })

  // Reset form
  newBlock.value = { ip: '', reason: '', duration: 'permanent' }
  showAddModal.value = false
}

const getDurationMs = (duration) => {
  const map = {
    '1h': 3600000,
    '6h': 21600000,
    '24h': 86400000,
    '7d': 604800000
  }
  return map[duration] || 0
}

const unblockIP = (ip) => {
  if (confirm(`Bạn có chắc muốn gỡ chặn IP ${ip}?`)) {
    blacklist.value = blacklist.value.filter(item => item.ip !== ip)
    alertStore.addNotification({
      type: 'success',
      message: `Đã gỡ chặn IP ${ip}`
    })
  }
}

const exportBlacklist = () => {
  const dataStr = JSON.stringify(blacklist.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `blacklist_${new Date().toISOString().slice(0,10)}.json`
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

// Search
const filterBlacklist = () => {
  // Already handled by computed
}

onMounted(() => {
  console.log('🛡️ BlacklistView loaded')
})
</script>

<style scoped>
.input-field {
  @apply bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500;
}
.badge {
  @apply px-3 py-1 rounded-full text-xs font-medium;
}
.badge-blue { @apply bg-blue-500/20 text-blue-400; }
.badge-danger { @apply bg-red-500/20 text-red-400; }
</style>