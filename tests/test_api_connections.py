"""
API Connection Tests - CRITICAL: Run these first before implementation
Tests all external API connections to verify credentials and connectivity.

Run with: pytest tests/test_api_connections.py -v
"""

import os
import pytest
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

pytestmark = pytest.mark.live_api


class TestWatsonxAIConnection:
    """Test watsonx.ai LLM API connection"""
    
    def test_watsonx_credentials_exist(self):
        """Verify watsonx.ai credentials are in .env"""
        assert os.getenv("WATSONX_API_KEY"), "WATSONX_API_KEY not found in .env"
        assert os.getenv("WATSONX_PROJECT_ID"), "WATSONX_PROJECT_ID not found in .env"
        assert os.getenv("WATSONX_URL"), "WATSONX_URL not found in .env"
        print("\n✓ watsonx.ai credentials found in .env")
    
    @pytest.mark.asyncio
    async def test_watsonx_connection(self):
        """Test actual connection to watsonx.ai"""
        try:
            from langchain_ibm import WatsonxLLM
            
            # Initialize WatsonxLLM with a supported instruct model (not restricted)
            # Note: granite-8b-code-instruct is deprecated but still functional
            llm = WatsonxLLM(
                model_id="ibm/granite-8b-code-instruct",  # Use supported IBM instruct model
                url=os.getenv("WATSONX_URL"),
                apikey=os.getenv("WATSONX_API_KEY"),
                project_id=os.getenv("WATSONX_PROJECT_ID"),
                params={
                    "max_new_tokens": 100,
                    "temperature": 0.1,
                }
            )
            
            # Test simple prompt
            response = llm.invoke("Say hello")
            
            assert response, "No response from watsonx.ai"
            assert len(response) > 0, "Empty response from watsonx.ai"
            
            print(f"\n✓ watsonx.ai connection successful")
            print(f"  Response: {response[:100]}...")
            
        except ImportError as e:
            pytest.skip(f"langchain-ibm not installed: {e}")
        except Exception as e:
            pytest.fail(f"watsonx.ai connection failed: {e}")


class TestTicketmasterAPI:
    """Test Ticketmaster API connection"""
    
    def test_ticketmaster_credentials_exist(self):
        """Verify Ticketmaster API key is in .env"""
        api_key = os.getenv("TICKETMASTER_API_KEY")
        assert api_key, "TICKETMASTER_API_KEY not found in .env"
        print(f"\n✓ Ticketmaster API key found: {api_key[:10]}...")
    
    @pytest.mark.asyncio
    async def test_ticketmaster_search_events(self):
        """Test Ticketmaster event search endpoint"""
        api_key = os.getenv("TICKETMASTER_API_KEY")
        base_url = os.getenv("TICKETMASTER_BASE_URL", "https://app.ticketmaster.com/discovery/v2")
        
        if not api_key:
            pytest.skip("TICKETMASTER_API_KEY not configured")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{base_url}/events.json",
                    params={
                        "apikey": api_key,
                        "city": "New York",
                        "size": 5
                    }
                )
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                
                data = response.json()
                assert "_embedded" in data, "No _embedded field in response"
                assert "events" in data["_embedded"], "No events field in response"
                
                events = data["_embedded"]["events"]
                print(f"\n✓ Ticketmaster API connection successful")
                print(f"  Found {len(events)} events in New York")
                
                if events:
                    print(f"  Sample event: {events[0].get('name', 'N/A')}")
                
            except httpx.TimeoutException:
                pytest.fail("Ticketmaster API request timed out")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    pytest.fail("Ticketmaster API authentication failed - check API key")
                elif e.response.status_code == 429:
                    pytest.fail("Ticketmaster API rate limit exceeded")
                else:
                    pytest.fail(f"Ticketmaster API error: {e}")
            except Exception as e:
                pytest.fail(f"Ticketmaster API connection failed: {e}")


class TestGeoapifyAPI:
    """Test Geoapify API connection"""
    
    def test_geoapify_credentials_exist(self):
        """Verify Geoapify API key is in .env"""
        api_key = os.getenv("GEOAPIFY_API_KEY")
        assert api_key, "GEOAPIFY_API_KEY not found in .env"
        print(f"\n✓ Geoapify API key found: {api_key[:10]}...")
    
    @pytest.mark.asyncio
    async def test_geoapify_places_search(self):
        """Test Geoapify places search endpoint"""
        api_key = os.getenv("GEOAPIFY_API_KEY")
        base_url = os.getenv("GEOAPIFY_BASE_URL", "https://api.geoapify.com/v2")
        
        if not api_key:
            pytest.skip("GEOAPIFY_API_KEY not configured")
        
        # Test coordinates: New York City
        lat, lon = 40.7128, -74.0060
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{base_url}/places",
                    params={
                        "apiKey": api_key,
                        "categories": "entertainment.culture",
                        "filter": f"circle:{lon},{lat},5000",
                        "limit": 5
                    }
                )
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                
                data = response.json()
                assert "features" in data, "No features field in response"
                
                places = data["features"]
                print(f"\n✓ Geoapify API connection successful")
                print(f"  Found {len(places)} places near NYC")
                
                if places:
                    place_name = places[0].get("properties", {}).get("name", "N/A")
                    print(f"  Sample place: {place_name}")
                
            except httpx.TimeoutException:
                pytest.fail("Geoapify API request timed out")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401 or e.response.status_code == 403:
                    pytest.fail("Geoapify API authentication failed - check API key")
                elif e.response.status_code == 429:
                    pytest.fail("Geoapify API rate limit exceeded")
                else:
                    pytest.fail(f"Geoapify API error: {e}")
            except Exception as e:
                pytest.fail(f"Geoapify API connection failed: {e}")


class TestOpenWeatherAPI:
    """Test OpenWeather API connection"""
    
    def test_openweather_credentials_exist(self):
        """Verify OpenWeather API key is in .env"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        assert api_key, "OPENWEATHER_API_KEY not found in .env"
        print(f"\n✓ OpenWeather API key found: {api_key[:10]}...")
    
    @pytest.mark.asyncio
    async def test_openweather_current_weather(self):
        """Test OpenWeather current weather endpoint"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        base_url = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
        
        if not api_key:
            pytest.skip("OPENWEATHER_API_KEY not configured")
        
        # Test coordinates: New York City
        lat, lon = 40.7128, -74.0060
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{base_url}/weather",
                    params={
                        "appid": api_key,
                        "lat": lat,
                        "lon": lon,
                        "units": "metric"
                    }
                )
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"
                
                data = response.json()
                assert "weather" in data, "No weather field in response"
                assert "main" in data, "No main field in response"
                
                temp = data["main"].get("temp")
                weather_desc = data["weather"][0].get("description", "N/A")
                
                print(f"\n✓ OpenWeather API connection successful")
                print(f"  NYC Weather: {weather_desc}, {temp}°C")
                
            except httpx.TimeoutException:
                pytest.fail("OpenWeather API request timed out")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    pytest.fail("OpenWeather API authentication failed - check API key")
                elif e.response.status_code == 429:
                    pytest.fail("OpenWeather API rate limit exceeded")
                else:
                    pytest.fail(f"OpenWeather API error: {e}")
            except Exception as e:
                pytest.fail(f"OpenWeather API connection failed: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("API CONNECTION TESTS - Run before Phase 3 implementation")
    print("="*70)
    pytest.main([__file__, "-v", "-s"])

# Made with Bob
