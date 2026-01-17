"""
LLM Handler for AI interactions using Groq API
"""
import streamlit as st
import json
from typing import Optional, Dict, List, Any
import logging

try:
    from groq import Groq
except ImportError as e:
    st.error(f"Failed to import groq: {e}")
    st.error("Please install groq: pip install groq")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles all LLM interactions using Groq"""
    
    def __init__(self):
        """Initialize Groq client"""
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            # Using llama-3.3-70b-versatile - one of the best free models on Groq
            self.model = "llama-3.3-70b-versatile"
            logger.info("LLM Handler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM Handler: {e}")
            st.error("Failed to initialize AI service. Please check your API key.")
            self.client = None
    
    def generate_response(
        self, 
        prompt: str, 
        system_message: str = "You are a helpful AI travel assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_message: System message to set context
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated response or None
        """
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            st.error("Failed to generate AI response. Please try again.")
            return None
    
    def generate_json_response(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI assistant that returns responses in valid JSON format.",
        temperature: float = 0.5,
        max_tokens: int = 16000
    ) -> Optional[Dict]:
        """
        Generate a JSON response from the LLM
        
        Args:
            prompt: User prompt requesting JSON
            system_message: System message
            temperature: Creativity level
            max_tokens: Maximum tokens (default 16000 for large responses like 30-day trips)
            
        Returns:
            Parsed JSON dict or None
        """
        response = self.generate_response(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if response:
            try:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response.strip()
                
                # Try parsing first without modification
                try:
                    parsed = json.loads(json_str)
                    logger.info("Successfully parsed JSON response (without cleaning)")
                    return parsed
                except json.JSONDecodeError:
                    # If that fails, try with minimal cleaning (preserve structure)
                    # Remove trailing commas before } or ]
                    import re
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)
                    
                    # Try to find and extract JSON object boundaries
                    # Look for first { and last }
                    first_brace = json_str.find('{')
                    last_brace = json_str.rfind('}')
                    
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        json_str = json_str[first_brace:last_brace + 1]
                    
                    parsed = json.loads(json_str)
                    logger.info("Successfully parsed JSON response (with cleaning)")
                    return parsed
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response length: {len(response)} characters")
                logger.error(f"Response preview: {response[:500]}...")
                
                # Try to show in Streamlit for debugging
                try:
                    st.error(f"JSON Parse Error: {e}")
                    st.error(f"Response length: {len(response)} characters")
                    with st.expander("View raw response (first 5000 chars)"):
                        st.code(response[:5000])
                    with st.expander("View raw response (full)"):
                        st.code(response)
                except:
                    pass
                
                return None
        
        logger.error("No response received from LLM")
        return None
    
    def generate_destination_info(self, city: str, country: str) -> Optional[Dict]:
        """
        Generate comprehensive destination information
        
        Args:
            city: Destination city
            country: Destination country
            
        Returns:
            Dictionary with destination info
        """
        prompt = f"""
Generate comprehensive information about {city}, {country} for travel planning.
Return ONLY a valid JSON object with this exact structure:

{{
    "description": "Brief 2-3 sentence description of the city",
    "popular_places": [
        {{
            "name": "Place name",
            "description": "Brief description",
            "category": "Museum/Temple/Beach/etc"
        }}
    ],
    "culture": "Description of local culture and traditions",
    "local_language": "Primary language(s) spoken",
    "famous_foods": [
        {{
            "name": "Food name",
            "description": "Brief description"
        }}
    ],
    "best_time_to_visit": "Best season/months to visit",
    "local_tips": "2-3 useful tips for travelers"
}}

Include at least 5 popular places and 5 famous foods. Be specific and accurate.
"""
        
        system_message = "You are an expert travel guide with deep knowledge of destinations worldwide. Provide accurate, helpful information in valid JSON format only."
        
        return self.generate_json_response(prompt, system_message)
    
    def generate_itinerary(
        self,
        city: str,
        country: str,
        start_date: str,
        end_date: str,
        num_days: int,
        budget: float,
        currency: str,
        trip_type: str,
        food_preference: str,
        num_people: int
    ) -> Optional[Dict]:
        """
        Generate day-by-day itinerary
        
        Returns:
            Dictionary with itinerary
        """
        prompt = f"""
Create a detailed {num_days}-day travel itinerary for {city}, {country}.

TRIP DETAILS:
- Dates: {start_date} to {end_date}
- Budget: {budget} {currency} (total for all {num_people} people)
- Trip Type: {trip_type}
- Food Preference: {food_preference}
- Travelers: {num_people} people

IMPORTANT: Return ONLY valid JSON with NO additional text, explanations, or markdown formatting.

Use this EXACT structure:

{{
    "trip_overview": "A brief 2-3 sentence overview of the trip",
    "total_estimated_cost": 1500.00,
    "daily_itinerary": [
        {{
            "day": 1,
            "date": "{start_date}",
            "title": "Arrival and City Exploration",
            "summary": "A 2-3 sentence description of what this day is about, the overall theme, and what travelers can expect to experience.",
            "activities": [
                {{
                    "time": "09:00 AM",
                    "activity": "Activity name",
                    "description": "Brief description of what you'll do",
                    "location": "Specific location name",
                    "estimated_cost": 50.00,
                    "duration": "2 hours"
                }}
            ],
            "meals": [
                {{
                    "type": "Breakfast",
                    "restaurant": "Restaurant name",
                    "cuisine": "Cuisine type",
                    "estimated_cost": 25.00
                }},
                {{
                    "type": "Lunch",
                    "restaurant": "Restaurant name",
                    "cuisine": "Cuisine type",
                    "estimated_cost": 35.00
                }},
                {{
                    "type": "Dinner",
                    "restaurant": "Restaurant name",
                    "cuisine": "Cuisine type",
                    "estimated_cost": 45.00
                }}
            ],
            "accommodation": {{
                "hotel": "Hotel name",
                "area": "Neighborhood/Area name",
                "estimated_cost": 150.00
            }}
        }}
    ]
}}

REQUIREMENTS:
1. Include {num_days} days in daily_itinerary array
2. Each day must have a "summary" with 2-3 sentences describing the day's theme and activities
3. Each day must have 3-5 activities with different times
4. Each day must have breakfast, lunch, and dinner
4. Each day must have accommodation info
5. Keep total costs within budget of {budget} {currency}
6. Consider the {trip_type} trip type and {food_preference} food preference
7. Use realistic restaurant and hotel names from {city}
8. Return ONLY the JSON object, no other text
"""
        
        system_message = "You are an expert travel planner. Generate ONLY valid JSON with no additional text or formatting. Do not include markdown code blocks or explanations."
        
        # Increase max_tokens for longer trips (30 days can be very large)
        # Estimate: ~500-800 tokens per day, so 30 days = ~15k-24k tokens
        estimated_tokens = max(8000, num_days * 600)  # Minimum 8000, or 600 per day
        max_tokens = min(16000, estimated_tokens)  # Cap at 16000 (model limit)
        
        return self.generate_json_response(prompt, system_message, temperature=0.7, max_tokens=max_tokens)


# Global LLM instance
_llm_instance = None


def get_llm() -> LLMHandler:
    """
    Get or create LLM handler instance
    
    Returns:
        LLMHandler instance
    """
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = LLMHandler()
    
    return _llm_instance