"""APICache model for caching external API responses."""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class APICache(Base):
    """Model for API cache table."""
    
    __tablename__ = "api_cache"
    
    cache_key = Column(String(255), primary_key=True)
    tool_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=True)
    request_hash = Column(String(64), nullable=False, index=True)
    response_json = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<APICache(key={self.cache_key}, tool={self.tool_name}, provider={self.provider})>"

# Made with Bob
