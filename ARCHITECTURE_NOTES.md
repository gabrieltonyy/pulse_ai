# Pulse AI — Architecture Notes

**Purpose:** Document key architectural decisions and rationale.

---

## Database: PostgreSQL vs SQLite

**Decision:** Use PostgreSQL with asyncpg

**Rationale:**
- Production-ready scalability
- Better concurrent access handling
- Advanced features (JSON columns, full-text search)
- Async support with asyncpg
- Required by master.md specification

**Implementation:**
- SQLAlchemy 2.x with async engine
- Connection pooling configured
- Alembic for migrations
- Database URL: `postgresql+asyncpg://...`

---

## Async Architecture

**Decision:** Fully async application

**Rationale:**
- Better performance for I/O-bound operations
- Multiple external API calls per request
- Database operations are async
- FastAPI native async support

**Implementation:**
- All route handlers are async
- Database sessions use AsyncSession
- HTTP clients use httpx (async)
- LangGraph nodes are async functions

---

## LangGraph Workflow Design

**Decision:** Linear workflow with 9 nodes

**Rationale:**
- Clear separation of concerns
- Easy to debug and test
- Matches natural event search flow
- Allows for future conditional branching

**Node Sequence:**
1. parse_query - Extract intent from user query
2. validate_query - Validate search parameters
3. search_events - Call Ticketmaster API
4. normalize_events - Standardize event data
5. enrich_venues - Add venue context (Geoapify)
6. weather_context - Add weather data (OpenWeather)
7. rank_events - Score and rank events
8. generate_explanations - Create natural language explanations
9. prepare_response - Format final response

---

## MCP (Model Context Protocol) Integration

**Decision:** Use FastMCP for tool exposure

**Rationale:**
- Standard protocol for LLM tool calling
- Clean separation between tools and workflow
- Easy to test tools independently
- Supports future tool additions

**Tool Categories:**
- Event search tools
- Location/venue tools
- Weather tools
- Ranking tools
- Calendar export tools
- Redirect/tracking tools
- Demo mode tools

---

## Configuration Management

**Decision:** Pydantic Settings with .env file

**Rationale:**
- Type-safe configuration
- Automatic validation
- Environment variable support
- No hardcoded secrets
- Easy to override for testing

**Key Settings:**
- API keys (Ticketmaster, Geoapify, OpenWeather, watsonx)
- Database connection
- CORS origins
- Cache TTLs
- Demo mode flag

---

## LLM Provider: watsonx.ai

**Decision:** Use IBM watsonx.ai with Granite models

**Rationale:**
- Hackathon requirement
- Good performance for structured tasks
- Supports function calling
- IBM ecosystem integration

**Configuration:**
- Model: ibm/granite-13b-chat-v2
- Temperature: 0.7
- Max tokens: 2048

---

## Caching Strategy

**Decision:** Database-backed API cache

**Rationale:**
- Reduce external API calls
- Improve response times
- Persist across restarts
- Easy to invalidate

**Implementation:**
- api_cache table with TTL
- Separate TTLs per API type
- Cache key based on request hash

---

## Demo Mode

**Decision:** Built-in demo mode with fallback data

**Rationale:**
- Testing without API keys
- Hackathon judging without exposing keys
- Graceful degradation
- Development without rate limits

**Implementation:**
- DEMO_MODE environment variable
- Fallback data in demo_tools.py
- Clearly marked in responses

---

## Security Considerations

**Decisions:**
- No secrets in code
- All API keys in .env
- .env not committed to git
- CORS configured
- Input validation on all endpoints
- SQL injection prevention (SQLAlchemy ORM)

---

## Testing Strategy

**Decisions:**
- Unit tests for individual nodes
- Integration tests for workflow
- API endpoint tests
- Mock external APIs in tests
- Separate test database

**Tools:**
- pytest
- pytest-asyncio
- httpx for API testing

---

## Deployment Considerations

**Decisions:**
- Docker containerization
- docker-compose for local development
- PostgreSQL as separate service
- Environment-based configuration
- Health check endpoint

---

## Future Scalability

**Considerations:**
- Redis for distributed caching
- Message queue for async processing
- Horizontal scaling with load balancer
- CDN for static assets
- Database read replicas

---

## Code Organization

**Structure:**
```
app/
  config/       - Configuration management
  db/           - Database models and migrations
  graph/        - LangGraph workflow and nodes
  integrations/ - External API clients
  mcp/          - MCP server and tools
  models/       - Database models
  routes/       - FastAPI routes
  services/     - Business logic
  static/       - Static files (CSS, JS)
  templates/    - Jinja2 templates
```

**Rationale:**
- Clear separation of concerns
- Easy to navigate
- Scalable structure
- Standard Python package layout

---

## Dependencies Management

**Decision:** requirements.txt with pinned versions

**Rationale:**
- Reproducible builds
- Avoid dependency conflicts
- Easy to audit
- Compatible with pip and Docker

**Key Dependencies:**
- fastapi==0.115.0
- sqlalchemy==2.0.35 (compatible with langchain)
- langgraph==0.2.45
- fastmcp==0.2.0
- pydantic==2.10.2

---

## Error Handling

**Strategy:**
- Graceful degradation
- Fallback to demo data
- Clear error messages
- Workflow trace for debugging
- HTTP status codes

---

## Monitoring & Observability

**Planned:**
- Health check endpoint
- Workflow trace in responses
- Database connection monitoring
- API call tracking
- Performance metrics

---

## Documentation

**Strategy:**
- Inline code comments
- Docstrings for all functions
- README for setup
- HAND_OVER.md for continuity
- TASKS.md for progress tracking
- Architecture notes (this file)