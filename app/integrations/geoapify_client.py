"""
Geoapify API Client for Pulse AI
Handles location and places search.
"""

import logging

import httpx
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.config.settings import settings


logger = logging.getLogger(__name__)


class GeoapifyClient:
    """Client for Geoapify Places API."""
    
    def __init__(self):
        """Initialize Geoapify client with settings."""
        self.api_key = settings.geoapify_api_key
        self.base_url = settings.geoapify_base_url
        self.timeout = float(settings.geoapify_timeout)
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    async def get_nearby_places(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        categories: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get nearby places around a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            categories: Comma-separated category filters
            limit: Maximum number of results
            
        Returns:
            List of place dictionaries
            
        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        params = {
            "apiKey": self.api_key,
            "filter": f"circle:{lon},{lat},{radius}",
            "limit": limit
        }
        
        if categories:
            params["categories"] = categories

        logger.debug(
            "Geoapify nearby places lookup started",
            extra={
                "provider": "geoapify",
                "radius": radius,
                "categories_present": bool(categories),
                "limit": limit,
            },
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/places",
                    params=params
                )

                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(
                        "Geoapify rate limit hit",
                        extra={"provider": "geoapify", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()

                # Extract features (places) from response
                places = data.get("features", [])
                logger.info(
                    "Geoapify nearby places lookup succeeded",
                    extra={"provider": "geoapify", "place_count": len(places)},
                )
                return places
        except httpx.HTTPStatusError as exc:
            if exc.response is None or exc.response.status_code != 429:
                logger.error(
                    "Geoapify nearby places lookup failed",
                    extra={
                        "provider": "geoapify",
                        "status_code": exc.response.status_code if exc.response else None,
                        "error_type": type(exc).__name__,
                    },
                )
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "Geoapify nearby places lookup failed",
                extra={"provider": "geoapify", "error_type": type(exc).__name__},
            )
            raise
        except Exception as exc:
            logger.error(
                "Geoapify nearby places lookup failed",
                extra={"provider": "geoapify", "error_type": type(exc).__name__},
            )
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    async def geocode_city(
        self,
        city: str,
        country: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Geocode a city name to get coordinates.
        
        Args:
            city: City name
            country: Optional country name for disambiguation
            
        Returns:
            Geocoding result with coordinates or None if not found
        """
        # Use Geoapify geocoding API
        geocode_url = "https://api.geoapify.com/v1/geocode/search"
        
        query = city
        if country:
            query = f"{city}, {country}"
        
        params = {
            "apiKey": self.api_key,
            "text": query,
            "limit": 1,
            "type": "city"
        }

        logger.debug(
            "Geoapify city geocode started",
            extra={"provider": "geoapify", "country_present": bool(country)},
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(geocode_url, params=params)

                if response.status_code == 429:
                    logger.warning(
                        "Geoapify rate limit hit",
                        extra={"provider": "geoapify", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()

                # Extract first result
                features = data.get("features", [])
                logger.info(
                    "Geoapify city geocode succeeded",
                    extra={"provider": "geoapify", "result_count": len(features)},
                )
                if features:
                    return features[0]

                return None
        except httpx.HTTPStatusError as exc:
            if exc.response is None or exc.response.status_code != 429:
                logger.error(
                    "Geoapify city geocode failed",
                    extra={
                        "provider": "geoapify",
                        "status_code": exc.response.status_code if exc.response else None,
                        "error_type": type(exc).__name__,
                    },
                )
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "Geoapify city geocode failed",
                extra={"provider": "geoapify", "error_type": type(exc).__name__},
            )
            raise
        except Exception as exc:
            logger.error(
                "Geoapify city geocode failed",
                extra={"provider": "geoapify", "error_type": type(exc).__name__},
            )
            raise
    
    def get_place_categories(self, place_type: str) -> str:
        """
        Map event categories to Geoapify place categories.
        
        Args:
            place_type: Event category type
            
        Returns:
            Comma-separated Geoapify categories
        """
        category_map = {
            "music": "entertainment.culture,entertainment.music",
            "sports": "sport,sport.stadium",
            "arts": "entertainment.culture,entertainment.museum",
            "theater": "entertainment.culture",
            "family": "entertainment,leisure.park",
            "food": "catering.restaurant,catering.cafe"
        }
        return category_map.get(place_type.lower(), "entertainment")


# Made with Bob
