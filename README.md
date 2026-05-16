# Pulse AI 🎵

**AI-Powered Event Discovery & Recommendation Platform**

Pulse AI is an intelligent event discovery system that combines LangGraph workflows, IBM watsonx.ai, and multiple external APIs to provide personalized event recommendations with natural language explanations.

---

## 🌟 Features

- **Natural Language Search**: Describe what you're looking for in plain English
- **Multi-Factor Ranking**: Events ranked by relevance, date, affordability, popularity, venue context, and weather
- **Venue Context**: Enriched with nearby POIs, transit info, and neighborhood details
- **Weather Integration**: Outdoor suitability assessment for events
- **Smart Explanations**: AI-generated reasoning for recommendations
- **Calendar Export**: One-click .ics file generation
- **Demo Mode**: Test without API keys using fallback data

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: FastAPI (async)
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.x (async)
- **Workflow**: LangGraph
- **LLM**: IBM watsonx.ai (Granite models)
- **MCP**: FastMCP for tool exposure
- **Frontend**: HTMX + Jinja2 templates

### Workflow Pipeline
```
User Query
  → Parse Intent (LLM)
    → Validate Parameters
      → Search Events (Ticketmaster)
        → Normalize Data
          → Enrich Venues (Geoapify)
            → Add Weather Context (OpenWeather)
              → Rank & Score Events
                → Generate Explanations (LLM)
                  → Return Results
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### 1. Clone Repository
```bash
git clone https://github.com/gabrieltonyy/pulse_ai.git
cd pulse_ai
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
# Required:
# - TICKETMASTER_API_KEY
# - GEOAPIFY_API_KEY
# - OPENWEATHER_API_KEY
# - WATSONX_API_KEY
# - WATSONX_PROJECT_ID
# - DATABASE_URL
```

### 4. Set Up Database
```bash
# Start PostgreSQL (if using Docker)
docker-compose up -d postgres

# Run migrations
alembic upgrade head
```

### 5. Run Application
```bash
# Development mode
uvicorn app.main:app --reload

# Or use Docker Compose
docker-compose up
```

### 6. Access Application
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t pulse-ai .

# Run container
docker run -p 8000:8000 --env-file .env pulse-ai
```

---

## 📁 Project Structure

```
pulse_ai/
├── app/
│   ├── config/          # Configuration management
│   ├── db/              # Database models & migrations
│   ├── graph/           # LangGraph workflow & nodes
│   ├── integrations/    # External API clients
│   ├── mcp/             # MCP server & tools
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # FastAPI routes
│   ├── services/        # Business logic
│   ├── static/          # CSS, JS files
│   ├── templates/       # Jinja2 templates
│   └── main.py          # Application entry point
├── docs/                # Documentation
├── tests/               # Test suite
├── bob_sessions/        # Bob AI session exports
├── alembic.ini          # Alembic configuration
├── docker-compose.yml   # Docker Compose config
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
├── TASKS.md             # Development task tracking
├── HAND_OVER.md         # Session continuity
└── README.md            # This file
```

---

## 🔧 Configuration

### Environment Variables

#### Application
- `DEBUG`: Enable debug mode (default: false)
- `DEMO_MODE`: Use demo data instead of real APIs (default: false)

#### Database
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_POOL_SIZE`: Connection pool size (default: 5)

#### APIs
- `TICKETMASTER_API_KEY`: Ticketmaster Discovery API key
- `GEOAPIFY_API_KEY`: Geoapify Places API key
- `OPENWEATHER_API_KEY`: OpenWeather API key

#### LLM (watsonx.ai)
- `WATSONX_API_KEY`: IBM watsonx.ai API key
- `WATSONX_PROJECT_ID`: watsonx.ai project ID
- `WATSONX_URL`: watsonx.ai endpoint URL
- `WATSONX_MODEL`: Model name (default: ibm/granite-13b-chat-v2)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_workflow.py

# Run in verbose mode
pytest -v
```

---

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Home page
- `GET /health` - Health check
- `POST /api/search` - Search events
- `GET /api/events/{event_id}` - Get event details
- `GET /api/calendar/{event_id}` - Export to calendar
- `GET /api/redirect/{event_id}` - Get ticket purchase URL

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

---

## 🛠️ Development

### Running Locally
```bash
# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --log-level debug

# Run MCP server separately (optional)
python -m app.mcp.server
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

---

## 📝 Documentation

- **[Project Brief](docs/01-Project-Brief.md)** - Overview and goals
- **[Technical Architecture](docs/03-Technical-Architecture.md)** - System design
- **[Data Models](docs/08-data-models-and-schemas.md)** - Schema definitions
- **[API Integration](docs/09-api-and-external-services.md)** - External APIs
- **[Development Plan](docs/06-bob-development-task-plan.md)** - Implementation roadmap

---

## 🤝 Contributing

This is a hackathon project developed for the IBM Bob AI Hackathon (May 2026).

### Development Workflow
1. Check `TASKS.md` for current priorities
2. Read `HAND_OVER.md` for project state
3. Make changes in feature branch
4. Update `TASKS.md` with progress
5. Update `HAND_OVER.md` before ending session

---

## 📄 License

This project is developed for the IBM Bob AI Hackathon.

---

## 🙏 Acknowledgments

- **IBM watsonx.ai** - LLM provider
- **Ticketmaster** - Event data
- **Geoapify** - Location services
- **OpenWeather** - Weather data
- **LangGraph** - Workflow orchestration
- **FastAPI** - Web framework

---

## 📧 Contact

- **GitHub**: https://github.com/gabrieltonyy/pulse_ai
- **Hackathon**: IBM Bob AI Hackathon (May 2026)

---

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Database setup
- [x] FastAPI bootstrap
- [x] LangGraph scaffold
- [x] MCP scaffold

### Phase 2: Core Implementation 🚧
- [ ] LLM integration
- [ ] API integrations
- [ ] Workflow implementation
- [ ] Demo mode

### Phase 3: Frontend 📋
- [ ] HTMX search interface
- [ ] Results display
- [ ] Event details
- [ ] Calendar export

### Phase 4: Polish 🎨
- [ ] Testing
- [ ] Documentation
- [ ] Performance optimization
- [ ] Demo preparation

---

**Built with ❤️ for the IBM Bob AI Hackathon**