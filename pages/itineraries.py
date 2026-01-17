"""
Itineraries Page - View saved trips and popular itineraries
"""
import streamlit as st
from agents.itinerary_agent import get_itinerary_agent
from database.queries import (
    delete_trip, add_favorite_trip, remove_favorite_trip, is_trip_favorited, get_user_favorites,
    get_user_bookmarks, remove_bookmark_hotel, remove_bookmark_restaurant
)
from utils.helpers import format_date_readable, get_trip_type_emoji, format_currency, get_food_type_emoji
from utils.pdf_generator import generate_trip_pdf, generate_filename
from datetime import date, timedelta
import json


def render_popular_trips():
    """Render popular pre-made trip cards"""
    st.markdown("### 🌟 Popular Trip Ideas")
    
    # Get user's country if logged in
    user_country = None
    if st.session_state.get('logged_in'):
        user_country = st.session_state.get('user_country', 'USA')
        st.markdown(f"*Personalized trips for travelers from {user_country}*")
    else:
        st.markdown("*Click on any trip to customize and plan your journey*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # All available trips by country
    all_trips = {
        "India": [
            {
                "title": "Golden Triangle Experience",
                "destination": "Delhi-Agra-Jaipur, India",
                "duration": "7 Days",
                "type": "Cultural",
                "emoji": "🕌",
                "description": "Discover India's rich heritage through the iconic Golden Triangle circuit.",
                "highlights": ["Taj Mahal", "Amber Fort", "Red Fort", "Hawa Mahal"],
                "budget": "50000 INR"
            },
            {
                "title": "Kerala Backwaters & Beaches",
                "destination": "Kerala, India",
                "duration": "6 Days",
                "type": "Relaxation",
                "emoji": "🏝️",
                "description": "Experience God's Own Country with serene backwaters and pristine beaches.",
                "highlights": ["Houseboat Stay", "Munnar Hills", "Kovalam Beach", "Kathakali Dance"],
                "budget": "40000 INR"
            },
            {
                "title": "Rajasthan Desert Safari",
                "destination": "Rajasthan, India",
                "duration": "8 Days",
                "type": "Adventure",
                "emoji": "🐪",
                "description": "Royal palaces, desert camps, and cultural experiences in the land of kings.",
                "highlights": ["Camel Safari", "Udaipur Palace", "Jaisalmer Fort", "Cultural Shows"],
                "budget": "60000 INR"
            },
            {
                "title": "Goa Beach Paradise",
                "destination": "Goa, India",
                "duration": "5 Days",
                "type": "Relaxation",
                "emoji": "🏖️",
                "description": "Sun, sand, and sea with vibrant nightlife and Portuguese heritage.",
                "highlights": ["Beach Hopping", "Water Sports", "Old Goa Churches", "Night Markets"],
                "budget": "35000 INR"
            },
            {
                "title": "Himalayan Adventure",
                "destination": "Himachal Pradesh, India",
                "duration": "7 Days",
                "type": "Adventure",
                "emoji": "🏔️",
                "description": "Mountain treks, valley views, and adventure sports in the Himalayas.",
                "highlights": ["Manali", "Rohtang Pass", "Solang Valley", "Paragliding"],
                "budget": "45000 INR"
            },
            {
                "title": "South India Temple Tour",
                "destination": "Tamil Nadu, India",
                "duration": "6 Days",
                "type": "Cultural",
                "emoji": "🛕",
                "description": "Ancient temples, classical arts, and rich cultural heritage of South India.",
                "highlights": ["Meenakshi Temple", "Mahabalipuram", "Thanjavur", "Classical Dance"],
                "budget": "38000 INR"
            }
        ],
        "USA": [
            {
                "title": "Silicon Valley Tech Tour",
                "destination": "San Francisco, USA",
                "duration": "5 Days",
                "type": "Business",
                "emoji": "💼",
                "description": "Explore the heart of tech innovation with visits to major tech companies.",
                "highlights": ["Google HQ", "Apple Park", "Stanford University", "SF Tech Museum"],
                "budget": "2500 USD"
            },
            {
                "title": "New York City Explorer",
                "destination": "New York, USA",
                "duration": "6 Days",
                "type": "City",
                "emoji": "🗽",
                "description": "The city that never sleeps - iconic landmarks and world-class culture.",
                "highlights": ["Statue of Liberty", "Times Square", "Central Park", "Broadway Shows"],
                "budget": "3000 USD"
            },
            {
                "title": "Grand Canyon Adventure",
                "destination": "Arizona, USA",
                "duration": "5 Days",
                "type": "Adventure",
                "emoji": "🏜️",
                "description": "Natural wonder exploration with hiking and breathtaking canyon views.",
                "highlights": ["Grand Canyon", "Horseshoe Bend", "Antelope Canyon", "Desert Trails"],
                "budget": "2000 USD"
            },
            {
                "title": "Miami Beach Getaway",
                "destination": "Miami, USA",
                "duration": "5 Days",
                "type": "Relaxation",
                "emoji": "🌴",
                "description": "Tropical paradise with vibrant culture, beaches, and nightlife.",
                "highlights": ["South Beach", "Art Deco District", "Little Havana", "Water Sports"],
                "budget": "2200 USD"
            },
            {
                "title": "Las Vegas Entertainment",
                "destination": "Las Vegas, USA",
                "duration": "4 Days",
                "type": "Nightlife",
                "emoji": "🎰",
                "description": "Entertainment capital with world-class shows, casinos, and dining.",
                "highlights": ["The Strip", "Cirque du Soleil", "Grand Canyon Tour", "Nightclubs"],
                "budget": "1800 USD"
            },
            {
                "title": "Yellowstone Nature Tour",
                "destination": "Wyoming, USA",
                "duration": "6 Days",
                "type": "Adventure",
                "emoji": "🦌",
                "description": "America's first national park with geysers, wildlife, and natural beauty.",
                "highlights": ["Old Faithful", "Grand Prismatic", "Wildlife Safari", "Hot Springs"],
                "budget": "2400 USD"
            }
        ],
        "International": [
            {
                "title": "Paris Romantic Getaway",
                "destination": "Paris, France",
                "duration": "4 Days",
                "type": "Romantic",
                "emoji": "💑",
                "description": "Experience the city of love with romantic walks and fine dining.",
                "highlights": ["Eiffel Tower", "Louvre Museum", "Seine River Cruise", "Montmartre"],
                "budget": "1800 EUR"
            },
            {
                "title": "Tokyo Food Adventure",
                "destination": "Tokyo, Japan",
                "duration": "6 Days",
                "type": "Culinary",
                "emoji": "🍜",
                "description": "A gastronomic journey through Tokyo's diverse food scene.",
                "highlights": ["Tsukiji Market", "Ramen Streets", "Sushi Experience", "Izakaya Hopping"],
                "budget": "200000 JPY"
            },
            {
                "title": "Bali Beach Escape",
                "destination": "Bali, Indonesia",
                "duration": "8 Days",
                "type": "Relaxation",
                "emoji": "🏖️",
                "description": "Unwind on pristine beaches and explore temples.",
                "highlights": ["Seminyak Beach", "Ubud Rice Terraces", "Tanah Lot Temple", "Beach Clubs"],
                "budget": "1500 USD"
            },
            {
                "title": "Swiss Alps Adventure",
                "destination": "Switzerland",
                "duration": "7 Days",
                "type": "Adventure",
                "emoji": "🏔️",
                "description": "Thrilling mountain adventures with skiing and Alpine views.",
                "highlights": ["Jungfrau", "Matterhorn", "Interlaken", "Lake Geneva"],
                "budget": "3000 CHF"
            },
            {
                "title": "Dubai Luxury Experience",
                "destination": "Dubai, UAE",
                "duration": "5 Days",
                "type": "Luxury",
                "emoji": "🏙️",
                "description": "Futuristic city with luxury shopping, dining, and architecture.",
                "highlights": ["Burj Khalifa", "Palm Jumeirah", "Desert Safari", "Dubai Mall"],
                "budget": "3500 USD"
            },
            {
                "title": "Thailand Island Hopping",
                "destination": "Thailand",
                "duration": "10 Days",
                "type": "Beach",
                "emoji": "🏝️",
                "description": "Tropical paradise with stunning islands and Thai hospitality.",
                "highlights": ["Phuket", "Phi Phi Islands", "Krabi", "Bangkok Temples"],
                "budget": "1200 USD"
            }
        ]
    }
    
    # Select trips based on user's country
    if user_country:
        if user_country == "India":
            popular_trips = all_trips["India"]
        elif user_country in ["USA", "United States", "America"]:
            popular_trips = all_trips["USA"]
        else:
            # Show international trips for other countries
            popular_trips = all_trips["International"]
    else:
        # Guest users see a mix of all trips
        popular_trips = (
            all_trips["International"][:2] + 
            all_trips["India"][:2] + 
            all_trips["USA"][:2]
        )
    
    # Display in grid
    cols = st.columns(2)
    
    for idx, trip in enumerate(popular_trips):
        col = cols[idx % 2]
        
        with col:
            render_popular_trip_card(trip, idx)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_popular_trip_card(trip: dict, idx: int):
    """Render a single popular trip card"""
    
    # Ensure trip data is in correct format (handle both dict and string keys)
    title = trip.get('title', '') if isinstance(trip, dict) else str(trip.get('title', ''))
    destination = trip.get('destination', '') if isinstance(trip, dict) else str(trip.get('destination', ''))
    duration = trip.get('duration', '') if isinstance(trip, dict) else str(trip.get('duration', ''))
    emoji = trip.get('emoji', '✈️') if isinstance(trip, dict) else str(trip.get('emoji', '✈️'))
    description = trip.get('description', '') if isinstance(trip, dict) else str(trip.get('description', ''))
    budget = trip.get('budget', '') if isinstance(trip, dict) else str(trip.get('budget', ''))
    
    # Ensure highlights is always a list
    highlights = trip.get('highlights', [])
    if not isinstance(highlights, list):
        if isinstance(highlights, str):
            # Try to parse if it's a JSON string
            try:
                highlights = json.loads(highlights)
            except:
                highlights = [highlights] if highlights else []
        else:
            highlights = []
    
    # Format highlights - ensure HTML-safe
    highlights_list = [str(highlight) for highlight in highlights] if highlights else []
    highlights_html = '<br>'.join([f"• {highlight}" for highlight in highlights_list]) if highlights_list else "No highlights available"
    
    # Check if user is logged in and if trip is favorited
    is_favorited = False
    user_id = st.session_state.get('user_id')
    if user_id:
        is_favorited = is_trip_favorited(
            user_id,
            popular_trip_title=title,
            popular_trip_destination=destination
        )
    
    # Build heart icon HTML if user is logged in
    heart_html = ""
    if user_id:
        heart_color = "#ff6b6b" if is_favorited else "#ccc"
        heart_emoji = "❤️" if is_favorited else "🤍"
        heart_title = "Remove from favorites" if is_favorited else "Add to favorites"
        heart_html = f'<div style="font-size: 1.5rem; color: {heart_color};" title="{heart_title}">{heart_emoji}</div>'
    
    # Build the HTML string using string concatenation to avoid f-string issues
    html_content = (
        '<div class="feature-card">'
        '<div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">'
        f'<div style="text-align: center; font-size: 3rem; flex: 1;">{emoji}</div>'
        f'{heart_html}'
        '</div>'
        f'<div class="feature-title" style="text-align: center;">{title}</div>'
        f'<div style="text-align: center; color: #667eea; font-weight: 600; margin-bottom: 1rem;">📍 {destination} • ⏱️ {duration}</div>'
        f'<div class="feature-description" style="margin-bottom: 1rem;">{description}</div>'
        '<div style="margin: 1rem 0;">'
        '<strong style="color: #667eea;">Highlights:</strong><br>'
        '<div style="margin-top: 0.5rem;">'
        f'{highlights_html}'
        '</div>'
        '</div>'
        '<div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">'
        '<span style="color: #666;">Budget: </span>'
        f'<span style="color: #667eea; font-weight: bold;">{budget}</span>'
        '</div>'
        '</div>'
    )
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"✨ Customize This Trip", use_container_width=True, key=f"popular_trip_{idx}", type="primary"):
            # Extract city from destination
            destination_str = trip.get('destination', '') if isinstance(trip, dict) else str(trip.get('destination', ''))
            dest_parts = destination_str.split(',')
            city = dest_parts[0].strip()
            country = dest_parts[1].strip() if len(dest_parts) > 1 else ""
            
            # Pre-fill Plan Trip page
            st.session_state.destination_city = city
            st.session_state.destination_country = country
            st.session_state.plan_city = city
            st.session_state.plan_country = country
            st.session_state.plan_trip_type = trip.get('type', 'Travel') if isinstance(trip, dict) else str(trip.get('type', 'Travel'))
            
            # Navigate to Plan Trip
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col2:
        if user_id:
            if is_favorited:
                if st.button(f"❤️ Remove from Favorites", use_container_width=True, key=f"unfavorite_popular_{idx}"):
                    if remove_favorite_trip(
                        user_id,
                        popular_trip_title=trip['title'],
                        popular_trip_destination=trip['destination']
                    ):
                        st.success("Removed from favorites!")
                        st.rerun()
                    else:
                        st.error("Failed to remove from favorites")
            else:
                if st.button(f"🤍 Add to Favorites", use_container_width=True, key=f"favorite_popular_{idx}"):
                    # Ensure trip data is properly formatted
                    trip_data = trip if isinstance(trip, dict) else dict(trip)
                    if add_favorite_trip(user_id, popular_trip_data=trip_data):
                        st.success("Added to favorites! ❤️")
                        st.rerun()
                    else:
                        st.error("Failed to add to favorites")
        else:
            st.button("🔐 Login to Favorite", use_container_width=True, key=f"login_popular_{idx}", disabled=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_user_trips():
    """Render user's saved trips"""
    st.markdown("### 📋 Your Saved Trips")
    
    # Check if user is logged in
    if not st.session_state.get('logged_in'):
        st.info("🔐 Please login to view your saved trips")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Login Now", use_container_width=True, type="primary", key="login_saved_trips"):
                st.session_state.current_page = "Login"
                st.rerun()
        
        return
    
    # Get user trips from database
    user_id = st.session_state.get('user_id')
    
    if user_id:
        agent = get_itinerary_agent()
        trips = agent.get_user_trips(user_id)
        
        if trips:
            st.markdown(f"*You have {len(trips)} saved trip(s)*")
            st.markdown("<br>", unsafe_allow_html=True)
            
            for trip in trips:
                render_saved_trip_card(trip)
        else:
            st.info("You haven't planned any trips yet! Start planning your first adventure.")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("Plan a Trip", use_container_width=True, type="primary", key="plan_trip_from_saved"):
                    st.session_state.current_page = "Plan Trip"
                    st.rerun()
    else:
        st.warning("Unable to load trips. Please try logging in again.")


def render_saved_trip_card(trip: dict, context: str = "saved"):
    """
    Render a saved trip card
    
    Args:
        trip: Trip dictionary
        context: Context prefix for unique keys ('saved' or 'favs')
    """
    
    trip_id = trip.get('trip_id')
    destination_city = trip.get('destination_city', 'Unknown')
    destination_country = trip.get('destination_country', '')
    start_date = trip.get('start_date')
    end_date = trip.get('end_date')
    budget = trip.get('budget', 0)
    currency = trip.get('currency', 'USD')
    trip_type = trip.get('trip_type', 'Travel')
    num_people = trip.get('num_people', 1)
    created_at = trip.get('created_at')
    
    # Format dates
    if isinstance(start_date, str):
        from datetime import datetime
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
    
    duration = (end_date - start_date).days + 1
    
    # Trip type emoji
    emoji = get_trip_type_emoji(trip_type)
    
    st.markdown(f"""
    <div class="place-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: bold; color: #333; margin-bottom: 0.5rem;">
                    {emoji} {destination_city}, {destination_country}
                </div>
                <div style="color: #666; margin-bottom: 0.5rem;">
                    📅 {format_date_readable(start_date)} - {format_date_readable(end_date)} ({duration} days)
                </div>
                <div style="color: #666; margin-bottom: 0.5rem;">
                    💰 Budget: {format_currency(budget, currency)} • 👥 {num_people} {'person' if num_people == 1 else 'people'}
                </div>
                <div style="color: #888; font-size: 0.9rem;">
                    Trip Type: {trip_type} • Created: {created_at.strftime('%b %d, %Y') if created_at else 'N/A'}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if trip is favorited
    user_id = st.session_state.get('user_id')
    is_favorited = False
    if user_id:
        is_favorited = is_trip_favorited(user_id, trip_id=trip_id)
    
    # Action buttons - use context prefix for unique keys
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("👁️ View Details", key=f"{context}_view_trip_{trip_id}", use_container_width=True):
            # Load trip details
            st.session_state.viewing_trip_id = trip_id
            st.session_state.show_trip_details = True
            st.rerun()
    
    with col2:
        if st.button("✏️ Modify Trip", key=f"{context}_edit_trip_{trip_id}", use_container_width=True):
            # Pre-fill Plan Trip form
            st.session_state.destination_city = destination_city
            st.session_state.destination_country = destination_country
            st.session_state.plan_city = destination_city
            st.session_state.plan_country = destination_country
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col3:
        if st.button("📄 Export PDF", key=f"{context}_export_trip_{trip_id}", use_container_width=True):
            st.session_state[f'{context}_export_trip_pdf_{trip_id}'] = True
    
    with col4:
        if user_id:
            if is_favorited:
                if st.button("❤️ Favorited", key=f"{context}_unfavorite_trip_{trip_id}", use_container_width=True):
                    if remove_favorite_trip(user_id, trip_id=trip_id):
                        st.success("Removed from favorites!")
                        st.rerun()
                    else:
                        st.error("Failed to remove from favorites")
            else:
                if st.button("🤍 Favorite", key=f"{context}_favorite_trip_{trip_id}", use_container_width=True):
                    if add_favorite_trip(user_id, trip_id=trip_id):
                        st.success("Added to favorites! ❤️")
                        st.rerun()
                    else:
                        st.error("Failed to add to favorites")
        else:
            st.button("🔐 Login", key=f"{context}_login_trip_{trip_id}", use_container_width=True, disabled=True)
    
    with col5:
        if st.button("🗑️ Delete", key=f"{context}_delete_trip_{trip_id}", use_container_width=True, type="secondary"):
            st.session_state[f'{context}_confirm_delete_{trip_id}'] = True
    
    # Handle PDF export
    if st.session_state.get(f'{context}_export_trip_pdf_{trip_id}'):
        try:
            # Get full trip details
            agent = get_itinerary_agent()
            full_trip = agent.get_trip_by_id(trip_id)
            
            if full_trip and full_trip.get('itinerary'):
                trip_data = {
                    'start_date': full_trip['start_date'].isoformat() if hasattr(full_trip['start_date'], 'isoformat') else str(full_trip['start_date']),
                    'end_date': full_trip['end_date'].isoformat() if hasattr(full_trip['end_date'], 'isoformat') else str(full_trip['end_date']),
                    'budget': full_trip['budget'],
                    'currency': full_trip['currency'],
                    'num_people': full_trip['num_people'],
                    'trip_type': full_trip['trip_type']
                }
                
                pdf_buffer = generate_trip_pdf(trip_data, full_trip['itinerary'])
                filename = generate_filename(f"{destination_city}, {destination_country}")
                
                st.success("✅ PDF generated!")
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"{context}_download_trip_pdf_{trip_id}"
                )
                
                if st.button("✅ Done", key=f"{context}_done_export_{trip_id}"):
                    del st.session_state[f'{context}_export_trip_pdf_{trip_id}']
                    st.rerun()
            else:
                st.error("Unable to load trip details for PDF generation")
        except Exception as e:
            st.error(f"Failed to generate PDF: {str(e)}")
    
    # Show delete confirmation if requested
    if st.session_state.get(f'{context}_confirm_delete_{trip_id}'):
        st.warning(f"⚠️ Are you sure you want to delete this trip to {destination_city}?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Yes, Delete", key=f"{context}_confirm_yes_{trip_id}", type="primary"):
                user_id = st.session_state.get('user_id')
                if delete_trip(trip_id, user_id):
                    st.success("✅ Trip deleted successfully!")
                    # Remove confirmation flag
                    del st.session_state[f'{context}_confirm_delete_{trip_id}']
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to delete trip. Please try again.")
        
        with col2:
            if st.button("❌ Cancel", key=f"{context}_confirm_no_{trip_id}"):
                del st.session_state[f'{context}_confirm_delete_{trip_id}']
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_trip_details(trip_id: int):
    """Render detailed view of a trip"""
    agent = get_itinerary_agent()
    trip = agent.get_trip_by_id(trip_id)
    
    if not trip:
        st.error("Trip not found!")
        return
    
    # Back button
    if st.button("← Back to Itineraries"):
        st.session_state.show_trip_details = False
        st.session_state.viewing_trip_id = None
        st.rerun()
    
    st.markdown("---")
    
    # Display trip details
    st.markdown(f"## 🗺️ {trip['destination_city']}, {trip['destination_country']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{(trip['end_date'] - trip['start_date']).days + 1} Days")
    
    with col2:
        st.metric("Budget", format_currency(trip['budget'], trip['currency']))
    
    with col3:
        st.metric("Travelers", f"{trip['num_people']} People")
    
    with col4:
        st.markdown(f"**Type:** {get_trip_type_emoji(trip['trip_type'])} {trip['trip_type']}")
    
    st.markdown("---")
    
    # Display itinerary if available
    if trip.get('itinerary'):
        itinerary = trip['itinerary']
        
        if itinerary.get('trip_overview'):
            st.markdown("### 📖 Trip Overview")
            st.info(itinerary['trip_overview'])
        
        st.markdown("### 📅 Day-by-Day Plan")
        
        for day_info in itinerary.get('daily_itinerary', []):
            render_day_summary(day_info)
    else:
        st.info("No detailed itinerary available for this trip.")


def render_day_summary(day_info: dict):
    """Render a compact day summary"""
    day_num = day_info.get('day', 1)
    day_title = day_info.get('title', f'Day {day_num}')
    activities = day_info.get('activities', [])
    
    with st.expander(f"**Day {day_num}: {day_title}**", expanded=False):
        if activities:
            for activity in activities:
                st.markdown(f"• **{activity.get('time', '')}** - {activity.get('activity', '')}")
        else:
            st.info("No activities planned")


def render_favorites():
    """Render user's favorite trips"""
    st.markdown("### ❤️ Your Favorite Trips")
    
    # Check if user is logged in
    if not st.session_state.get('logged_in'):
        st.info("🔐 Please login to view your favorite trips")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Login Now", use_container_width=True, type="primary", key="login_favorites"):
                st.session_state.current_page = "Login"
                st.rerun()
        
        return
    
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.warning("Unable to load favorites. Please try logging in again.")
        return
    
    # Get user favorites
    favorites = get_user_favorites(user_id)
    saved_trips = favorites.get('saved_trips', [])
    popular_trips = favorites.get('popular_trips', [])
    
    total_favorites = len(saved_trips) + len(popular_trips)
    
    if total_favorites == 0:
        st.info("💔 You haven't favorited any trips yet! Click the ❤️ or 🤍 button on any trip to add it to your favorites.")
        return
    
    st.markdown(f"*You have {total_favorites} favorite trip(s)*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display saved trip favorites
    if saved_trips:
        st.markdown("#### 📋 Your Saved Trip Favorites")
        for trip in saved_trips:
            render_saved_trip_card(trip, context="favs")
    
    # Display popular trip favorites
    if popular_trips:
        st.markdown("#### 🌟 Popular Trip Favorites")
        
        # Display in grid
        cols = st.columns(2)
        
        for idx, trip in enumerate(popular_trips):
            col = cols[idx % 2]
            
            with col:
                render_favorite_popular_trip_card(trip, idx)


def render_favorite_popular_trip_card(trip: dict, idx: int):
    """Render a favorite popular trip card"""
    
    # Ensure all values are properly formatted
    emoji = str(trip.get('emoji', '✈️'))
    title = str(trip.get('title', 'Unknown Trip'))
    destination = str(trip.get('destination', 'Unknown'))
    duration = str(trip.get('duration', 'N/A'))
    description = str(trip.get('description', 'No description available'))
    budget = str(trip.get('budget', 'N/A'))
    
    # Ensure highlights is always a list
    highlights = trip.get('highlights', [])
    if not isinstance(highlights, list):
        if isinstance(highlights, str):
            # Try to parse if it's a JSON string
            try:
                highlights = json.loads(highlights)
            except:
                highlights = [highlights] if highlights else []
        else:
            highlights = []
    
    # Format highlights
    highlights_html = '<br>'.join([f"• {str(highlight)}" for highlight in highlights]) if highlights else "No highlights available"
    
    st.markdown(f"""
    <div class="feature-card">
        <div style="text-align: center; font-size: 3rem; margin-bottom: 1rem;">
            {emoji}
        </div>
        <div class="feature-title" style="text-align: center;">
            {title}
        </div>
        <div style="text-align: center; color: #667eea; font-weight: 600; margin-bottom: 1rem;">
            📍 {destination} • ⏱️ {duration}
        </div>
        <div class="feature-description" style="margin-bottom: 1rem;">
            {description}
        </div>
        <div style="margin: 1rem 0;">
            <strong style="color: #667eea;">Highlights:</strong><br>
            <div style="margin-top: 0.5rem;">
                {highlights_html}
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">
            <span style="color: #666;">Budget: </span>
            <span style="color: #667eea; font-weight: bold;">{budget}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"✨ Customize This Trip", use_container_width=True, key=f"fav_customize_{idx}", type="primary"):
            # Extract city from destination
            destination = trip.get('destination', '')
            dest_parts = destination.split(',')
            city = dest_parts[0].strip()
            country = dest_parts[1].strip() if len(dest_parts) > 1 else ""
            
            # Pre-fill Plan Trip page
            st.session_state.destination_city = city
            st.session_state.destination_country = country
            st.session_state.plan_city = city
            st.session_state.plan_country = country
            st.session_state.plan_trip_type = trip.get('type', 'Travel')
            
            # Navigate to Plan Trip
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col2:
        user_id = st.session_state.get('user_id')
        if st.button(f"❤️ Remove from Favorites", use_container_width=True, key=f"fav_remove_{idx}"):
            if remove_favorite_trip(
                user_id,
                popular_trip_title=trip.get('title', ''),
                popular_trip_destination=trip.get('destination', '')
            ):
                st.success("Removed from favorites!")
                st.rerun()
            else:
                st.error("Failed to remove from favorites")
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_bookmarks():
    """Render user's bookmarked hotels and restaurants"""
    st.markdown("### 🔖 Your Bookmarks")
    
    # Check if user is logged in
    if not st.session_state.get('logged_in'):
        st.info("🔐 Please login to view your bookmarks")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Login Now", use_container_width=True, type="primary", key="login_bookmarks"):
                st.session_state.current_page = "Login"
                st.rerun()
        
        return
    
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.warning("Unable to load bookmarks. Please try logging in again.")
        return
    
    # Get user bookmarks
    bookmarks = get_user_bookmarks(user_id)
    hotels = bookmarks.get('hotels', [])
    restaurants = bookmarks.get('restaurants', [])
    
    total_bookmarks = len(hotels) + len(restaurants)
    
    if total_bookmarks == 0:
        st.info("💔 You haven't bookmarked any hotels or restaurants yet! Click the 🔖 button on any hotel or restaurant to bookmark it.")
        return
    
    st.markdown(f"*You have {total_bookmarks} bookmark(s)*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create subsections for Hotels and Restaurants
    bookmark_tab1, bookmark_tab2 = st.tabs(["🏨 Hotels", "🍽️ Restaurants"])
    
    with bookmark_tab1:
        render_bookmarked_hotels(hotels)
    
    with bookmark_tab2:
        render_bookmarked_restaurants(restaurants)


def render_bookmarked_hotels(hotels: list):
    """Render bookmarked hotels"""
    if not hotels:
        st.info("🏨 No bookmarked hotels yet. Search for hotels and bookmark the ones you like!")
        return
    
    st.markdown(f"#### 🏨 Bookmarked Hotels ({len(hotels)})")
    
    for hotel in hotels:
        render_bookmarked_hotel_card(hotel)


def render_bookmarked_hotel_card(hotel: dict):
    """Render a bookmarked hotel card"""
    name = hotel.get('name', 'Hotel')
    description = hotel.get('description', 'No description available')
    location = hotel.get('location', 'Location')
    price = hotel.get('price_per_night', 0)
    rating = hotel.get('rating', 0)
    image_url = hotel.get('image_url', 'https://source.unsplash.com/800x600/?hotel,luxury')
    amenities = hotel.get('amenities', [])
    room_type = hotel.get('room_type', 'Room')
    maps_link = hotel.get('maps_link', '#')
    city = hotel.get('city', '')
    country = hotel.get('country', '')
    
    # Get currency from session state
    currency = st.session_state.get('plan_currency', 'USD')
    
    # Format rating
    try:
        rating_value = float(rating)
    except (ValueError, TypeError):
        rating_value = 0.0
    
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
    
    # Hotel card
    st.markdown(f"""
    <div class="horizontal-card">
        <img src="{image_url}" class="card-image" alt="{name}">
        <div class="card-content">
            <div>
                <div class="card-title">{name}</div>
                <div style="color: #888; margin-bottom: 0.5rem;">
                    📍 {location} • 🛏️ {room_type}
                    {f' • 🌍 {city}, {country}' if city and country else ''}
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
    
    # Action buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button" style="width: 100%; padding: 10px;">
                📍 View on Google Maps
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        user_id = st.session_state.get('user_id')
        if st.button("🔖 Remove Bookmark", use_container_width=True, key=f"remove_hotel_bookmark_{hotel.get('bookmark_id', 0)}"):
            if remove_bookmark_hotel(user_id, name, location):
                st.success("Removed from bookmarks!")
                st.rerun()
            else:
                st.error("Failed to remove bookmark")
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_bookmarked_restaurants(restaurants: list):
    """Render bookmarked restaurants"""
    if not restaurants:
        st.info("🍽️ No bookmarked restaurants yet. Search for restaurants and bookmark the ones you like!")
        return
    
    st.markdown(f"#### 🍽️ Bookmarked Restaurants ({len(restaurants)})")
    
    for restaurant in restaurants:
        render_bookmarked_restaurant_card(restaurant)


def render_bookmarked_restaurant_card(restaurant: dict):
    """Render a bookmarked restaurant card"""
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
    city = restaurant.get('city', '')
    country = restaurant.get('country', '')
    
    # Format rating
    try:
        rating_value = float(rating)
    except (ValueError, TypeError):
        rating_value = 0.0
    
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
    
    # Restaurant card
    st.markdown(f"""
    <div class="horizontal-card">
        <img src="{image_url}" class="card-image" alt="{name}">
        <div class="card-content">
            <div>
                <div class="card-title">{name}</div>
                <div style="color: #888; margin-bottom: 0.5rem;">
                    📍 {location} • 🍽️ {cuisine} • {food_emoji} {food_type}
                    {f' • 🌍 {city}, {country}' if city and country else ''}
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
    
    # Action buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button" style="width: 100%; padding: 10px;">
                📍 View on Google Maps
            </button>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        user_id = st.session_state.get('user_id')
        if st.button("🔖 Remove Bookmark", use_container_width=True, key=f"remove_restaurant_bookmark_{restaurant.get('bookmark_id', 0)}"):
            if remove_bookmark_restaurant(user_id, name, location):
                st.success("Removed from bookmarks!")
                st.rerun()
            else:
                st.error("Failed to remove bookmark")
    
    st.markdown("<br>", unsafe_allow_html=True)


def render():
    """Main render function for Itineraries page"""
    
    st.markdown("## 📋 Trip Itineraries")
    st.markdown("*Explore popular trips or view your saved itineraries*")
    st.markdown("---")
    
    # Check if viewing trip details
    if st.session_state.get('show_trip_details') and st.session_state.get('viewing_trip_id'):
        render_trip_details(st.session_state.viewing_trip_id)
        return
    
    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs(["🌟 Popular Trips", "📋 Your Trips", "Your Favs", "🔖 Bookmarks"])
    
    with tab1:
        render_popular_trips()
    
    with tab2:
        render_user_trips()

    with tab3:
        render_favorites()
    
    with tab4:
        render_bookmarks()