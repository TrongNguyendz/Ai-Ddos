# TextDDOS Monitoring System

Một hệ thống giám sát **DDoS realtime** tích hợp, được xây dựng với:

- **Frontend**: Vue.js 3 + Tailwind CSS + Vite
- **Backend**: FastAPI + WebSocket
- **Database**: MongoDB

## 📋 Cấu trúc Project

```
textddos-monitoring/
├── frontend-vue/                    # Vue.js Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardCards.vue   # Statistics
│   │   │   ├── LiveFlowTable.vue    # Real-time flows
│   │   │   ├── TrafficChart.vue     # Charts
│   │   │   └── AlertList.vue        # Alerts
│   │   ├── views/
│   │   │   ├── OverviewView.vue     # Dashboard
│   │   │   ├── LiveFlowsView.vue    # Live flows
│   │   │   ├── AnalyticsView.vue    # Analytics
│   │   │   ├── AlertsView.vue       # Alerts
│   │   │   └── RulesView.vue        # Rules
│   │   ├── stores/
│   │   │   └── index.js             # Pinia stores
│   │   ├── composables/
│   │   │   └── useWebSocket.js      # WebSocket
│   │   ├── router/
│   │   │   └── index.js             # Router config
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── main.css
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── README.md
│
├── backend/                         # FastAPI Backend
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── docker-compose.yml
└── .env
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# MongoDB: mongodb://localhost:27017
```

### Option 2: Manual Setup

#### Frontend
```bash
cd frontend-vue
npm install
npm run dev
# Access: http://localhost:5173
```

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
# API: http://localhost:8000
```

## 📊 Features Overview

### 1. **Overview Dashboard**
- 📈 Real-time statistics cards
- 📊 Line charts for pktrate & tot_kbps
- 🍰 Pie chart for Normal vs Attack ratio
- 🎯 Top 5 attacking and targeted IPs

### 2. **Live Flows**
- 📡 Real-time flow table with auto-refresh
- 🔍 Advanced filtering (Protocol, Label, IP, etc.)
- 🔴 Highlight attack flows (confidence > 0.8)
- 📄 Pagination support

### 3. **Traffic Analytics**
- 📈 Multi-line chart (pktrate, tot_kbps, pktperflow)
- 📊 Protocol distribution (TCP, UDP, ICMP)
- 🔥 Switch activity heatmap
- 📋 Detailed statistics table

### 4. **Alerts & Incidents**
- ⚠️ Real-time attack alerts
- 🚫 Block IP / Add to Blacklist
- ✅ Alert resolution tracking
- 🎯 Severity-based filtering

### 5. **Rules Management**
- ➕ Create custom detection rules
- 🎛️ Rule enable/disable toggle
- 📊 Trigger history tracking
- 🗑️ CRUD operations

## 🔌 API Integration

### WebSocket Connection
```javascript
ws://localhost:8000/ws
```

### REST API Endpoints
```
GET  /api/flows           # Get all flows
POST /api/flows           # Add flow
GET  /api/alerts          # Get alerts
POST /api/alerts/block    # Block IP
GET  /api/rules           # Get rules
POST /api/rules           # Create rule
```

## 🎨 UI Components

All components use **Tailwind CSS** for styling with custom utility classes:

- `.btn`, `.btn-primary`, `.btn-danger`, `.btn-success`, `.btn-ghost`
- `.card`, `.card-hover`
- `.input-field`
- `.badge`, `.badge-success`, `.badge-danger`, `.badge-warning`, `.badge-info`
- `.highlight-danger`, `.highlight-success`

## 🛠️ Development

### Watch Mode
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 📦 Dependencies

### Frontend Core
- `vue`: 3.4.21 - Progressive framework
- `vue-router`: 4.2.5 - Routing
- `pinia`: 2.1.7 - State management

### UI & Charts
- `tailwindcss`: 3.4.1 - CSS framework
- `chart.js`: 4.4.1 - Chart library
- `vue-chartjs`: 5.3.1 - Vue wrapper

### HTTP & WebSocket
- `axios`: 1.6.8 - HTTP client

### Build Tools
- `vite`: 5.0.8 - Build tool
- `@vitejs/plugin-vue`: 5.0.4 - Vue plugin

## 🔐 Security

- CORS headers configured
- HTTPS ready for production
- Input validation on all forms
- XSS protection via Vue's template escaping

## 🚢 Deployment

### Production Build
```bash
npm run build
# Output: dist/ folder
```

### Docker Build
```bash
docker build -t textddos-frontend:latest .
docker run -p 80:80 textddos-frontend:latest
```

### Environment Variables
See `.env.example` for available options:
```
VITE_API_BASE_URL=http://api.example.com
VITE_WS_URL=ws://api.example.com/ws
VITE_APP_TITLE=TextDDOS
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in vite.config.js
server: {
  port: 3000  # Change here
}
```

### WebSocket Connection Failed
- Check backend is running
- Verify WebSocket URL in `.env.local`
- Check CORS/firewall settings

### Styling Issues
- Clear node_modules: `rm -rf node_modules && npm install`
- Rebuild Tailwind: `npx tailwindcss -i ./src/main.css -o ./dist/output.css`

## 📚 Resources

- [Vue 3 Documentation](https://vuejs.org)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Vite Documentation](https://vitejs.dev)
- [Pinia Documentation](https://pinia.vuejs.org)
- [Chart.js Documentation](https://www.chartjs.org)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- **Frontend Lead**: Your Name
- **Backend Lead**: Your Name
- **DevOps**: Your Name

## 📞 Contact

- Email: textddos-team@example.com
- Issues: [GitHub Issues](https://github.com/textddos/issues)
- Wiki: [Project Wiki](https://github.com/textddos/wiki)

---

**Last Updated**: 2024
**Status**: Active Development
