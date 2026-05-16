# 🎯 Pulse AI - AI-Powered Event Discovery Platform

> **IBM Lablab Hackathon Submission - May 2026**
> 
> An intelligent event discovery platform that uses IBM watsonx.ai, LangGraph workflows, and MCP tools to provide personalized event recommendations with context-aware ranking.

## 🌟 Key Features

- **Natural Language Search** - Ask in plain English: "rock concerts in London this weekend"
- **AI-Powered Query Understanding** - IBM watsonx.ai parses and extracts search intent
- **Multi-Source Event Discovery** - Integrates Ticketmaster API for comprehensive event data
- **Context-Aware Enrichment** - Adds venue details (Geoapify) and weather forecasts (OpenWeather)
- **Intelligent Ranking** - 6-component scoring algorithm with personalized recommendations
- **MCP Tool Integration** - Expose functionality via Model Context Protocol for AI assistants
- **Demo Mode** - Reliable presentation mode without API dependencies
- **HTMX Interface** - Fast, modern web UI with progressive enhancement

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.12
- FastAPI (async web framework)
- LangGraph (workflow orchestration)
- PostgreSQL (data persistence)
- SQLAlchemy 2.x (async ORM)

**AI & APIs:**
- IBM watsonx.ai (LLM for query parsing & explanations)
- Ticketmaster Discovery API (event search)
- Geoapify Places API (venue context)
- OpenWeather API (weather forecasts)

**Frontend:**
- HTMX (dynamic interactions)
- Tailwind CSS (styling)
- Jinja2 (templating)

**Integration:**
- MCP (Model Context Protocol) server
- Docker & Docker Compose

### Workflow Architecture

```
User Query → Parse (watsonx.ai) → Validate → Search (Ticketmaster)
    ↓
Normalize → Enrich Venues (Geoapify) → Weather Context (OpenWeather)
    ↓
Rank & Score → Generate Explanations (watsonx.ai) → Prepare Response
```

**9 LangGraph Nodes:**
1. `parse_query` - Extract search intent using watsonx.ai
2. `validate_query` - Validate required parameters
3. `search_events` - Query Ticketmaster API
4. `normalize_events` - Standardize event data
5. `enrich_venues` - Add nearby places via Geoapify
6. `weather_context` - Add weather forecasts via OpenWeather
7. `rank_events` - Score and rank using 6-component algorithm
8. `generate_explanations` - Create AI explanations via watsonx.ai
9. `prepare_response` - Format final response

### Ranking Algorithm

**6 Scoring Components (0-100 each):**
- **Relevance** (30%) - Category, keyword, preference matching
- **Date Match** (20%) - Proximity to requested dates
- **Affordability** (20%) - Budget compatibility
- **Popularity** (15%) - Event metadata quality
- **Context** (10%) - Venue richness (nearby amenities)
- **Weather** (5%) - Outdoor suitability

**Labels:** Best Overall, Best Budget Pick, Trending Option, Closest Match

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- API Keys (see Environment Variables)

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# IBM watsonx.ai
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Ticketmaster
TICKETMASTER_API_KEY=your_ticketmaster_key

# Geoapify
GEOAPIFY_API_KEY=your_geoapify_key

# OpenWeather
OPENWEATHER_API_KEY=your_openweather_key

# Database
DATABASE_URL=postgresql+asyncpg://pulse_user:pulse_pass@db:5432/pulse_db
```

### Run with Docker (Recommended)

```bash
# Start all services
docker compose up

# Access application
# Web UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Run Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker compose up db

# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
# Run all tests with coverage
./run_tests.sh

# Run specific test file
pytest tests/test_workflow_integration.py -v

# Run with markers
pytest tests/ -m "not slow" -v
```

## 🎮 Demo Mode

Demo mode provides reliable functionality without API dependencies:

```bash
# Via web UI
Click "Try Demo" button on home page

# Via API
curl http://localhost:8000/api/search/demo

