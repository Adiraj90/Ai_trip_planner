"""
Hotel Agent - Finds and recommends hotels
"""
import streamlit as st
from utils.llm_handler import get_llm
from utils.maps_handler import get_maps_handler
from config.database import get_db
import json
import logging

logger = logging.getLogger(__name__)


class HotelAgent:
    """Agent for finding hotels"""
    
    def __init__(self):
        self.llm = get_llm()
        self.maps = get_maps_handler()
        self.db = get_db()
    
    def find_hotels(
        self,
        city: str,
        country: str,
        room_type: str = None,
        amenities: list = None,
        price_range: str = "Medium",
        num_results: int = 10
    ) -> list:
        """
        Find hotels in a city
        
        Args:
            city: City name
            country: Country name
            room_type: Single/Double/Suite/etc
            amenities: List of required amenities
            price_range: Budget/Medium/Luxury
            num_results: Number of hotels to return
            
        Returns:
            List of hotel dictionaries
        """
        logger.info(f"Finding hotels in {city}, {country}")
        
        # Create prompt for LLM
        prompt = self._create_hotel_search_prompt(
            city, country, room_type, amenities, price_range, num_results
        )
        
        # Get hotels from LLM
        hotels_data = self.llm.generate_json_response(
            prompt=prompt,
            system_message="You are a hotel recommendation expert. Return ONLY valid JSON with no additional text."
        )
        
        if not hotels_data or 'hotels' not in hotels_data:
            logger.error("Failed to get hotels from LLM")
            return []
        
        hotels = hotels_data['hotels']
        
        # Add map links and coordinates
        hotels = self._add_location_data(hotels, city, country)
        
        # Save to database
        self._save_hotels_to_db(hotels, city, country)
        
        return hotels
    
    def _create_hotel_search_prompt(
        self,
        city: str,
        country: str,
        room_type: str,
        amenities: list,
        price_range: str,
        num_results: int
    ) -> str:
        """Create prompt for hotel search"""
        
        amenities_str = ", ".join(amenities) if amenities else "standard amenities"
        room_str = room_type if room_type else "any room type"
        
        prompt = f"""
Find {num_results} real hotels in {city}, {country}.

REQUIREMENTS:
- Price Range: {price_range} ({self._get_price_range_description(price_range)})
- Room Type: {room_str}
- Amenities: {amenities_str}
- Use REAL hotel names that exist in {city}

Return ONLY valid JSON with this EXACT structure:

{{
    "hotels": [
        {{
            "name": "Hotel Name",
            "description": "2-3 sentence description of the hotel",
            "location": "Specific area/neighborhood in the city",
            "price_per_night": 150.00,
            "rating": 4.5,
            "room_type": "Deluxe Room",
            "amenities": ["WiFi", "Pool", "Restaurant", "Gym", "Spa"],
            "image_url": "https://source.unsplash.com/800x600/?hotel,luxury,{city.replace(' ', '-')}"
        }}
    ]
}}

IMPORTANT:
1. Include exactly {num_results} hotels
2. Use realistic prices for {city}
3. Ratings between 3.5 and 5.0
4. Each hotel should have 4-6 amenities
5. Make descriptions unique and appealing
6. Return ONLY the JSON, no other text
"""
        
        return prompt
    
    def _get_price_range_description(self, price_range: str) -> str:
        """Get price range description"""
        ranges = {
            "Budget": "$50-$100 per night",
            "Medium": "$100-$250 per night",
            "Luxury": "$250+ per night"
        }
        return ranges.get(price_range, "$100-$250 per night")
    
    def _add_location_data(self, hotels: list, city: str, country: str) -> list:
        """Add coordinates and map links to hotels"""
        updated_hotels = []
        
        for hotel in hotels:
            hotel_name = hotel.get('name', '')
            location = hotel.get('location', '')
            
            # Try to get coordinates
            search_query = f"{hotel_name}, {location}, {city}, {country}"
            coords = self.maps.geocode(search_query)
            
            if coords:
                hotel['latitude'] = coords['latitude']
                hotel['longitude'] = coords['longitude']
                hotel['maps_link'] = self.maps.get_google_maps_link(
                    lat=coords['latitude'],
                    lon=coords['longitude']
                )
            else:
                # Fallback to city-level location
                hotel['latitude'] = None
                hotel['longitude'] = None
                hotel['maps_link'] = self.maps.get_google_maps_link(
                    location=f"{hotel_name}, {city}, {country}"
                )
            
            updated_hotels.append(hotel)
        
        return updated_hotels
    
    def _save_hotels_to_db(self, hotels: list, city: str, country: str):
        """Save hotels to database"""
        try:
            for hotel in hotels:
                # Check if hotel already exists
                check_query = """
                    SELECT hotel_id FROM hotels 
                    WHERE name = %s AND city = %s AND country = %s
                """
                existing = self.db.execute_query(
                    check_query,
                    (hotel['name'], city, country)
                )
                
                if existing:
                    continue  # Skip if already exists
                
                # Insert new hotel
                insert_query = """
                    INSERT INTO hotels 
                    (name, description, location, city, country, price_per_night,
                     rating, image_url, amenities, room_type, latitude, longitude, maps_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                self.db.execute_query(
                    insert_query,
                    (
                        hotel.get('name'),
                        hotel.get('description'),
                        hotel.get('location'),
                        city,
                        country,
                        hotel.get('price_per_night'),
                        hotel.get('rating'),
                        hotel.get('image_url'),
                        json.dumps(hotel.get('amenities', [])),
                        hotel.get('room_type'),
                        hotel.get('latitude'),
                        hotel.get('longitude'),
                        hotel.get('maps_link')
                    ),
                    fetch=False
                )
            
            logger.info(f"Saved {len(hotels)} hotels to database")
            
        except Exception as e:
            logger.error(f"Error saving hotels to database: {e}")
    
    def get_hotels_from_db(
        self,
        city: str,
        country: str,
        price_min: float = None,
        price_max: float = None,
        rating_min: float = None,
        room_type: str = None,
        sort_by: str = "rating_desc"
    ) -> list:
        """Get hotels from database with filters"""
        try:
            query = "SELECT * FROM hotels WHERE city = %s AND country = %s"
            params = [city, country]
            
            # Apply filters
            if price_min is not None:
                query += " AND price_per_night >= %s"
                params.append(price_min)
            
            if price_max is not None:
                query += " AND price_per_night <= %s"
                params.append(price_max)
            
            if rating_min is not None:
                query += " AND rating >= %s"
                params.append(rating_min)
            
            if room_type and room_type != "All":
                query += " AND room_type LIKE %s"
                params.append(f"%{room_type}%")
            
            # Apply sorting
            if sort_by == "price_low":
                query += " ORDER BY price_per_night ASC"
            elif sort_by == "price_high":
                query += " ORDER BY price_per_night DESC"
            elif sort_by == "rating_desc":
                query += " ORDER BY rating DESC"
            elif sort_by == "rating_asc":
                query += " ORDER BY rating ASC"
            
            results = self.db.execute_query(query, tuple(params))
            
            # Parse amenities JSON
            for hotel in results:
                if hotel.get('amenities'):
                    try:
                        hotel['amenities'] = json.loads(hotel['amenities'])
                    except:
                        hotel['amenities'] = []
            
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error getting hotels from database: {e}")
            return []


# Global agent instance
_hotel_agent = None


def get_hotel_agent() -> HotelAgent:
    """Get or create hotel agent instance"""
    global _hotel_agent
    
    if _hotel_agent is None:
        _hotel_agent = HotelAgent()
    
    return _hotel_agent