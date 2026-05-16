# Pulse AI - Pre-Development Setup Checklist

## Overview
This comprehensive checklist covers everything you need to prepare before implementing the Pulse AI roadmap. Complete these steps to ensure a smooth development experience.

**Estimated Total Setup Time**: 45-60 minutes (excluding optional items)

---

## 1. Environment Variables & API Keys

### 1.1 Required API Keys (Core Functionality)

#### ✅ Ticketmaster Discovery API
- **Priority**: **REQUIRED** for event search
- **Free Tier**: ✓ Yes (1,000 API calls/day)
- **Cost**: Free
- **Where to Obtain**: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- **Registration Steps**:
  1. Create account at https://developer-acct.ticketmaster.com/user/register
  2. Verify email address
  3. Navigate to "My Apps" → "Create New App"
  4. Fill in app details (name: "Pulse AI", description: "Event discovery platform")
  5. Copy your API Key (shown as "Consumer Key")
- **Configuration**: Add to `.env` as `TICKETMASTER_API_KEY=your_key_here`
- **Testing**: Test at https://developer.ticketmaster.com/api-explorer/v2/
- **Estimated Time**: ⏱️ 5 minutes

#### ✅ Geoapify Places API
- **Priority**: **REQUIRED** for venue enrichment
- **Free Tier**: ✓ Yes (3,000 requests/day)
- **Cost**: Free
- **Where to Obtain**: https://www.geoapify.com/
- **Registration Steps**:
  1. Sign up at https://myprojects.geoapify.com/register
  2. Verify email address
  3. Create a new project (name: "Pulse AI")
  4. Copy API key from project dashboard
- **Configuration**: Add to `.env` as `GEOAPIFY_API_KEY=your_key_here`
- **Testing**: Test at https://apidocs.geoapify.com/playground/places/
- **Estimated Time**: ⏱️ 5 minutes

### 1.2 Optional API Keys (Enhanced Features)

#### 🔶 OpenWeather API
- **Priority**: **OPTIONAL** (nice-to-have for outdoor events)
- **Free Tier**: ✓ Yes (1,000 calls/day, 60 calls/minute)
- **Cost**: Free
- **Where to Obtain**: https://openweathermap.org/api
- **Registration Steps**:
  1. Sign up at https://home.openweathermap.org/users/sign_up
  2. Verify email address
  3. Navigate to "API keys" tab in dashboard
  4. Copy default API key or create new one
  5. ⚠️ Wait ~10 minutes for key activation
- **Configuration**: Add to `.env` as `OPENWEATHER_API_KEY=your_key_here`
- **Testing**: Test at https://openweathermap.org/api
- **Estimated Time**: ⏱️ 5 minutes + 10 min activation wait

### 1.3 LLM Provider Keys (Choose ONE or NONE)

> **Note**: LLM providers are **OPTIONAL**. The app includes deterministic fallback parsing that works without any LLM.

#### Option A: OpenAI (Recommended for Hackathon)
- **Priority**: **OPTIONAL** (fallback to deterministic parsing available)
- **Free Tier**: ✗ No ($5 minimum credit required)
- **Cost**: ~$0.002 per request (GPT-3.5-turbo)
- **Where to Obtain**: https://platform.openai.com/api-keys
- **Registration Steps**:
  1. Sign up at https://platform.openai.com/signup
  2. Add payment method (minimum $5 credit)
  3. Navigate to API Keys section
  4. Create new secret key
  5. Copy and save immediately (shown only once)
- **Configuration**: 
  ```env
  LLM_PROVIDER=openai
  OPENAI_API_KEY=sk-...your_key_here
  ```
- **Estimated Time**: ⏱️ 10 minutes

#### Option B: Anthropic Claude
- **Priority**: **OPTIONAL**
- **Free Tier**: ✗ No ($5 minimum credit required)
- **Cost**: ~$0.003 per request (Claude 3 Haiku)
- **Where to Obtain**: https://console.anthropic.com/
- **Registration Steps**:
  1. Sign up at https://console.anthropic.com/
  2. Add payment method
  3. Navigate to API Keys
  4. Create new key
  5. Copy and save immediately
- **Configuration**:
  ```env
  LLM_PROVIDER=anthropic
  ANTHROPIC_API_KEY=sk-ant-...your_key_here
  ```
