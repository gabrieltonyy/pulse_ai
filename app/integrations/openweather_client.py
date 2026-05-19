"""
OpenWeather API Client for Pulse AI
Handles weather data retrieval.
"""

import logging

import httpx
from typing import Optional, Dict, Any
from datetime import date, datetime
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.config.settings import settings


logger = logging.getLogger(__name__)


class OpenWeatherClient:
    """Client for OpenWeather API."""
    
    def __init__(self):
        """Initialize OpenWeather client with settings."""
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
        self.timeout = float(settings.openweather_timeout)
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    async def get_weather(
        self,
        lat: float,
        lon: float,
        event_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get weather data for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            event_date: Optional date for forecast (if in future)
            
        Returns:
            Weather data dictionary or None if unavailable
            
        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        # Determine if we need current weather or forecast
        today = datetime.now().date()
        
        if event_date and event_date > today:
            # Use forecast API for future dates (up to 5 days)
            days_ahead = (event_date - today).days
            if days_ahead <= settings.weather_forecast_horizon_days:
                return await self._get_forecast(lat, lon, event_date)
            logger.info(
                "OpenWeather forecast skipped; event date outside supported horizon",
                extra={"provider": "openweather", "days_ahead": days_ahead},
            )
            return None
        
        # Use current weather API
        return await self._get_current_weather(lat, lon)
    
    async def _get_current_weather(
        self,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """Get current weather for a location."""
        params = {
            "appid": self.api_key,
            "lat": lat,
            "lon": lon,
            "units": settings.openweather_units,
            "lang": settings.openweather_lang
        }

        logger.debug(
            "OpenWeather current weather lookup started",
            extra={"provider": "openweather"},
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params=params
                )

                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(
                        "OpenWeather rate limit hit",
                        extra={"provider": "openweather", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()
                logger.info(
                    "OpenWeather current weather lookup succeeded",
                    extra={"provider": "openweather", "weather_available": True},
                )
                return data
        except httpx.HTTPStatusError as exc:
            if exc.response is None or exc.response.status_code != 429:
                logger.error(
                    "OpenWeather current weather lookup failed",
                    extra={
                        "provider": "openweather",
                        "status_code": exc.response.status_code if exc.response else None,
                        "error_type": type(exc).__name__,
                    },
                )
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "OpenWeather current weather lookup failed",
                extra={"provider": "openweather", "error_type": type(exc).__name__},
            )
            raise
        except Exception as exc:
            logger.error(
                "OpenWeather current weather lookup failed",
                extra={"provider": "openweather", "error_type": type(exc).__name__},
            )
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True
    )
    async def get_forecast(
        self,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """
        Get 5-day weather forecast for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Forecast data dictionary
        """
        return await self._get_forecast(lat, lon)
    
    async def _get_forecast(
        self,
        lat: float,
        lon: float,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get forecast data, optionally filtered to a specific date."""
        params = {
            "appid": self.api_key,
            "lat": lat,
            "lon": lon,
            "units": settings.openweather_units,
            "lang": settings.openweather_lang
        }

        logger.debug(
            "OpenWeather forecast lookup started",
            extra={"provider": "openweather", "target_date_present": bool(target_date)},
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params=params
                )

                if response.status_code == 429:
                    logger.warning(
                        "OpenWeather rate limit hit",
                        extra={"provider": "openweather", "status_code": response.status_code},
                    )
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()

                # If target date specified, filter to closest forecast
                if target_date and "list" in data:
                    target_datetime = datetime.combine(target_date, datetime.min.time())
                    closest_forecast = None
                    min_diff = float('inf')

                    for forecast in data["list"]:
                        forecast_dt = datetime.fromtimestamp(forecast["dt"])
                        diff = abs((forecast_dt - target_datetime).total_seconds())

                        if diff < min_diff:
                            min_diff = diff
                            closest_forecast = forecast

                    if closest_forecast:
                        logger.info(
                            "OpenWeather forecast lookup succeeded",
                            extra={"provider": "openweather", "forecast_count": 1},
                        )
                        # Return forecast in same format as current weather
                        return {
                            "weather": closest_forecast.get("weather", []),
                            "main": closest_forecast.get("main", {}),
                            "wind": closest_forecast.get("wind", {}),
                            "clouds": closest_forecast.get("clouds", {}),
                            "dt": closest_forecast.get("dt"),
                            "dt_txt": closest_forecast.get("dt_txt")
                        }

                forecast_count = len(data.get("list", [])) if isinstance(data.get("list"), list) else 0
                logger.info(
                    "OpenWeather forecast lookup succeeded",
                    extra={"provider": "openweather", "forecast_count": forecast_count},
                )
                return data
        except httpx.HTTPStatusError as exc:
            if exc.response is None or exc.response.status_code != 429:
                logger.error(
                    "OpenWeather forecast lookup failed",
                    extra={
                        "provider": "openweather",
                        "status_code": exc.response.status_code if exc.response else None,
                        "error_type": type(exc).__name__,
                    },
                )
            raise
        except httpx.HTTPError as exc:
            logger.error(
                "OpenWeather forecast lookup failed",
                extra={"provider": "openweather", "error_type": type(exc).__name__},
            )
            raise
        except Exception as exc:
            logger.error(
                "OpenWeather forecast lookup failed",
                extra={"provider": "openweather", "error_type": type(exc).__name__},
            )
            raise
    
    def is_outdoor_friendly(self, weather_data: Dict[str, Any]) -> bool:
        """
        Determine if weather is suitable for outdoor events.
        
        Args:
            weather_data: Weather data from API
            
        Returns:
            True if weather is outdoor-friendly
        """
        if not weather_data or "weather" not in weather_data:
            return True  # Assume OK if no data
        
        # Check weather conditions
        weather_conditions = weather_data.get("weather", [])
        if weather_conditions:
            main_condition = weather_conditions[0].get("main", "").lower()
            
            # Bad conditions for outdoor events
            bad_conditions = ["rain", "snow", "thunderstorm", "drizzle"]
            if main_condition in bad_conditions:
                return False
        
        # Check temperature (if available)
        main_data = weather_data.get("main", {})
        temp = main_data.get("temp")
        
        if temp is not None:
            # Uncomfortable temperatures (in Celsius)
            if temp < 5 or temp > 35:
                return False
        
        # Check wind speed
        wind_data = weather_data.get("wind", {})
        wind_speed = wind_data.get("speed")
        
        if wind_speed is not None and wind_speed > 10:  # m/s
            return False
        
        return True


# Made with Bob
