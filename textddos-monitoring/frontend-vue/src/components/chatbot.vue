<template>
  <!-- Chatbot Container -->
  <div class="fixed bottom-6 right-6 z-[60] font-sans">
    
    <!-- Cửa sổ chat -->
    <transition
      enter-active-class="transition duration-400 cubic-bezier(0.34, 1.56, 0.64, 1)"
      enter-from-class="transform scale-75 translate-y-20 opacity-0"
      enter-to-class="transform scale-100 translate-y-0 opacity-100"
      leave-active-class="transition duration-250 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-75 translate-y-10 opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute bottom-20 right-0 w-[380px] h-[560px] flex flex-col overflow-hidden rounded-[2.5rem] border border-gray-100 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-950"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-red-600 to-rose-700 px-6 py-5 text-white">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="relative">
                <div class="h-10 w-10 rounded-full border-2 border-white/30 bg-black/30 p-1 flex items-center justify-center">
                  <span class="text-2xl">🛡️</span>
                </div>
                <span class="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-rose-700 bg-green-400 animate-pulse"></span>
              </div>
              <div>
                <h3 class="text-lg font-bold tracking-tight">DDOS Guardian AI</h3>
                <p class="text-xs text-red-200">Hệ thống giám sát tấn công thời gian thực</p>
              </div>
            </div>
            <button
              @click="isOpen = false"
              class="rounded-full p-2 hover:bg-white/10 transition-colors"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto bg-gray-50 p-5 space-y-6 dark:bg-gray-900/50 custom-scrollbar">
          <div v-for="(msg, i) in messages" :key="i" :class="msg.isBot ? 'flex justify-start' : 'flex justify-end'">
            <div class="group max-w-[85%]">
              <div
                :class="msg.isBot
                  ? 'bg-white border border-gray-200 text-gray-800 rounded-2xl rounded-tl-none'
                  : 'bg-gradient-to-br from-red-600 to-rose-600 text-white rounded-2xl rounded-tr-none'"
                class="px-4 py-3 shadow-sm"
              >
                <p class="text-[13.5px] leading-relaxed whitespace-pre-wrap">{{ msg.text }}</p>
              </div>
              <p :class="msg.isBot ? 'text-left' : 'text-right'" class="mt-1 text-[10px] text-gray-400">
                {{ msg.time }}
              </p>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="border-t border-gray-100 bg-white p-5 dark:border-gray-800 dark:bg-gray-950">
          <div class="relative flex items-center">
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              type="text"
              placeholder="Hỏi về flow, attack, IP nghi ngờ..."
              class="w-full rounded-2xl border border-gray-200 bg-gray-100 px-5 py-3.5 text-sm focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-900 dark:border-gray-700"
            />
            <button
              @click="sendMessage"
              class="absolute right-2 h-10 w-10 flex items-center justify-center rounded-xl bg-red-600 text-white hover:bg-red-700 transition-all active:scale-95"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
              </svg>
            </button>
          </div>
          <p class="mt-2 text-center text-[10px] text-gray-400">Hỗ trợ giám sát & phân tích DDoS</p>
        </div>
      </div>
    </transition>

    <!-- Nút mở chat -->
    <button
      @click="toggleChat"
      class="group relative h-16 w-16 flex items-center justify-center transition-all duration-500 active:scale-90"
    >
      <div class="absolute inset-0 rounded-full bg-gradient-to-br from-red-600 to-rose-700 shadow-[0_10px_40px_rgba(225,29,72,0.4)] group-hover:scale-110 transition-all"></div>
      
      <div v-if="!isOpen" class="relative z-10">
        <span class="text-3xl">🛡️</span>
        <div class="absolute -right-1 -top-1 h-4 w-4 rounded-full bg-green-400 ring-2 ring-white animate-ping"></div>
      </div>

      <svg v-else class="relative z-10 h-7 w-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import Groq from 'groq-sdk'
import { getFlows } from '../composables/flow'
import { computed } from 'vue'
const GROQ_API_KEY = "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"

const groq = new Groq({
  apiKey: GROQ_API_KEY,
  dangerouslyAllowBrowser: true
})

