#!/bin/bash
set -e

echo "🧪 Running Pulse AI Test Suite"
echo "================================"

echo ""
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx

echo ""
echo "🔧 Running unit tests..."
pytest tests/test_ranking_service.py -v

echo ""
echo "🔌 Running API connection tests..."
pytest tests/test_api_connections.py -v

echo ""
echo "🔗 Running integration tests..."
pytest tests/test_workflow_integration.py -v -m "not slow"

echo ""
echo "🌐 Running API route tests..."
pytest tests/test_api_routes.py -v

echo ""
echo "🛠️ Running MCP tool tests..."
pytest tests/test_mcp_tools.py -v

echo ""
echo "⚡ Running performance tests..."
pytest tests/test_performance.py -v

echo ""
echo "📊 Generating coverage report..."
pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

echo ""
echo "✅ All tests complete!"
echo "📈 Coverage report: htmlcov/index.html"

# Made with Bob
