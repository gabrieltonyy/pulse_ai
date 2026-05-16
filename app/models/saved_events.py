"""SavedEvents model for storing user-saved events."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class SavedEvent(Base):
    """Model for saved events table."""
    
    __tablename__ = "saved_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    title = Column(Text, nullable=False)
    event_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<SavedEvent(id={self.id}, event_id={self.event_id}, provider={self.provider})>"

# Made with Bob
