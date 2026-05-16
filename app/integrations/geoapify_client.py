"""
Geoapify API Client for Pulse AI
Handles location and places search.
"""

import httpx
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config.settings import settings


class GeoapifyClient:
    """Client for Geoapify Places API."""
    
    def __init__(self):
        """Initialize Geoapify client with settings."""
        self.api_key = settings.geoapify_api_key
        self.base_url = settings.geoapify_base_url
        self.timeout = 10.0
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
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
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/places",
                params=params
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=response.request,
                    response=response
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract features (places) from response
            return data.get("features", [])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
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
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(geocode_url, params=params)
            
            if response.status_code == 429:
                raise httpx.HTTPStatusError(
                    "Rate limit exceeded",
                    request=response.request,
                    response=response
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract first result
            features = data.get("features", [])
            if features:
                return features[0]
            
            return None
    
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