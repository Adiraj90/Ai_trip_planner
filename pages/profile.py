"""
Profile Page - User profile and settings (Enhanced Version)
"""
import streamlit as st
from database.queries import (
    get_user_by_id, get_user_trip_stats, 
    get_user_preferences, update_user_profile,
    update_user_preferences
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
    
    # Profile image section - bigger image on left, details on right
    profile_image_url = user.get('profile_image_url')
    
    col_img, col_info = st.columns([1, 2])
    
    with col_img:
        # Add top spacing to center the image vertically
        st.markdown("""
        <div style="margin-top: 3rem;"></div>
        """, unsafe_allow_html=True)
        
        # Display larger circular profile image
        if profile_image_url:
            try:
                # Display image in circular container using custom HTML/CSS
                st.markdown(f"""
                <div style="width: 320px; height: 320px; border-radius: 50%; overflow: hidden; 
                            border: 6px solid #667eea; box-shadow: 0 8px 20px rgba(0,0,0,0.3); margin: 0 auto;">
                    <img src="{profile_image_url}" 
                         style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                """, unsafe_allow_html=True)
            except:
                # Fallback if image fails to load
                st.markdown("""
                <div style="width: 320px; height: 320px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            display: flex; align-items: center; justify-content: center; font-size: 8rem; color: white; margin: 0 auto;
                            border: 6px solid #667eea; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
                    👤
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="width: 320px; height: 320px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        display: flex; align-items: center; justify-content: center; font-size: 8rem; color: white; margin: 0 auto;
                        border: 6px solid #667eea; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
                👤
            </div>
            """, unsafe_allow_html=True)
        
        # Display username below the image
        st.markdown(f"""
        <div style="text-align: center; margin-top: 1.5rem;">
            <span style="color: #667eea; font-size: 1.3rem; font-weight: 600;">@{user.get('username', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info:
        # Display user details on the right side of image
        # ALL sections now have unsafe_allow_html=True
        st.markdown(f"""
        <div style="padding: 1rem;">
            <div class="info-box" style="margin-bottom: 1rem;">
                <strong>📛 Full Name:</strong><br>
                <span style="font-size: 1.1rem; color: #333;">{user.get('full_name', 'N/A')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="padding: 0 1rem;">
            <div class="info-box" style="margin-bottom: 1rem;">
                <strong>📧 Email:</strong><br>
                <span style="font-size: 1.1rem; color: #333;">{user.get('email', 'N/A')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="padding: 0 1rem;">
            <div class="info-box" style="margin-bottom: 1rem;">
                <strong>📱 Mobile Number:</strong><br>
                <span style="font-size: 1.1rem; color: #333;">{user.get('mobile_number', 'Not provided') or 'Not provided'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="padding: 0 1rem;">
            <div class="info-box">
                <strong>📅 Member Since:</strong><br>
                <span style="font-size: 1.1rem; color: #333;">{user.get('created_at').strftime('%B %d, %Y') if user.get('created_at') else 'N/A'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

def convert_image_to_url(uploaded_file):
    """Convert uploaded image file to a compressed data URL"""
    import base64
    from io import BytesIO
    from PIL import Image
    
    try:
        # Open the image
        image = Image.open(uploaded_file)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize if image is too large (max 800x800 to keep file size manageable)
        max_size = (800, 800)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO with compression
        buffered = BytesIO()
        
        # Save as JPEG with quality optimization
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        
        # Get bytes
        img_bytes = buffered.getvalue()
        
        # Check file size (warn if > 500KB)
        file_size_kb = len(img_bytes) / 1024
        if file_size_kb > 500:
            st.warning(f"⚠️ Image size: {file_size_kb:.0f}KB. Large images may take longer to save.")
        
        # Convert to base64
        base64_encoded = base64.b64encode(img_bytes).decode()
        
        # Create data URL
        data_url = f"data:image/jpeg;base64,{base64_encoded}"
        
        return data_url
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")
        return None


def render_preferences():
    """Render user preferences section"""
    st.markdown("### ⚙️ Travel Preferences")
    
    user_id = st.session_state.get('user_id')
    prefs = get_user_preferences(user_id)
    
    # Check if we're in editing mode - if yes, show edit form here
    if st.session_state.get('editing_profile'):
        # Show the edit form in place of preferences
        render_edit_profile_form()
    else:
        # Show normal preferences display
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
        
        # Edit Profile button in preferences section
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("✏️ Edit Profile", use_container_width=True, type="primary", key="edit_profile_from_prefs"):
                st.session_state.editing_profile = True
                st.rerun()


def render_edit_profile_form():
    """Render comprehensive edit profile form with image upload and preferences"""
    st.markdown("### ✏️ Edit Profile")
    
    user_id = st.session_state.get('user_id')
    user = get_user_by_id(user_id)
    prefs = get_user_preferences(user_id)
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📝 Personal Info", "📷 Profile Picture", "⚙️ Preferences"])
    
    with tab1:
        st.markdown("#### Update Personal Information")
        with st.form("edit_personal_info_form"):
            new_full_name = st.text_input(
                "Full Name *",
                value=user.get('full_name', ''),
                key="edit_fullname"
            )
            
            new_email = st.text_input(
                "Email *",
                value=user.get('email', ''),
                key="edit_email"
            )
            
            new_mobile = st.text_input(
                "Mobile Number",
                value=user.get('mobile_number', '') or '',
                placeholder="+1234567890",
                key="edit_mobile"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_personal_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            
            with col2:
                cancel_personal_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_personal_button:
            # Import the update function
            from database.queries import update_user_profile_with_mobile
            
            if update_user_profile_with_mobile(user_id, full_name=new_full_name, email=new_email, mobile_number=new_mobile):
                st.session_state.full_name = new_full_name
                st.session_state.user_email = new_email
                st.success("✅ Personal information updated successfully!")
                import time
                time.sleep(1)
                st.session_state.editing_profile = False
                st.rerun()
            else:
                st.error("❌ Failed to update profile. Email may already be in use.")
        
        if cancel_personal_button:
            st.session_state.editing_profile = False
            st.rerun()
    
    with tab2:
        st.markdown("#### Update Profile Picture")
        
        # Show current image if exists
        current_image = user.get('profile_image_url')
        if current_image:
            col_preview, col_spacer = st.columns([1, 2])
            with col_preview:
                try:
                    # Display current image in circle
                    st.markdown(f"""
                    <div style="width: 200px; height: 200px; border-radius: 50%; overflow: hidden; 
                                border: 4px solid #667eea; box-shadow: 0 6px 12px rgba(0,0,0,0.2); margin: 0 auto;">
                        <img src="{current_image}" 
                             style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <p style="text-align: center; margin-top: 10px; color: #666;">Current Profile Picture</p>
                    """, unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div style="width: 200px; height: 200px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                display: flex; align-items: center; justify-content: center; font-size: 5rem; color: white; margin: 0 auto;">
                        👤
                    </div>
                    <p style="text-align: center; margin-top: 10px; color: #666;">Current Profile Picture</p>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Upload method selection
        upload_method = st.radio(
            "Choose upload method:",
            options=["📁 Upload from Device", "🔗 Use Image URL"],
            key="upload_method_selection"
        )
        
        if upload_method == "📁 Upload from Device":
            # File upload method
            with st.form("profile_image_upload_form"):
                st.markdown("**Upload Image from Device**")
                st.info("💡 Upload any image file (JPG, PNG, GIF, WebP, BMP, TIFF, etc.)")
                
                uploaded_file = st.file_uploader(
                    "Choose an image file",
                    type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'svg', 'ico'],
                    key="profile_image_file_upload"
                )
                
                # Preview the uploaded image
                if uploaded_file is not None:
                    # Display preview in circle
                    import base64
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode()
                    
                    st.markdown(f"""
                    <div style="width: 200px; height: 200px; border-radius: 50%; overflow: hidden; 
                                border: 4px solid #4CAF50; box-shadow: 0 6px 12px rgba(0,0,0,0.2); margin: 0 auto;">
                        <img src="data:{uploaded_file.type};base64,{base64_image}" 
                             style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <p style="text-align: center; margin-top: 10px; color: #4CAF50; font-weight: bold;">Preview</p>
                    """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    upload_button = st.form_submit_button("💾 Upload & Save", use_container_width=True, type="primary")
                
                with col2:
                    remove_image_button = st.form_submit_button("🗑️ Remove Image", use_container_width=True, type="secondary")
                
                with col3:
                    cancel_upload_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if upload_button:
                if uploaded_file is not None:
                    with st.spinner("Processing and uploading image..."):
                        # Convert uploaded file to data URL
                        data_url = convert_image_to_url(uploaded_file)
                        
                        if data_url:
                            # Try to save to database
                            try:
                                # First, get current user to check existing image
                                current_user = get_user_by_id(user_id)
                                existing_image = current_user.get('profile_image_url') if current_user else None
                                
                                # Log for debugging
                                st.info(f"🔍 Image data length: {len(data_url)} characters")
                                
                                # Update profile with new image (this will replace the old one)
                                result = update_user_profile(user_id, profile_image_url=data_url)
                                
                                if result:
                                    if existing_image:
                                        st.success("✅ Profile image updated successfully! (Previous image replaced)")
                                    else:
                                        st.success("✅ Profile image uploaded successfully!")
                                    import time
                                    time.sleep(1.5)
                                    st.session_state.editing_profile = False
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to save profile image to database.")
                                    st.error(f"Data URL length: {len(data_url)} - Database column may be too small")
                                    st.info("💡 **Solution**: Ask your developer to run this SQL command:")
                                    st.code("ALTER TABLE users MODIFY COLUMN profile_image_url MEDIUMTEXT;", language="sql")
                            except Exception as e:
                                st.error(f"❌ Database error: {str(e)}")
                                st.error(f"Image data size: {len(data_url) if data_url else 0} characters")
                                st.info("💡 The database column 'profile_image_url' needs to be enlarged. Please run:")
                                st.code("ALTER TABLE users MODIFY COLUMN profile_image_url MEDIUMTEXT;", language="sql")
                        else:
                            st.error("❌ Failed to process image file.")
                else:
                    st.warning("⚠️ Please select an image file to upload.")
            
            if remove_image_button:
                if update_user_profile(user_id, profile_image_url=""):
                    st.success("✅ Profile image removed!")
                    import time
                    time.sleep(1)
                    st.session_state.editing_profile = False
                    st.rerun()
            
            if cancel_upload_button:
                st.session_state.editing_profile = False
                st.rerun()
        
        else:
            # Image URL input method
            with st.form("profile_image_url_form"):
                st.markdown("**Enter Image URL**")
                st.info("💡 Provide a direct link to your profile image (supports JPG, PNG, GIF, WebP, etc.)")
                
                image_url = st.text_input(
                    "Image URL",
                    value=current_image or "",
                    placeholder="https://example.com/your-image.jpg",
                    key="profile_image_url_input"
                )
                
                # Preview the image before saving
                if image_url and image_url.strip():
                    try:
                        # Display preview in circle
                        st.markdown(f"""
                        <div style="width: 200px; height: 200px; border-radius: 50%; overflow: hidden; 
                                    border: 4px solid #4CAF50; box-shadow: 0 6px 12px rgba(0,0,0,0.2); margin: 0 auto;">
                            <img src="{image_url.strip()}" 
                                 style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                        <p style="text-align: center; margin-top: 10px; color: #4CAF50; font-weight: bold;">Preview</p>
                        """, unsafe_allow_html=True)
                    except:
                        st.warning("⚠️ Unable to load image preview. Please check the URL.")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    save_image_button = st.form_submit_button("💾 Save Image", use_container_width=True, type="primary")
                
                with col2:
                    remove_image_button = st.form_submit_button("🗑️ Remove Image", use_container_width=True, type="secondary")
                
                with col3:
                    cancel_image_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if save_image_button:
                if image_url and image_url.strip():
                    if update_user_profile(user_id, profile_image_url=image_url.strip()):
                        st.success("✅ Profile image updated successfully!")
                        import time
                        time.sleep(1)
                        st.session_state.editing_profile = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to update profile image.")
                else:
                    st.warning("⚠️ Please enter a valid image URL.")
            
            if remove_image_button:
                if update_user_profile(user_id, profile_image_url=""):
                    st.success("✅ Profile image removed!")
                    import time
                    time.sleep(1)
                    st.session_state.editing_profile = False
                    st.rerun()
            
            if cancel_image_button:
                st.session_state.editing_profile = False
                st.rerun()
    
    with tab3:
        st.markdown("#### Update Travel Preferences")
        
        with st.form("edit_preferences_form"):
            # Get current preferences
            current_prefs = prefs if prefs else {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                default_currency = st.selectbox(
                    "Default Currency *",
                    options=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"],
                    index=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"].index(
                        current_prefs.get('default_currency', 'USD')
                    ),
                    key="edit_currency"
                )
                
                preferred_food_type = st.selectbox(
                    "Preferred Food Type *",
                    options=["Mixed", "Vegetarian", "Vegan", "Non-Vegetarian", "Pescatarian", "Halal", "Kosher"],
                    index=["Mixed", "Vegetarian", "Vegan", "Non-Vegetarian", "Pescatarian", "Halal", "Kosher"].index(
                        current_prefs.get('preferred_food_type', 'Mixed') or 'Mixed'
                    ),
                    key="edit_food_type"
                )
            
            with col2:
                preferred_trip_type = st.selectbox(
                    "Preferred Trip Type *",
                    options=["Adventure", "Relaxation", "Cultural", "Culinary", "Shopping", "Nightlife", "Romantic", "Family", "Business", "Solo", "Beach", "Mountains", "City"],
                    index=["Adventure", "Relaxation", "Cultural", "Culinary", "Shopping", "Nightlife", "Romantic", "Family", "Business", "Solo", "Beach", "Mountains", "City"].index(
                        current_prefs.get('preferred_trip_type', 'Adventure') or 'Adventure'
                    ),
                    key="edit_trip_type"
                )
                
                preferred_budget_range = st.selectbox(
                    "Preferred Budget Range *",
                    options=["Budget", "Medium", "Luxury"],
                    index=["Budget", "Medium", "Luxury"].index(
                        current_prefs.get('preferred_budget_range', 'Medium') or 'Medium'
                    ),
                    key="edit_budget_range"
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_prefs_button = st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary")
            
            with col2:
                cancel_prefs_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_prefs_button:
            if update_user_preferences(
                user_id,
                default_currency=default_currency,
                preferred_trip_type=preferred_trip_type,
                preferred_food_type=preferred_food_type,
                preferred_budget_range=preferred_budget_range
            ):
                st.session_state.user_currency = default_currency
                st.success("✅ Preferences updated successfully!")
                import time
                time.sleep(1)
                st.session_state.editing_profile = False
                st.rerun()
            else:
                st.error("❌ Failed to update preferences.")
        
        if cancel_prefs_button:
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
    
    # Always show Personal Information
    render_personal_info()
    
    st.markdown("---")
    
    # Show preferences or edit form (edit form replaces preferences section)
    render_preferences()

    st.markdown("---")

    # Render sections
    render_trip_stats(stats)
    
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