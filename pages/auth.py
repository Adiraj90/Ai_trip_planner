"""
Authentication Page - Login and Signup (Fixed with Phone Number)
"""
import streamlit as st
from database.queries import (
    create_user, authenticate_user, check_email_exists, 
    check_username_exists, get_user_preferences
)
from utils.helpers import validate_email
import re


def render_login_form():
    """Render login form"""
    st.markdown("### 🔐 Welcome Back!")
    st.markdown("*Login to access your saved trips and preferences*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username_or_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        remember_me = st.checkbox("Remember me", value=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_button = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
        
        with col2:
            if st.form_submit_button("📝 Sign Up Instead", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.rerun()
    
    if login_button:
        if not username_or_email or not password:
            st.error("⚠️ Please enter both username/email and password!")
            return
        
        with st.spinner("Authenticating..."):
            user = authenticate_user(username_or_email, password)
            
            if user:
                # Set session state
                st.session_state.logged_in = True
                st.session_state.user_id = user['user_id']
                st.session_state.username = user['username']
                st.session_state.user_email = user['email']
                st.session_state.full_name = user['full_name']
                st.session_state.user_country = user.get('country', 'Unknown')
                
                # Get user preferences
                if user.get('preferences'):
                    st.session_state.user_currency = user['preferences'].get('default_currency', 'USD')
                
                st.success(f"✅ Welcome back, {user['full_name']}!")
                st.balloons()
                
                # Redirect to home
                import time
                time.sleep(1)
                st.session_state.current_page = "Home"
                st.rerun()
            else:
                st.error("❌ Invalid credentials! Please check your username/email and password.")


def render_signup_form():
    """Render signup form"""
    st.markdown("### ✈️ Join AI Trip Planner")
    st.markdown("*Start planning your dream trips today!*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        full_name = st.text_input(
            "Full Name *",
            placeholder="e.g., John Doe",
            key="signup_fullname"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "Email Address *",
                placeholder="your.email@example.com",
                key="signup_email"
            )
        
        with col2:
            username = st.text_input(
                "Username *",
                placeholder="johndoe",
                key="signup_username"
            )
        
        # Phone number input
        mobile_number = st.text_input(
            "Mobile Number (Optional)",
            placeholder="+1234567890 or 1234567890",
            key="signup_mobile",
            help="Enter your phone number with country code (optional)"
        )
        
        # Country selection
        country = st.selectbox(
            "Your Country *",
            options=[
                "Select your country",
                "India",
                "USA",
                "UK",
                "Canada",
                "Australia",
                "Germany",
                "France",
                "Japan",
                "China",
                "Singapore",
                "UAE",
                "Thailand",
                "Indonesia",
                "Malaysia",
                "Brazil",
                "Mexico",
                "Spain",
                "Italy",
                "Netherlands",
                "Switzerland",
                "Other"
            ],
            key="signup_country"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Minimum 8 characters",
                key="signup_password"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password",
                key="signup_confirm_password"
            )
        
        agree_terms = st.checkbox(
            "I agree to the Terms & Conditions and Privacy Policy",
            key="signup_agree"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            signup_button = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
        
        with col2:
            if st.form_submit_button("🔐 Login Instead", use_container_width=True):
                st.session_state.auth_tab = "login"
                st.rerun()
    
    if signup_button:
        # Validation
        errors = []
        
        if not full_name:
            errors.append("Full name is required")
        
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        elif check_email_exists(email):
            errors.append("⚠️ This email is already registered! Please login or use a different email.")
        
        if not username:
            errors.append("Username is required")
        elif len(username) < 3 or len(username) > 20:
            errors.append("Username must be 3-20 characters long")
        elif not re.match("^[a-zA-Z0-9_]+$", username):
            errors.append("Username can only contain letters, numbers, and underscores")
        elif check_username_exists(username):
            errors.append("⚠️ This username is already taken! Please choose a different one.")
        
        # Validate mobile number if provided
        if mobile_number and mobile_number.strip():
            # Remove spaces and dashes for validation
            cleaned_mobile = mobile_number.strip().replace(" ", "").replace("-", "")
            # Check if it's a valid phone number format (digits only, possibly with + prefix)
            if not re.match(r"^\+?[0-9]{10,15}$", cleaned_mobile):
                errors.append("Invalid mobile number format. Use format: +1234567890 or 1234567890")
        
        if country == "Select your country":
            errors.append("Please select your country")
        
        if not password:
            errors.append("Password is required")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not agree_terms:
            errors.append("You must agree to the Terms & Conditions")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
            return
        
        # Create user with mobile number
        with st.spinner("Creating your account..."):
            # Clean mobile number before saving
            cleaned_mobile = mobile_number.strip().replace(" ", "").replace("-", "") if mobile_number and mobile_number.strip() else None
            
            result = create_user_with_mobile(username, email, password, full_name, country, cleaned_mobile)
            
            if 'error' in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Account created successfully!")
                st.balloons()
                
                # Auto-login
                st.session_state.logged_in = True
                st.session_state.user_id = result['user_id']
                st.session_state.username = result['username']
                st.session_state.user_email = result['email']
                st.session_state.full_name = result['full_name']
                st.session_state.user_country = result['country']
                
                st.info(f"🎉 Welcome to AI Trip Planner, {full_name}! Redirecting to home...")
                
                # Redirect to home
                import time
                time.sleep(2)
                st.session_state.current_page = "Home"
                st.rerun()


def create_user_with_mobile(username: str, email: str, password: str, full_name: str, country: str, mobile_number: str = None) -> dict:
    """
    Create a new user with mobile number
    
    Args:
        username: Username
        email: Email address
        password: Plain text password (will be hashed)
        full_name: Full name
        country: User's country
        mobile_number: Mobile number (optional)
        
    Returns:
        User dict if successful, error dict otherwise
    """
    try:
        from config.database import get_db
        from utils.helpers import hash_password, get_currency_for_country
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if email exists
        if check_email_exists(email):
            return {'error': 'Email is already registered'}
        
        # Check if username exists
        if check_username_exists(username):
            return {'error': 'Username is already taken'}
        
        # Hash password
        password_hash = hash_password(password)
        
        db = get_db()
        
        # Try to insert with mobile_number column
        try:
            query = """
                INSERT INTO users (username, email, password_hash, full_name, country, mobile_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query, (username, email, password_hash, full_name, country, mobile_number), fetch=False)
        except Exception as e:
            # If mobile_number column doesn't exist, try without it
            logger.warning(f"Failed to insert with mobile_number, trying without: {e}")
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
            currency = get_currency_for_country(country)
            
            db.execute_query(pref_query, (user_id, currency, 'Adventure'), fetch=False)
            
            # Return user data
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'country': country,
                'mobile_number': mobile_number
            }
        
        return {'error': 'Failed to create user'}
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {'error': str(e)}


def render():
    """Main render function for Auth page"""
    
    # Check if already logged in
    if st.session_state.get('logged_in'):
        st.info("✅ You are already logged in!")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Go to Home", use_container_width=True, type="primary"):
                st.session_state.current_page = "Home"
                st.rerun()
        return
    
    # Initialize tab state
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "login"
    
    # Tab selection
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_signup_form()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p style="font-size: 0.9rem;">By signing up, you agree to our Terms of Service and Privacy Policy</p>
            <p style="font-size: 0.85rem;">Secure authentication • Your data is encrypted</p>
        </div>
        """,
        unsafe_allow_html=True
    )