- **Estimated Time**: ⏱️ 10 minutes

#### Option C: IBM watsonx.ai
- **Priority**: **OPTIONAL** (IBM-specific integration)
- **Free Tier**: ✓ Yes (trial available)
- **Cost**: Free trial, then pay-as-you-go
- **Where to Obtain**: https://www.ibm.com/watsonx
- **Registration Steps**:
  1. Sign up for IBM Cloud at https://cloud.ibm.com/registration
  2. Create watsonx.ai service instance
  3. Navigate to service credentials
  4. Copy API key, Project ID, and URL
- **Configuration**:
  ```env
  LLM_PROVIDER=watsonx
  WATSONX_API_KEY=your_key_here
  WATSONX_PROJECT_ID=your_project_id
  WATSONX_URL=https://us-south.ml.cloud.ibm.com
  ```
- **Estimated Time**: ⏱️ 15 minutes

#### Option D: No LLM (Deterministic Mode)
- **Priority**: **RECOMMENDED FOR INITIAL SETUP**
- **Free Tier**: ✓ Yes (always free)
- **Cost**: Free
- **Configuration**:
  ```env
  LLM_PROVIDER=none
  ```
- **Note**: App will use rule-based query parsing and template-based explanations
- **Estimated Time**: ⏱️ 0 minutes

---

## 2. GitHub Repository Setup

### 2.1 Repository Initialization
- [ ] Create new GitHub repository
  - Name: `pulse-ai` or `pulse-ai-hackathon`
  - Visibility: Public (for hackathon submission)
  - Initialize with README: No (will create custom one)
  - Add .gitignore: Python
  - License: MIT (recommended for hackathons)
- [ ] Clone repository locally:
  ```bash
  git clone https://github.com/YOUR_USERNAME/pulse-ai.git
  cd pulse-ai
  ```
- **Estimated Time**: ⏱️ 5 minutes

### 2.2 Branch Strategy
- [ ] Set up branch protection for `main`
  - Settings → Branches → Add rule
  - Require pull request reviews: Optional for solo hackathon
- [ ] Create development branch:
  ```bash
  git checkout -b develop
  ```
- **Recommended Branches**:
  - `main` - Production-ready code
  - `develop` - Active development
  - `feature/*` - Individual features
  - `hotfix/*` - Quick fixes
- **Estimated Time**: ⏱️ 5 minutes

### 2.3 Issue Templates
- [ ] Create `.github/ISSUE_TEMPLATE/` directory
- [ ] Add bug report template (`.github/ISSUE_TEMPLATE/bug_report.md`)
- [ ] Add feature request template (`.github/ISSUE_TEMPLATE/feature_request.md`)
- [ ] Add task template (`.github/ISSUE_TEMPLATE/task.md`)
- **Estimated Time**: ⏱️ 10 minutes (optional for hackathon)

### 2.4 GitHub Project Board
- [ ] Create new Project (Projects tab)
  - Template: "Basic kanban"
  - Columns: To Do, In Progress, Done
- [ ] Add initial issues from roadmap phases
- [ ] Link project to repository
- **Estimated Time**: ⏱️ 10 minutes (optional but helpful)

### 2.5 GitHub Secrets Configuration
- [ ] Navigate to Settings → Secrets and variables → Actions
- [ ] Add repository secrets (for CI/CD):
  - `TICKETMASTER_API_KEY`
  - `GEOAPIFY_API_KEY`
  - `OPENWEATHER_API_KEY` (if using)
  - `OPENAI_API_KEY` (if using)
  - `ANTHROPIC_API_KEY` (if using)
  - `WATSONX_API_KEY` (if using)
- **Note**: Only add secrets if setting up GitHub Actions
- **Estimated Time**: ⏱️ 5 minutes (optional)

### 2.6 Collaboration Settings
- [ ] Add collaborators (if team project)
  - Settings → Collaborators → Add people
- [ ] Set up branch protection rules (if needed)
- [ ] Configure merge settings:
  - Allow squash merging: ✓
  - Allow merge commits: ✓
  - Allow rebase merging: ✓
- **Estimated Time**: ⏱️ 5 minutes

---

## 3. Local Development Environment

### 3.1 Required Software Installations

