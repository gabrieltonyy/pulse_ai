"""OutboundClicks model for tracking user clicks to external event pages."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class OutboundClick(Base):
    """Model for outbound clicks table."""
    
    __tablename__ = "outbound_clicks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=True, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    clicked_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    
    def __repr__(self) -> str:
        return f"<OutboundClick(id={self.id}, event_id={self.event_id}, provider={self.provider})>"

# Made with Bob
