"""
Header component with navigation
"""
import streamlit as st


def render_header(current_page: str = "Home"):
    """
    Render the custom header with navigation
    
    Args:
        current_page: Current active page
    """
    # Create header with navigation buttons
    st.markdown(
        """
        <div class="custom-header">
            <div class="header-container">
                <div class="logo-section">
                    <div class="logo-text">✈️ AI Trip Planner</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show welcome message if logged in
    if st.session_state.get('logged_in'):
        username = st.session_state.get('username', 'User')
        full_name = st.session_state.get('full_name', username)
        st.markdown(f"""
        <div style="text-align: right; color: #667eea; font-weight: 600; padding: 0.5rem 1rem;">
            Welcome back, {full_name}! 👋
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation using Streamlit columns
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create navigation bar
    if st.session_state.get('logged_in'):
        # Logged in: Show Profile instead of Login
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
    else:
        # Guest: Show Login
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True, type="primary" if current_page == "Home" else "secondary"):
            st.session_state.current_page = "Home"
            st.rerun()
    
    with col2:
        if st.button("🗺️ Plan Trip", use_container_width=True, type="primary" if current_page == "Plan Trip" else "secondary"):
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col3:
        if st.button("🏨 Hotels", use_container_width=True, type="primary" if current_page == "Hotels" else "secondary"):
            st.session_state.current_page = "Hotels"
            st.rerun()
    
    with col4:
        if st.button("🍽️ Foods", use_container_width=True, type="primary" if current_page == "Foods" else "secondary"):
            st.session_state.current_page = "Foods"
            st.rerun()
    
    with col5:
        if st.button("📋 Itineraries", use_container_width=True, type="primary" if current_page == "Itineraries" else "secondary"):
            st.session_state.current_page = "Itineraries"
            st.rerun()
    
    with col6:
        st.write("")  # Spacer
    
    with col7:
        if st.session_state.get('logged_in'):
            # Show Profile button
            if st.button("👤 Profile", use_container_width=True, type="primary" if current_page == "Profile" else "secondary"):
                st.session_state.current_page = "Profile"
                st.rerun()
        else:
            # Show Login button
            if st.button("🔐 Login", use_container_width=True, type="primary" if current_page == "Login" else "secondary"):
                st.session_state.current_page = "Login"
                st.rerun()
    
    st.markdown("---")


def get_navigation_links():
    """
    Get list of navigation pages
    
    Returns:
        List of page names
    """
    return ["Home", "Plan Trip", "Hotels", "Foods", "Itineraries", "Login", "Profile"]


def navigate_to(page: str):
    """
    Navigate to a specific page
    
    Args:
        page: Page name to navigate to
    """
    st.session_state.current_page = page
    st.rerun()