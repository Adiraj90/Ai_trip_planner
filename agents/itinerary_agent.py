"""
Itinerary Agent - Generates personalized day-by-day trip plans
"""
import streamlit as st
from utils.llm_handler import get_llm
from utils.maps_handler import get_maps_handler
from utils.helpers import calculate_days_between, generate_date_range, format_date_readable
from config.database import get_db
from datetime import date
import json
import logging

logger = logging.getLogger(__name__)


class ItineraryAgent:
    """Agent for generating trip itineraries"""
    
    def __init__(self):
        self.llm = get_llm()
        self.maps = get_maps_handler()
        self.db = get_db()
    
    def generate_itinerary(
        self,
        city: str,
        country: str,
        state: str,
        start_date: date,
        end_date: date,
        budget: float,
        currency: str,
        trip_types: list,
        food_preference: str,
        num_people: int,
        user_id: int = None
    ) -> dict:
        """
        Generate complete trip itinerary
        
        Returns:
            Dictionary with complete itinerary
        """
        # Calculate number of days
        num_days = calculate_days_between(start_date, end_date)
        
        # Convert trip_types list to string
        trip_type_str = ", ".join(trip_types) if isinstance(trip_types, list) else trip_types
        
        logger.info(f"Generating {num_days}-day itinerary for {city}, {state or ''}, {country}")
        
        # Check if this exact trip already exists (unique validation)
        if user_id:
            if self._check_duplicate_trip(user_id, city, state, country, num_days, budget, num_people):
                logger.warning("Duplicate trip detected - will generate but not save")
                st.warning("⚠️ You already have a similar trip saved! This itinerary will be generated but not saved as a duplicate.")
                user_id = None  # Don't save this trip
        
        try:
            # Generate itinerary using LLM
            location_str = f"{city}, {state}, {country}" if state else f"{city}, {country}"
            
            itinerary_data = self.llm.generate_itinerary(
                city=location_str,
                country=country,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                num_days=num_days,
                budget=budget,
                currency=currency,
                trip_type=trip_type_str,
                food_preference=food_preference,
                num_people=num_people
            )
            
            if not itinerary_data:
                logger.error("LLM returned None for itinerary")
                return None
            
            logger.info(f"Itinerary generated successfully with {len(itinerary_data.get('daily_itinerary', []))} days")
            
            # Add map links to activities
            itinerary_data['daily_itinerary'] = self._add_map_links_to_itinerary(
                itinerary_data.get('daily_itinerary', []),
                city,
                country
            )
            
            # Save to database if user is logged in
            trip_id = None
            if user_id:
                trip_id = self._save_trip_to_db(
                    user_id=user_id,
                    city=city,
                    state=state,
                    country=country,
                    start_date=start_date,
                    end_date=end_date,
                    budget=budget,
                    currency=currency,
                    trip_type=trip_type_str,
                    food_preference=food_preference,
                    num_people=num_people,
                    itinerary_json=json.dumps(itinerary_data)
                )
            
            # Add metadata
            itinerary_data['trip_id'] = trip_id
            itinerary_data['destination'] = f"{city}, {country}"
            itinerary_data['start_date'] = start_date.isoformat()
            itinerary_data['end_date'] = end_date.isoformat()
            itinerary_data['num_days'] = num_days
            
            return itinerary_data
            
        except Exception as e:
            logger.error(f"Error in generate_itinerary: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _add_map_links_to_itinerary(self, daily_itinerary: list, city: str, country: str) -> list:
        """Add Google Maps links to activities"""
        updated_itinerary = []
        
        for day in daily_itinerary:
            updated_activities = []
            
            for activity in day.get('activities', []):
                location_name = activity.get('location', '')
                
                if location_name:
                    # Get map link
                    map_link = self.maps.get_google_maps_link(
                        location=f"{location_name}, {city}, {country}"
                    )
                    activity['maps_link'] = map_link
                
                updated_activities.append(activity)
            
            day['activities'] = updated_activities
            
            # Add map links to meals
            updated_meals = []
            for meal in day.get('meals', []):
                restaurant_name = meal.get('restaurant', '')
                if restaurant_name:
                    map_link = self.maps.get_google_maps_link(
                        location=f"{restaurant_name}, {city}, {country}"
                    )
                    meal['maps_link'] = map_link
                updated_meals.append(meal)
            
            day['meals'] = updated_meals
            
            updated_itinerary.append(day)
        
        return updated_itinerary
    
    def _check_duplicate_trip(
        self,
        user_id: int,
        city: str,
        state: str,
        country: str,
        num_days: int,
        budget: float,
        num_people: int
    ) -> bool:
        """
        Check if an identical trip already exists
        Unique criteria: city, state, country, duration (num_days), budget, num_people
        """
        try:
            # Allow 10% budget variance
            budget_min = budget * 0.9
            budget_max = budget * 1.1
            
            query = """
                SELECT trip_id FROM trips 
                WHERE user_id = %s 
                AND destination_city = %s 
                AND destination_country = %s
                AND DATEDIFF(end_date, start_date) + 1 = %s
                AND budget BETWEEN %s AND %s
                AND num_people = %s
            """
            
            params = [user_id, city, country, num_days, budget_min, budget_max, num_people]
            
            # Add state check if provided
            if state:
                query += " AND destination_state = %s"
                params.append(state)
            else:
                query += " AND (destination_state IS NULL OR destination_state = '')"
            
            result = self.db.execute_query(query, tuple(params))
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Error checking duplicate trip: {e}")
            return False
    
    def _save_trip_to_db(
        self,
        user_id: int,
        city: str,
        state: str,
        country: str,
        start_date: date,
        end_date: date,
        budget: float,
        currency: str,
        trip_type: str,
        food_preference: str,
        num_people: int,
        itinerary_json: str
    ) -> int:
        """Save trip to database"""
        try:
            query = """
                INSERT INTO trips 
                (user_id, destination_city, destination_state, destination_country, start_date, end_date,
                 budget, currency, trip_type, food_preference, num_people, itinerary_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db.execute_query(
                query,
                (
                    user_id, city, state, country, start_date, end_date,
                    budget, currency, trip_type, food_preference, num_people, itinerary_json
                ),
                fetch=False
            )
            
            trip_id = self.db.get_last_insert_id()
            logger.info(f"Trip saved with ID: {trip_id}")
            return trip_id
            
        except Exception as e:
            logger.error(f"Error saving trip to database: {e}")
            return None
    
    def get_user_trips(self, user_id: int) -> list:
        """Get all trips for a user"""
        try:
            query = """
                SELECT * FROM trips 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """
            
            results = self.db.execute_query(query, (user_id,))
            return results if results else []
            
        except Exception as e:
            logger.error(f"Error getting user trips: {e}")
            return []
    
    def get_trip_by_id(self, trip_id: int) -> dict:
        """Get trip by ID"""
        try:
            query = "SELECT * FROM trips WHERE trip_id = %s"
            results = self.db.execute_query(query, (trip_id,))
            
            if results:
                trip = results[0]
                if trip['itinerary_json']:
                    trip['itinerary'] = json.loads(trip['itinerary_json'])
                return trip
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting trip by ID: {e}")
            return None


# Global agent instance
_itinerary_agent = None


def get_itinerary_agent() -> ItineraryAgent:
    """Get or create itinerary agent instance"""
    global _itinerary_agent
    
    if _itinerary_agent is None:
        _itinerary_agent = ItineraryAgent()
    
    return _itinerary_agent