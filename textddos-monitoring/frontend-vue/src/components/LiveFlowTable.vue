<template>
  <div class="space-y-6">
    <!-- Filters & Search -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <input v-model="filters.switch" type="text" placeholder="Tìm kiếm switch" class="input-field" />
        <select v-model="filters.protocol" class="input-field">
          <option value="">Tất cả Protocol</option>
          <option value="TCP">TCP</option>
          <option value="UDP">UDP</option>
          <option value="ICMP">ICMP</option>
        </select>
        <select v-model="filters.label" class="input-field">
          <option value="">Tất cả Label</option>
          <option value="0">Normal</option>
          <option value="1">Attack</option>
        </select>
        <input v-model="filters.srcIP" type="text" placeholder="Src IP..." class="input-field" />
        <input v-model="filters.dstIP" type="text" placeholder="Dst IP..." class="input-field" />
        <button
          @click="autoRefresh = !autoRefresh"
          :class="autoRefresh ? 'btn-success' : 'btn-ghost'"
          class="btn"
        >
          {{ autoRefresh ? 'Auto: ON' : 'Auto: OFF' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      <span class="ml-2 text-slate-400">Đang tải dữ liệu...</span>
    </div>

    <!-- Bản đồ lớn -->
    <div class="card overflow-hidden">
      <div class="relative">
        <div class="h-[500px] w-full" id="map-container">
          <div id="live-map" class="h-full w-full"></div>
        </div>

        <!-- Nút Clear Markers -->
        <button 
          @click="clearMarkers"
          class="absolute top-4 right-4 z-[1000] btn btn-ghost text-sm px-4 py-2 bg-slate-800/90 hover:bg-slate-700 shadow-lg">
          🗑️ Xóa tất cả Markers
        </button>
      </div>
    </div>

    <!-- Bảng dữ liệu -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-slate-700">
            <tr>
              <th class="px-4 py-3 text-left text-slate-300">Timestamp</th>
              <th class="px-4 py-3 text-left text-slate-300">Switch</th>
              <th class="px-4 py-3 text-left text-slate-300">Src IP</th>
              <th class="px-4 py-3 text-left text-slate-300">Dst IP</th>
              <th class="px-4 py-3 text-left text-slate-300">Protocol</th>
              <th class="px-4 py-3 text-right text-slate-300">pktrate</th>
              <th class="px-4 py-3 text-right text-slate-300">tot_kbps</th>
              <th class="px-4 py-3 text-right text-slate-300">pktcount</th>
              <th class="px-4 py-3 text-right text-slate-300">bytecount</th>
              <th class="px-4 py-3 text-center text-slate-300">Label</th>
              <th class="px-4 py-3 text-right text-slate-300">Confidence</th>
              <th class="px-4 py-3 text-center text-slate-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && flows.length === 0">
              <td colspan="12" class="text-center py-8 text-slate-400">Đang tải dữ liệu...</td>
            </tr>
            <tr v-else-if="!loading && flows.length === 0">
              <td colspan="12" class="text-center py-8 text-slate-400">Không có dữ liệu</td>
            </tr>
            <tr
              v-for="(flow, idx) in paginatedFlows"
              :key="idx"
              :class="isHighlightedAttack(flow) ? 'highlight-danger' : 'hover:bg-slate-700/50'"
              class="border-b border-slate-700 transition-colors"
            >
              <td class="px-4 py-3 text-slate-400 text-xs">{{ formatTimeRelative(flow.timestamp) }}</td>
              <td class="px-4 py-3 font-mono">{{ flow.switch }}</td>
              <td class="px-4 py-3 font-mono text-orange-400">{{ flow.src_ip }}</td>
              <td class="px-4 py-3 font-mono text-cyan-400">{{ flow.dst_ip }}</td>
              <td class="px-4 py-3"><span class="badge badge-info">{{ flow.protocol }}</span></td>
              <td class="px-4 py-3 text-right">{{ flow.pktrate }}</td>
              <td class="px-4 py-3 text-right">{{ flow.tot_kbps }}</td>
              <td class="px-4 py-3 text-right">{{ flow.pktcount }}</td>
              <td class="px-4 py-3 text-right">{{ flow.bytecount }}</td>
              <td class="px-6 py-3 text-center">
                <span :class="flow.label === 1 ? 'badge-danger' : 'badge-success'" class="badge">
                  {{ flow.label === 1 ? 'Nghi ngờ ' : 'Bình thường' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <span :class="getConfidenceClass(flow.confidence)">
                  {{ (flow.confidence * 100).toFixed(1) }}%
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <button v-if="flow.label === 1" @click="blockIP(flow.src_ip)" class="text-red-400 hover:text-red-300 text-xs">
                  🚫
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-4 border-t border-slate-700 flex items-center justify-between">
        <div class="text-sm text-slate-400">
          Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, totalItems) }} of {{ totalItems }} flows
        </div>
        <div class="flex space-x-2">
          <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1" class="btn btn-ghost disabled:opacity-50 disabled:cursor-not-allowed">← Prev</button>
          <span class="px-3 py-2 text-slate-300">Page {{ currentPage }} / {{ totalPages }}</span>
          <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages" class="btn btn-ghost disabled:opacity-50 disabled:cursor-not-allowed">Next →</button>
        </div>
      </div>
    </div>
    <chatbot />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted,nextTick } from 'vue'
