#!/bin/bash
set -e

echo "🧪 Running Pulse AI Test Suite"
echo "================================"

echo ""
echo "📦 Installing test dependencies..."
.venv/bin/python -m pip install -q pytest pytest-asyncio pytest-cov httpx

echo ""
echo "🔧 Running unit tests..."
.venv/bin/python -m pytest tests/test_ranking_service.py -v

if [ "${RUN_LIVE_API_TESTS:-0}" = "1" ]; then
  echo ""
  echo "🔌 Running live API connection tests..."
  .venv/bin/python -m pytest tests/test_api_connections.py -v -m live_api
else
  echo ""
  echo "🔌 Skipping live API connection tests (set RUN_LIVE_API_TESTS=1 to enable)"
fi

echo ""
echo "🔗 Running integration tests..."
.venv/bin/python -m pytest tests/test_workflow_integration.py -v -m "not slow and not live_api"

echo ""
echo "🌐 Running API route tests..."
.venv/bin/python -m pytest tests/test_api_routes.py -v -m "not live_api"

echo ""
echo "🛠️ Running MCP tool tests..."
.venv/bin/python -m pytest tests/test_mcp_tools.py -v -m "not live_api"

echo ""
echo "⚡ Running performance tests..."
.venv/bin/python -m pytest tests/test_performance.py -v -m "not live_api"

echo ""
echo "📊 Generating coverage report..."
.venv/bin/python -m pytest tests/ -m "not live_api" --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "✅ All tests complete!"
echo "📈 Coverage report: htmlcov/index.html"

# Made with Bob
