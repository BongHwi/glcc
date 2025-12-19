# GLCC - Global Logistics Command Center

Self-hosted platform for tracking deliveries worldwide, integrating Korean and international shipping carriers.

## Features

- **Automatic Carrier Detection** 🆕
  - Pattern-based tracking number recognition
  - Supports 12+ carriers with configurable patterns
  - Auto-detect API endpoint and UI integration
  - Confidence levels (high/medium/low) for detection accuracy
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
  - Carrier detection endpoint
  - Swagger documentation at `/docs`
- **Streamlit Dashboard**
  - Interactive web UI for package management
  - Auto-detect carrier button
  - Real-time status updates
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
# Edit .env with your settings (optional - defaults are provided)
# You can customize ports and other settings here
```

3. Start all services:
```bash
# Option 1: Using the build script (recommended)
./build.sh

# Option 2: Manual build
docker compose up -d --build
```

4. Access the services:
- Backend API: http://localhost:8080 (or your BACKEND_PORT)
- API Docs: http://localhost:8080/docs
- Frontend Dashboard: http://localhost:8501 (or your FRONTEND_PORT)
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

# Docker Port Mapping (host:container)
BACKEND_PORT=8080
FRONTEND_PORT=8501

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

### Auto-detect Carrier (New!)

Automatically identify carrier from tracking number:

```bash
curl -X POST "http://localhost:8080/carriers/detect" \
  -H "Content-Type: application/json" \
  -d '{"tracking_number": "EN387436585JP"}'
```

Response:
```json
{
  "carrier": "global.jppost",
  "confidence": "high",
  "pattern_matched": "Ends with JP (e.g., EN123456789JP)",
  "tracking_number": "EN387436585JP"
}
```

### Register a Package

With explicit carrier:
```bash
curl -X POST "http://localhost:8080/packages" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "1234567890",
    "carrier": "kr.cj",
    "alias": "My Package",
    "notify_enabled": true
  }'
```

With auto-detection (carrier optional):
```bash
curl -X POST "http://localhost:8080/packages" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "EN387436585JP",
    "alias": "Package from Japan"
  }'
```

### List All Packages

```bash
curl "http://localhost:8080/packages"
```

### List Supported Carriers

```bash
curl "http://localhost:8080/carriers/"
```

### Refresh All Packages

```bash
curl -X POST "http://localhost:8080/packages/refresh"
```

### Track Specific Package

```bash
curl -X POST "http://localhost:8080/packages/1/track"
```

## Supported Carriers

### Korean Carriers (via delivery-tracker)

All carriers supported by [delivery-tracker](https://github.com/shlee322/delivery-tracker):
- CJ Logistics (`kr.cj`)
- Hanjin (`kr.hanjin`)
- Korea Post (`kr.epost`)
- Lotte (`kr.lotte`)
- KD Express (`kr.kdexp`)
- And more...

### International Carriers (Playwright Web Scraping)

**Fully Implemented:**
- **China Post** (`global.chinapost`) - via 17track.net
  - Pattern: Starts with RB/RC/RA/CP/LZ/ZC etc.
- **Japan Post** (`global.jppost`) - via official tracking site
  - Pattern: Ends with JP (e.g., EN123456789JP)
- **Sagawa Express** (`global.sagawa`) - via official site
  - Pattern: 10-12 digit numbers

**Planned/Skeleton:**
- UPS (`global.ups`) - Pattern: 1Z + 16 chars
- FedEx (`global.fedex`) - Pattern: 12-15 digits
- DHL (`global.dhl`) - Pattern: 10-11 digits

### Carrier Auto-Detection

The system can automatically detect carriers based on tracking number patterns:
- **High confidence**: Unique patterns (e.g., ends with "JP" → Japan Post)
- **Medium confidence**: Common prefixes (e.g., "1Z" → UPS)
- **Low confidence**: Generic length patterns (e.g., 12 digits → might be FedEx)

See `/carriers/` API endpoint for full pattern list.

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
│   ├── carrier_detector.py  # Auto-detection logic (NEW)
│   ├── trackers/
│   │   ├── kr_adapter.py    # Korean tracker adapter
│   │   └── global_scraper.py # International scraper
│   ├── routers/
│   │   ├── packages.py      # Package API endpoints
│   │   └── carriers.py      # Carrier detection API (NEW)
│   └── libs/
│       └── delivery-tracker/ # Submodule
├── frontend/
│   └── app.py              # Streamlit dashboard
├── docker-compose.yml      # Service orchestration
└── README.md               # This file
```

## License

See LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