import { useAlertStore } from '../stores'
import { getFlows } from '../composables/flow'
import { useWebSocket } from '../composables/useWebsocket'
import L from 'leaflet'
import chatbot from './chatbot.vue'
const alertStore = useAlertStore()
const ws = useWebSocket()

// ================== CONFIG ==================
const IPINFO_TOKEN = '7da40361fec9a1' // ← Thay bằng token của bạn[](https://ipinfo.io)

// State
const flows = ref([])  // Chứa dữ liệu từ API
const loading = ref(false)
const searchQuery = ref('')
const autoRefresh = ref(true)
const currentPage = ref(1)
const itemsPerPage = ref(10)

const filters = ref({
  protocol: '',
  label: '',
  srcIP: '',
  dstIP: '',
  switch: ''
})

let refreshInterval = null

// Map
let map = null
let markersLayer = null

// ================== LEAFLET INIT ==================
const initMap = async () => {
  await nextTick() // Đợi DOM render xong

  const mapContainer = document.getElementById('live-map')
  if (!mapContainer) {
    console.error('❌ Không tìm thấy element #live-map')
    return
  }

  map = L.map('live-map', {
      center: [16.0, 108.0], // Trung tâm VN tốt hơn
      zoom: 5,
      zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18,
  }).addTo(map)

  markersLayer = L.layerGroup().addTo(map)

  console.log('🗺️ Leaflet Map initialized successfully')
}

// ================== IPINFO & MARKER ==================
const getGeoFromIP = async (ip) => {
  if (!ip || ip === '0.0.0.0' || ip.startsWith('192.168.') || ip.startsWith('10.')) return null

  try {
    const res = await fetch(`https://ipinfo.io/${ip}/json?token=${IPINFO_TOKEN}`)
    if (!res.ok) return null
    const data = await res.json()
    console.log(`🌍 Geo info for ${ip}:`, data)
    if (data.loc) {
      const [lat, lng] = data.loc.split(',').map(Number)
      return { lat, lng, city: data.city, country: data.country }
    }
  } catch (err) {
    console.warn(`Geo lookup failed for ${ip}:`, err.message)
  }
  return null
}

const getMarkerColor = (flow) => {
  if (flow.label === 1) {
    return flow.confidence > 0.85 ? '#ef4444' : '#f97316'
  }
  return '#22c55e'
}

const createCustomIcon = (color) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="background-color:${color}; width:14px; height:14px; border-radius:50%; border:2px solid white; box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
})

const addFlowToMap = async (flow) => {
  if (!map || !flow.src_ip) return

  const geo = await getGeoFromIP(flow.src_ip)
  if (!geo) return

  const color = getMarkerColor(flow)
  const icon = createCustomIcon(color)

  const popupContent = `
    <b>${flow.label === 1 ? '🚨 ATTACK' : '✅ Normal'}</b><br>
    <b>Src:</b> ${flow.src_ip}<br>
    <b>Dst:</b> ${flow.dst_ip}<br>
    <b>Protocol:</b> ${flow.protocol}<br>
    <b>Confidence:</b> ${(flow.confidence * 100).toFixed(1)}%<br>
    ${geo.city ? `<b>${geo.city}, ${geo.country}</b>` : ''}
  `

  L.marker([geo.lat, geo.lng], { icon })
    .bindPopup(popupContent)
    .addTo(markersLayer)

  // Zoom vào attack
  if (flow.label === 1 && flow.confidence > 0.8) {
    map.flyTo([geo.lat, geo.lng], 9, { duration: 1.2 })
  }
}

