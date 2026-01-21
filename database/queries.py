"""
Database query functions for user management
"""
from config.database import get_db
from utils.helpers import hash_password
import logging

logger = logging.getLogger(__name__)


def check_email_exists(email: str) -> bool:
    """
    Check if email already exists in database
    
    Args:
        email: Email to check
        
    Returns:
        True if exists, False otherwise
    """
    try:
        db = get_db()
        query = "SELECT user_id FROM users WHERE email = %s"
        result = db.execute_query(query, (email,))
        return len(result) > 0
    except Exception as e:
        logger.error(f"Error checking email: {e}")
        return False


def check_username_exists(username: str) -> bool:
    """
    Check if username already exists in database
    
    Args:
        username: Username to check
        
    Returns:
        True if exists, False otherwise
    """
    try:
        db = get_db()
        query = "SELECT user_id FROM users WHERE username = %s"
        result = db.execute_query(query, (username,))
        return len(result) > 0
    except Exception as e:
        logger.error(f"Error checking username: {e}")
        return False


def create_user(username: str, email: str, password: str, full_name: str, country: str) -> dict:
    """
    Create a new user
    
    Args:
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: Full name
        country: User's country
        
    Returns:
        User dict if successful, None otherwise
    """
    try:
        # Check if email exists
        if check_email_exists(email):
            return {'error': 'Email is already registered'}
        
        # Check if username exists
        if check_username_exists(username):
            return {'error': 'Username is already taken'}
        
        # Hash password
        password_hash = hash_password(password)
        
        db = get_db()
        query = """
            INSERT INTO users (username, email, password_hash, full_name, country)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        db.execute_query(query, (username, email, password_hash, full_name, country), fetch=False)
        user_id = db.get_last_insert_id()
        
        if user_id:
            # Create user preferences with country
            pref_query = """
                INSERT INTO user_preferences (user_id, default_currency, preferred_trip_type)
                VALUES (%s, %s, %s)
            """
            # Auto-detect currency based on country
            from utils.helpers import get_currency_for_country
            currency = get_currency_for_country(country)
            
            db.execute_query(pref_query, (user_id, currency, 'Adventure'), fetch=False)
            
            # Return user data
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'country': country
            }
        
        return {'error': 'Failed to create user'}
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {'error': str(e)}

def authenticate_user(username_or_email: str, password: str) -> dict:
    """
    Authenticate user credentials
    
    Args:
        username_or_email: Username or email
        password: Plain text password
        
    Returns:
        User dict if successful, None otherwise
    """
    try:
        password_hash = hash_password(password)
        
        db = get_db()
        # Updated to include mobile_number
        query = """
            SELECT user_id, username, email, full_name, country, mobile_number
            FROM users
            WHERE (username = %s OR email = %s) AND password_hash = %s
        """
        
        result = db.execute_query(query, (username_or_email, username_or_email, password_hash))
        
        if result:
            user = result[0]
            
            # Get user preferences
            pref_query = """
                SELECT default_currency, preferred_trip_type, preferred_food_type
                FROM user_preferences
                WHERE user_id = %s
            """
            prefs = db.execute_query(pref_query, (user['user_id'],))
            
            if prefs:
                user['preferences'] = prefs[0]
            
            return user
        
        return None
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None


def get_user_by_id(user_id: int) -> dict:
    """
    Get user by ID (Fixed to include mobile_number)
    
    Args:
        user_id: User ID
        
    Returns:
        User dict
    """
    try:
        db = get_db()
        # First, try with mobile_number and profile_image_url
        query = """
            SELECT user_id, username, email, full_name, created_at, mobile_number, profile_image_url
            FROM users
            WHERE user_id = %s
        """
        
        try:
            result = db.execute_query(query, (user_id,))
            if result:
                return result[0]
        except Exception as col_error:
            logger.warning(f"Error fetching with mobile_number/profile_image_url: {col_error}")
            
            # Fallback 1: Try with just mobile_number
            try:
                query = """
                    SELECT user_id, username, email, full_name, created_at, mobile_number
                    FROM users
                    WHERE user_id = %s
                """
                result = db.execute_query(query, (user_id,))
                if result:
                    user = result[0]
                    user['profile_image_url'] = None
                    return user
            except:
                pass
            
            # Fallback 2: Try with just profile_image_url
            try:
                query = """
                    SELECT user_id, username, email, full_name, created_at, profile_image_url
                    FROM users
                    WHERE user_id = %s
                """
                result = db.execute_query(query, (user_id,))
                if result:
                    user = result[0]
                    user['mobile_number'] = None
                    return user
            except:
                pass
            
            # Fallback 3: Basic query without mobile_number or profile_image_url
            query = """
                SELECT user_id, username, email, full_name, created_at
                FROM users
                WHERE user_id = %s
            """
            result = db.execute_query(query, (user_id,))
            if result:
                user = result[0]
                user['mobile_number'] = None
                user['profile_image_url'] = None
                return user
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


def update_user_profile(user_id: int, full_name: str = None, email: str = None, profile_image_url: str = None) -> bool:
    """
    Update user profile
    
    Args:
        user_id: User ID
        full_name: New full name (optional)
        email: New email (optional)
        profile_image_url: Profile image URL (optional)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        if email:
            # Check if new email already exists
            if check_email_exists(email):
                return False
            updates.append("email = %s")
            params.append(email)
        
        if profile_image_url is not None:
            updates.append("profile_image_url = %s")
            params.append(profile_image_url)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        db.execute_query(query, tuple(params), fetch=False)
        return True
        
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return False
    
