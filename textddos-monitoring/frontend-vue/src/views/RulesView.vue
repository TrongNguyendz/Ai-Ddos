<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-white mb-2">Quản Lý Quy Tắc</h2>
      <p class="text-slate-400">Tạo, sửa đổi và quản lý các quy tắc tự động</p>
    </div>

    <!-- Add New Rule Form -->
    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4">➕ Tạo Quy Tắc Mới</h3>
      <form @submit.prevent="addNewRule" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            v-model="newRule.name"
            type="text"
            placeholder="Tên quy tắc"
            class="input-field"
            required
          />
          <input
            v-model="newRule.description"
            type="text"
            placeholder="Mô tả"
            class="input-field"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm text-slate-400 mb-2">pktrate ></label>
            <input
              v-model.number="newRule.pktrate_threshold"
              type="number"
              placeholder="e.g., 1000"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-sm text-slate-400 mb-2">Protocol</label>
            <select v-model="newRule.protocol" class="input-field">
              <option value="">Tất cả</option>
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-slate-400 mb-2">Action</label>
            <select v-model="newRule.action" class="input-field">
              <option value="block">Block IP</option>
              <option value="alert">Alert</option>
              <option value="log">Log Only</option>
            </select>
          </div>
        </div>

        <button type="submit" class="btn btn-success w-full" :disabled="loading">
          {{ loading ? 'Đang tạo...' : '+ Tạo Quy Tắc' }}
        </button>
      </form>
    </div>

    <!-- Rules List -->
    <div class="card">
      <h3 class="text-lg font-semibold text-white mb-4 flex justify-between items-center">
        📋 Danh Sách Quy Tắc
        <button @click="fetchRules" class="text-sm text-slate-400 hover:text-white">
          🔄 Làm mới
        </button>
      </h3>
      
      <div v-if="loading" class="text-center py-8 text-slate-400">
        Đang tải dữ liệu...
      </div>

      <div class="space-y-3">
        <div
          v-for="rule in rules"
          :key="rule.id"
          class="border border-slate-700 rounded-lg p-4 hover:bg-slate-700/30 transition-colors"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <button
                  @click="toggleRule(rule.id, !rule.enabled)"
                  :class="rule.enabled ? 'bg-green-600' : 'bg-slate-600'"
                  class="w-10 h-6 rounded-full flex items-center px-1 transition-all"
                >
                  <div :class="rule.enabled ? 'translate-x-4' : 'translate-x-0'" 
                       class="w-4 h-4 bg-white rounded-full transition-transform"></div>
                </button>
                <div>
                  <h4 class="font-semibold text-white">{{ rule.name }}</h4>
                  <p class="text-sm text-slate-400">{{ rule.description }}</p>
                  <div class="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                    <span v-if="rule.conditions?.protocol">Protocol: <span class="text-blue-400 font-mono">{{ rule.conditions?.protocol }}</span></span>
                    <span>pktrate > <span class="text-cyan-400">{{ rule.conditions?.pktrate_threshold || 'N/A' }}</span></span>
                    <span>Action: <span class="badge" :class="getActionBadge(rule.actions)">{{ rule.actions }}</span></span>
                    <span>Triggered: <span class="text-yellow-400">{{ rule.triggered_count || 0 }}x</span></span>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex space-x-2">
              <button @click="editRule(rule)" class="btn btn-ghost py-1 px-2 text-sm">
                ✏️ Edit
              </button>
              <button @click="deleteRule(rule.id)" class="btn btn-danger py-1 px-2 text-sm">
                🗑️ Delete
              </button>
            </div>
          </div>
        </div>

        <div v-if="!loading && rules.length === 0" class="text-center py-8 text-slate-400">
          Không có quy tắc nào. Tạo quy tắc đầu tiên để bắt đầu.
        </div>
      </div>
    </div>

    <!-- Rule History -->
    <!-- Rule History -->
