"""SearchHistory model for tracking user searches."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.db.database import Base


class SearchHistory(Base):
    """Model for search history table."""
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=True, index=True)
    raw_query = Column(Text, nullable=False)
    parsed_intent_json = Column(Text, nullable=True)
    result_count = Column(Integer, default=0, nullable=False)
    fallback_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, query={self.raw_query[:50]}, results={self.result_count})>"

# Made with Bob