#### Python 3.12+
- **Priority**: **REQUIRED**
- **Where to Download**: https://www.python.org/downloads/
- **Installation Steps**:
  - **macOS**: 
    ```bash
    brew install python@3.12
    ```
  - **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt update
    sudo apt install python3.12 python3.12-venv python3-pip
    ```
  - **Windows**: Download installer from python.org
- **Verify Installation**:
  ```bash
  python3 --version  # Should show 3.12.x or higher
  ```
- **Estimated Time**: ⏱️ 10 minutes

#### Git
- **Priority**: **REQUIRED**
- **Where to Download**: https://git-scm.com/downloads
- **Verify Installation**:
  ```bash
  git --version
  ```
- **Estimated Time**: ⏱️ 5 minutes

#### Docker & Docker Compose
- **Priority**: **RECOMMENDED** (for PostgreSQL and deployment)
- **Where to Download**: https://docs.docker.com/get-docker/
- **Installation Steps**:
  - **macOS**: Install Docker Desktop
  - **Linux**: 
    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose-plugin
    ```
  - **Windows**: Install Docker Desktop
- **Verify Installation**:
  ```bash
  docker --version
  docker compose version
  ```
- **Estimated Time**: ⏱️ 15 minutes

### 3.2 IDE/Editor Setup

#### Recommended: VS Code
- **Download**: https://code.visualstudio.com/
- **Required Extensions**:
  - [ ] Python (ms-python.python)
  - [ ] Pylance (ms-python.vscode-pylance)
  - [ ] Python Debugger (ms-python.debugpy)
  - [ ] Ruff (charliermarsh.ruff)
  - [ ] Docker (ms-azuretools.vscode-docker)
- **Optional Extensions**:
  - [ ] GitHub Copilot (github.copilot)
  - [ ] GitLens (eamodio.gitlens)
  - [ ] Better Jinja (samuelcolvin.jinjahtml)
  - [ ] REST Client (humao.rest-client)
- **Estimated Time**: ⏱️ 10 minutes

#### Alternative: PyCharm
- **Download**: https://www.jetbrains.com/pycharm/download/
- **Edition**: Community (free) or Professional
- **Estimated Time**: ⏱️ 10 minutes

### 3.3 Python Virtual Environment
- [ ] Create virtual environment:
  ```bash
  cd pulse-ai
  python3 -m venv .venv
  ```
- [ ] Activate virtual environment:
  - **macOS/Linux**:
    ```bash
    source .venv/bin/activate
    ```
  - **Windows**:
    ```bash
    .venv\Scripts\activate
    ```
- [ ] Verify activation (prompt should show `(.venv)`)
- [ ] Upgrade pip:
  ```bash
  pip install --upgrade pip
  ```
- **Estimated Time**: ⏱️ 3 minutes

---

## 4. Database Setup

### 4.1 PostgreSQL Installation Options

> **Note**: Roadmap specifies PostgreSQL from the start (not SQLite)

#### Option A: Docker PostgreSQL (Recommended)
- **Priority**: **RECOMMENDED** (easiest setup)
- **Prerequisites**: Docker installed
- **Setup Steps**:
  1. Create `docker-compose.yml` in project root:
     ```yaml
     version: '3.8'
     services:
       postgres:
         image: postgres:16-alpine
         container_name: pulse_ai_db
         environment:
           POSTGRES_USER: pulse_user
           POSTGRES_PASSWORD: pulse_password
           POSTGRES_DB: pulse_ai
         ports:
           - "5432:5432"
         volumes:
           - postgres_data:/var/lib/postgresql/data
     volumes:
       postgres_data:
     ```
  2. Start PostgreSQL:
     ```bash
     docker compose up -d
     ```
  3. Verify connection:
     ```bash
     docker exec -it pulse_ai_db psql -U pulse_user -d pulse_ai
     ```
- **Connection String**:
  ```env
  DATABASE_URL=postgresql+asyncpg://pulse_user:pulse_password@localhost:5432/pulse_ai
  ```
- **Estimated Time**: ⏱️ 5 minutes

