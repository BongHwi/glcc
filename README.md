# GLCC - Global Logistics Command Center

Self-hosted platform for tracking deliveries worldwide, integrating Korean and international shipping carriers.

## Features

- **Hybrid Tracking Engine**
  - Korean carriers via delivery-tracker (GraphQL service)
  - International carriers via Playwright web scraping
- **Automated Monitoring**
  - Scheduled tracking updates (configurable interval)
  - Status change detection
  - Telegram notifications
- **REST API**
  - Full CRUD operations for packages
  - Bulk refresh endpoint
  - Swagger documentation at `/docs`
- **Docker Support**
  - Multi-container architecture
  - Easy deployment with docker-compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Telegram Bot for notifications

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd glcc
```

2. Configure environment variables:
```bash
cp .env .env.local
# Edit .env.local with your settings
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the services:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend Dashboard: http://localhost:8501
- Delivery Tracker: http://localhost:4000

## Configuration

### Environment Variables

Edit `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./glcc.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler Settings
SCHEDULER_INTERVAL_HOURS=1

# Telegram Notifications (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Telegram Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Add credentials to `.env`

## API Usage

### Register a Package

```bash
curl -X POST "http://localhost:8000/packages" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "1234567890",
    "carrier": "kr.cj",
    "alias": "My Package",
    "notify_enabled": true
  }'
```

### List All Packages

```bash
curl "http://localhost:8000/packages"
```

### Refresh All Packages

```bash
curl -X POST "http://localhost:8000/packages/refresh"
```

### Track Specific Package

```bash
curl -X POST "http://localhost:8000/packages/1/track"
```

## Supported Carriers

### Korean Carriers (via delivery-tracker)

All carriers supported by [delivery-tracker](https://github.com/shlee322/delivery-tracker):
- CJ Logistics (`kr.cj`)
- Hanjin (`kr.hanjin`)
- Korea Post (`kr.epost`)
- And many more...

### International Carriers (Playwright)

Currently skeleton implementations:
- UPS (`global.ups`)
- FedEx (`global.fedex`) - planned
- DHL (`global.dhl`) - planned

## Development

### Local Development (without Docker)

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

2. Start delivery-tracker service:
```bash
cd backend/libs/delivery-tracker
docker-compose up -d
```

3. Run the backend:
```bash
cd backend
python main.py
```

### Project Structure

```
glcc/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── scheduler.py         # Background jobs
│   ├── notifications.py     # Telegram notifications
│   ├── trackers/
│   │   ├── kr_adapter.py    # Korean tracker adapter
│   │   └── global_scraper.py # International scraper
│   ├── routers/
│   │   └── packages.py      # API endpoints
│   └── libs/
│       └── delivery-tracker/ # Submodule
├── frontend/
│   └── app.py              # Streamlit dashboard
└── docker-compose.yml      # Service orchestration
```

## License

See LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
