# TextDDOS - DDoS Monitoring Dashboard

Một hệ thống giám sát DDoS realtime được xây dựng với **Vue.js 3**, **Tailwind CSS**, và **Vite**, tích hợp **Pinia** để quản lý state và **Chart.js** để hiển thị dữ liệu.

## 🎯 Tính Năng

### 📊 Overview Dashboard
- **Statistics Cards**: Tổng Flows, Attack Flows, Normal Flows, Attack Percentage Gauge
- **Line Chart**: Biểu đồ Packet Rate & Total Kbps theo thời gian
- **Pie Chart**: Tỷ lệ Normal vs Attack
- **Top IPs Tables**: Top 5 Attacking IPs & Top 5 Targeted IPs

### 📡 Live Flows (Realtime)
- Bảng động với filter, search, và pagination
- Highlight attack flows (label=1, confidence > 0.8) bằng màu đỏ
- Auto-refresh tùy chỉnh
- Các cột: Timestamp, Switch, Src IP, Dst IP, Protocol, pktrate, tot_kbps, pktcount, bytecount, Label, Confidence

### 📈 Traffic Analytics
- Multi-line chart: pktrate, tot_kbps, pktperflow
- Bar chart: Traffic theo Protocol (UDP/TCP/ICMP)
- Switch Activity Heatmap
- Thống kê chi tiết theo Switch

### ⚠️ Alerts & Incidents
- Danh sách attack realtime
- Action: Block IP, Add to Blacklist, Resolve
- Status tracking (new, acknowledged, resolved)
- Filter theo severity

### ⚙️ Rules Management
- CRUD rules đơn giản
- Toggle bật/tắt rule
- Rule history (trigger events)
- Ví dụ: if pktrate > X and protocol = UDP → Block

## 🚀 Cài Đặt & Chạy

### Yêu cầu
- Node.js >= 16.0.0
- npm hoặc yarn

### Các bước cài đặt

1. **Vào thư mục frontend**
```bash
cd textddos-monitoring/frontend-vue
```

2. **Cài đặt dependencies**
```bash
npm install
```

3. **Chạy development server**
```bash
npm run dev
```

Truy cập: `http://localhost:5173`

4. **Build for production**
```bash
npm run build
```

## 📁 Cấu trúc Thư Mục

```
frontend-vue/
├── src/
│   ├── components/
│   │   ├── DashboardCards.vue      # Statistics cards
│   │   ├── LiveFlowTable.vue       # Real-time table
│   │   ├── TrafficChart.vue        # Charts & graphs
│   │   └── AlertList.vue           # Alert list
│   ├── views/
│   │   ├── OverviewView.vue        # Dashboard overview
│   │   ├── LiveFlowsView.vue       # Live flows page
│   │   ├── AnalyticsView.vue       # Analytics page
│   │   ├── AlertsView.vue          # Alerts page
│   │   └── RulesView.vue           # Rules management
│   ├── stores/
│   │   └── index.js                # Pinia stores (flows, alerts, rules)
│   ├── composables/
│   │   └── useWebSocket.js         # WebSocket integration
│   ├── router/
│   │   └── index.js                # Vue Router configuration
│   ├── App.vue                     # Root component
│   ├── main.js                     # Entry point
│   └── main.css                    # Tailwind styles
├── public/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── .gitignore
```

## 🔌 API Integration

### WebSocket Configuration
Chỉnh sửa URL trong `src/composables/useWebSocket.js`:
```javascript
const connect = (url = 'ws://localhost:8000/ws') => {
  // ...
}
```

### Backend API Proxy
Được cấu hình trong `vite.config.js`:
```javascript
'/api': {
  target: 'http://localhost:8000',
  changeOrigin: true,
}
```

## 🎨 Tailwind CSS

Các class tùy chỉnh đã được định nghĩa:
- `.btn`, `.btn-primary`, `.btn-danger`, `.btn-success`, `.btn-ghost`
- `.card`, `.card-hover`
- `.input-field`
- `.badge`, `.badge-success`, `.badge-danger`, etc.
- `.highlight-danger`, `.highlight-success`

Chỉnh sửa trong `src/main.css`

## 📊 State Management (Pinia)

### Flow Store
- `addFlow(flow)` - Thêm flow mới
- `updateStats()` - Cập nhật thống kê
- `getFilteredFlows(filters)` - Lấy flows với filter

### Alert Store
- `addAlert(alert)` - Thêm alert
- `resolveAlert(alertId)` - Giải quyết alert
- `blockIP(ip)` - Block IP
- `addToBlacklist(ip)` - Thêm vào blacklist

### Rule Store
- `addRule(rule)` - Thêm rule
- `updateRule(id, updates)` - Cập nhật rule
- `deleteRule(id)` - Xóa rule
- `toggleRule(id)` - Bật/tắt rule

## 🛠️ Development

### Debugging
```bash
# Với source maps
npm run dev
```

### Lint
```bash
npm run lint
```

### Type Checking (Optional)
Cài đặt TypeScript:
```bash
npm install -D typescript
```

## 🚢 Deployment

### Build
```bash
npm run build
```

Output: `dist/` folder

### Docker (Optional)
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📝 Environment Variables

Tạo file `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_TITLE=TextDDOS - DDoS Monitor
```

Sử dụng:
```javascript
import.meta.env.VITE_API_BASE_URL
```

## 🔐 Security

- Không lưu credentials trong code
- Sử dụng environment variables
- CORS configuration trong backend
- Input validation trước khi gửi API

## 📚 Dependencies

- **vue**: ^3.4.21 - Framework
- **vue-router**: ^4.2.5 - Routing
- **pinia**: ^2.1.7 - State management
- **axios**: ^1.6.8 - HTTP client
- **chart.js**: ^4.4.1 - Charts
- **tailwindcss**: ^3.4.1 - CSS framework
- **vite**: ^5.0.8 - Build tool

## 🤝 Contribute

Mở issue hoặc pull request để contribute.

## 📄 License

MIT License

---

**Liên hệ**: textddos-team@example.com