<div class="card">
  <h3 class="text-lg font-semibold text-white mb-4 flex justify-between items-center">
    📊 Lịch Sử Kích Hoạt
    <button @click="fetchRuleHistory" class="text-sm text-slate-400 hover:text-white">
      🔄 Làm mới
    </button>
  </h3>

  <div v-if="historyLoading" class="text-center py-8 text-slate-400">
    Đang tải lịch sử...
  </div>

  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead class="bg-slate-700">
        <tr>
          <th class="px-4 py-3 text-left text-slate-300">Thời gian</th>
          <th class="px-4 py-3 text-left text-slate-300">Quy Tắc</th>
          <th class="px-4 py-3 text-left text-slate-300">Src IP</th>
          <th class="px-4 py-3 text-right text-slate-300">pktrate</th>
          <th class="px-4 py-3 text-left text-slate-300">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="event in ruleHistory" :key="event.id" class="border-b border-slate-700 hover:bg-slate-700/50">
          <td class="px-4 py-3 text-slate-400 text-xs">{{ formatTime(event.timestamp) }}</td>
          <td class="px-4 py-3">{{ event.ruleName }}</td>
          <td class="px-4 py-3 font-mono text-orange-400">{{ event.src_ip }}</td>
          <td class="px-4 py-3 text-right font-mono">{{ event.pktrate }}</td>
          <td class="px-4 py-3">
            <span class="badge" :class="getActionBadge(event.action)">{{ event.action }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="!historyLoading && ruleHistory.length === 0" class="text-center py-8 text-slate-400">
    Chưa có lịch sử kích hoạt nào.
  </div>
</div>
    <!-- Edit Rule Modal -->
<div v-if="showEditModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
  <div class="bg-slate-800 rounded-xl p-6 w-full max-w-md mx-4">
    <h3 class="text-xl font-semibold text-white mb-4">✏️ Chỉnh Sửa Quy Tắc</h3>
    
    <div class="space-y-4">
      <input
        v-model="editForm.name"
        type="text"
        placeholder="Tên quy tắc"
        class="input-field w-full"
      />
      <input
        v-model="editForm.description"
        type="text"
        placeholder="Mô tả"
        class="input-field w-full"
      />
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm text-slate-400 mb-2">pktrate ></label>
          <input
            v-model.number="editForm.pktrate_threshold"
            type="number"
            class="input-field w-full"
          />
        </div>
        <div>
          <label class="block text-sm text-slate-400 mb-2">Protocol</label>
          <select v-model="editForm.protocol" class="input-field w-full">
            <option value="">Tất cả</option>
            <option value="TCP">TCP</option>
            <option value="UDP">UDP</option>
            <option value="ICMP">ICMP</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-slate-400 mb-2">Action</label>
          <select v-model="editForm.action" class="input-field w-full">
            <option value="block">Block IP</option>
            <option value="alert">Alert</option>
            <option value="log">Log Only</option>
          </select>
        </div>
      </div>
    </div>

    <div class="flex gap-3 mt-6">
      <button @click="cancelEdit" class="btn btn-ghost flex-1">
        Hủy
      </button>
      <button @click="saveEdit" class="btn btn-success flex-1" :disabled="loading">
        {{ loading ? 'Đang lưu...' : 'Lưu thay đổi' }}
      </button>
    </div>
  </div>
</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as ruleApi from '../composables/rule'

const rules = ref([])
const ruleHistory = ref([])
const loading = ref(false)
const historyLoading = ref(false)
// Modal edit
const showEditModal = ref(false)
const editingRule = ref(null)

const newRule = ref({
  name: '',
  description: '',
  pktrate_threshold: '',
  protocol: '',
  action: ''
})

// Rule đang edit
const editForm = ref({
  name: '',
  description: '',
  pktrate_threshold: '',
  protocol: '',
  action: ''
})

// Transform frontend data to backend format
const transformToBackend = (rule) => ({
  name: rule.name,
  description: rule.description || '',
  conditions: {
    pktrate_threshold: rule.pktrate_threshold ,
    ...(rule.protocol && { protocol: rule.protocol })
  },
  actions: [rule.action],
  enabled: true
})

const fetchRules = async () => {
  loading.value = true
  try {
    const data = await ruleApi.getRules()
    rules.value = Array.isArray(data) ? data : data.results || data.data || []
  } catch (error) {
    console.error('Lỗi khi lấy danh sách rules:', error)
    alert('Không thể tải danh sách quy tắc')
  } finally {
    loading.value = false
  }
}

const fetchRuleHistory = async () => {
  historyLoading.value = true
  try {
    const data = await ruleApi.getRuleHistory({ limit: 20, skip: 0 })
    
    // Map dữ liệu từ API về format phù hợp với bảng
    ruleHistory.value = (data.history || []).map(item => ({
      id: item.id,
      timestamp: item.timestamp,
      ruleName: item.rule_name || 'Unknown Rule',
      src_ip: item.src_ip,
      pktrate: item.pktrate?.toFixed(2) || item.pktrate,
      action: item.action,
      confidence: item.confidence,
      protocol: item.flow_details?.protocol
    }))
  } catch (error) {
    console.error('Lỗi khi lấy lịch sử:', error)
    ruleHistory.value = []
  } finally {
    historyLoading.value = false
  }
}

const addNewRule = async () => {
  if (!newRule.value.name) {
    alert('Vui lòng nhập tên quy tắc')
    return
  }

  loading.value = true
  try {
    const payload = transformToBackend(newRule.value)
    await ruleApi.createRule(payload)
    
    alert('✅ Quy tắc đã được tạo thành công!')
    newRule.value = { name: '', description: '', pktrate_threshold: 1000, protocol: '', action: 'block' }
    await fetchRules()
  } catch (error) {
    console.error(error)
    alert('❌ Lỗi khi tạo quy tắc: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// ==================== EDIT FUNCTIONS ====================
const editRule = (rule) => {
  editingRule.value = { ...rule }
  
  editForm.value = {
    name: rule.name || '',
    description: rule.description || '',
    pktrate_threshold: rule.conditions?.pktrate_threshold || 1000,
    protocol: rule.conditions?.protocol || '',
    action: Array.isArray(rule.actions) ? rule.actions[0] : rule.actions || 'block'
  }
  
  showEditModal.value = true
}

const saveEdit = async () => {
  if (!editingRule.value || !editForm.value.name) {
    alert('Vui lòng nhập tên quy tắc')
    return
  }

  loading.value = true
  try {
    const payload = transformToBackend(editForm.value)
    await ruleApi.updateRule(editingRule.value.id, payload)
    
    alert('✅ Cập nhật quy tắc thành công!')
    showEditModal.value = false
    await fetchRules()
  } catch (error) {
    console.error(error)
    alert('❌ Lỗi khi cập nhật: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  showEditModal.value = false
  editingRule.value = null
}

// ==================== Các hàm khác giữ nguyên ====================
const toggleRule = async (id, enabled) => {
  try {
    await ruleApi.toggleRule(id, enabled)
    await fetchRules()
  } catch (error) {
    console.error(error)
    alert('Không thể thay đổi trạng thái quy tắc')
  }
}

const deleteRule = async (id) => {
  if (!confirm('Bạn có chắc chắn muốn xóa quy tắc này?')) return
  
  try {
    await ruleApi.deleteRule(id)
    alert('✅ Đã xóa quy tắc')
    await fetchRules()
  } catch (error) {
    console.error(error)
    alert('Không thể xóa quy tắc')
  }
}

const formatTime = (timestamp) => new Date(timestamp).toLocaleString('vi-VN')

const getActionBadge = (action) => {
  const badges = {
    block: 'badge-danger',
    alert: 'badge-warning',
    log: 'badge-info'
  }
  return badges[action] || 'badge-info'
}

onMounted(() => {
  fetchRules()
  fetchRuleHistory()
})
</script>