# Via MCP tool
pulse_search_events(query="concerts", use_demo=True)
```

Demo data includes 14 realistic events across multiple categories.

## 🔧 MCP Tools

Pulse AI exposes 3 MCP tools for AI assistants:

**1. pulse_search_events**
- Search and rank events using full workflow
- Inputs: query, city, country, category, dates, budget, use_demo
- Returns: ranked events with recommendations

**2. pulse_enrich_venue**
- Get nearby places for a location
- Inputs: latitude, longitude, radius
- Returns: nearby restaurants, entertainment, transport

**3. pulse_get_weather**
- Get weather forecast for event
- Inputs: latitude, longitude, date
- Returns: temperature, conditions, outdoor suitability

See [`docs/MCP_USAGE.md`](docs/MCP_USAGE.md) for detailed documentation.

## 📚 API Documentation

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Key Endpoints

- `GET /` - Home page with search form
- `POST /api/search/` - JSON search endpoint
- `POST /api/search/htmx` - HTMX search endpoint
- `GET /api/search/demo` - Demo search
- `GET /api/events/{id}` - Event details
- `GET /api/events/{id}/calendar` - Export to calendar (.ics)
- `POST /api/events/{id}/track-click` - Track outbound clicks

## 🔒 Security Notes

- **API Keys:** Never commit `.env` file
- **Secrets:** Use environment variables only
- **Database:** Change default credentials in production
- **CORS:** Configure allowed origins in production
- **Rate Limiting:** Implement for production deployment

## 🤖 Bob (AI Assistant) Usage

This project was built with Bob, an AI coding assistant:

**Development Workflow:**
1. Bob analyzed project requirements from `docs/` folder
2. Created 8-phase development roadmap
3. Implemented each phase incrementally
4. Maintained operational docs (TASKS.md, HAND_OVER.md)
5. Created comprehensive test suite

**Bob Session Proof:**
- Session exports: `bob_sessions/`
- Screenshots: `bob_sessions/screenshots/`
- See [`bob_sessions/README.md`](bob_sessions/README.md) for details

## 🏆 Hackathon Submission

**IBM Technologies Used:**
- ✅ IBM watsonx.ai (LLM for query parsing & explanations)
- ✅ LangGraph (workflow orchestration)
- ✅ MCP (Model Context Protocol integration)

**Innovation Highlights:**
- Context-aware event ranking with 6-component algorithm
- Multi-API orchestration via LangGraph
- MCP tools for AI assistant integration
- Demo mode for reliable presentations
- Comprehensive test coverage (52+ tests)

**Project Metrics:**
- 8 phases completed
- 60+ files created
- 9 LangGraph nodes
- 3 MCP tools
- 6 API routes
- 52+ tests (>70% coverage)
- 4 external API integrations

## 📖 Documentation

- [`ROADMAP.md`](ROADMAP.md) - 8-phase development plan
- [`TASKS.md`](TASKS.md) - Detailed task tracking
- [`HAND_OVER.md`](HAND_OVER.md) - Session continuity
- [`ARCHITECTURE_NOTES.md`](ARCHITECTURE_NOTES.md) - Technical decisions
- [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) - Known limitations
- [`docs/MCP_USAGE.md`](docs/MCP_USAGE.md) - MCP tool documentation

## 🐛 Troubleshooting

**Application won't start:**
- Check `.env` file exists with all required keys
- Verify Docker is running
- Check port 8000 is available

**Tests failing:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check PostgreSQL is running

**MCP server issues:**
- Verify Python path in MCP config
- Check stdio transport configuration
- See [`docs/MCP_USAGE.md`](docs/MCP_USAGE.md)

**API errors:**
- Verify API keys are valid
- Check API rate limits
- Use demo mode for testing

## 📝 License

MIT License - See [LICENSE](LICENSE) file

## 👥 Team

Built with Bob AI Assistant for IBM Lablab Hackathon May 2026

---

**Questions?** Check [`docs/`](docs/) folder or open an issue.