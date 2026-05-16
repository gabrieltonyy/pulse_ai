"""Database repositories for Pulse AI.

Provides async repository pattern for database operations.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_events import SavedEvent
from app.models.search_history import SearchHistory
from app.models.api_cache import APICache
from app.models.outbound_clicks import OutboundClick


class SavedEventsRepository:
    """Repository for saved events operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def save_event(
        self,
        session_id: str,
        event_id: str,
        provider: str,
        title: str,
        event_json: str,
    ) -> SavedEvent:
        """
        Save an event for a user session.
        
        Args:
            session_id: User session identifier
            event_id: Event identifier
            provider: Event provider name
            title: Event title
            event_json: JSON string of full event data
        
        Returns:
            Created SavedEvent instance
        """
        saved_event = SavedEvent(
            session_id=session_id,
            event_id=event_id,
            provider=provider,
            title=title,
            event_json=event_json,
        )
        self.session.add(saved_event)
        await self.session.flush()
        return saved_event
    
    async def get_by_session(self, session_id: str) -> List[SavedEvent]:
        """
        Get all saved events for a session.
        
        Args:
            session_id: User session identifier
        
        Returns:
            List of SavedEvent instances
        """
        result = await self.session.execute(
            select(SavedEvent)
            .where(SavedEvent.session_id == session_id)
            .order_by(SavedEvent.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, saved_event_id: int) -> Optional[SavedEvent]:
        """
        Get a saved event by ID.
        
        Args:
            saved_event_id: Saved event ID
        
        Returns:
            SavedEvent instance or None
        """
        result = await self.session.execute(
            select(SavedEvent).where(SavedEvent.id == saved_event_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_by_id(self, saved_event_id: int) -> bool:
        """
        Delete a saved event by ID.
        
        Args:
            saved_event_id: Saved event ID
        
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(SavedEvent).where(SavedEvent.id == saved_event_id)
        )
        return result.rowcount > 0
    
    async def exists(self, session_id: str, event_id: str) -> bool:
        """
        Check if an event is already saved for a session.
        
        Args:
            session_id: User session identifier
            event_id: Event identifier
        
        Returns:
            True if event is saved, False otherwise
        """
        result = await self.session.execute(
            select(SavedEvent.id)
            .where(
                and_(
                    SavedEvent.session_id == session_id,
                    SavedEvent.event_id == event_id
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None


class SearchHistoryRepository:
    """Repository for search history operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def create_search(
        self,
        raw_query: str,
        session_id: Optional[str] = None,
        parsed_intent_json: Optional[str] = None,
        result_count: int = 0,
        fallback_used: bool = False,
    ) -> SearchHistory:
        """
        Record a search query.
        
        Args:
            raw_query: The raw search query string
            session_id: Optional user session identifier
            parsed_intent_json: Optional JSON string of parsed intent
            result_count: Number of results returned
            fallback_used: Whether fallback data was used
        
        Returns:
            Created SearchHistory instance
        """
        search = SearchHistory(
            session_id=session_id,
            raw_query=raw_query,
            parsed_intent_json=parsed_intent_json,
            result_count=result_count,
            fallback_used=fallback_used,
        )
        self.session.add(search)
        await self.session.flush()
        return search
    
    async def get_by_session(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[SearchHistory]:
        """
        Get search history for a session.
        
        Args:
            session_id: User session identifier
            limit: Maximum number of records to return
        
        Returns:
            List of SearchHistory instances
        """
        result = await self.session.execute(
            select(SearchHistory)
            .where(SearchHistory.session_id == session_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent(self, limit: int = 100) -> List[SearchHistory]:
        """
        Get recent searches across all sessions.
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of SearchHistory instances
        """
        result = await self.session.execute(
            select(SearchHistory)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class ApiCacheRepository:
    """Repository for API cache operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def set_cache(
        self,
        cache_key: str,
        tool_name: str,
        request_hash: str,
        response_json: str,
        expires_at: datetime,
        provider: Optional[str] = None,
    ) -> APICache:
        """
        Store API response in cache.
        
        Args:
            cache_key: Unique cache key
            tool_name: Name of the tool/API
            request_hash: Hash of the request parameters
            response_json: JSON string of the response
            expires_at: Cache expiration datetime
            provider: Optional provider name
        
        Returns:
            Created or updated APICache instance
        """
        # Check if cache entry exists
        existing = await self.get_cache(cache_key)
        
        if existing:
            # Update existing entry
            existing.response_json = response_json
            existing.expires_at = expires_at
            existing.request_hash = request_hash
            await self.session.flush()
            return existing
        else:
            # Create new entry
            cache_entry = APICache(
                cache_key=cache_key,
                tool_name=tool_name,
                provider=provider,
                request_hash=request_hash,
                response_json=response_json,
                expires_at=expires_at,
            )
            self.session.add(cache_entry)
            await self.session.flush()
            return cache_entry
    
    async def get_cache(self, cache_key: str) -> Optional[APICache]:
        """
        Get cached API response.
        
        Args:
            cache_key: Unique cache key
        
        Returns:
            APICache instance or None if not found or expired
        """
        result = await self.session.execute(
            select(APICache)
            .where(
                and_(
                    APICache.cache_key == cache_key,
                    APICache.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def delete_expired(self) -> int:
        """
        Delete expired cache entries.
        
        Returns:
            Number of deleted entries
        """
        result = await self.session.execute(
            delete(APICache).where(APICache.expires_at <= datetime.utcnow())
        )
        return result.rowcount
    
    async def clear_by_tool(self, tool_name: str) -> int:
        """
        Clear all cache entries for a specific tool.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            Number of deleted entries
        """
        result = await self.session.execute(
            delete(APICache).where(APICache.tool_name == tool_name)
        )
        return result.rowcount


class OutboundClicksRepository:
    """Repository for outbound clicks tracking."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def record_click(
        self,
        event_id: str,
        provider: str,
        session_id: Optional[str] = None,
    ) -> OutboundClick:
        """
        Record an outbound click to an event.
        
        Args:
            event_id: Event identifier
            provider: Event provider name
            session_id: Optional user session identifier
        
        Returns:
            Created OutboundClick instance
        """
        click = OutboundClick(
            session_id=session_id,
            event_id=event_id,
            provider=provider,
        )
        self.session.add(click)
        await self.session.flush()
        return click
    
    async def get_by_event(self, event_id: str) -> List[OutboundClick]:
        """
        Get all clicks for a specific event.
        
        Args:
            event_id: Event identifier
        
        Returns:
            List of OutboundClick instances
        """
        result = await self.session.execute(
            select(OutboundClick)
            .where(OutboundClick.event_id == event_id)
            .order_by(OutboundClick.clicked_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_session(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[OutboundClick]:
        """
        Get clicks for a specific session.
        
        Args:
            session_id: User session identifier
            limit: Maximum number of records to return
        
        Returns:
            List of OutboundClick instances
        """
        result = await self.session.execute(
            select(OutboundClick)
            .where(OutboundClick.session_id == session_id)
            .order_by(OutboundClick.clicked_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_event(self, event_id: str) -> int:
        """
        Count total clicks for an event.
        
        Args:
            event_id: Event identifier
        
        Returns:
            Number of clicks
        """
        result = await self.session.execute(
            select(OutboundClick.id)
            .where(OutboundClick.event_id == event_id)
        )
        return len(list(result.scalars().all()))


# Made with Bob