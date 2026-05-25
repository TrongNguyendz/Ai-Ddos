<template>
  <div class="min-h-screen bg-slate-900">
    <div class="flex">
      <!-- Sidebar -->
      <aside class="w-64 bg-slate-800 border-r border-slate-700 min-h-screen sticky top-0 flex flex-col">
        <div class="p-6 border-b border-slate-700">
          <h1 class="text-2xl font-bold text-blue-400">TextDDOS</h1>
          <p class="text-xs text-slate-400 mt-1">Giám sát DDoS Realtime</p>
        </div>

        <nav class="p-4 flex-1 space-y-2">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="block px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            :class="{ 'bg-blue-600 text-white': isActive(item.path) }"
          >
            <span class="inline-block w-5">{{ item.icon }}</span>
            <span class="ml-2">{{ item.label }}</span>
          </router-link>
        </nav>

        <!-- User Info + Logout -->
        <div class="p-4 border-t border-slate-700 bg-slate-800 mt-auto">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                A
              </div>
              <div>
                <p class="text-sm font-medium text-white">Admin User</p>
                <p class="text-xs text-emerald-400">● Trực tuyến</p>
              </div>
            </div>

            <button
              @click="handleLogout"
              class="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded-lg transition-colors"
              title="Đăng xuất"
            >
              ⬅️
            </button>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-auto">
        <!-- Top Header -->
        <header class="bg-slate-800 border-b border-slate-700 sticky top-0 z-10">
          <div class="px-8 py-4 flex justify-between items-center">
            <div>
              <h2 class="text-xl font-semibold text-white">{{ currentPageTitle }}</h2>
            </div>
            <div class="flex items-center space-x-4">
              <button class="relative p-2 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                <span class="text-xl">🔔</span>
                <span v-if="alertCount > 0" class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                  {{ alertCount }}
                </span>
              </button>
              <button class="p-2 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                <span class="text-xl">⚙️</span>
              </button>
            </div>
          </div>
        </header>

        <!-- Page Content -->
        <div class="p-8">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', label: 'Tổng Quan', icon: '📊' },
  { path: '/live-flows', label: 'Live Flows', icon: '📡' },
  { path: '/analytics', label: 'Phân Tích', icon: '📈' },
  // { path: '/alerts', label: 'Cảnh Báo', icon: '⚠️' },
  { path: '/rules', label: 'Quy Tắc', icon: '⚙️' },
]

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path === path
}

const currentPageTitle = computed(() => {
  const item = navItems.find(item => isActive(item.path))
  return item?.label || 'Dashboard'
})

const alertCount = 12

const handleLogout = () => {
  if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('username')
    router.push('/login')
  }
}
</script>