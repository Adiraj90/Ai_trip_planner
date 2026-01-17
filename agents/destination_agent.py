"""
Destination Agent - Researches and provides destination information
"""
import streamlit as st
from utils.llm_handler import get_llm
from utils.maps_handler import get_maps_handler
from utils.image_service import get_image_service
from config.database import get_db
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DestinationAgent:
    """Agent for researching destinations"""
    
    def __init__(self):
        self.llm = get_llm()
        self.maps = get_maps_handler()
        self.db = get_db()
    
    def get_destination_info(self, city: str, country: str, use_cache: bool = True) -> dict:
        """
        Get comprehensive destination information
        
        Args:
            city: City name
            country: Country name
            use_cache: Whether to use cached data
            
        Returns:
            Dictionary with destination info
        """
        # Check cache first
        if use_cache:
            cached_info = self._get_from_cache(city, country)
            if cached_info:
                logger.info(f"Using cached data for {city}, {country}")
                return cached_info
        
        # Generate new information
        logger.info(f"Generating new data for {city}, {country}")
        
        # Get coordinates
        location_data = self.maps.geocode(f"{city}, {country}")
        
        # Generate destination info using LLM
        dest_info = self.llm.generate_destination_info(city, country)
        
        if not dest_info:
            return None
        
        # Get image URLs using image service
        image_service = get_image_service()
        images = image_service.get_city_images(city, country, count=4)
        # Ensure we have at least 4 images
        if len(images) < 4:
            # Fill with fallback if needed
            fallback_images = self._get_city_images(city, country, count=4)
            images = images + fallback_images[:4-len(images)]
        
        # Prepare complete info
        complete_info = {
            'city': city,
            'country': country,
            'description': dest_info.get('description', ''),
            'popular_places': dest_info.get('popular_places', []),
            'culture': dest_info.get('culture', ''),
            'local_language': dest_info.get('local_language', ''),
            'famous_foods': dest_info.get('famous_foods', []),
            'best_time_to_visit': dest_info.get('best_time_to_visit', ''),
            'local_tips': dest_info.get('local_tips', ''),
            'images': images,
            'coordinates': {
                'latitude': location_data['latitude'] if location_data else None,
                'longitude': location_data['longitude'] if location_data else None
            }
        }
        
        # Add place coordinates
        complete_info['popular_places'] = self._add_place_coordinates(
            complete_info['popular_places'], 
            city, 
            country
        )
        
        # Cache the information
        self._save_to_cache(complete_info)
        
        return complete_info
    
    def _get_from_cache(self, city: str, country: str) -> dict:
        """Get destination info from cache"""
        try:
            query = """
                SELECT * FROM destinations_cache 
                WHERE city = %s AND country = %s
                ORDER BY updated_at DESC
                LIMIT 1
            """
            result = self.db.execute_query(query, (city, country))
            
            if result:
                data = result[0]
                return {
                    'city': data['city'],
                    'country': data['country'],
                    'description': data['description'],
                    'popular_places': json.loads(data['popular_places']) if data['popular_places'] else [],
                    'culture': data['culture_info'],
                    'local_language': data['local_language'],
                    'famous_foods': json.loads(data['famous_foods']) if data['famous_foods'] else [],
                    'images': json.loads(data['images_json']) if data['images_json'] else [],
                    'best_time_to_visit': '',
                    'local_tips': '',
                    'coordinates': {'latitude': None, 'longitude': None}
                }
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
        
        return None
    
    def _save_to_cache(self, info: dict):
        """Save destination info to cache"""
        try:
            query = """
                INSERT INTO destinations_cache 
                (city, country, description, popular_places, culture_info, 
                 local_language, famous_foods, images_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                description = VALUES(description),
                popular_places = VALUES(popular_places),
                culture_info = VALUES(culture_info),
                local_language = VALUES(local_language),
                famous_foods = VALUES(famous_foods),
                images_json = VALUES(images_json),
                updated_at = CURRENT_TIMESTAMP
            """
            
            self.db.execute_query(
                query,
                (
                    info['city'],
                    info['country'],
                    info['description'],
                    json.dumps(info['popular_places']),
                    info['culture'],
                    info['local_language'],
                    json.dumps(info['famous_foods']),
                    json.dumps(info['images'])
                ),
                fetch=False
            )
            
            logger.info(f"Cached data for {info['city']}, {info['country']}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def _get_city_images(self, city: str, country: str, count: int = 4) -> list:
        """
        Get placeholder images for the city
        Using Unsplash Source API for free, high-quality images
        """
        images = []
        # Using Unsplash Source for random city images
        search_query = f"{city}+{country}+landmark"
        
        for i in range(count):
            # Unsplash Source provides free random images
            img_url = f"https://source.unsplash.com/800x600/?{search_query}&sig={i}"
            images.append(img_url)
        
        return images
    
    def _add_place_coordinates(self, places: list, city: str, country: str) -> list:
        """Add coordinates and map links to places"""
        updated_places = []
        
        for place in places:
            place_name = place.get('name', '')
            
            # Get coordinates
            coords = self.maps.get_place_coordinates(place_name, city, country)
            
            if coords:
                place['latitude'] = coords[0]
                place['longitude'] = coords[1]
                place['maps_link'] = self.maps.get_google_maps_link(
                    lat=coords[0], 
                    lon=coords[1]
                )
            else:
                # Fallback: use city-level link
                place['latitude'] = None
                place['longitude'] = None
                place['maps_link'] = self.maps.get_google_maps_link(
                    location=f"{place_name}, {city}, {country}"
                )
            
            updated_places.append(place)
        
        return updated_places


# Global agent instance
_destination_agent = None


def get_destination_agent() -> DestinationAgent:
    """Get or create destination agent instance"""
    global _destination_agent
    
    if _destination_agent is None:
        _destination_agent = DestinationAgent()
    
    return _destination_agent