def update_user_profile_with_mobile(user_id: int, full_name: str = None, email: str = None, 
                                     mobile_number: str = None, profile_image_url: str = None) -> bool:
    """
    Update user profile including mobile number
    
    Args:
        user_id: User ID
        full_name: New full name (optional)
        email: New email (optional)
        mobile_number: New mobile number (optional)
        profile_image_url: Profile image URL (optional)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        
        updates = []
        params = []
        
        # Handle full name update
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        # Handle email update - only check if email is being changed
        if email:
            # Get current user's email
            current_user_query = "SELECT email FROM users WHERE user_id = %s"
            current_user = db.execute_query(current_user_query, (user_id,))
            
            if current_user:
                current_email = current_user[0]['email']
                
                # Only check if email already exists if user is trying to change it
                if email != current_email:
                    # Check if new email is already used by another user
                    email_check_query = "SELECT user_id FROM users WHERE email = %s AND user_id != %s"
                    email_exists = db.execute_query(email_check_query, (email, user_id))
                    
                    if email_exists:
                        logger.warning(f"Email {email} already exists for another user")
                        return False
                
                # Add email to updates
                updates.append("email = %s")
                params.append(email)
        
        # Handle mobile number update (can be duplicate across users)
        if mobile_number is not None:  # Allow empty string to clear mobile
            updates.append("mobile_number = %s")
            params.append(mobile_number if mobile_number.strip() else None)
        
        # Handle profile image update
        if profile_image_url is not None:
            updates.append("profile_image_url = %s")
            params.append(profile_image_url)
        
        # If no updates, return False
        if not updates:
            logger.warning("No updates provided to update_user_profile_with_mobile")
            return False
        
        # Build and execute update query
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        db.execute_query(query, tuple(params), fetch=False)
        logger.info(f"Successfully updated profile for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return False


def get_user_preferences(user_id: int) -> dict:
    """
    Get user preferences
    
    Args:
        user_id: User ID
        
    Returns:
        Preferences dict
    """
    try:
        db = get_db()
        query = """
            SELECT default_currency, preferred_trip_type, 
                   preferred_food_type, preferred_budget_range
            FROM user_preferences
            WHERE user_id = %s
        """
        
        result = db.execute_query(query, (user_id,))
        
        if result:
            return result[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return None


def update_user_preferences(
    user_id: int,
    default_currency: str = None,
    preferred_trip_type: str = None,
    preferred_food_type: str = None,
    preferred_budget_range: str = None
) -> bool:
    """
    Update user preferences
    
    Args:
        user_id: User ID
        default_currency: Default currency
        preferred_trip_type: Preferred trip type
        preferred_food_type: Preferred food type
        preferred_budget_range: Preferred budget range
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        
        updates = []
        params = []
        
        if default_currency:
            updates.append("default_currency = %s")
            params.append(default_currency)
        
        if preferred_trip_type:
            updates.append("preferred_trip_type = %s")
            params.append(preferred_trip_type)
        
        if preferred_food_type:
            updates.append("preferred_food_type = %s")
            params.append(preferred_food_type)
        
        if preferred_budget_range:
            updates.append("preferred_budget_range = %s")
            params.append(preferred_budget_range)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = %s"
        
        db.execute_query(query, tuple(params), fetch=False)
        return True
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        return False


