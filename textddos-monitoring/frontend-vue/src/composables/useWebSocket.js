import { ref, onMounted, onUnmounted } from 'vue'

export const useWebSocket = () => {
  const ws = ref(null)
  const isConnected = ref(false)
  const lastMessage = ref(null)
  const messageHandlers = ref(new Set())   // Hỗ trợ nhiều listener

  const connect = (url = 'ws://localhost:8000/ws') => {
    return new Promise((resolve, reject) => {
      try {
        if (ws.value && ws.value.readyState === WebSocket.OPEN) {
          resolve()
          return
        }

        ws.value = new WebSocket(url)

        ws.value.onopen = () => {
          isConnected.value = true
          console.log('✅ WebSocket connected to', url)
          resolve()
        }

        ws.value.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('📩 Received message:', data)
            lastMessage.value = data

            // Gọi tất cả các handler
            messageHandlers.value.forEach(handler => handler(data))
          } catch (err) {
            console.error('❌ Parse message error:', err)
          }
        }

        ws.value.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          reject(error)
        }

        ws.value.onclose = () => {
          isConnected.value = false
          console.log('🔌 WebSocket disconnected')
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  // Thêm listener cho message
  const onMessage = (callback) => {
    messageHandlers.value.add(callback)
    
    // Trả về hàm unsubscribe
    return () => messageHandlers.value.delete(callback)
  }

  const send = (data) => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket chưa kết nối')
    }
  }

  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    messageHandlers.value.clear()
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    lastMessage,
    connect,
    onMessage,        // ← Dùng cái này
    send,
    disconnect
  }
}