#### Option B: Local PostgreSQL Installation
- **Priority**: **ALTERNATIVE**
- **Installation Steps**:
  - **macOS**:
    ```bash
    brew install postgresql@16
    brew services start postgresql@16
    ```
  - **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    sudo systemctl start postgresql
    ```
  - **Windows**: Download from https://www.postgresql.org/download/windows/
- **Database Creation**:
  ```bash
  sudo -u postgres psql
  CREATE DATABASE pulse_ai;
  CREATE USER pulse_user WITH PASSWORD 'pulse_password';
  GRANT ALL PRIVILEGES ON DATABASE pulse_ai TO pulse_user;
  \q
  ```
- **Connection String**:
  ```env
  DATABASE_URL=postgresql+asyncpg://pulse_user:pulse_password@localhost:5432/pulse_ai
  ```
- **Estimated Time**: ⏱️ 15 minutes

#### Option C: Cloud PostgreSQL (Production)
- **Priority**: **OPTIONAL** (for deployment)
- **Providers**:
  - **Render**: https://render.com/docs/databases
  - **Railway**: https://railway.app/
  - **Supabase**: https://supabase.com/ (free tier available)
  - **ElephantSQL**: https://www.elephantsql.com/ (free tier available)
- **Setup**: Follow provider-specific instructions
- **Estimated Time**: ⏱️ 10 minutes

### 4.2 Database Configuration
- [ ] Add connection string to `.env`:
  ```env
  DATABASE_URL=postgresql+asyncpg://pulse_user:pulse_password@localhost:5432/pulse_ai
  ```
- [ ] Test connection (after Phase 1 implementation)
- **Estimated Time**: ⏱️ 2 minutes

---

## 5. Pre-Development Decisions

### 5.1 LLM Provider Selection
**Decision Required**: Which LLM provider will you use (if any)?

- [ ] **Option A: None (Deterministic)** ✅ RECOMMENDED FOR START
  - Pros: Free, fast, reliable, no API dependency
  - Cons: Less flexible query understanding
  - Best for: Initial development, demo mode

- [ ] **Option B: OpenAI**
  - Pros: Best performance, well-documented
  - Cons: Costs money, requires payment method
  - Best for: Production deployment

- [ ] **Option C: Anthropic Claude**
  - Pros: Good performance, strong reasoning
  - Cons: Costs money, similar to OpenAI pricing
  - Best for: Alternative to OpenAI

- [ ] **Option D: IBM watsonx.ai**
  - Pros: IBM integration, free trial
  - Cons: More complex setup
  - Best for: IBM-focused hackathon projects

**Recommendation**: Start with `LLM_PROVIDER=none`, add LLM later if needed.

### 5.2 Deployment Platform Preference
**Decision Required**: Where will you deploy for the demo?

- [ ] **Render** (Recommended)
  - Pros: Easy setup, free tier, PostgreSQL included
  - Cons: Cold starts on free tier
  - URL: https://render.com/

- [ ] **Railway**
  - Pros: Simple deployment, good free tier
  - Cons: Credit card required for free tier
  - URL: https://railway.app/

- [ ] **IBM Cloud Code Engine**
  - Pros: IBM integration, serverless
  - Cons: More complex setup
  - URL: https://www.ibm.com/cloud/code-engine

- [ ] **Docker + VPS**
  - Pros: Full control, no cold starts
  - Cons: Requires server management
  - Providers: DigitalOcean, Linode, Vultr

**Recommendation**: Render for easiest hackathon deployment.

### 5.3 Demo Mode vs Live API Priority
**Decision Required**: What's your development priority?

- [ ] **Demo Mode First** ✅ RECOMMENDED
  - Build with static demo data
  - Add live APIs incrementally
  - Ensures reliable presentation
  - Follows roadmap Phase 2

- [ ] **Live APIs First**
  - Integrate real APIs immediately
  - Add demo mode as fallback
  - More realistic but riskier for demo

**Recommendation**: Demo mode first (as per roadmap).

### 5.4 Testing Framework Preferences
**Decision Required**: How comprehensive should testing be?

- [ ] **Minimal Testing** (Hackathon Speed)
  - Unit tests for critical functions only
  - Manual testing for UI
  - Target: 40-50% coverage

- [ ] **Moderate Testing** ✅ RECOMMENDED
  - Unit tests for business logic
  - Integration tests for API clients
  - Basic E2E test for demo flow
  - Target: 60% coverage (roadmap goal)

- [ ] **Comprehensive Testing** (Production Quality)
  - Full unit test coverage
  - Integration tests for all routes
  - Multiple E2E scenarios
  - Target: 80%+ coverage

**Recommendation**: Moderate testing (60% coverage as per roadmap).

---

## 6. Optional Enhancements

### 6.1 IBM Cloud Account Setup
**Priority**: **OPTIONAL** (only if using watsonx or Cloudant)

- [ ] Sign up at https://cloud.ibm.com/registration
- [ ] Verify email and complete profile
- [ ] Create resource group for Pulse AI
- [ ] Set up billing (free tier available)
- [ ] Create watsonx.ai service instance (if using)
- [ ] Create Cloudant database (if replacing PostgreSQL)
- **Estimated Time**: ⏱️ 20 minutes

### 6.2 CI/CD Pipeline Setup
**Priority**: **OPTIONAL** (nice-to-have for hackathon)

#### GitHub Actions
- [ ] Create `.github/workflows/` directory
- [ ] Add `test.yml` workflow:
  ```yaml
  name: Tests
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.12'
        - run: pip install -r requirements.txt
        - run: pytest
  ```
- [ ] Add `lint.yml` workflow for code quality
- **Estimated Time**: ⏱️ 15 minutes

### 6.3 Monitoring & Logging Tools
**Priority**: **OPTIONAL** (post-MVP)

#### Sentry (Error Tracking)
- [ ] Sign up at https://sentry.io/
- [ ] Create new project (Python/FastAPI)
- [ ] Copy DSN
- [ ] Add to `.env`: `SENTRY_DSN=your_dsn_here`
- **Estimated Time**: ⏱️ 10 minutes

#### LogTail (Log Management)
- [ ] Sign up at https://logtail.com/
- [ ] Create source token
- [ ] Add to `.env`: `LOGTAIL_TOKEN=your_token_here`
- **Estimated Time**: ⏱️ 10 minutes

---

## 7. Environment Configuration Checklist

### 7.1 Create `.env` File
- [ ] Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- [ ] Fill in all required values:

```env
# =========================================
# APPLICATION
# =========================================
APP_NAME=Pulse AI
APP_ENV=development
DEBUG=true
SECRET_KEY=your_secret_key_here_change_in_production

