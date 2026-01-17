"""
Profile Page - User profile and settings
"""
import streamlit as st
from database.queries import (
    get_user_by_id, get_user_trip_stats, 
    get_user_preferences, update_user_profile
)
from utils.helpers import format_currency, get_currency_for_country


def render_trip_stats(stats: dict):
    """Render trip statistics"""
    st.markdown("### 📊 Your Travel Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <div style="font-size: 3rem;">🗺️</div>
            <div style="font-size: 2rem; font-weight: bold; color: #667eea; margin: 1rem 0;">
                {trips}
            </div>
            <div style="color: #666;">Total Trips Planned</div>
        </div>
        """.format(trips=stats.get('total_trips', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <div style="font-size: 3rem;">🌍</div>
            <div style="font-size: 2rem; font-weight: bold; color: #667eea; margin: 1rem 0;">
                {countries}
            </div>
            <div style="color: #666;">Countries Explored</div>
        </div>
        """.format(countries=stats.get('countries_visited', 0)), unsafe_allow_html=True)
    
    with col3:
        currency = st.session_state.get('user_currency', 'USD')
        budget = stats.get('total_budget', 0)
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <div style="font-size: 3rem;">💰</div>
            <div style="font-size: 2rem; font-weight: bold; color: #667eea; margin: 1rem 0;">
                {budget}
            </div>
            <div style="color: #666;">Total Budget Spent</div>
        </div>
        """.format(budget=format_currency(budget, currency)), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_personal_info():
    """Render personal information section"""
    st.markdown("### 📝 Personal Information")
    
    user_id = st.session_state.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        st.error("Unable to load user information")
        return
    
    # Profile image section
    profile_image_url = user.get('profile_image_url')
    if profile_image_url:
        col_img, col_info = st.columns([1, 3])
        with col_img:
            st.image(profile_image_url, width=150, caption="Profile Picture")
        with col_info:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📷 Change Profile Picture", use_container_width=True):
                st.session_state.uploading_profile_image = True
                st.rerun()
    else:
        col_img, col_info = st.columns([1, 3])
        with col_img:
            st.markdown("""
            <div style="width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        display: flex; align-items: center; justify-content: center; font-size: 4rem; color: white;">
                👤
            </div>
            """, unsafe_allow_html=True)
        with col_info:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📷 Add Profile Picture", use_container_width=True):
                st.session_state.uploading_profile_image = True
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <strong>Full Name:</strong><br>
            {user.get('full_name', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Username:</strong><br>
            @{user.get('username', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <strong>Email:</strong><br>
            {user.get('email', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        member_since = user.get('created_at')
        if member_since:
            st.markdown(f"""
            <div class="info-box">
                <strong>Member Since:</strong><br>
                {member_since.strftime('%B %d, %Y')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_preferences():
    """Render user preferences section"""
    st.markdown("### ⚙️ Travel Preferences")
    
    user_id = st.session_state.get('user_id')
    prefs = get_user_preferences(user_id)
    
    if prefs:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-box">
                <strong>Default Currency:</strong><br>
                {prefs.get('default_currency', 'USD')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-box">
                <strong>Preferred Food Type:</strong><br>
                {prefs.get('preferred_food_type', 'Mixed') or 'Mixed'}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-box">
                <strong>Preferred Trip Type:</strong><br>
                {prefs.get('preferred_trip_type', 'Adventure') or 'Adventure'}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="info-box">
                <strong>Budget Range:</strong><br>
                {prefs.get('preferred_budget_range', 'Medium') or 'Medium'}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No preferences set yet. They will be updated as you plan trips!")
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_profile_image_upload():
    """Render profile image upload section"""
    st.markdown("### 📷 Upload Profile Picture")
    
    user_id = st.session_state.get('user_id')
    user = get_user_by_id(user_id)
    current_image = user.get('profile_image_url') if user else None
    
    # Show current image if exists
    if current_image:
        st.image(current_image, width=200, caption="Current Profile Picture")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png'],
        key="profile_image_upload"
    )
    
    if uploaded_file is not None:
        # For Streamlit Cloud or local, we can use a URL service or save to a temporary location
        # For simplicity, we'll convert to base64 and store as data URI, or use an image hosting service
        # For now, let's use a placeholder approach - user can provide image URL
        
        st.info("💡 For now, please use an image URL. In production, you would upload directly.")
    
    # Alternative: Image URL input
    st.markdown("---")
    with st.form("profile_image_url_form"):
        image_url = st.text_input(
            "Or enter image URL",
            value=current_image or "",
            placeholder="https://example.com/image.jpg",
            key="profile_image_url_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            save_button = st.form_submit_button("💾 Save Image", use_container_width=True, type="primary")
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
    
    if save_button:
        if image_url and image_url.strip():
            if update_user_profile(user_id, profile_image_url=image_url.strip()):
                st.success("✅ Profile image updated successfully!")
                import time
                time.sleep(1)
                st.session_state.uploading_profile_image = False
                st.rerun()
            else:
                st.error("❌ Failed to update profile image.")
        else:
            # Remove image if URL is empty
            if update_user_profile(user_id, profile_image_url=""):
                st.success("✅ Profile image removed!")
                import time
                time.sleep(1)
                st.session_state.uploading_profile_image = False
                st.rerun()
    
    if cancel_button:
        st.session_state.uploading_profile_image = False
        st.rerun()


def render_edit_profile_form():
    """Render edit profile form"""
    st.markdown("### ✏️ Edit Profile")
    
    user_id = st.session_state.get('user_id')
    user = get_user_by_id(user_id)
    
    with st.form("edit_profile_form"):
        new_full_name = st.text_input(
            "Full Name",
            value=user.get('full_name', ''),
            key="edit_fullname"
        )
        
        new_email = st.text_input(
            "Email",
            value=user.get('email', ''),
            key="edit_email"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
    
    if save_button:
        if update_user_profile(user_id, full_name=new_full_name, email=new_email):
            st.session_state.full_name = new_full_name
            st.session_state.user_email = new_email
            st.success("✅ Profile updated successfully!")
            import time
            time.sleep(1)
            st.session_state.editing_profile = False
            st.rerun()
        else:
            st.error("❌ Failed to update profile. Email may already be in use.")
    
    if cancel_button:
        st.session_state.editing_profile = False
        st.rerun()


def render_logout_section():
    """Render logout section"""
    st.markdown("---")
    st.markdown("### 🚪 Account Actions")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.show_logout_confirm = True
    
    # Logout confirmation
    if st.session_state.get('show_logout_confirm'):
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("⚠️ Are you sure you want to logout?")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Yes, Logout", use_container_width=True, type="primary"):
                # Clear all session state
                keys_to_keep = ['current_page']
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                
                st.session_state.current_page = "Home"
                st.success("✅ Logged out successfully!")
                import time
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_logout_confirm = False
                st.rerun()


def render():
    """Main render function for Profile page"""
    
    # Check if user is logged in
    if not st.session_state.get('logged_in'):
        st.warning("🔐 Please login to view your profile")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Login Now", use_container_width=True, type="primary"):
                st.session_state.current_page = "Login"
                st.rerun()
        return
    
    # Profile header
    st.markdown("## 👤 My Profile")
    username = st.session_state.get('username', 'User')
    country = st.session_state.get('user_country', 'Unknown')
    st.markdown(f"*@{username} • From {country}*")
    st.markdown("---")
    
    # Get user stats
    user_id = st.session_state.get('user_id')
    stats = get_user_trip_stats(user_id)
    
    # Render sections
    render_trip_stats(stats)
    
    st.markdown("---")
    
    # Check if uploading profile image
    if st.session_state.get('uploading_profile_image'):
        render_profile_image_upload()
    # Check if editing
    elif st.session_state.get('editing_profile'):
        render_edit_profile_form()
    else:
        render_personal_info()
        
        # Edit buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("📷 Profile Picture", use_container_width=True):
                st.session_state.uploading_profile_image = True
                st.rerun()
        with col2:
            if st.button("✏️ Edit Profile", use_container_width=True, type="primary"):
                st.session_state.editing_profile = True
                st.rerun()
    
    st.markdown("---")
    
    render_preferences()
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗺️ Plan New Trip", use_container_width=True):
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col2:
        if st.button("📋 View My Trips", use_container_width=True):
            st.session_state.current_page = "Itineraries"
            st.rerun()
    
    with col3:
        if st.button("🏠 Go Home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()
    
    # Logout section
    render_logout_section()