def get_user_trip_stats(user_id: int) -> dict:
    """
    Get user's trip statistics
    
    Args:
        user_id: User ID
        
    Returns:
        Stats dict
    """
    try:
        db = get_db()
        
        # Total trips
        trips_query = "SELECT COUNT(*) as count FROM trips WHERE user_id = %s"
        trips_result = db.execute_query(trips_query, (user_id,))
        total_trips = trips_result[0]['count'] if trips_result else 0
        
        # Total budget
        budget_query = "SELECT SUM(budget) as total FROM trips WHERE user_id = %s"
        budget_result = db.execute_query(budget_query, (user_id,))
        total_budget = budget_result[0]['total'] if budget_result and budget_result[0]['total'] else 0
        
        # Countries visited
        countries_query = """
            SELECT COUNT(DISTINCT destination_country) as count 
            FROM trips 
            WHERE user_id = %s
        """
        countries_result = db.execute_query(countries_query, (user_id,))
        countries_visited = countries_result[0]['count'] if countries_result else 0
        
        return {
            'total_trips': total_trips,
            'total_budget': total_budget,
            'countries_visited': countries_visited
        }
        
    except Exception as e:
        logger.error(f"Error getting trip stats: {e}")
        return {
            'total_trips': 0,
            'total_budget': 0,
            'countries_visited': 0
        }


def delete_trip(trip_id: int, user_id: int) -> bool:
    """
    Delete a trip
    
    Args:
        trip_id: Trip ID to delete
        user_id: User ID (for security check)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        
        # Security check: Ensure trip belongs to user
        check_query = "SELECT user_id FROM trips WHERE trip_id = %s"
        result = db.execute_query(check_query, (trip_id,))
        
        if not result or result[0]['user_id'] != user_id:
            logger.warning(f"Unauthorized delete attempt: trip {trip_id} by user {user_id}")
            return False
        
        # Delete trip
        delete_query = "DELETE FROM trips WHERE trip_id = %s AND user_id = %s"
        db.execute_query(delete_query, (trip_id, user_id), fetch=False)
        
        logger.info(f"Deleted trip {trip_id} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting trip: {e}")
        return False


def add_favorite_trip(user_id: int, trip_id: int = None, popular_trip_data: dict = None) -> bool:
    """
    Add a trip to favorites
    
    Args:
        user_id: User ID
        trip_id: Trip ID for saved trips (optional)
        popular_trip_data: Dictionary with popular trip info (optional)
            Should contain: title, destination, duration, type, emoji, description, highlights, budget
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db = get_db()
        
        # Check if already favorited
        if trip_id:
            check_query = "SELECT favorite_id FROM favorite_trips WHERE user_id = %s AND trip_id = %s"
            result = db.execute_query(check_query, (user_id, trip_id))
        else:
            # Check for popular trip using title and destination as unique identifier
            title = popular_trip_data.get('title', '')
            destination = popular_trip_data.get('destination', '')
            check_query = """
                SELECT favorite_id FROM favorite_trips 
                WHERE user_id = %s AND trip_id IS NULL 
                AND popular_trip_title = %s AND popular_trip_destination = %s
            """
            result = db.execute_query(check_query, (user_id, title, destination))
        
        if result:
            # Already favorited
            return True
        
        # Add to favorites
        if trip_id:
            query = """
                INSERT INTO favorite_trips (user_id, trip_id, is_popular_trip)
                VALUES (%s, %s, 0)
            """
            db.execute_query(query, (user_id, trip_id), fetch=False)
        else:
            import json
            query = """
                INSERT INTO favorite_trips 
                (user_id, trip_id, is_popular_trip, popular_trip_title, popular_trip_destination, 
                 popular_trip_data)
                VALUES (%s, NULL, 1, %s, %s, %s)
            """
            title = popular_trip_data.get('title', '')
            destination = popular_trip_data.get('destination', '')
            trip_data_json = json.dumps(popular_trip_data)
            db.execute_query(query, (user_id, title, destination, trip_data_json), fetch=False)
        
        logger.info(f"Added favorite trip for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding favorite trip: {e}")
        return False


