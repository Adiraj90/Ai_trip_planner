"""
AI Trip Planner - Main Application
Multi-agent AI-powered travel planning system
"""
import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import components
from components.header import render_header

# Import pages
from pages import home, plan_trip, hotels, foods, itineraries, auth, profile

# Import utilities
from utils.helpers import init_session_state


# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar completely
)

# Hide Streamlit's default navigation
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .stDeployButton {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def load_css():
    """Load custom CSS"""
    css_file = Path("assets/styles.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    # Navigation
    init_session_state('current_page', 'Home')
    
    # User authentication
    init_session_state('logged_in', False)
    init_session_state('user_id', None)
    init_session_state('username', None)
    init_session_state('user_email', None)
    
    # Trip planning data
    init_session_state('destination_city', '')
    init_session_state('destination_country', '')
    init_session_state('destination_info', None)
    init_session_state('current_trip_id', None)
    init_session_state('trip_data', None)
    
    # Filters and preferences
    init_session_state('hotel_filters', {})
    init_session_state('food_filters', {})
    
    # Generated data
    init_session_state('generated_itinerary', None)
    init_session_state('hotels_list', [])
    init_session_state('restaurants_list', [])


def handle_navigation():
    """Handle page navigation from URL parameters"""
    # Check URL parameters for page navigation
    query_params = st.query_params
    
    if 'page' in query_params:
        page = query_params['page']
        if page in ['Home', 'Plan Trip', 'Hotels', 'Foods', 'Itineraries', 'Login', 'Profile']:
            st.session_state.current_page = page


def render_page():
    """Render the current page based on session state"""
    current_page = st.session_state.current_page
    
    # Render header with current page highlighted
    render_header(current_page)
    
    # Render the appropriate page
    if current_page == "Home":
        home.render()
    elif current_page == "Plan Trip":
        plan_trip.render()
    elif current_page == "Hotels":
        hotels.render()
    elif current_page == "Foods":
        foods.render()
    elif current_page == "Itineraries":
        itineraries.render()
    elif current_page == "Login":
        auth.render()
    elif current_page == "Profile":
        profile.render()
    else:
        st.error(f"Page '{current_page}' not found")


def main():
    """Main application entry point"""
    # Load custom CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Handle navigation from URL
    handle_navigation()
    
    # Render current page
    render_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 2rem 0;">
            <p>© 2026 AI Trip Planner | Powered by AI Agents</p>
            <p style="font-size: 0.9rem;">Plan your perfect journey with intelligent recommendations</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()