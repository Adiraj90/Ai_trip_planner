"""
Helper utility functions
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
import re
import hashlib
import streamlit as st


def calculate_days_between(start_date: date, end_date: date) -> int:
    """
    Calculate number of days between two dates
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of days
    """
    return (end_date - start_date).days + 1


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency with proper symbol
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
        "JPY": "¥",
        "AUD": "A$",
        "CAD": "C$"
    }
    
    symbol = symbols.get(currency, currency)
    
    if currency == "JPY":
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"


def get_currency_for_country(country: str) -> str:
    """
    Get currency code for a country
    
    Args:
        country: Country name
        
    Returns:
        Currency code
    """
    # Simplified mapping - can be expanded
    country_lower = country.lower()
    
    if "india" in country_lower:
        return "INR"
    elif any(x in country_lower for x in ["usa", "united states", "america"]):
        return "USD"
    elif any(x in country_lower for x in ["uk", "united kingdom", "england", "britain"]):
        return "GBP"
    elif "japan" in country_lower:
        return "JPY"
    elif "australia" in country_lower:
        return "AUD"
    elif "canada" in country_lower:
        return "CAD"
    elif any(x in country_lower for x in ["france", "germany", "italy", "spain", "portugal", "netherlands", "belgium"]):
        return "EUR"
    else:
        return "USD"  # Default


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Generate list of dates between start and end
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of dates
    """
    dates = []
    current = start_date
    
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def format_date_readable(date_obj: date) -> str:
    """
    Format date in readable format
    
    Args:
        date_obj: Date object
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime("%B %d, %Y")


def get_trip_type_emoji(trip_type: str) -> str:
    """
    Get emoji for trip type
    
    Args:
        trip_type: Type of trip
        
    Returns:
        Emoji string
    """
    emojis = {
        "adventure": "🏔️",
        "relaxation": "🏖️",
        "cultural": "🏛️",
        "culinary": "🍽️",
        "shopping": "🛍️",
        "nightlife": "🌃",
        "romantic": "💑",
        "family": "👨‍👩‍👧‍👦",
        "business": "💼",
        "solo": "🎒",
        "beach": "🏖️",
        "mountains": "⛰️",
        "city": "🌆"
    }
    
    return emojis.get(trip_type.lower(), "✈️")


def get_food_type_emoji(food_type: str) -> str:
    """
    Get emoji for food type
    
    Args:
        food_type: Type of food preference
        
    Returns:
        Emoji string
    """
    emojis = {
        "vegetarian": "🥗",
        "vegan": "🌱",
        "non-vegetarian": "🍖",
        "pescatarian": "🐟",
        "mixed": "🍽️",
        "halal": "🕌",
        "kosher": "✡️"
    }
    
    return emojis.get(food_type.lower(), "🍴")


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def init_session_state(key: str, default_value):
    """
    Initialize session state variable if not exists
    
    Args:
        key: Session state key
        default_value: Default value
    """
    if key not in st.session_state:
        st.session_state[key] = default_value


def clear_session_state():
    """Clear all session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def get_rating_stars(rating: float) -> str:
    """
    Convert rating to star display
    
    Args:
        rating: Rating value (0-5)
        
    Returns:
        Star string
    """
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    return "⭐" * full_stars + "✨" * half_star + "☆" * empty_stars


def format_price_range(min_price: float, max_price: float, currency: str = "USD") -> str:
    """
    Format price range
    
    Args:
        min_price: Minimum price
        max_price: Maximum price
        currency: Currency code
        
    Returns:
        Formatted price range
    """
    return f"{format_currency(min_price, currency)} - {format_currency(max_price, currency)}"