# =========================================
# SERVER
# =========================================
HOST=0.0.0.0
PORT=8000

# =========================================
# DATABASE
# =========================================
DATABASE_URL=postgresql+asyncpg://pulse_user:pulse_password@localhost:5432/pulse_ai

# =========================================
# DEMO MODE
# =========================================
DEMO_MODE=true
CACHE_TTL_SECONDS=900

# =========================================
# EVENT PROVIDERS
# =========================================
TICKETMASTER_API_KEY=your_ticketmaster_key_here
GEOAPIFY_API_KEY=your_geoapify_key_here
OPENWEATHER_API_KEY=your_openweather_key_here_or_leave_empty

# =========================================
# LLM PROVIDERS
# =========================================
LLM_PROVIDER=none
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=

# =========================================
# SECURITY
# =========================================
ALLOWED_HOSTS=localhost,127.0.0.1
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax

# =========================================
# LOGGING
# =========================================
LOG_LEVEL=INFO

# =========================================
# FEATURE FLAGS
# =========================================
ENABLE_WORKFLOW_TRACE=true
ENABLE_CALENDAR_EXPORT=true
ENABLE_VENUE_ENRICHMENT=true
ENABLE_WEATHER_CONTEXT=true

# =========================================
# RATE LIMITING
# =========================================
SEARCH_RATE_LIMIT_PER_MINUTE=20
REDIRECT_RATE_LIMIT_PER_MINUTE=60
CALENDAR_RATE_LIMIT_PER_MINUTE=30
```

### 7.2 Verify `.gitignore`
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Verify `.venv/` is ignored
- [ ] Check `__pycache__/` is ignored
- [ ] Confirm `*.pyc` is ignored
- [ ] Add `pulse_ai.db` (if using SQLite for testing)
- [ ] Add `bob_sessions/private/` if needed

---

## 8. Quick Start Commands Reference

### Development Workflow
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies (after Phase 1)
pip install -r requirements.txt

# Start PostgreSQL (Docker)
docker compose up -d

# Run database migrations (after Phase 1)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Stop PostgreSQL
docker compose down
```