def remove_favorite_trip(user_id: int, trip_id: int = None, popular_trip_title: str = None, 
                         popular_trip_destination: str = None) -> bool:
    """
    Remove a trip from favorites
    
    Args:
        user_id: User ID
        trip_id: Trip ID for saved trips (optional)
        popular_trip_title: Title of popular trip (optional)
        popular_trip_destination: Destination of popular trip (optional)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        
        if trip_id:
            query = "DELETE FROM favorite_trips WHERE user_id = %s AND trip_id = %s"
            db.execute_query(query, (user_id, trip_id), fetch=False)
        else:
            query = """
                DELETE FROM favorite_trips 
                WHERE user_id = %s AND trip_id IS NULL 
                AND popular_trip_title = %s AND popular_trip_destination = %s
            """
            db.execute_query(query, (user_id, popular_trip_title, popular_trip_destination), fetch=False)
        
        logger.info(f"Removed favorite trip for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing favorite trip: {e}")
        return False


def is_trip_favorited(user_id: int, trip_id: int = None, popular_trip_title: str = None,
                      popular_trip_destination: str = None) -> bool:
    """
    Check if a trip is favorited by user
    
    Args:
        user_id: User ID
        trip_id: Trip ID for saved trips (optional)
        popular_trip_title: Title of popular trip (optional)
        popular_trip_destination: Destination of popular trip (optional)
        
    Returns:
        True if favorited, False otherwise
    """
    try:
        db = get_db()
        
        if trip_id:
            query = "SELECT favorite_id FROM favorite_trips WHERE user_id = %s AND trip_id = %s"
            result = db.execute_query(query, (user_id, trip_id))
        else:
            query = """
                SELECT favorite_id FROM favorite_trips 
                WHERE user_id = %s AND trip_id IS NULL 
                AND popular_trip_title = %s AND popular_trip_destination = %s
            """
            result = db.execute_query(query, (user_id, popular_trip_title, popular_trip_destination))
        
        return len(result) > 0
        
    except Exception as e:
        logger.error(f"Error checking if trip is favorited: {e}")
        return False


def get_user_favorites(user_id: int) -> dict:
    """
    Get all favorite trips for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with 'saved_trips' and 'popular_trips' lists
    """
    try:
        db = get_db()
        
        # Get saved trip favorites with trip details
        saved_query = """
            SELECT ft.favorite_id, ft.created_at as favorited_at, t.*
            FROM favorite_trips ft
            JOIN trips t ON ft.trip_id = t.trip_id
            WHERE ft.user_id = %s AND ft.trip_id IS NOT NULL
            ORDER BY ft.created_at DESC
        """
        saved_trips = db.execute_query(saved_query, (user_id,)) or []
        
        # Get popular trip favorites
        popular_query = """
            SELECT favorite_id, popular_trip_title, popular_trip_destination, 
                   popular_trip_data, created_at as favorited_at
            FROM favorite_trips
            WHERE user_id = %s AND trip_id IS NULL
            ORDER BY created_at DESC
        """
        popular_trips_raw = db.execute_query(popular_query, (user_id,)) or []
        
        # Parse JSON data for popular trips
        import json
        popular_trips = []
        for trip in popular_trips_raw:
            try:
                trip_data = json.loads(trip['popular_trip_data']) if trip.get('popular_trip_data') else {}
                trip_data['favorite_id'] = trip['favorite_id']
                trip_data['favorited_at'] = trip['favorited_at']
                popular_trips.append(trip_data)
            except:
                # Fallback if JSON parsing fails
                popular_trips.append({
                    'title': trip.get('popular_trip_title', ''),
                    'destination': trip.get('popular_trip_destination', ''),
                    'favorite_id': trip['favorite_id'],
                    'favorited_at': trip['favorited_at']
                })
        
        return {
            'saved_trips': saved_trips,
            'popular_trips': popular_trips
        }
        
    except Exception as e:
        logger.error(f"Error getting user favorites: {e}")
        return {
            'saved_trips': [],
            'popular_trips': []
        }


def add_bookmark_hotel(user_id: int, hotel_data: dict) -> bool:
    """
    Add a hotel to bookmarks
    
    Args:
        user_id: User ID
        hotel_data: Dictionary with hotel info (name, location, city, country, etc.)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        import json
        
        # Check if already bookmarked using name and location as unique identifier
        check_query = """
            SELECT bookmark_id FROM bookmarks 
            WHERE user_id = %s AND item_type = 'hotel' 
            AND item_name = %s AND item_location = %s
        """
        name = hotel_data.get('name', '')
        location = hotel_data.get('location', '')
        result = db.execute_query(check_query, (user_id, name, location))
        
        if result:
            # Already bookmarked
            return True
        
        # Add to bookmarks
        query = """
            INSERT INTO bookmarks 
            (user_id, item_type, item_name, item_location, item_city, item_country, item_data)
            VALUES (%s, 'hotel', %s, %s, %s, %s, %s)
        """
        city = hotel_data.get('city', '')
        country = hotel_data.get('country', '')
        item_data_json = json.dumps(hotel_data)
        db.execute_query(query, (user_id, name, location, city, country, item_data_json), fetch=False)
        
        logger.info(f"Added bookmarked hotel for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding bookmarked hotel: {e}")
        return False


