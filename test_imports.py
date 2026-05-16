"""
Quick test to verify all imports work correctly.
This doesn't require a database connection.
"""
import sys

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test config
        print("✓ Importing config...")
        from app.config import settings
        print(f"  - App name: {settings.app_name}")
        print(f"  - LLM provider: {settings.llm_provider}")
        
        # Test database module
        print("✓ Importing database...")
        from app.db import Base, get_db
        
        # Test models
        print("✓ Importing models...")
        from app.models import SavedEvent, SearchHistory, APICache, OutboundClick
        
        # Test graph
        print("✓ Importing graph...")
        from app.graph import PulseGraphState, get_workflow
        
        # Test MCP
        print("✓ Importing MCP...")
        from app.mcp import get_mcp_server
        
        # Test main app
        print("✓ Importing main app...")
        from app.main import app
        print(f"  - FastAPI app: {app.title}")
        
        print("\n✅ All imports successful!")
        print("\nNext steps:")
        print("1. Start PostgreSQL: docker-compose up -d postgres")
        print("2. Run migrations: alembic upgrade head")
        print("3. Start app: uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

# Made with Bob
