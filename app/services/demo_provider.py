"""Demo data provider for Pulse AI.

Provides realistic event data for demo mode without requiring external API keys.
"""
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional
from app.models.event import Event


class DemoProvider:
    """Provides demo event data from local JSON file."""
    
    def __init__(self):
        """Initialize demo provider and load events."""
        self.events: list[Event] = []
        self._load_events()
    
    def _load_events(self) -> None:
        """Load events from demo_events.json file."""
        demo_file = Path(__file__).parent.parent / "data" / "demo_events.json"
        
        if not demo_file.exists():
            raise FileNotFoundError(f"Demo events file not found: {demo_file}")
        
        with open(demo_file, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        
        # Convert JSON data to Event objects
        for event_data in events_data:
            # Parse datetime strings
            if event_data.get("start_datetime"):
                event_data["start_datetime"] = datetime.fromisoformat(
                    event_data["start_datetime"]
                )
            if event_data.get("end_datetime"):
                event_data["end_datetime"] = datetime.fromisoformat(
                    event_data["end_datetime"]
                )
            
            self.events.append(Event(**event_data))
    
    def search_events(
        self,
        city: Optional[str] = None,
        country: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        budget_max: Optional[float] = None,
        limit: int = 10,
    ) -> list[Event]:
        """
        Search demo events with filters.
        
        Args:
            city: Filter by city name (case-insensitive)
            country: Filter by country name (case-insensitive)
            category: Filter by event category (case-insensitive)
            keyword: Search in title and description (case-insensitive)
            date_from: Filter events starting from this date
            date_to: Filter events up to this date
            budget_max: Filter events with price_min <= budget_max
            limit: Maximum number of events to return
        
        Returns:
            List of Event objects matching the filters
        """
        filtered_events = self.events.copy()
        
        # Apply city filter
        if city:
            city_lower = city.lower()
            filtered_events = [
                e for e in filtered_events
                if e.venue_city and city_lower in e.venue_city.lower()
            ]
        
        # Apply country filter
        if country:
            country_lower = country.lower()
            filtered_events = [
                e for e in filtered_events
                if e.venue_country and country_lower in e.venue_country.lower()
            ]
        
        # Apply category filter
        if category:
            category_lower = category.lower()
            filtered_events = [
                e for e in filtered_events
                if e.category and category_lower in e.category.lower()
            ]
        
        # Apply keyword filter (search in title and description)
        if keyword:
            keyword_lower = keyword.lower()
            filtered_events = [
                e for e in filtered_events
                if (e.title and keyword_lower in e.title.lower()) or
                   (e.description and keyword_lower in e.description.lower())
            ]
        
        # Apply date range filter
        if date_from:
            filtered_events = [
                e for e in filtered_events
                if e.start_datetime and e.start_datetime.date() >= date_from
            ]
        
        if date_to:
            filtered_events = [
                e for e in filtered_events
                if e.start_datetime and e.start_datetime.date() <= date_to
            ]
        
        # Apply budget filter
        if budget_max is not None:
            filtered_events = [
                e for e in filtered_events
                if e.price_min is not None and e.price_min <= budget_max
            ]
        
        # Sort by start date (upcoming first) and popularity
        filtered_events.sort(
            key=lambda e: (
                e.start_datetime or datetime.max,
                -(e.popularity_score or 0)
            )
        )
        
        # Apply limit
        return filtered_events[:limit]
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: The event ID to search for
        
        Returns:
            Event object if found, None otherwise
        """
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def get_cities(self) -> list[str]:
        """
        Get list of all available cities in demo data.
        
        Returns:
            List of unique city names
        """
        cities = set()
        for event in self.events:
            if event.venue_city:
                cities.add(event.venue_city)
        return sorted(list(cities))
    
    def get_categories(self) -> list[str]:
        """
        Get list of all available categories in demo data.
        
        Returns:
            List of unique category names
        """
        categories = set()
        for event in self.events:
            if event.category:
                categories.add(event.category)
        return sorted(list(categories))


# Global demo provider instance
_demo_provider: Optional[DemoProvider] = None


def get_demo_provider() -> DemoProvider:
    """
    Get or create the global demo provider instance.
    
    Returns:
        DemoProvider instance
    """
    global _demo_provider
    if _demo_provider is None:
        _demo_provider = DemoProvider()
    return _demo_provider


# Made with Bob