def add_bookmark_restaurant(user_id: int, restaurant_data: dict) -> bool:
    """
    Add a restaurant to bookmarks
    
    Args:
        user_id: User ID
        restaurant_data: Dictionary with restaurant info (name, location, city, country, etc.)
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        import json
        
        # Check if already bookmarked using name and location as unique identifier
        check_query = """
            SELECT bookmark_id FROM bookmarks 
            WHERE user_id = %s AND item_type = 'restaurant' 
            AND item_name = %s AND item_location = %s
        """
        name = restaurant_data.get('name', '')
        location = restaurant_data.get('location', '')
        result = db.execute_query(check_query, (user_id, name, location))
        
        if result:
            # Already bookmarked
            return True
        
        # Add to bookmarks
        query = """
            INSERT INTO bookmarks 
            (user_id, item_type, item_name, item_location, item_city, item_country, item_data)
            VALUES (%s, 'restaurant', %s, %s, %s, %s, %s)
        """
        city = restaurant_data.get('city', '')
        country = restaurant_data.get('country', '')
        item_data_json = json.dumps(restaurant_data)
        db.execute_query(query, (user_id, name, location, city, country, item_data_json), fetch=False)
        
        logger.info(f"Added bookmarked restaurant for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding bookmarked restaurant: {e}")
        return False


def remove_bookmark_hotel(user_id: int, hotel_name: str, hotel_location: str) -> bool:
    """
    Remove a hotel from bookmarks
    
    Args:
        user_id: User ID
        hotel_name: Hotel name
        hotel_location: Hotel location
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        query = """
            DELETE FROM bookmarks 
            WHERE user_id = %s AND item_type = 'hotel' 
            AND item_name = %s AND item_location = %s
        """
        db.execute_query(query, (user_id, hotel_name, hotel_location), fetch=False)
        logger.info(f"Removed bookmarked hotel for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing bookmarked hotel: {e}")
        return False


def remove_bookmark_restaurant(user_id: int, restaurant_name: str, restaurant_location: str) -> bool:
    """
    Remove a restaurant from bookmarks
    
    Args:
        user_id: User ID
        restaurant_name: Restaurant name
        restaurant_location: Restaurant location
        
    Returns:
        True if successful
    """
    try:
        db = get_db()
        query = """
            DELETE FROM bookmarks 
            WHERE user_id = %s AND item_type = 'restaurant' 
            AND item_name = %s AND item_location = %s
        """
        db.execute_query(query, (user_id, restaurant_name, restaurant_location), fetch=False)
        logger.info(f"Removed bookmarked restaurant for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing bookmarked restaurant: {e}")
        return False


def is_hotel_bookmarked(user_id: int, hotel_name: str, hotel_location: str) -> bool:
    """
    Check if a hotel is bookmarked by user
    
    Args:
        user_id: User ID
        hotel_name: Hotel name
        hotel_location: Hotel location
        
    Returns:
        True if bookmarked
    """
    try:
        db = get_db()
        query = """
            SELECT bookmark_id FROM bookmarks 
            WHERE user_id = %s AND item_type = 'hotel' 
            AND item_name = %s AND item_location = %s
        """
        result = db.execute_query(query, (user_id, hotel_name, hotel_location))
        return len(result) > 0
        
    except Exception as e:
        logger.error(f"Error checking if hotel is bookmarked: {e}")
        return False


def is_restaurant_bookmarked(user_id: int, restaurant_name: str, restaurant_location: str) -> bool:
    """
    Check if a restaurant is bookmarked by user
    
    Args:
        user_id: User ID
        restaurant_name: Restaurant name
        restaurant_location: Restaurant location
        
    Returns:
        True if bookmarked
    """
    try:
        db = get_db()
        query = """
            SELECT bookmark_id FROM bookmarks 
            WHERE user_id = %s AND item_type = 'restaurant' 
            AND item_name = %s AND item_location = %s
        """
        result = db.execute_query(query, (user_id, restaurant_name, restaurant_location))
        return len(result) > 0
        
    except Exception as e:
        logger.error(f"Error checking if restaurant is bookmarked: {e}")
        return False


