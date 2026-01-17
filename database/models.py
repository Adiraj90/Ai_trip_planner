"""
Database models and data classes
"""
from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class User:
    """User model"""
    user_id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Trip:
    """Trip model"""
    trip_id: Optional[int] = None
    user_id: Optional[int] = None
    destination_country: str = ""
    destination_city: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    currency: str = "USD"
    trip_type: Optional[str] = None
    food_preference: Optional[str] = None
    num_people: int = 1
    itinerary_json: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert date objects to strings
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data
    
    def get_itinerary(self) -> Optional[Dict]:
        """Parse and return itinerary JSON"""
        if self.itinerary_json:
            try:
                return json.loads(self.itinerary_json)
            except:
                return None
        return None


@dataclass
class Hotel:
    """Hotel model"""
    hotel_id: Optional[int] = None
    trip_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    price_per_night: Optional[float] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    amenities: Optional[str] = None
    room_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maps_link: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_amenities_list(self) -> List[str]:
        """Parse and return amenities as list"""
        if self.amenities:
            try:
                return json.loads(self.amenities)
            except:
                return self.amenities.split(',')
        return []


@dataclass
class Restaurant:
    """Restaurant model"""
    restaurant_id: Optional[int] = None
    trip_id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    cuisine_type: Optional[str] = None
    food_type: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None
    popular_dishes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    maps_link: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_dishes_list(self) -> List[str]:
        """Parse and return popular dishes as list"""
        if self.popular_dishes:
            try:
                return json.loads(self.popular_dishes)
            except:
                return self.popular_dishes.split(',')
        return []


@dataclass
class DestinationCache:
    """Destination cache model"""
    cache_id: Optional[int] = None
    city: str = ""
    country: str = ""
    description: Optional[str] = None
    popular_places: Optional[str] = None
    culture_info: Optional[str] = None
    local_language: Optional[str] = None
    famous_foods: Optional[str] = None
    images_json: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_images(self) -> List[str]:
        """Parse and return images as list"""
        if self.images_json:
            try:
                return json.loads(self.images_json)
            except:
                return []
        return []
    
    def get_popular_places(self) -> List[Dict]:
        """Parse and return popular places"""
        if self.popular_places:
            try:
                return json.loads(self.popular_places)
            except:
                return []
        return []


@dataclass
class Itinerary:
    """Itinerary model"""
    itinerary_id: Optional[int] = None
    trip_id: Optional[int] = None
    day_number: int = 1
    day_title: Optional[str] = None
    activities_json: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_activities(self) -> List[Dict]:
        """Parse and return activities"""
        if self.activities_json:
            try:
                return json.loads(self.activities_json)
            except:
                return []
        return []


@dataclass
class UserPreference:
    """User preferences model"""
    preference_id: Optional[int] = None
    user_id: Optional[int] = None
    default_currency: str = "USD"
    preferred_trip_type: Optional[str] = None
    preferred_food_type: Optional[str] = None
    preferred_budget_range: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)