"""
Hotels Page - Search and filter hotels
"""
import streamlit as st
from agents.hotel_agent import get_hotel_agent
from database.queries import add_bookmark_hotel, remove_bookmark_hotel, is_hotel_bookmarked
from utils.helpers import format_currency, get_rating_stars
import time


def render_search_section():
    """Render hotel search section"""
    st.markdown("## 🏨 Find Your Perfect Stay")
    
    # Pre-fill from previous searches
    default_city = st.session_state.get('destination_city', '')
    default_country = st.session_state.get('destination_country', '')
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        city = st.text_input(
            "City",
            value=default_city,
            placeholder="e.g., Paris",
            key="hotel_city"
        )
    
    with col2:
        country = st.text_input(
            "Country",
            value=default_country,
            placeholder="e.g., France",
            key="hotel_country"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Search Hotels",
            use_container_width=True,
            type="primary"
        )
    
    return city, country, search_button


def render_filters_panel():
    """Render filters panel on the left side"""
    
    # Use columns to create a sidebar-like layout
    filter_col, content_col = st.columns([1, 3])
    
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
                ("Price (High to Low)", "price_high")
            ],
            format_func=lambda x: x[0],
            key="hotel_sort",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Budget Category Filter
        st.markdown("**💵 Budget Category**")
        budget_category = st.selectbox(
            "Budget",
            options=["All", "Budget ($50-$100)", "Medium ($100-$250)", "Luxury ($250+)"],
            key="hotel_budget_category",
            label_visibility="collapsed"
        )
        
        # Price Range Filter
        st.markdown("**💰 Price Range**")
        price_range = st.slider(
            "Price per night ($)",
            min_value=0,
            max_value=1000,
            value=(0, 1000),
            step=50,
            key="hotel_price_range"
        )
        
        st.markdown("---")
        
        # Rating Filter
        st.markdown("**⭐ Minimum Rating**")
        min_rating = st.slider(
            "Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
            key="hotel_min_rating"
        )
        
        st.markdown("---")
        
        # Room Type Filter
        st.markdown("**🛏️ Room Type**")
        room_type = st.selectbox(
            "Type",
            options=["All", "Single", "Double", "Suite", "Deluxe", "Family"],
            key="hotel_room_type",
            label_visibility="collapsed"
        )
        
        # AC/Non-AC Filter
        st.markdown("**❄️ Air Conditioning**")
        ac_preference = st.radio(
            "AC Preference",
            options=["All", "AC Only", "Non-AC Only"],
            key="hotel_ac_filter",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Amenities Filter
        st.markdown("**🎯 Amenities**")
        amenities = st.multiselect(
            "Must-have amenities",
            options=["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Bar", "Parking", "AC", "Pet Friendly", "Room Service", "Laundry"],
            key="hotel_amenities",
            label_visibility="collapsed"
        )
        
        # Star Rating Filter
        st.markdown("**🌟 Star Rating**")
        star_rating = st.selectbox(
            "Minimum Stars",
            options=["All", "3 Star+", "4 Star+", "5 Star"],
            key="hotel_star_rating",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Clear Filters
        if st.button("🔄 Clear All Filters", use_container_width=True, key="clear_hotel_filters"):
            st.session_state.hotel_price_range = (0, 1000)
            st.session_state.hotel_min_rating = 0.0
            st.session_state.hotel_room_type = "All"
            st.session_state.hotel_amenities = []
            st.session_state.hotel_budget_category = "All"
            st.session_state.hotel_ac_filter = "All"
            st.session_state.hotel_star_rating = "All"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        return {
            'sort_by': sort_by[1],
            'budget_category': budget_category,
            'price_min': price_range[0],
            'price_max': price_range[1],
            'min_rating': min_rating,
            'room_type': room_type,
            'amenities': amenities,
            'ac_preference': ac_preference,
            'star_rating': star_rating
        }
    
    return content_col


def render_hotel_card(hotel: dict):
    """Render a single hotel card"""
    
    name = hotel.get('name', 'Hotel')
    description = hotel.get('description', 'No description available')
    location = hotel.get('location', 'Location')
    price = hotel.get('price_per_night', 0)
    rating = hotel.get('rating', 0)
    image_url = hotel.get('image_url', 'https://source.unsplash.com/800x600/?hotel,luxury')
    amenities = hotel.get('amenities', [])
    room_type = hotel.get('room_type', 'Room')
    maps_link = hotel.get('maps_link', '#')
    
    # Get currency from session state
    currency = st.session_state.get('plan_currency', 'USD')
    
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
    
    # Format price
    try:
        price_value = float(price)
    except (ValueError, TypeError):
        price_value = 0.0
    
    price_formatted = format_currency(price_value, currency)
    
    # Amenities string
    amenities_list = amenities if isinstance(amenities, list) else []
    amenities_display = ", ".join(amenities_list[:5])
    if len(amenities_list) > 5:
        amenities_display += "..."
    
    # Create horizontal card
    st.markdown(f"""
    <div class="horizontal-card">
        <img src="{image_url}" class="card-image" alt="{name}">
        <div class="card-content">
            <div>
                <div class="card-title">{name}</div>
                <div style="color: #888; margin-bottom: 0.5rem;">
                    📍 {location} • 🛏️ {room_type}
                </div>
                <div class="card-description">{description}</div>
                <div style="margin: 0.5rem 0;">
                    <strong>Amenities:</strong> {amenities_display}
                </div>
            </div>
            <div class="card-footer">
                <div class="rating">
                    <span style="font-size: 1.2rem;">{stars_html}</span> 
                    <span style="color: #667eea; font-weight: 600; margin-left: 5px;">{rating_value}/5</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">
                        {price_formatted}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">per night</div>
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
        hotel_key = f"hotel_{name}_{location}".replace(" ", "_").replace("/", "_")[:50]
        
        if user_id:
            is_bookmarked = is_hotel_bookmarked(user_id, name, location)
        
        if user_id:
            if is_bookmarked:
                if st.button("🔖 Bookmarked", use_container_width=True, key=f"unbookmark_{hotel_key}"):
                    if remove_bookmark_hotel(user_id, name, location):
                        st.success("Removed from bookmarks!")
                        st.rerun()
                    else:
                        st.error("Failed to remove bookmark")
            else:
                if st.button("🔖 Bookmark", use_container_width=True, key=f"bookmark_{hotel_key}"):
                    # Prepare hotel data with city/country from session state if available
                    hotel_data = hotel.copy()
                    if 'hotel_search_city' in st.session_state:
                        hotel_data['city'] = st.session_state.hotel_search_city
                    if 'hotel_search_country' in st.session_state:
                        hotel_data['country'] = st.session_state.hotel_search_country
                    
                    if add_bookmark_hotel(user_id, hotel_data):
                        st.success("Added to bookmarks! 🔖")
                        st.rerun()
                    else:
                        st.error("Failed to add bookmark")
        else:
            if st.button("🔖 Bookmark", use_container_width=True, key=f"bookmark_login_{hotel_key}"):
                st.session_state.bookmark_login_required = True
                st.session_state.bookmark_type = "hotel"
                st.rerun()
    
    # Handle login prompt
    if st.session_state.get('bookmark_login_required', False) and st.session_state.get('bookmark_type') == "hotel":
        st.warning("🔐 Please login or sign up to bookmark hotels!")
        login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
        with login_col1:
            if st.button("🔐 Login", use_container_width=True, type="primary", key=f"hotel_bookmark_login_{hotel_key}"):
                st.session_state.bookmark_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "login"
                st.rerun()
        with login_col2:
            if st.button("📝 Sign Up", use_container_width=True, type="primary", key=f"hotel_bookmark_signup_{hotel_key}"):
                st.session_state.bookmark_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "signup"
                st.rerun()
        with login_col3:
            if st.button("❌ Cancel", use_container_width=True, key=f"hotel_bookmark_cancel_{hotel_key}"):
                st.session_state.bookmark_login_required = False
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)


def filter_hotels_by_amenities(hotels: list, required_amenities: list) -> list:
    """Filter hotels by required amenities"""
    if not required_amenities:
        return hotels
    
    filtered = []
    for hotel in hotels:
        hotel_amenities = hotel.get('amenities', [])
        if all(amenity in hotel_amenities for amenity in required_amenities):
            filtered.append(hotel)
    
    return filtered


def render():
    """Main render function for Hotels page"""
    
    # Initialize bookmark login flag
    if 'bookmark_login_required' not in st.session_state:
        st.session_state.bookmark_login_required = False
    if 'bookmark_type' not in st.session_state:
        st.session_state.bookmark_type = None
    
    # Render search section
    city, country, search_clicked = render_search_section()
    
    st.markdown("---")
    
    # Check if hotels have been generated
    has_hotels = bool(st.session_state.get('hotels_list'))
    
    # Create layout with filters and content (only show filters if hotels exist)
    if has_hotels:
        filter_col, content_col = st.columns([1, 3])
    else:
        content_col = st.container()
        filter_col = None
    
    # Render filters in left column (only if hotels exist)
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
                    ("Price (High to Low)", "price_high")
                ],
                format_func=lambda x: x[0],
                key="hotel_sort",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Budget Category Filter
            st.markdown("**💵 Budget Category**")
            budget_category = st.selectbox(
                "Budget",
                options=["All", "Budget ($50-$100)", "Medium ($100-$250)", "Luxury ($250+)"],
                key="hotel_budget_category",
                label_visibility="collapsed"
            )
            
            # Price Range Filter
            st.markdown("**💰 Price Range**")
            price_range = st.slider(
                "Price per night ($)",
                min_value=0,
                max_value=1000,
                value=(0, 1000),
                step=50,
                key="hotel_price_range"
            )
            
            st.markdown("---")
            
            # Rating Filter
            st.markdown("**⭐ Minimum Rating**")
            min_rating = st.slider(
                "Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key="hotel_min_rating"
            )
            
            st.markdown("---")
            
            # Room Type Filter
            st.markdown("**🛏️ Room Type**")
            room_type = st.selectbox(
                "Type",
                options=["All", "Single", "Double", "Suite", "Deluxe", "Family"],
                key="hotel_room_type",
                label_visibility="collapsed"
            )
            
            # AC/Non-AC Filter
            st.markdown("**❄️ Air Conditioning**")
            ac_preference = st.radio(
                "AC Preference",
                options=["All", "AC Only", "Non-AC Only"],
                key="hotel_ac_filter",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Amenities Filter
            st.markdown("**🎯 Amenities**")
            amenities = st.multiselect(
                "Must-have amenities",
                options=["WiFi", "Pool", "Gym", "Spa", "Restaurant", "Bar", "Parking", "AC", "Pet Friendly", "Room Service", "Laundry"],
                key="hotel_amenities",
                label_visibility="collapsed"
            )
            
            # Star Rating Filter
            st.markdown("**🌟 Star Rating**")
            star_rating = st.selectbox(
                "Minimum Stars",
                options=["All", "3 Star+", "4 Star+", "5 Star"],
                key="hotel_star_rating",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Clear Filters
            if st.button("🔄 Clear All Filters", use_container_width=True, key="clear_hotel_filters"):
                st.session_state.hotel_price_range = (0, 1000)
                st.session_state.hotel_min_rating = 0.0
                st.session_state.hotel_room_type = "All"
                st.session_state.hotel_amenities = []
                st.session_state.hotel_budget_category = "All"
                st.session_state.hotel_ac_filter = "All"
                st.session_state.hotel_star_rating = "All"
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        filters = {
            'sort_by': sort_by[1],
            'budget_category': budget_category,
            'price_min': price_range[0],
            'price_max': price_range[1],
            'min_rating': min_rating,
            'room_type': room_type,
            'amenities': amenities,
            'ac_preference': ac_preference,
            'star_rating': star_rating
        }
    else:
        # Default filters when no hotels loaded yet
        filters = {
            'sort_by': "rating_desc",
            'budget_category': "All",
            'price_min': 0,
            'price_max': 1000,
            'min_rating': 0.0,
            'room_type': "All",
            'amenities': [],
            'ac_preference': "All",
            'star_rating': "All"
        }
    
    # Content column
    with content_col:
        # Handle search
        if search_clicked:
            if not city or not country:
                st.error("⚠️ Please enter both city and country!")
                return
            
            with st.spinner(f"🔍 Finding the best hotels in {city}... This may take 20-30 seconds..."):
                try:
                    agent = get_hotel_agent()
                    
                    # Determine price range category
                    avg_price = (filters['price_min'] + filters['price_max']) / 2
                    if avg_price < 100:
                        price_range_cat = "Budget"
                    elif avg_price < 250:
                        price_range_cat = "Medium"
                    else:
                        price_range_cat = "Luxury"
                    
                    # Find initial hotels (5 results)
                    hotels = agent.find_hotels(
                        city=city,
                        country=country,
                        room_type=filters['room_type'] if filters['room_type'] != "All" else None,
                        amenities=filters['amenities'],
                        price_range=price_range_cat,
                        num_results=5
                    )
                    
                    if hotels:
                        st.session_state.hotels_list = hotels
                        st.session_state.hotel_search_city = city
                        st.session_state.hotel_search_country = country
                        st.session_state.hotels_total_loaded = 5
                        st.success(f"✅ Found {len(hotels)} hotels in {city}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ No hotels found. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display hotels if available
        if st.session_state.get('hotels_list'):
            hotels = st.session_state.hotels_list
            search_city = st.session_state.get('hotel_search_city', city)
            search_country = st.session_state.get('hotel_search_country', country)
            
            # Apply budget category filter first
            if filters['budget_category'] != "All":
                if "Budget" in filters['budget_category']:
                    hotels = [h for h in hotels if 50 <= h.get('price_per_night', 0) <= 100]
                elif "Medium" in filters['budget_category']:
                    hotels = [h for h in hotels if 100 <= h.get('price_per_night', 0) <= 250]
                elif "Luxury" in filters['budget_category']:
                    hotels = [h for h in hotels if h.get('price_per_night', 0) >= 250]
            
            # Apply other filters
            filtered_hotels = [
                h for h in hotels
                if (filters['price_min'] <= h.get('price_per_night', 0) <= filters['price_max'])
                and (h.get('rating', 0) >= filters['min_rating'])
            ]
            
            # Filter by room type
            if filters['room_type'] != "All":
                filtered_hotels = [
                    h for h in filtered_hotels
                    if filters['room_type'].lower() in h.get('room_type', '').lower()
                ]
            
            # Filter by AC preference
            if filters['ac_preference'] == "AC Only":
                filtered_hotels = [
                    h for h in filtered_hotels
                    if 'AC' in h.get('amenities', []) or 'Air Conditioning' in h.get('amenities', [])
                ]
            elif filters['ac_preference'] == "Non-AC Only":
                filtered_hotels = [
                    h for h in filtered_hotels
                    if 'AC' not in h.get('amenities', []) and 'Air Conditioning' not in h.get('amenities', [])
                ]
            
            # Filter by star rating
            if filters['star_rating'] != "All":
                min_stars = 3 if "3 Star" in filters['star_rating'] else (4 if "4 Star" in filters['star_rating'] else 5)
                filtered_hotels = [
                    h for h in filtered_hotels
                    if h.get('rating', 0) >= min_stars
                ]
            
            # Filter by amenities
            filtered_hotels = filter_hotels_by_amenities(filtered_hotels, filters['amenities'])
            
            # Sort hotels
            if filters['sort_by'] == "price_low":
                filtered_hotels.sort(key=lambda x: x.get('price_per_night', 0))
            elif filters['sort_by'] == "price_high":
                filtered_hotels.sort(key=lambda x: x.get('price_per_night', 0), reverse=True)
            elif filters['sort_by'] == "rating_desc":
                filtered_hotels.sort(key=lambda x: x.get('rating', 0), reverse=True)
            elif filters['sort_by'] == "rating_asc":
                filtered_hotels.sort(key=lambda x: x.get('rating', 0))
            
            # Initialize counters
            if 'hotels_total_loaded' not in st.session_state:
                st.session_state.hotels_total_loaded = len(hotels)
            
            # Display results
            st.markdown(f"### 🏨 Hotels in {search_city}, {search_country}")
            st.markdown(f"*Showing {len(filtered_hotels)} hotels*")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if filtered_hotels:
                # Display all filtered hotels
                for hotel in filtered_hotels:
                    render_hotel_card(hotel)
                
                # Determine max limit
                major_cities = ["delhi", "mumbai", "new york", "london", "paris", "tokyo", "beijing", "shanghai", "dubai", "singapore", "hong kong", "sydney", "los angeles", "chicago", "toronto"]
                is_major_city = search_city.lower() in major_cities
                max_limit = 30 if is_major_city else 20
                
                # Load More button
                if st.session_state.hotels_total_loaded < max_limit:
                    st.markdown("---")
                    st.markdown(f"<p style='text-align: center; color: #666; font-size: 1.1rem; margin: 1rem 0;'>💡 Want to see more options?</p>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("🔄 Load More Hotels (Generate 5 new)", use_container_width=True, type="primary", key="load_more_hotels_btn"):
                            with st.spinner("🔍 Finding more hotels..."):
                                try:
                                    agent = get_hotel_agent()
                                    
                                    # Determine price range
                                    avg_price = (filters['price_min'] + filters['price_max']) / 2
                                    if avg_price < 100:
                                        price_range_cat = "Budget"
                                    elif avg_price < 250:
                                        price_range_cat = "Medium"
                                    else:
                                        price_range_cat = "Luxury"
                                    
                                    # Generate 5 more hotels
                                    new_hotels = agent.find_hotels(
                                        city=search_city,
                                        country=search_country,
                                        room_type=filters['room_type'] if filters['room_type'] != "All" else None,
                                        amenities=filters['amenities'],
                                        price_range=price_range_cat,
                                        num_results=5
                                    )
                                    
                                    if new_hotels:
                                        st.session_state.hotels_list.extend(new_hotels)
                                        st.session_state.hotels_total_loaded += len(new_hotels)
                                        st.success(f"✅ Added {len(new_hotels)} more hotels!")
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.warning("No more hotels found.")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.9rem;'>Loaded {st.session_state.hotels_total_loaded}/{max_limit} hotels</p>", unsafe_allow_html=True)
                else:
                    st.markdown("---")
                    st.markdown(f"<p style='text-align: center; color: #28a745; font-size: 1.1rem;'>✅ <strong>Maximum hotels loaded for {search_city}!</strong></p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; color: #666;'>You've explored {st.session_state.hotels_total_loaded} hotels. Try adjusting filters for different options.</p>", unsafe_allow_html=True)
            else:
                st.info("No hotels match your filters. Try adjusting the criteria.")
                
                # Reset filters button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🔄 Reset All Filters", use_container_width=True, type="primary"):
                        st.session_state.hotel_price_range = (0, 1000)
                        st.session_state.hotel_min_rating = 0.0
                        st.session_state.hotel_room_type = "All"
                        st.session_state.hotel_amenities = []
                        st.session_state.hotel_budget_category = "All"
                        st.rerun()
        else:
            # Show placeholder
            st.info("👆 Enter a city and country to search for hotels!")