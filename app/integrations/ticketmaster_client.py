"""
Ticketmaster API Client for Pulse AI
Handles event search with retry logic and rate limiting.
"""

import logging

import httpx
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.config.settings import settings


logger = logging.getLogger(__name__)


class TicketmasterClient:
    """Client for Ticketmaster Discovery API."""
    
    def __init__(self):
        """Initialize Ticketmaster client with settings."""
        self.api_key = settings.ticketmaster_api_key
        self.base_url = settings.ticketmaster_base_url
        self.timeout = float(settings.ticketmaster_timeout)
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    async def search_events(
        self,
        city: Optional[str] = None,
        country: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for events using Ticketmaster API.
        
        Args:
            city: City name
            country: Country name
            category: Event category (music, sports, arts, etc.)
            keyword: Search keywords
            date_from: Start date for events
            date_to: End date for events
            size: Number of results to return
            
        Returns:
            List of event dictionaries from Ticketmaster API
            
        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        params = {
            "apikey": self.api_key,
            "source": "ticketmaster",
            "size": min(size or settings.ticketmaster_default_size, 10),
            "sort": settings.ticketmaster_default_sort,
        }
        
        # Add optional parameters
        if city:
            params["city"] = city
        
        if country:
            params["countryCode"] = self._get_country_code(country)
        
        if category:
            # Map our categories to Ticketmaster classification IDs
            classification = self._map_category(category)
            if classification:
                params["classificationName"] = classification
        
        if keyword:
            params["keyword"] = keyword
        
        if date_from:
            params["startDateTime"] = self._to_start_utc(date_from)
        
        if date_to:
            params["endDateTime"] = self._to_end_utc(date_to)

        logger.debug(
            "Ticketmaster event search started",
            extra={
                "provider": "ticketmaster",
                "city_present": bool(city),
                "country_present": bool(country),
                "category": category,
                "keyword_present": bool(keyword),
                "size": params["size"],
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/events.json",
                    params=params
                )

                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(
                        "Ticketmaster rate limit hit",
                        extra={"provider": "ticketmaster", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()

                # Extract events from response
                if "_embedded" in data and "events" in data["_embedded"]:
                    events = data["_embedded"]["events"]
                else:
                    events = []

                logger.info(
                    "Ticketmaster event search succeeded",
                    extra={"provider": "ticketmaster", "event_count": len(events)},
                )
                return events
        except httpx.HTTPStatusError as exc:
            if exc.response is None or exc.response.status_code != 429:
                logger.error(
                    "Ticketmaster event search failed",
                    extra={
                        "provider": "ticketmaster",
                        "status_code": exc.response.status_code if exc.response else None,
                        "error_type": type(exc).__name__,
                    },
                )
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "Ticketmaster event search failed",
                extra={"provider": "ticketmaster", "error_type": type(exc).__name__},
            )
            raise
        except Exception as exc:
            logger.error(
                "Ticketmaster event search failed",
                extra={"provider": "ticketmaster", "error_type": type(exc).__name__},
            )
            raise
    
    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific event.
        
        Args:
            event_id: Ticketmaster event ID
            
        Returns:
            Event dictionary or None if not found
        """
        params = {"apikey": self.api_key}

        logger.debug(
            "Ticketmaster event detail lookup started",
            extra={"provider": "ticketmaster", "event_id_present": bool(event_id)},
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/events/{event_id}.json",
                    params=params
                )

                if response.status_code == 429:
                    logger.warning(
                        "Ticketmaster rate limit hit",
                        extra={"provider": "ticketmaster", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                event = response.json()
                logger.info(
                    "Ticketmaster event detail lookup succeeded",
                    extra={"provider": "ticketmaster", "event_found": True},
                )
                return event
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    logger.info(
                        "Ticketmaster event detail lookup returned no result",
                        extra={"provider": "ticketmaster", "event_found": False},
                    )
                    return None
                if exc.response.status_code != 429:
                    logger.error(
                        "Ticketmaster event detail lookup failed",
                        extra={
                            "provider": "ticketmaster",
                            "status_code": exc.response.status_code,
                            "error_type": type(exc).__name__,
                        },
                    )
                raise
            except httpx.HTTPError as exc:
                logger.error(
                    "Ticketmaster event detail lookup failed",
                    extra={"provider": "ticketmaster", "error_type": type(exc).__name__},
                )
                raise
            except Exception as exc:
                logger.error(
                    "Ticketmaster event detail lookup failed",
                    extra={"provider": "ticketmaster", "error_type": type(exc).__name__},
                )
                raise
    
    def _map_category(self, category: str) -> Optional[str]:
        """Map our internal categories to Ticketmaster classifications."""
        category_map = {
            "music": "Music",
            "sports": "Sports",
            "arts": "Arts & Theatre",
            "theater": "Arts & Theatre",
            "theatre": "Arts & Theatre",
            "family": "Family",
            "film": "Film",
            "miscellaneous": "Miscellaneous"
        }
        return category_map.get(category.lower())
    
    def _get_country_code(self, country: str) -> str:
        """Convert country name to ISO country code."""
        country_codes = {
            "united states": "US",
            "usa": "US",
            "us": "US",
            "canada": "CA",
            "united kingdom": "GB",
            "uk": "GB",
            "germany": "DE",
            "france": "FR",
            "spain": "ES",
            "italy": "IT",
            "netherlands": "NL",
            "belgium": "BE",
            "australia": "AU",
            "new zealand": "NZ",
            "mexico": "MX",
        }
        return country_codes.get(country.lower(), "US")

    def _to_start_utc(self, value: date | datetime) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"{value.isoformat()}T00:00:00Z"

    def _to_end_utc(self, value: date | datetime) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"{value.isoformat()}T23:59:59Z"


# Made with Bob