### Useful Commands
```bash
# Check Python version
python3 --version

# Check pip version
pip --version

# List installed packages
pip list

# Check PostgreSQL connection
docker exec -it pulse_ai_db psql -U pulse_user -d pulse_ai

# View PostgreSQL logs
docker logs pulse_ai_db

# Format code with black
black app/

# Lint with ruff
ruff check app/

# Type check with mypy
mypy app/
```

---

## 9. Pre-Development Checklist Summary

### Essential (Must Complete Before Starting)
- [ ] ✅ Ticketmaster API key obtained and configured
- [ ] ✅ Geoapify API key obtained and configured
- [ ] ✅ Python 3.12+ installed and verified
- [ ] ✅ Git installed and configured
- [ ] ✅ GitHub repository created and cloned
- [ ] ✅ Virtual environment created and activated
- [ ] ✅ PostgreSQL running (Docker or local)
- [ ] ✅ `.env` file created with required values
- [ ] ✅ IDE/editor set up with Python extensions

### Recommended (Should Complete)
- [ ] 🔶 OpenWeather API key obtained (optional but useful)
- [ ] 🔶 Docker installed for PostgreSQL
- [ ] 🔶 LLM provider decision made
- [ ] 🔶 Deployment platform selected
- [ ] 🔶 GitHub project board created
- [ ] 🔶 Development branch created

### Optional (Nice to Have)
- [ ] ⭐ IBM Cloud account (if using watsonx)
- [ ] ⭐ CI/CD pipeline configured
- [ ] ⭐ Monitoring tools set up
- [ ] ⭐ Issue templates created
- [ ] ⭐ GitHub Actions configured

---

## 10. Troubleshooting Common Setup Issues

### Issue: Python version too old
**Solution**:
```bash
# macOS
brew install python@3.12

# Linux
sudo apt install python3.12

# Verify
python3 --version
```

### Issue: PostgreSQL connection refused
**Solution**:
```bash
# Check if PostgreSQL is running
docker ps

# Restart PostgreSQL
docker compose restart

# Check logs
docker logs pulse_ai_db
```

### Issue: API key not working
**Solution**:
1. Verify key is correctly copied (no extra spaces)
2. Check if key is activated (OpenWeather takes ~10 min)
3. Test key directly in provider's API explorer
4. Ensure `.env` file is in project root
5. Restart development server after changing `.env`

### Issue: Virtual environment not activating
**Solution**:
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv

# Activate with full path
source /full/path/to/pulse-ai/.venv/bin/activate
```

### Issue: Port 8000 already in use
**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
uvicorn app.main:app --reload --port 8001
```

---

## 11. Next Steps After Setup

Once you've completed this checklist:

1. **Verify Setup**: Run through the "Quick Start Commands" to ensure everything works
2. **Review Roadmap**: Read [`ROADMAP.md`](ROADMAP.md) to understand the development phases
3. **Start Phase 1**: Begin with "Foundation & Project Structure"
4. **Use Bob Mode**: Switch to Code mode to start implementation
5. **Track Progress**: Update `TASKS.md` and `HAND_OVER.md` as you work

---

## 12. Estimated Total Setup Time

| Category | Time |
|----------|------|
| API Keys (Required) | 15 minutes |
| API Keys (Optional) | 15-30 minutes |
| GitHub Setup | 15 minutes |
| Local Environment | 30 minutes |
| Database Setup | 10-20 minutes |
| Configuration | 10 minutes |
| **Total (Minimum)** | **1-1.5 hours** |
| **Total (With Optional)** | **2-2.5 hours** |

---

## 13. Support Resources

### Documentation
- **Ticketmaster API**: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- **Geoapify API**: https://apidocs.geoapify.com/
- **OpenWeather API**: https://openweathermap.org/api
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Community
- **FastAPI Discord**: https://discord.gg/fastapi
- **LangChain Discord**: https://discord.gg/langchain
- **Python Discord**: https://discord.gg/python

### Hackathon Resources
- **Lablab.ai**: https://lablab.ai/
- **IBM Developer**: https://developer.ibm.com/

---

## Checklist Complete! 🎉

Once you've completed the essential items, you're ready to start development. Switch to **Code mode** and begin with **Phase 1: Foundation & Project Structure** from the roadmap.

**Good luck with your hackathon project!** 🚀