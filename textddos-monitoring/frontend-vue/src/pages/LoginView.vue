<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center relative overflow-hidden">
    <!-- Background Effect -->
    <div class="absolute inset-0 bg-[radial-gradient(at_center,#1e3a8a_0%,transparent_70%)] opacity-30"></div>
    <div class="absolute inset-0 bg-grid-slate-800/30"></div>

    <div class="relative z-10 w-full max-w-md px-6">
      <!-- Login Card -->
      <div class="bg-slate-900/90 backdrop-blur-xl border border-slate-700 rounded-3xl shadow-2xl p-10">
        <!-- Logo & Title -->
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl mb-6 shadow-lg shadow-blue-500/30">
            <span class="text-5xl">🛡️</span>
          </div>
          <h1 class="text-4xl font-bold text-white tracking-tight">TextDDOS</h1>
          <p class="text-slate-400 mt-2">Giám sát DDoS Realtime</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username / Email -->
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-2">Tên đăng nhập / Email</label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">👤</span>
              <input
                v-model="form.username"
                type="text"
                placeholder="admin@textddos.com"
                required
                class="w-full bg-slate-800 border border-slate-700 rounded-2xl py-4 pl-11 pr-4 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-2">Mật khẩu</label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">🔒</span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                required
                class="w-full bg-slate-800 border border-slate-700 rounded-2xl py-4 pl-11 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
              >
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <!-- Remember & Forgot -->
          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.remember"
                type="checkbox"
                class="w-4 h-4 accent-blue-500 bg-slate-800 border-slate-600 rounded"
              />
              <span class="text-slate-400">Ghi nhớ đăng nhập</span>
            </label>
            <a href="#" class="text-blue-400 hover:text-blue-300 transition-colors">
              Quên mật khẩu?
            </a>
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-semibold py-4 rounded-2xl transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-blue-500/30 disabled:opacity-70"
          >
            <span v-if="isLoading" class="animate-spin">⟳</span>
            {{ isLoading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
          </button>
        </form>

        <!-- Footer -->
        <div class="mt-8 text-center">
          <p class="text-xs text-slate-500">
            © 2026 TextDDOS • Security Operations Center
          </p>
        </div>
      </div>

      <!-- Security Badge -->
      <div class="flex justify-center mt-6">
        <div class="flex items-center gap-2 text-xs text-emerald-400 bg-slate-900/80 px-4 py-1.5 rounded-full border border-emerald-500/20">
          <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
          Hệ thống được bảo vệ bởi SSL + 2FA
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({ username: '', password: '', remember: true })
const showPassword = ref(false)
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true

  try {
    await new Promise(r => setTimeout(r, 800)) // giả lập

    // Lưu trạng thái đăng nhập
    localStorage.setItem('isAuthenticated', 'true')
    localStorage.setItem('username', form.value.username)

    router.push('/')
  } catch (err) {
    alert('Đăng nhập thất bại!')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.bg-grid-slate-800\/30 {
  background-image: 
    linear-gradient(to right, #334155 1px, transparent 1px),
    linear-gradient(to bottom, #334155 1px, transparent 1px);
  background-size: 40px 40px;
}
</style>