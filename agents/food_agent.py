"""
Food Agent - Finds and recommends restaurants
"""
import streamlit as st
from utils.llm_handler import get_llm
from utils.maps_handler import get_maps_handler
from config.database import get_db
import json
import logging

logger = logging.getLogger(__name__)


class FoodAgent:
    """Agent for finding restaurants"""
    
    def __init__(self):
        self.llm = get_llm()
        self.maps = get_maps_handler()
        self.db = get_db()
    
    def find_restaurants(
        self,
        city: str,
        country: str,
        food_type: str = "Mixed",
        cuisine_type: str = None,
        price_range: str = "Medium",
        num_results: int = 10
    ) -> list:
        """
        Find restaurants in a city
        
        Args:
            city: City name
            country: Country name
            food_type: Veg/Non-Veg/Vegan/etc
            cuisine_type: Italian/Chinese/Local/etc
            price_range: Budget/Medium/Expensive
            num_results: Number of restaurants to return
            
        Returns:
            List of restaurant dictionaries
        """
        logger.info(f"Finding restaurants in {city}, {country}")
        
        # Create prompt for LLM
        prompt = self._create_restaurant_search_prompt(
            city, country, food_type, cuisine_type, price_range, num_results
        )
        
        # Get restaurants from LLM
        restaurants_data = self.llm.generate_json_response(
            prompt=prompt,
            system_message="You are a food and restaurant expert. Return ONLY valid JSON with no additional text."
        )
        
        if not restaurants_data or 'restaurants' not in restaurants_data:
            logger.error("Failed to get restaurants from LLM")
            return []
        
        restaurants = restaurants_data['restaurants']
        
        # Add map links and coordinates
        restaurants = self._add_location_data(restaurants, city, country)
        
        # Save to database
        self._save_restaurants_to_db(restaurants, city, country)
        
        return restaurants
    
    def _create_restaurant_search_prompt(
        self,
        city: str,
        country: str,
        food_type: str,
        cuisine_type: str,
        price_range: str,
        num_results: int
    ) -> str:
        """Create prompt for restaurant search"""
        
        cuisine_str = cuisine_type if cuisine_type else "various cuisines"
        
        prompt = f"""
Find {num_results} real restaurants in {city}, {country}.

REQUIREMENTS:
- Food Type: {food_type} (Vegetarian/Non-Vegetarian/Vegan/etc)
- Cuisine: {cuisine_str}
- Price Range: {price_range} ({self._get_price_range_description(price_range)})
- Use REAL restaurant names that exist in {city}
- Include local/traditional restaurants of {country}

Return ONLY valid JSON with this EXACT structure:

{{
    "restaurants": [
        {{
            "name": "Restaurant Name",
            "description": "2-3 sentence description of the restaurant and its specialty",
            "location": "Specific area/neighborhood in the city",
            "cuisine_type": "Italian/Chinese/Local/etc",
            "food_type": "Vegetarian/Non-Vegetarian/Vegan/Mixed",
            "price_range": "Budget/Medium/Expensive",
            "rating": 4.5,
            "popular_dishes": ["Dish 1", "Dish 2", "Dish 3"],
            "opening_hours": "08:00 AM",
            "closing_hours": "10:00 PM",
            "image_url": "https://source.unsplash.com/800x600/?restaurant,food,{cuisine_str.replace(' ', '-')}"
        }}
    ]
}}

IMPORTANT:
1. Include exactly {num_results} restaurants
2. Mix of different cuisine types
3. Ratings between 3.5 and 5.0
4. Each restaurant should have 3-5 popular dishes
5. Make descriptions appetizing and unique
6. Include traditional/local restaurants of {country}
7. Include realistic opening_hours and closing_hours (e.g., "09:00 AM" to "11:00 PM")
8. Opening/closing hours should reflect typical restaurant hours in {city}, {country}
9. Return ONLY the JSON, no other text
"""
        
        return prompt
    
    def _get_price_range_description(self, price_range: str) -> str:
        """Get price range description"""
        ranges = {
            "Budget": "$5-$15 per person",
            "Medium": "$15-$40 per person",
            "Expensive": "$40+ per person"
        }
        return ranges.get(price_range, "$15-$40 per person")
    
    def _add_location_data(self, restaurants: list, city: str, country: str) -> list:
        """Add coordinates and map links to restaurants"""
        updated_restaurants = []
        
        for restaurant in restaurants:
            restaurant_name = restaurant.get('name', '')
            location = restaurant.get('location', '')
            
            # Try to get coordinates
            search_query = f"{restaurant_name}, {location}, {city}, {country}"
            coords = self.maps.geocode(search_query)
            
            if coords:
                restaurant['latitude'] = coords['latitude']
                restaurant['longitude'] = coords['longitude']
                restaurant['maps_link'] = self.maps.get_google_maps_link(
                    lat=coords['latitude'],
                    lon=coords['longitude']
                )
            else:
                # Fallback to city-level location
                restaurant['latitude'] = None
                restaurant['longitude'] = None
                restaurant['maps_link'] = self.maps.get_google_maps_link(
                    location=f"{restaurant_name}, {city}, {country}"
                )
            
            updated_restaurants.append(restaurant)
        
        return updated_restaurants
    
    def _save_restaurants_to_db(self, restaurants: list, city: str, country: str):
        """Save restaurants to database"""
        try:
            for restaurant in restaurants:
                # Check if restaurant already exists
                check_query = """
                    SELECT restaurant_id FROM restaurants 
                    WHERE name = %s AND city = %s AND country = %s
                """
                existing = self.db.execute_query(
                    check_query,
                    (restaurant['name'], city, country)
                )
                
                if existing:
                    continue  # Skip if already exists
                
                # Insert new restaurant
                insert_query = """
                    INSERT INTO restaurants 
                    (name, description, location, city, country, cuisine_type,
                     food_type, price_range, rating, image_url, popular_dishes,
                     latitude, longitude, maps_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                self.db.execute_query(
                    insert_query,
                    (
                        restaurant.get('name'),
                        restaurant.get('description'),
                        restaurant.get('location'),
                        city,
                        country,
                        restaurant.get('cuisine_type'),
                        restaurant.get('food_type'),
                        restaurant.get('price_range'),
                        restaurant.get('rating'),
                        restaurant.get('image_url'),
                        json.dumps(restaurant.get('popular_dishes', [])),
                        restaurant.get('latitude'),
                        restaurant.get('longitude'),
                        restaurant.get('maps_link')
                    ),
                    fetch=False
                )
            
            logger.info(f"Saved {len(restaurants)} restaurants to database")
            
        except Exception as e:
            logger.error(f"Error saving restaurants to database: {e}")
    
    def get_restaurants_from_db(
        self,
        city: str,
        country: str,
        food_type: str = None,
        cuisine_type: str = None,
        price_range: str = None,
        rating_min: float = None,
        sort_by: str = "rating_desc"
    ) -> list:
        """Get restaurants from database with filters"""
        try:
            query = "SELECT * FROM restaurants WHERE city = %s AND country = %s"
            params = [city, country]
            
            # Apply filters
            if food_type and food_type != "All":
                query += " AND food_type = %s"
                params.append(food_type)
            
            if cuisine_type and cuisine_type != "All":
                query += " AND cuisine_type LIKE %s"
                params.append(f"%{cuisine_type}%")
            
            if price_range and price_range != "All":
                query += " AND price_range = %s"
                params.append(price_range)
            
            if rating_min is not None:
                query += " AND rating >= %s"
                params.append(rating_min)
            
            # Apply sorting
            if sort_by == "rating_desc":
                query += " ORDER BY rating DESC"
            elif sort_by == "rating_asc":
                query += " ORDER BY rating ASC"
            elif sort_by == "price_low":
                query += " ORDER BY FIELD(price_range, 'Budget', 'Medium', 'Expensive')"
            elif sort_by == "price_high":
                query += " ORDER BY FIELD(price_range, 'Expensive', 'Medium', 'Budget')"
            
            results = self.db.execute_query(query, tuple(params))
            
            # Parse popular_dishes JSON
            for restaurant in results:
                if restaurant.get('popular_dishes'):
                    try:
                        restaurant['popular_dishes'] = json.loads(restaurant['popular_dishes'])
                    except:
                        restaurant['popular_dishes'] = []
            
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error getting restaurants from database: {e}")
            return []


# Global agent instance
_food_agent = None


def get_food_agent() -> FoodAgent:
    """Get or create food agent instance"""
    global _food_agent
    
    if _food_agent is None:
        _food_agent = FoodAgent()
    
    return _food_agent