const flows = ref([])
const filters = ref({
  protocol: '',
  label: '',
  srcIP: '',
  dstIP: '',
  switch: ''
})
const searchQuery = ref('')
const fetchFlows = async () => {
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
    console.log('Sample flow:', flows.value || 'No flows')
  } catch (error) {
    console.error('Error fetching flows:', error)
    flows.value = []
  } finally {
    // Cập nhật lại chatbot nếu cần
  }
}

const isOpen = ref(false)
const newMessage = ref('')

const messages = ref([
  {
    text: 'Xin chào! Tôi là **DDOS Guardian AI** — trợ lý thông minh của hệ thống giám sát DDoS.\n\nTôi có thể hỗ trợ bạn phân tích flow, phát hiện tấn công, kiểm tra IP đáng ngờ, và tư vấn cách xử lý.',
    isBot: true,
    time: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
  }
])

const messagesContainer = ref(null)

const systemPrompt = computed(() => `Bạn là DDOS Guardian AI, một chuyên gia an ninh mạng cao cấp của hệ thống giám sát DDoS thời gian thực.

Phong cách trả lời:
- Ngắn gọn, chuyên nghiệp, rõ ràng, dùng thuật ngữ chuyên môn khi cần.
- Luôn trả lời bằng tiếng Việt.
- Sử dụng emoji phù hợp (🛡️, 🚨, 📊, ⚠️...).
- Giải thích dễ hiểu cho cả admin và người mới.

Kiến thức của bạn:
- Phân tích network flow (src_ip, dst_ip, protocol, pktrate, tot_kbps, pktcount, bytecount...)
- Phát hiện và phân loại tấn công DDoS (SYN Flood, UDP Flood, ICMP Flood, HTTP Flood...)
- Đánh giá mức độ nguy hiểm dựa trên confidence và traffic pattern.
- Hướng dẫn block IP, tạo rule firewall, tối ưu hóa hệ thống.
- Giải thích ý nghĩa các chỉ số: pktrate, tot_kbps, confidence...

DỮ LIỆU FLOW HIỆN TẠI (${flows.value.length} flows):
${JSON.stringify(flows.value, null, 2)}

Khi người dùng hỏi:
- Phân tích flow → đưa ra nhận định có phải tấn công không.
- Hỏi về IP → phân tích xem có đáng ngờ không.
- Hỏi cách xử lý → đưa ra hướng dẫn cụ thể.

Trả lời hữu ích, hành động nhanh, tập trung vào bảo vệ hệ thống.`)
const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) nextTick(() => scrollToBottom())
}

const sendMessage = async () => {
  const messageText = newMessage.value.trim()
  if (!messageText) return

  messages.value.push({
    text: messageText,
    isBot: false,
    time: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
  })

  newMessage.value = ''
  nextTick(() => scrollToBottom())

  try {
    const historyMessages = [
      { role: "system", content: systemPrompt.value },
      ...messages.value.slice(0, -1).map(msg => ({
        role: msg.isBot ? "assistant" : "user",
        content: msg.text
      })),
      { role: "user", content: messageText }
    ]

    const completion = await groq.chat.completions.create({
      messages: historyMessages,
      model: "llama-3.3-70b-versatile",
      temperature: 0.6,
      max_tokens: 1024,
    })

    const botResponse = completion.choices[0]?.message?.content?.trim() 
      || "Tôi chưa hiểu rõ câu hỏi. Bạn có thể mô tả chi tiết hơn không?"

    messages.value.push({
      text: botResponse,
      isBot: true,
      time: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    })

  } catch (error) {
    console.error("Lỗi Groq:", error)
    messages.value.push({
      text: '❌ Xin lỗi, hiện tại tôi không thể kết nối với AI. Vui lòng thử lại sau.',
      isBot: true,
      time: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
    })
  }

  nextTick(() => scrollToBottom())
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Lưu tin nhắn
watch(messages, (newMessages) => {
  localStorage.setItem('ddosChatMessages', JSON.stringify(newMessages))
}, { deep: true })

onMounted(() => {
  const saved = localStorage.getItem('ddosChatMessages')
  if (saved) messages.value = JSON.parse(saved)
  fetchFlows() // Load flow khi chatbot khởi động
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #4b5563; }
</style>