"""
Pulse AI - FastAPI Application Entry Point
Main application initialization and configuration.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import init_db, close_db, check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Pulse AI...")
    print(f"📊 Environment: {'Production' if settings.is_production else 'Development'}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")
    print(f"🎭 Demo Mode: {settings.demo_mode}")
    
    # Initialize database
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Shutting down Pulse AI...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered event discovery and recommendation platform",
    lifespan=lifespan,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error_code": "NOT_FOUND",
            "message": "The requested resource was not found",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    Returns application status and database connectivity.
    """
    db_healthy = await check_db_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db_healthy else "disconnected",
        "llm_provider": settings.llm_provider,
        "demo_mode": settings.demo_mode,
    }


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Pulse AI",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers (will be added in later phases)
# from app.routes import search, events, calendar
# app.include_router(search.router, prefix="/api/search", tags=["search"])
# app.include_router(events.router, prefix="/api/events", tags=["events"])
# app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )

# Made with Bob
