"""
Maps Handler for location and geocoding services
Uses Nominatim (OpenStreetMap) - completely free, no API key needed
"""
import requests
from typing import Optional, Dict, Tuple
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MapsHandler:
    """Handles geocoding and location services"""
    
    def __init__(self):
        """Initialize Maps Handler"""
        # Nominatim (OpenStreetMap) - Free geocoding service
        self.geocoding_base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            'User-Agent': 'AI_Trip_Planner/1.0'  # Required by Nominatim
        }
        # Rate limiting: Max 1 request per second
        self.last_request_time = 0
        self.min_request_interval = 1.0
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def geocode(self, location: str) -> Optional[Dict]:
        """
        Get coordinates for a location
        
        Args:
            location: Location string (e.g., "Paris, France")
            
        Returns:
            Dict with lat, lon, and display_name
        """
        try:
            self._rate_limit()
            
            params = {
                'q': location,
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(
                f"{self.geocoding_base_url}/search",
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = data[0]
                    return {
                        'latitude': float(result['lat']),
                        'longitude': float(result['lon']),
                        'display_name': result['display_name']
                    }
            
            logger.warning(f"Geocoding failed for location: {location}")
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding location: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get location details from coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict with address details
        """
        try:
            self._rate_limit()
            
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            
            response = requests.get(
                f"{self.geocoding_base_url}/reverse",
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")
            return None
    
    def get_google_maps_link(
        self, 
        location: str = None, 
        lat: float = None, 
        lon: float = None
    ) -> str:
        """
        Generate Google Maps link
        
        Args:
            location: Location string (used if lat/lon not provided)
            lat: Latitude
            lon: Longitude
            
        Returns:
            Google Maps URL
        """
        if lat and lon:
            # Direct coordinates link
            return f"https://www.google.com/maps?q={lat},{lon}"
        elif location:
            # Search query link
            return f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(location)}"
        else:
            return "https://www.google.com/maps"
    
    def get_place_coordinates(self, place_name: str, city: str, country: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a specific place
        
        Args:
            place_name: Name of the place
            city: City name
            country: Country name
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        location = f"{place_name}, {city}, {country}"
        result = self.geocode(location)
        
        if result:
            return (result['latitude'], result['longitude'])
        
        return None
    
    def search_nearby_places(
        self,
        lat: float,
        lon: float,
        category: str,
        radius: int = 5000
    ) -> Optional[list]:
        """
        Search for places near coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            category: Place category (restaurant, hotel, etc.)
            radius: Search radius in meters
            
        Returns:
            List of places or None
        """
        # Note: For nearby search, we would need a different API
        # Nominatim doesn't support category-based nearby search well
        # For now, returning None - we'll use LLM to generate recommendations
        logger.info("Nearby search not fully implemented with free tier")
        return None


# Global maps instance
_maps_instance = None


def get_maps_handler() -> MapsHandler:
    """
    Get or create maps handler instance
    
    Returns:
        MapsHandler instance
    """
    global _maps_instance
    
    if _maps_instance is None:
        _maps_instance = MapsHandler()
    
    return _maps_instance