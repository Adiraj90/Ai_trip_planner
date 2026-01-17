"""
Image Service - Fetch images from free APIs (Pexels, Unsplash)
"""
import streamlit as st
import requests
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class ImageService:
    """Service for fetching images from free APIs"""
    
    def __init__(self):
        """Initialize image service with API keys from secrets"""
        # Pexels API (free, 200 requests/hour, no auth for basic usage)
        # Unsplash API (free, 50 requests/hour, requires API key)
        self.pexels_api_key = st.secrets.get("PEXELS_API_KEY", None)
        self.unsplash_api_key = st.secrets.get("UNSPLASH_API_KEY", None)
        # Fallback to Unsplash Source (no key needed but less reliable)
        self.use_fallback = not (self.pexels_api_key or self.unsplash_api_key)
    
    def get_city_images(self, city: str, country: str, count: int = 4) -> List[str]:
        """
        Get images for a city
        
        Args:
            city: City name
            country: Country name
            count: Number of images to fetch (default 4)
            
        Returns:
            List of image URLs
        """
        query = f"{city} {country}"
        
        # Try Pexels first (best free option)
        if self.pexels_api_key:
            images = self._get_pexels_images(query, count)
            if images:
                return images
        
        # Try Unsplash if available
        if self.unsplash_api_key:
            images = self._get_unsplash_images(query, count)
            if images:
                return images
        
        # Fallback to Unsplash Source (no key needed)
        return self._get_unsplash_source_images(query, count)
    
    def get_place_image(self, place_name: str, city: str = "", country: str = "") -> Optional[str]:
        """
        Get a single image for a place/attraction
        
        Args:
            place_name: Name of the place (e.g., "Taj Mahal")
            city: Optional city name
            country: Optional country name
            
        Returns:
            Image URL or None
        """
        # Build query
        if city and country:
            query = f"{place_name} {city} {country}"
        else:
            query = place_name
        
        # Try Pexels first
        if self.pexels_api_key:
            images = self._get_pexels_images(query, 1)
            if images:
                return images[0]
        
        # Try Unsplash
        if self.unsplash_api_key:
            images = self._get_unsplash_images(query, 1)
            if images:
                return images[0]
        
        # Fallback
        images = self._get_unsplash_source_images(query, 1)
        return images[0] if images else None
    
    def get_hotel_image(self, hotel_name: str, city: str = "") -> Optional[str]:
        """Get image for a hotel"""
        query = f"{hotel_name} hotel {city}" if city else f"{hotel_name} hotel"
        return self.get_place_image(query)
    
    def get_restaurant_image(self, restaurant_name: str, city: str = "") -> Optional[str]:
        """Get image for a restaurant"""
        query = f"{restaurant_name} restaurant {city}" if city else f"{restaurant_name} restaurant"
        return self.get_place_image(query)
    
    def _get_pexels_images(self, query: str, count: int = 4) -> List[str]:
        """
        Fetch images from Pexels API (free, 200 requests/hour)
        Requires API key from https://www.pexels.com/api/
        """
        if not self.pexels_api_key:
            return []
        
        try:
            headers = {"Authorization": self.pexels_api_key}
            url = f"https://api.pexels.com/v1/search"
            params = {
                "query": query,
                "per_page": min(count, 15),  # Max 15 per request
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data.get("photos", [])[:count]:
                    # Get medium size image
                    img_url = photo.get("src", {}).get("medium") or photo.get("src", {}).get("original")
                    if img_url:
                        images.append(img_url)
                return images
            else:
                logger.warning(f"Pexels API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from Pexels: {e}")
            return []
    
    def _get_unsplash_images(self, query: str, count: int = 4) -> List[str]:
        """
        Fetch images from Unsplash API (free, 50 requests/hour)
        Requires API key from https://unsplash.com/developers
        """
        if not self.unsplash_api_key:
            return []
        
        try:
            headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": min(count, 30),
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data.get("results", [])[:count]:
                    # Get regular size image
                    img_url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("full")
                    if img_url:
                        images.append(img_url)
                return images
            else:
                logger.warning(f"Unsplash API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from Unsplash: {e}")
            return []
    
    def _get_unsplash_source_images(self, query: str, count: int = 4) -> List[str]:
        """
        Fallback: Use placeholder images and alternative free image services
        Uses multiple sources for better reliability
        """
        images = []
        search_query = query.replace(" ", "+").replace(",", "").lower()
        
        # Use Picsum Photos (Lorem Picsum) as a reliable fallback
        # It provides high-quality random images
        for i in range(count):
            # Method 1: Picsum Photos (reliable, no API key needed)
            # Using specific IDs for variety
            pic_id = 1000 + (i * 50) + (hash(search_query) % 100)
            img_url = f"https://picsum.photos/id/{pic_id}/800/600"
            images.append(img_url)
        
        return images
    
    def _get_lorem_picsum_images(self, query: str, count: int = 4) -> List[str]:
        """Get images from Lorem Picsum (Picsum Photos) - very reliable"""
        images = []
        # Use hash of query to get consistent but varied images
        seed = abs(hash(query)) % 1000
        
        for i in range(count):
            # Picsum Photos with seed for consistency
            img_url = f"https://picsum.photos/seed/{seed + i}/800/600"
            images.append(img_url)
        
        return images


# Global image service instance
_image_service = None


def get_image_service() -> ImageService:
    """Get or create global image service instance"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