const formatTimeRelative = (timestamp) => {
  if (!timestamp) return '—'
  
  const date = new Date(timestamp)

  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return 'Vừa xong'
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} phút trước`
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} giờ trước`
  
  return date.toLocaleString('vi-VN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}
// Hàm fetch dữ liệu từ API
// ====================== FETCH API ======================
const fetchFlows = async () => {
  if (loading.value) return
  loading.value = true
  try {
    const params = {
      protocol: filters.value.protocol || undefined,
      label: filters.value.label !== '' ? Number(filters.value.label) : undefined,
      src_ip: filters.value.srcIP ||  undefined,      // ← convert sang snake_case
      dst_ip: filters.value.dstIP ||  undefined,
      switch: filters.value.switch || undefined,
      search: searchQuery.value || undefined
    }

    // Loại bỏ các key undefined
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) delete params[key]
    })

    const response = await getFlows(params)
    flows.value = response || []
    console.log(`📥 Loaded ${flows.value.length} flows from API`)
  } catch (error) {
    console.error('Error fetching flows:', error)
    flows.value = []
  } finally {
    loading.value = false
  }
}

// Debounce cho search/filter
let debounceTimer
const debouncedFetch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1 // Reset về trang 1 khi filter thay đổi
    fetchFlows()
  }, 500)
}

// Watch các filter thay đổi
watch([searchQuery, filters], () => {
  debouncedFetch()
}, { deep: true })

// Auto refresh
watch(autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// const startAutoRefresh = () => {
//   if (refreshInterval) clearInterval(refreshInterval)
//   refreshInterval = setInterval(() => {
//     fetchFlows()
//   }, 5000) // Refresh mỗi 5 giây

// }

// const stopAutoRefresh = () => {
//   if (refreshInterval) {
//     clearInterval(refreshInterval)
//     refreshInterval = null
//   }

// }
let unsubscribe = null

const startAutoRefresh = async () => {
  try {
    await ws.connect('ws://localhost:8000/ws')

    unsubscribe = ws.onMessage(async (message) => {
      // Xử lý theo cấu trúc message từ backend
      // console.log('📩 Received WebSocket message:', message)
      if (message.type === 'flow' && message.data) {
        const newFlow = message.data

        // Tránh duplicate (dựa trên Src IP + timestamp hoặc id)
        const isDuplicate = flows.value.some(flow => 
          flow.src_ip === newFlow.src_ip && 
          flow.timestamp === newFlow.timestamp
        )

        if (!isDuplicate) {
          flows.value.unshift(newFlow)   // Thêm flow mới nhất lên đầu

          // Giới hạn tối đa 200 flows để tránh lag
          if (flows.value.length > 200) {
            flows.value.pop()
          }
          // 🔥 Quan trọng: Vẽ marker
          await addFlowToMap(newFlow)
        }
      }
    })

    console.log('🚀 WebSocket Live Flow started')
  } catch (error) {
    console.error('❌ WebSocket connection failed:', error)
  }
}

const stopAutoRefresh = () => {
  if (unsubscribe) {
    unsubscribe()
    unsubscribe = null
  }
  ws.disconnect()
}


// Pagination computed (chỉ xử lý phân trang, không filter)
const totalItems = computed(() => flows.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value)
const endIndex = computed(() => startIndex.value + itemsPerPage.value)

const paginatedFlows = computed(() => {
  return flows.value.slice(startIndex.value, endIndex.value)
})

// Reset page khi totalPages thay đổi
watch(totalPages, (newTotalPages) => {
  if (currentPage.value > newTotalPages && newTotalPages > 0) {
    currentPage.value = newTotalPages
  }
})

// const formatTime = (timestamp) => {
//   return new Date(timestamp).toLocaleTimeString('vi-VN')
// }

const isHighlightedAttack = (flow) => {
  return flow.label === 1 && flow.confidence > 0.8
}

const getConfidenceClass = (confidence) => {
  if (confidence > 0.8) return 'text-red-400 font-semibold'
  if (confidence > 0.5) return 'text-yellow-400'
  return 'text-green-400'
}

const blockIP = (ip) => {
  alertStore.blockIP(ip)
  alert(`Đã block IP: ${ip}`)
}

// Lifecycle
onMounted(async () => {
  await initMap()           // ← Quan trọng!
  await fetchFlows()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  if (map) map.remove()
})

</script>

<style scoped>
/* Fix Leaflet icon trong Vue */
:deep(.leaflet-marker-icon) {
  filter: drop-shadow(0 2px 3px rgba(0,0,0,0.3));
}
</style>