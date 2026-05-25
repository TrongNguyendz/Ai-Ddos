# TextDDOS Monitoring Backend

A comprehensive FastAPI backend for real-time DDoS monitoring with AI-powered detection, built with MongoDB and WebSocket support.

## Features

- 🚀 **FastAPI Framework**: High-performance async API with automatic OpenAPI docs
- 🤖 **AI-Powered Detection**: Machine learning model for DDoS attack classification
- 📊 **Real-time Monitoring**: WebSocket connections for live data streaming
- 🗄️ **MongoDB Integration**: NoSQL database for flow data and analytics
- 🔧 **Rule Engine**: Configurable rules for automated threat response
- 📈 **Analytics Dashboard**: Comprehensive statistics and visualizations
- 🔔 **Alert System**: Real-time notifications and incident management
- 🐳 **Docker Support**: Containerized deployment ready

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB 4.4+
- Your trained DDoS detection model (optional)

### Installation

1. **Clone and setup:**
   ```bash
   cd backend
   chmod +x run.sh
   ./run.sh
   ```

2. **Or manual setup:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings

   # Start the server
   python app/main.py
   ```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t textddos-backend .
docker run -p 8000:8000 --env-file .env textddos-backend
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Flows API (`/api/v1/flows`)
- `POST /flows` - Create new flow with AI prediction
- `GET /flows` - Get flows with filtering and pagination
- `GET /flows/{id}` - Get specific flow
- `PUT /flows/{id}` - Update flow
- `DELETE /flows/{id}` - Delete flow
- `GET /flows/stats/realtime` - Get real-time statistics

### Dashboard API (`/api/v1/dashboard`)
- `GET /dashboard/stats` - Get overview statistics
- `GET /dashboard/charts/pktrate-kbps` - Get packet rate/Kbps chart
- `GET /dashboard/charts/normal-attack` - Get normal vs attack distribution

### Alerts API (`/api/v1/alerts`)
- `POST /alerts` - Create alert
- `GET /alerts` - Get alerts with filtering
- `PUT /alerts/{id}` - Update alert
- `DELETE /alerts/{id}` - Delete alert
- `POST /alerts/{id}/block-ip` - Block IP address
- `POST /alerts/{id}/add-to-blacklist` - Add IP to blacklist

### Rules API (`/api/v1/rules`)
- `POST /rules` - Create rule
- `GET /rules` - Get rules
- `PUT /rules/{id}` - Update rule
- `DELETE /rules/{id}` - Delete rule
- `POST /rules/{id}/toggle` - Enable/disable rule
- `POST /rules/evaluate` - Manually evaluate rules

### WebSocket
- `ws://localhost:8000/ws` - Real-time data streaming

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection URL | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `textddos_db` |
| `MODEL_PATH` | Path to ML model file | `./models/ddos_model.pkl` |
| `MODEL_THRESHOLD` | Prediction confidence threshold | `0.8` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode | `True` |

### AI Model Integration

Place your trained model file at `./models/ddos_model.pkl`. The model should:
- Accept features: `[pktrate, tot_kbps, pktcount, bytecount, tcp_flag, udp_flag, icmp_flag]`
- Return probability predictions for binary classification

If no model is found, the system uses rule-based mock predictions.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   └── database.py            # MongoDB connection
│   ├── models/
│   │   └── flow.py                # Pydantic models + MongoDB schemas
│   ├── schemas/
│   │   ├── flow.py                # API request/response schemas
│   │   └── rule.py
│   ├── routers/
│   │   ├── flows.py               # Flow CRUD operations
│   │   ├── dashboard.py           # Statistics and charts
│   │   ├── alerts.py              # Alert management
│   │   └── rules.py               # Rule engine management
│   ├── services/
│   │   ├── inference.py           # AI model inference service
│   │   ├── websocket_manager.py   # WebSocket connection handling
│   │   └── rule_engine.py         # Rule evaluation engine
│   ├── utils/
│   │   └── helpers.py             # Utility functions
│   └── dependencies.py            # FastAPI dependencies
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
├── run.sh                         # Startup script
└── README.md                      # This file
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

### Code Formatting

```bash
# Install development dependencies
pip install black isort flake8

# Format code
black .
isort .

# Lint code
flake8 .
```

## Deployment

### Production Considerations

1. **Security**: Change `SECRET_KEY` and disable `DEBUG`
2. **Database**: Use MongoDB Atlas or production MongoDB instance
3. **Model**: Deploy trained model file to production
4. **Scaling**: Use reverse proxy (nginx) and load balancer
5. **Monitoring**: Implement logging and monitoring solutions

### Docker Compose Example

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
    depends_on:
      - mongodb

  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Check the API documentation at `/docs`
- Review the logs in `logs/app.log`
- Open an issue on GitHub

---

Built with ❤️ for network security and real-time monitoring
