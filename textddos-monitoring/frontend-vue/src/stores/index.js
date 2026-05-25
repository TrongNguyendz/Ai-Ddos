import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFlowStore = defineStore('flows', () => {
  const flows = ref([])
  const totalFlows = ref(0)
  const attackFlows = ref(0)
  const normalFlows = ref(0)
  const attackPercentage = ref(0)
  const topAttackingIPs = ref([])
  const topTargetedIPs = ref([])
  
  // Thêm method này
  const setFlows = (newFlows) => {
    flows.value = newFlows
    updateStats() // Cập nhật lại thống kê
  }
  // Thêm flow mới
  const addFlow = (flow) => {
    flows.value.unshift(flow)
    if (flows.value.length > 1000) {
      flows.value.pop()
    }
    updateStats()
  }

  // Cập nhật thống kê
  const updateStats = () => {
    totalFlows.value = flows.value.length
    attackFlows.value = flows.value.filter(f => f.label === 1).length
    normalFlows.value = flows.value.filter(f => f.label === 0).length
    attackPercentage.value = totalFlows.value > 0 ? (attackFlows.value / totalFlows.value * 100).toFixed(2) : 0

    // Tính top IPs
    const ipCounts = {}
    flows.value.forEach(flow => {
      ipCounts[flow.src_ip] = (ipCounts[flow.src_ip] || 0) + 1
    })
    topAttackingIPs.value = Object.entries(ipCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([ip, count]) => ({ ip, count }))

    const targetCounts = {}
    flows.value.forEach(flow => {
      targetCounts[flow.dst_ip] = (targetCounts[flow.dst_ip] || 0) + 1
    })
    topTargetedIPs.value = Object.entries(targetCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([ip, count]) => ({ ip, count }))
  }

  // Lấy flows với filter
  const getFilteredFlows = (filters) => {
    return flows.value.filter(flow => {
      if (filters.switch && flow.switch !== filters.switch) return false
      if (filters.protocol && flow.protocol !== filters.protocol) return false
      if (filters.label !== undefined && flow.label !== filters.label) return false
      if (filters.srcIP && !flow.src_ip.includes(filters.srcIP)) return false
      if (filters.dstIP && !flow.dst_ip.includes(filters.dstIP)) return false
      return true
    })
  }

  return {
    flows,
    totalFlows,
    attackFlows,
    normalFlows,
    attackPercentage,
    topAttackingIPs,
    topTargetedIPs,
    addFlow,
    setFlows,
    updateStats,
    getFilteredFlows
  }
})

export const useAlertStore = defineStore('alerts', () => {
  const alerts = ref([])
  const activeAlerts = ref(0)

  const addAlert = (alert) => {
    alerts.value.unshift({
      ...alert,
      id: Date.now(),
      timestamp: new Date(),
      status: 'new'
    })
  }

  const resolveAlert = (alertId) => {
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.status = 'resolved'
      activeAlerts.value = Math.max(0, activeAlerts.value - 1)
    }
  }

  const blockIP = (ip) => {
    console.log('Blocking IP:', ip)
    // Gửi request đến backend
  }

  const addToBlacklist = (ip) => {
    console.log('Adding to blacklist:', ip)
    // Gửi request đến backend
  }

  return {
    alerts,
    activeAlerts,
    addAlert,
    resolveAlert,
    blockIP,
    addToBlacklist
  }
})

export const useRuleStore = defineStore('rules', () => {
  const rules = ref([])

  const addRule = (rule) => {
    rules.value.push({
      ...rule,
      id: Date.now(),
      createdAt: new Date(),
      triggeredCount: 0,
      enabled: true
    })
  }

  const updateRule = (id, updates) => {
    const rule = rules.value.find(r => r.id === id)
    if (rule) {
      Object.assign(rule, updates)
    }
  }

  const deleteRule = (id) => {
    const index = rules.value.findIndex(r => r.id === id)
    if (index > -1) {
      rules.value.splice(index, 1)
    }
  }

  const toggleRule = (id) => {
    const rule = rules.value.find(r => r.id === id)
    if (rule) {
      rule.enabled = !rule.enabled
    }
  }

  return {
    rules,
    addRule,
    updateRule,
    deleteRule,
    toggleRule
  }
})
