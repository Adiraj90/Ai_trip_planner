"""
Home Page - Main entry point with destination search
"""
import streamlit as st
from agents.destination_agent import get_destination_agent
from utils.helpers import get_rating_stars
import time


def render_welcome_section():
    """Render welcome message and feature cards"""
    st.markdown("## Welcome to AI Trip Planner ✈️")
    st.markdown("### Your Intelligent Travel Companion")
    st.markdown("---")
    
    # Feature cards
    st.markdown("#### 🌟 What We Offer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Smart Planning</div>
            <div class="feature-description">
                AI-powered itinerary generation tailored to your preferences and budget
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏨</div>
            <div class="feature-title">Perfect Stays</div>
            <div class="feature-description">
                Curated hotel recommendations matching your style and budget
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🍜</div>
            <div class="feature-title">Local Flavors</div>
            <div class="feature-description">
                Discover authentic local cuisine and hidden gem restaurants
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_destination_search():
    """Render destination search input"""
    st.markdown("---")
    st.markdown("### 🌍 Explore Your Dream Destination")
    st.markdown("Enter a city and country to discover everything you need to know!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # City and Country input
        input_col1, input_col2 = st.columns(2)
        
        with input_col1:
            city = st.text_input(
                "City",
                placeholder="e.g., Paris",
                key="destination_city_input"
            )
        
        with input_col2:
            country = st.text_input(
                "Country",
                placeholder="e.g., France",
                key="destination_country_input"
            )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Explore Destination",
            use_container_width=True,
            type="primary"
        )
    
    return city, country, search_button


def render_destination_info(info: dict):
    """Render complete destination information"""
    
    # City Header
    st.markdown(f"# {info['city']}, {info['country']} 🌆")
    
    # Description
    st.markdown(f"### About {info['city']}")
    st.markdown(f"*{info['description']}*")
    
    st.markdown("---")
    
    # Images Gallery - Ensure at least 4 images
    st.markdown("### 📸 Glimpse of the City")
    images = info.get('images', [])
    
    # Ensure we have at least 4 images
    if len(images) < 4:
        from utils.image_service import get_image_service
        image_service = get_image_service()
        city = info.get('city', '')
        country = info.get('country', '')
        additional_images = image_service.get_city_images(city, country, count=4-len(images))
        images = images + additional_images
    
    if images:
        # Display exactly 4 images
        display_images = images[:4] if len(images) >= 4 else images
        
        # Ensure we have 4 images, fill with placeholder if needed
        while len(display_images) < 4:
            display_images.append("https://picsum.photos/800/600?random=" + str(len(display_images)))
        
        cols = st.columns(4)
        for idx, img_url in enumerate(display_images):
            if idx < 4 and img_url:
                try:
                    with cols[idx]:
                        # Add error handling with timeout
                        st.image(
                            img_url, 
                            use_container_width=True, 
                            caption=f"{info.get('city', 'City')} - Image {idx+1}",
                            output_format="PNG"
                        )
                except Exception as e:
                    # If image fails to load, show placeholder
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                            <div style="color: white; font-size: 3rem;">🏙️</div>
                        </div>
                        <p style="text-align: center; color: #666; margin-top: 5px;">{info.get('city', 'City')} - Image {idx+1}</p>
                        """, unsafe_allow_html=True)
    else:
        # Generate fallback images if none available
        from utils.image_service import get_image_service
        image_service = get_image_service()
        city = info.get('city', '')
        country = info.get('country', '')
        fallback_images = image_service._get_lorem_picsum_images(f"{city} {country}", 4)
        
        cols = st.columns(4)
        for idx, img_url in enumerate(fallback_images):
            if idx < 4:
                try:
                    with cols[idx]:
                        st.image(img_url, use_container_width=True, caption=f"{city} - Image {idx+1}")
                except:
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                            <div style="color: white; font-size: 3rem;">🏙️</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Popular Places
    st.markdown("### 🏛️ Popular Places to Visit")
    if info['popular_places']:
        for place in info['popular_places']:
            render_place_card(place)
    else:
        st.info("No popular places information available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Culture and Language
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎭 Culture & Traditions")
        st.markdown(f"<div class='info-box'>{info['culture']}</div>", unsafe_allow_html=True)
        
        st.markdown("### 🗣️ Local Language")
        st.markdown(f"<div class='info-box'><strong>{info['local_language']}</strong></div>", unsafe_allow_html=True)
    
    with col2:
        if info.get('best_time_to_visit'):
            st.markdown("### 🌤️ Best Time to Visit")
            st.markdown(f"<div class='info-box'>{info['best_time_to_visit']}</div>", unsafe_allow_html=True)
        
        if info.get('local_tips'):
            st.markdown("### 💡 Local Tips")
            st.markdown(f"<div class='info-box'>{info['local_tips']}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Famous Foods
    st.markdown("### 🍽️ Must-Try Local Cuisine")
    if info['famous_foods']:
        food_cols = st.columns(min(3, len(info['famous_foods'])))
        for idx, food in enumerate(info['famous_foods']):
            col_idx = idx % 3
            with food_cols[col_idx]:
                st.markdown(f"""
                <div class="place-card">
                    <div class="place-card-header">
                        <div class="place-name">🍜 {food.get('name', 'Unknown')}</div>
                    </div>
                    <p style="color: #666;">{food.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Plan My Trip Button
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🗺️ Plan My Trip", use_container_width=True, type="primary", key="plan_trip_btn"):
            # Save destination to session state
            st.session_state.destination_city = info['city']
            st.session_state.destination_country = info['country']
            st.session_state.destination_info = info
            st.session_state.current_page = "Plan Trip"
            st.rerun()


def render_place_card(place: dict):
    """Render a single place card"""
    maps_link = place.get('maps_link', '#')
    
    st.markdown(f"""
    <div class="place-card">
        <div class="place-card-header">
            <div class="place-name">{place.get('name', 'Unknown Place')}</div>
            <div class="place-category">{place.get('category', 'Attraction')}</div>
        </div>
        <p style="color: #666; margin-bottom: 1rem;">{place.get('description', '')}</p>
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button">📍 View on Google Maps</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


def render():
    """Main render function for Home page"""
    
    # Welcome section
    render_welcome_section()
    
    # Destination search
    city, country, search_clicked = render_destination_search()
    
    # Handle search
    if search_clicked:
        if not city or not country:
            st.error("⚠️ Please enter both city and country!")
        else:
            with st.spinner(f"🔍 Researching {city}, {country}... This may take a moment..."):
                try:
                    # Get destination agent
                    agent = get_destination_agent()
                    
                    # Get destination info
                    info = agent.get_destination_info(city.strip(), country.strip())
                    
                    if info:
                        st.session_state.destination_info = info
                        st.session_state.destination_city = city.strip()
                        st.session_state.destination_country = country.strip()
                        st.success(f"✅ Information loaded for {city}, {country}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Failed to get destination information. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display destination info if available
    if st.session_state.get('destination_info'):
        st.markdown("---")
        render_destination_info(st.session_state.destination_info)