def get_user_bookmarks(user_id: int) -> dict:
    """
    Get all bookmarks for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with 'hotels' and 'restaurants' lists
    """
    try:
        db = get_db()
        import json
        
        # Get hotel bookmarks
        hotels_query = """
            SELECT bookmark_id, item_name, item_location, item_city, 
                   item_country, item_data, created_at as bookmarked_at
            FROM bookmarks
            WHERE user_id = %s AND item_type = 'hotel'
            ORDER BY created_at DESC
        """
        hotels_raw = db.execute_query(hotels_query, (user_id,)) or []
        
        # Parse JSON data for hotels
        hotels = []
        for hotel in hotels_raw:
            try:
                hotel_data = json.loads(hotel['item_data']) if hotel.get('item_data') else {}
                hotel_data['bookmark_id'] = hotel['bookmark_id']
                hotel_data['bookmarked_at'] = hotel['bookmarked_at']
                hotels.append(hotel_data)
            except:
                # Fallback if JSON parsing fails
                hotels.append({
                    'name': hotel.get('item_name', ''),
                    'location': hotel.get('item_location', ''),
                    'city': hotel.get('item_city', ''),
                    'country': hotel.get('item_country', ''),
                    'bookmark_id': hotel['bookmark_id'],
                    'bookmarked_at': hotel['bookmarked_at']
                })
        
        # Get restaurant bookmarks
        restaurants_query = """
            SELECT bookmark_id, item_name, item_location, item_city, 
                   item_country, item_data, created_at as bookmarked_at
            FROM bookmarks
            WHERE user_id = %s AND item_type = 'restaurant'
            ORDER BY created_at DESC
        """
        restaurants_raw = db.execute_query(restaurants_query, (user_id,)) or []
        
        # Parse JSON data for restaurants
        restaurants = []
        for restaurant in restaurants_raw:
            try:
                restaurant_data = json.loads(restaurant['item_data']) if restaurant.get('item_data') else {}
                restaurant_data['bookmark_id'] = restaurant['bookmark_id']
                restaurant_data['bookmarked_at'] = restaurant['bookmarked_at']
                restaurants.append(restaurant_data)
            except:
                # Fallback if JSON parsing fails
                restaurants.append({
                    'name': restaurant.get('item_name', ''),
                    'location': restaurant.get('item_location', ''),
                    'city': restaurant.get('item_city', ''),
                    'country': restaurant.get('item_country', ''),
                    'bookmark_id': restaurant['bookmark_id'],
                    'bookmarked_at': restaurant['bookmarked_at']
                })
        
        return {
            'hotels': hotels,
            'restaurants': restaurants
        }
        
    except Exception as e:
        logger.error(f"Error getting user bookmarks: {e}")
        return {
            'hotels': [],
            'restaurants': []
        }

def verify_current_password(user_id: int, password: str) -> bool:
    """
    Verify if the provided password matches the user's current password
    
    Args:
        user_id: User ID
        password: Plain text password to verify
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        from utils.helpers import hash_password
        
        password_hash = hash_password(password)
        
        db = get_db()
        query = """
            SELECT user_id FROM users
            WHERE user_id = %s AND password_hash = %s
        """
        
        result = db.execute_query(query, (user_id, password_hash))
        return len(result) > 0
        
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def update_user_password(user_id: int, current_password: str, new_password: str) -> dict:
    """
    Update user password (requires current password verification)
    
    Args:
        user_id: User ID
        current_password: Current password for verification
        new_password: New password to set
        
    Returns:
        Dict with 'success' bool and 'message' string
    """
    try:
        from utils.helpers import hash_password
        
        # First verify current password
        if not verify_current_password(user_id, current_password):
            return {
                'success': False,
                'message': 'Current password is incorrect'
            }
        
        # Validate new password
        if len(new_password) < 8:
            return {
                'success': False,
                'message': 'New password must be at least 8 characters long'
            }
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password in database
        db = get_db()
        query = """
            UPDATE users 
            SET password_hash = %s
            WHERE user_id = %s
        """
        
        db.execute_query(query, (new_password_hash, user_id), fetch=False)
        
        logger.info(f"Password updated successfully for user {user_id}")
        return {
            'success': True,
            'message': 'Password updated successfully'
        }
        
    except Exception as e:
        logger.error(f"Error updating password: {e}")
        return {
            'success': False,
            'message': f'Failed to update password: {str(e)}'
        }