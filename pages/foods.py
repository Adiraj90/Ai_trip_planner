"""
Foods Page - Search and filter restaurants
"""
import streamlit as st
from agents.food_agent import get_food_agent
from database.queries import add_bookmark_restaurant, remove_bookmark_restaurant, is_restaurant_bookmarked
from utils.helpers import get_rating_stars, get_food_type_emoji
import time


def render_search_section():
    """Render restaurant search section"""
    st.markdown("## 🍽️ Discover Amazing Restaurants")
    
    # Pre-fill from previous searches
    default_city = st.session_state.get('destination_city', '')
    default_country = st.session_state.get('destination_country', '')
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        city = st.text_input(
            "City",
            value=default_city,
            placeholder="e.g., Tokyo",
            key="food_city"
        )
    
    with col2:
        country = st.text_input(
            "Country",
            value=default_country,
            placeholder="e.g., Japan",
            key="food_country"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Find Restaurants",
            use_container_width=True,
            type="primary"
        )
    
    return city, country, search_button


def render_restaurant_card(restaurant: dict):
    """Render a single restaurant card"""
    
    name = restaurant.get('name', 'Restaurant')
    description = restaurant.get('description', 'No description available')
    location = restaurant.get('location', 'Location')
    cuisine = restaurant.get('cuisine_type', 'Cuisine')
    food_type = restaurant.get('food_type', 'Mixed')
    price_range = restaurant.get('price_range', 'Medium')
    rating = restaurant.get('rating', 0)
    image_url = restaurant.get('image_url', 'https://source.unsplash.com/800x600/?restaurant,food')
    popular_dishes = restaurant.get('popular_dishes', [])
    maps_link = restaurant.get('maps_link', '#')
    
    # Safely convert rating to float
    try:
        rating_value = float(rating)
    except (ValueError, TypeError):
        rating_value = 0.0
    
    # Generate stars
    full_stars = int(rating_value)
    half_star = 1 if (rating_value - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars_html = "⭐" * full_stars + "✨" * half_star + "☆" * empty_stars
    
    # Opening/Closing hours
    opening_hours = restaurant.get('opening_hours', 'N/A')
    closing_hours = restaurant.get('closing_hours', 'N/A')
    hours_display = f"{opening_hours} - {closing_hours}"
    
    # Popular dishes string
    dishes_list = popular_dishes if isinstance(popular_dishes, list) else []
    dishes_display = ", ".join(dishes_list[:3])
    if len(dishes_list) > 3:
        dishes_display += "..."
    
    # Food type emoji
    food_emoji = get_food_type_emoji(food_type)
    
    # Create horizontal card
    st.markdown(f"""
    <div class="horizontal-card">
        <img src="{image_url}" class="card-image" alt="{name}">
        <div class="card-content">
            <div>
                <div class="card-title">{name}</div>
                <div style="color: #888; margin-bottom: 0.5rem;">
                    📍 {location} • 🍽️ {cuisine} • {food_emoji} {food_type}
                </div>
                <div class="card-description">{description}</div>
                <div style="margin: 0.5rem 0;">
                    <strong>Must Try:</strong> {dishes_display if dishes_display else "Various dishes"}
                </div>
            </div>
            <div class="card-footer">
                <div class="rating">
                    <span style="font-size: 1.2rem;">{stars_html}</span> 
                    <span style="color: #667eea; font-weight: 600; margin-left: 5px;">{rating_value}/5</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.1rem; font-weight: 600; color: #667eea;">
                        🕐 {hours_display}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">Opening Hours</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Map and Bookmark buttons below card
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown(f"""
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button" style="width: 100%; padding: 10px;">
                📍 View on Google Maps
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        # Bookmark button
        user_id = st.session_state.get('user_id')
        is_bookmarked = False
        restaurant_key = f"restaurant_{name}_{location}".replace(" ", "_").replace("/", "_")[:50]
        
        if user_id:
            is_bookmarked = is_restaurant_bookmarked(user_id, name, location)
        
        if user_id:
            if is_bookmarked:
                if st.button("🔖 Bookmarked", use_container_width=True, key=f"unbookmark_{restaurant_key}"):
                    if remove_bookmark_restaurant(user_id, name, location):
                        st.success("Removed from bookmarks!")
                        st.rerun()
                    else:
                        st.error("Failed to remove bookmark")
            else:
                if st.button("🔖 Bookmark", use_container_width=True, key=f"bookmark_{restaurant_key}"):
                    # Prepare restaurant data with city/country from session state if available
                    restaurant_data = restaurant.copy()
                    if 'food_search_city' in st.session_state:
                        restaurant_data['city'] = st.session_state.food_search_city
                    if 'food_search_country' in st.session_state:
                        restaurant_data['country'] = st.session_state.food_search_country
                    
                    if add_bookmark_restaurant(user_id, restaurant_data):
                        st.success("Added to bookmarks! 🔖")
                        st.rerun()
                    else:
                        st.error("Failed to add bookmark")
        else:
            if st.button("🔖 Bookmark", use_container_width=True, key=f"bookmark_login_{restaurant_key}"):
                st.session_state.bookmark_login_required = True
                st.session_state.bookmark_type = "restaurant"
                st.rerun()
    
    # Handle login prompt
    if st.session_state.get('bookmark_login_required', False) and st.session_state.get('bookmark_type') == "restaurant":
        st.warning("🔐 Please login or sign up to bookmark restaurants!")
        login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
        with login_col1:
            if st.button("🔐 Login", use_container_width=True, type="primary", key=f"restaurant_bookmark_login_{restaurant_key}"):
                st.session_state.bookmark_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "login"
                st.rerun()
        with login_col2:
            if st.button("📝 Sign Up", use_container_width=True, type="primary", key=f"restaurant_bookmark_signup_{restaurant_key}"):
                st.session_state.bookmark_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "signup"
                st.rerun()
        with login_col3:
            if st.button("❌ Cancel", use_container_width=True, key=f"restaurant_bookmark_cancel_{restaurant_key}"):
                st.session_state.bookmark_login_required = False
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)


def render():
    """Main render function for Foods page"""
    
    # Initialize bookmark login flag
    if 'bookmark_login_required' not in st.session_state:
        st.session_state.bookmark_login_required = False
    if 'bookmark_type' not in st.session_state:
        st.session_state.bookmark_type = None
    
    # Render search section
    city, country, search_clicked = render_search_section()
    
    st.markdown("---")
    
    # Check if restaurants have been generated
    has_restaurants = bool(st.session_state.get('restaurants_list'))
    
    # Create layout with filters and content (only show filters if restaurants exist)
    if has_restaurants:
        filter_col, content_col = st.columns([1, 3])
    else:
        content_col = st.container()
        filter_col = None
    
    # Render filters in left column (only if restaurants exist)
    if filter_col:
        with filter_col:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 1.5rem; border-radius: 15px; position: sticky; top: 20px;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🎛️ Filters & Sort</h3>
            """, unsafe_allow_html=True)
            
            # Sorting
            st.markdown("**📊 Sort By**")
            sort_by = st.selectbox(
                "Sort",
                options=[
                    ("Rating (High to Low)", "rating_desc"),
                    ("Rating (Low to High)", "rating_asc"),
                    ("Price (Low to High)", "price_low"),
                    ("Price (High to High)", "price_high")
                ],
                format_func=lambda x: x[0],
                key="food_sort",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Food Type Filter (Veg/Non-Veg specific)
            st.markdown("**🥗 Food Type**")
            food_type_options = st.multiselect(
                "Select food types",
                options=["Vegetarian", "Non-Vegetarian", "Vegan", "Pescatarian", "Mixed"],
                default=[],
                key="food_type_multi_filter",
                label_visibility="collapsed"
            )
            
            # Cuisine Type Filter
            st.markdown("**🌍 Cuisine Type**")
            cuisine_type = st.selectbox(
                "Cuisine",
                options=["All", "Local", "Italian", "Chinese", "Japanese", "Indian", "Mexican", "Thai", "French", "Mediterranean", "American", "Korean", "Vietnamese"],
                key="food_cuisine_filter",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Dietary Restrictions
            st.markdown("**🚫 Dietary Restrictions**")
            dietary_restrictions = st.multiselect(
                "Avoid",
                options=["Gluten", "Dairy", "Nuts", "Seafood", "Soy", "Eggs"],
                key="food_dietary_filter",
                label_visibility="collapsed"
            )
            
            # Price Range Filter
            st.markdown("**💰 Price Range**")
            price_range = st.selectbox(
                "Budget",
                options=["All", "Budget", "Medium", "Expensive"],
                key="food_price_filter",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Meal Type
            st.markdown("**🍽️ Meal Type**")
            meal_type = st.multiselect(
                "Suitable for",
                options=["Breakfast", "Brunch", "Lunch", "Dinner", "Late Night", "Snacks"],
                key="food_meal_type",
                label_visibility="collapsed"
            )
            
            # Rating Filter
            st.markdown("**⭐ Minimum Rating**")
            min_rating = st.slider(
                "Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key="food_min_rating"
            )
            
            st.markdown("---")
            
            # Service Type
            st.markdown("**🛎️ Service Type**")
            service_type = st.multiselect(
                "Available services",
                options=["Dine-in", "Takeaway", "Delivery", "Outdoor Seating", "Reservations"],
                key="food_service_type",
                label_visibility="collapsed"
            )
            
            # Ambiance
            st.markdown("**🎭 Ambiance**")
            ambiance = st.multiselect(
                "Atmosphere",
                options=["Casual", "Fine Dining", "Romantic", "Family Friendly", "Fast Food", "Cafe", "Bar & Grill"],
                key="food_ambiance",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Clear Filters
            if st.button("🔄 Clear All Filters", use_container_width=True, key="clear_food_filters"):
                st.session_state.food_type_multi_filter = []
                st.session_state.food_cuisine_filter = "All"
                st.session_state.food_price_filter = "All"
                st.session_state.food_min_rating = 0.0
                st.session_state.food_dietary_filter = []
                st.session_state.food_meal_type = []
                st.session_state.food_service_type = []
                st.session_state.food_ambiance = []
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        filters = {
            'sort_by': sort_by[1],
            'food_types': food_type_options,
            'cuisine_type': cuisine_type,
            'price_range': price_range,
            'min_rating': min_rating,
            'dietary_restrictions': dietary_restrictions,
            'meal_type': meal_type,
            'service_type': service_type,
            'ambiance': ambiance
        }
    else:
        # Default filters when no restaurants loaded yet
        filters = {
            'sort_by': "rating_desc",
            'food_types': [],
            'cuisine_type': "All",
            'price_range': "All",
            'min_rating': 0.0,
            'dietary_restrictions': [],
            'meal_type': [],
            'service_type': [],
            'ambiance': []
        }
    
    # Content column
    with content_col:
        # Handle search
        if search_clicked:
            if not city or not country:
                st.error("⚠️ Please enter both city and country!")
                return
            
            with st.spinner(f"🔍 Finding the best restaurants in {city}... This may take 20-30 seconds..."):
                try:
                    agent = get_food_agent()
                    
                    # Find initial restaurants (5 results)
                    restaurants = agent.find_restaurants(
                        city=city,
                        country=country,
                        food_type=filters['food_types'][0] if filters['food_types'] else "Mixed",
                        cuisine_type=filters['cuisine_type'] if filters['cuisine_type'] != "All" else None,
                        price_range=filters['price_range'] if filters['price_range'] != "All" else "Medium",
                        num_results=5
                    )
                    
                    if restaurants:
                        st.session_state.restaurants_list = restaurants
                        st.session_state.food_search_city = city
                        st.session_state.food_search_country = country
                        st.session_state.restaurants_total_loaded = 5
                        st.success(f"✅ Found {len(restaurants)} restaurants in {city}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ No restaurants found. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display restaurants if available
        if st.session_state.get('restaurants_list'):
            restaurants = st.session_state.restaurants_list
            search_city = st.session_state.get('food_search_city', city)
            search_country = st.session_state.get('food_search_country', country)
            
            # Apply filters
            filtered_restaurants = restaurants.copy()
            
            # Filter by food types (multiple selection)
            if filters['food_types']:
                filtered_restaurants = [
                    r for r in filtered_restaurants
                    if any(ft.lower() in r.get('food_type', '').lower() for ft in filters['food_types'])
                ]
            
            # Filter by cuisine type
            if filters['cuisine_type'] != "All":
                filtered_restaurants = [
                    r for r in filtered_restaurants
                    if filters['cuisine_type'].lower() in r.get('cuisine_type', '').lower()
                ]
            
            # Filter by price range
            if filters['price_range'] != "All":
                filtered_restaurants = [
                    r for r in filtered_restaurants
                    if r.get('price_range', '') == filters['price_range']
                ]
            
            # Filter by rating
            filtered_restaurants = [
                r for r in filtered_restaurants
                if float(r.get('rating', 0)) >= filters['min_rating']
            ]
            
            # Sort restaurants
            if filters['sort_by'] == "rating_desc":
                filtered_restaurants.sort(key=lambda x: float(x.get('rating', 0)), reverse=True)
            elif filters['sort_by'] == "rating_asc":
                filtered_restaurants.sort(key=lambda x: float(x.get('rating', 0)))
            elif filters['sort_by'] == "price_low":
                price_order = {"Budget": 1, "Medium": 2, "Expensive": 3}
                filtered_restaurants.sort(key=lambda x: price_order.get(x.get('price_range', 'Medium'), 2))
            elif filters['sort_by'] == "price_high":
                price_order = {"Expensive": 1, "Medium": 2, "Budget": 3}
                filtered_restaurants.sort(key=lambda x: price_order.get(x.get('price_range', 'Medium'), 2))
            
            # Initialize counter
            if 'restaurants_total_loaded' not in st.session_state:
                st.session_state.restaurants_total_loaded = len(restaurants)
            
            # Display results
            st.markdown(f"### 🍽️ Restaurants in {search_city}, {search_country}")
            st.markdown(f"*Showing {len(filtered_restaurants)} restaurants*")
            
            # Active filters display
            active_filters = []
            if filters['food_types']:
                active_filters.append(f"Food: {', '.join(filters['food_types'])}")
            if filters['cuisine_type'] != "All":
                active_filters.append(f"Cuisine: {filters['cuisine_type']}")
            if filters['price_range'] != "All":
                active_filters.append(f"Price: {filters['price_range']}")
            if filters['min_rating'] > 0:
                active_filters.append(f"Rating: {filters['min_rating']}+")
            
            if active_filters:
                st.markdown(f"**Active Filters:** {' • '.join(active_filters)}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_restaurants:
                # Display all filtered restaurants
                for restaurant in filtered_restaurants:
                    render_restaurant_card(restaurant)
                
                # Determine city type for max limit
                major_cities = ["delhi", "mumbai", "new york", "london", "paris", "tokyo", "beijing", "shanghai", "dubai", "singapore", "hong kong", "sydney", "los angeles", "chicago", "toronto", "bangkok", "rome", "barcelona"]
                is_major_city = search_city.lower() in major_cities
                max_limit = 30 if is_major_city else 20
                
                # Load More button
                if st.session_state.restaurants_total_loaded < max_limit:
                    st.markdown("---")
                    st.markdown(f"<p style='text-align: center; color: #666; font-size: 1.1rem; margin: 1rem 0;'>💡 Want to explore more restaurants?</p>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("🔄 Load More Restaurants (Generate 5 new)", use_container_width=True, type="primary", key="load_more_restaurants_btn"):
                            with st.spinner("🔍 Finding more restaurants..."):
                                try:
                                    agent = get_food_agent()
                                    
                                    # Generate 5 more restaurants
                                    new_restaurants = agent.find_restaurants(
                                        city=search_city,
                                        country=search_country,
                                        food_type=filters['food_types'][0] if filters['food_types'] else "Mixed",
                                        cuisine_type=filters['cuisine_type'] if filters['cuisine_type'] != "All" else None,
                                        price_range=filters['price_range'] if filters['price_range'] != "All" else "Medium",
                                        num_results=5
                                    )
                                    
                                    if new_restaurants:
                                        st.session_state.restaurants_list.extend(new_restaurants)
                                        st.session_state.restaurants_total_loaded += len(new_restaurants)
                                        st.success(f"✅ Added {len(new_restaurants)} more restaurants!")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.warning("No more restaurants found.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.9rem;'>Loaded {st.session_state.restaurants_total_loaded}/{max_limit} restaurants</p>", unsafe_allow_html=True)
                else:
                    st.markdown("---")
                    st.markdown(f"<p style='text-align: center; color: #28a745; font-size: 1.1rem;'>✅ <strong>Maximum restaurants loaded for {search_city}!</strong></p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; color: #666;'>You've explored {st.session_state.restaurants_total_loaded} restaurants. Try adjusting filters for different options.</p>", unsafe_allow_html=True)
            else:
                st.info("No restaurants match your filters. Try adjusting the criteria.")
                
                # Reset filters button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🔄 Reset All Filters", use_container_width=True, type="primary"):
                        st.session_state.food_type_multi_filter = []
                        st.session_state.food_cuisine_filter = "All"
                        st.session_state.food_price_filter = "All"
                        st.session_state.food_min_rating = 0.0
                        st.rerun()
        else:
            # Show placeholder
            st.info("👆 Enter a city and country to find amazing restaurants!")