"""
Plan Trip Page - Create personalized itineraries
"""
import streamlit as st
from agents.itinerary_agent import get_itinerary_agent
from database.queries import add_favorite_trip, is_trip_favorited, remove_favorite_trip
from utils.helpers import (
    format_currency, get_currency_for_country, 
    format_date_readable, get_trip_type_emoji,
    get_food_type_emoji, calculate_days_between
)
from utils.pdf_generator import generate_trip_pdf, generate_filename
from datetime import date, timedelta
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_trip_form():
    """Render the trip planning form"""
    st.markdown("## 🗺️ Plan Your Perfect Trip")
    st.markdown("Fill in the details below to generate your personalized itinerary")
    st.markdown("---")
    
    # Pre-fill from Home page if available
    default_city = st.session_state.get('destination_city', '')
    default_country = st.session_state.get('destination_country', '')
    
    # Form layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📍 Destination")
        
        country = st.text_input(
            "Country *",
            value=default_country,
            placeholder="e.g., India",
            key="plan_country"
        )
        
        # Show state field only for India
        state = None
        if country and "india" in country.lower():
            state = st.text_input(
                "State *",
                placeholder="e.g., Maharashtra",
                key="plan_state"
            )
        
        city = st.text_input(
            "City *",
            value=default_city,
            placeholder="e.g., Mumbai",
            key="plan_city"
        )
        
        st.markdown("### 📅 Travel Dates")
        start_date = st.date_input(
            "Start Date *",
            value=date.today() + timedelta(days=7),
            min_value=date.today(),
            key="plan_start_date"
        )
        end_date = st.date_input(
            "End Date *",
            value=date.today() + timedelta(days=14),
            min_value=start_date,
            key="plan_end_date"
        )
        
        # Calculate days
        if end_date >= start_date:
            num_days = calculate_days_between(start_date, end_date)
            st.info(f"📆 Trip Duration: **{num_days} days**")
    
    with col2:
        st.markdown("### 💰 Budget")
        
        # Auto-detect currency based on country
        auto_currency = get_currency_for_country(country) if country else "USD"
        
        currency = st.selectbox(
            "Currency *",
            options=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"],
            index=["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"].index(auto_currency),
            key="plan_currency"
        )
        
        budget = st.number_input(
            f"Total Budget ({currency}) *",
            min_value=0.0,
            value=1000.0,
            step=100.0,
            key="plan_budget"
        )
        
        st.markdown("### 👥 Travel Details")
        num_people = st.number_input(
            "Number of People *",
            min_value=1,
            max_value=20,
            value=1,
            key="plan_num_people"
        )
        
        # Multiple trip types selection
        trip_types = st.multiselect(
            "Trip Type(s) * (Select one or more)",
            options=[
                "Adventure", "Relaxation", "Cultural", "Culinary",
                "Shopping", "Nightlife", "Romantic", "Family",
                "Business", "Solo", "Beach", "Mountains", "City"
            ],
            default=["Adventure"],
            key="plan_trip_types"
        )
        
        food_preference = st.selectbox(
            "Food Preference *",
            options=[
                "Mixed", "Vegetarian", "Vegan", 
                "Non-Vegetarian", "Pescatarian", "Halal", "Kosher"
            ],
            key="plan_food_pref"
        )
    
    st.markdown("---")
    
    # Generate button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        generate_button = st.button(
            "✨ Generate Itinerary",
            use_container_width=True,
            type="primary"
        )
    
    return {
        'city': city,
        'state': state,
        'country': country,
        'start_date': start_date,
        'end_date': end_date,
        'budget': budget,
        'currency': currency,
        'num_people': num_people,
        'trip_types': trip_types, 
        'food_preference': food_preference,
        'generate': generate_button
    }


def calculate_daily_expenses(itinerary: dict):
    """Calculate expenses for each day"""
    daily_expenses = []
    
    for day_info in itinerary.get('daily_itinerary', []):
        day_num = day_info.get('day', 0)
        
        # Calculate total expenses for the day
        activities_cost = sum([float(activity.get('estimated_cost', 0)) for activity in day_info.get('activities', [])])
        meals_cost = sum([float(meal.get('estimated_cost', 0)) for meal in day_info.get('meals', [])])
        accommodation_cost = float(day_info.get('accommodation', {}).get('estimated_cost', 0))
        
        total_cost = activities_cost + meals_cost + accommodation_cost
        
        daily_expenses.append({
            'Day': f'Day {day_num}',
            'Activities': activities_cost,
            'Meals': meals_cost,
            'Accommodation': accommodation_cost,
            'Total': total_cost
        })
    
    return daily_expenses


def calculate_time_distribution(itinerary: dict):
    """Calculate time spent on different activity types"""
    time_data = {
        'Activities': 0,
        'Meals': 0,
        'Travel': 0,
        'Rest': 0
    }
    
    for day_info in itinerary.get('daily_itinerary', []):
        # Count activities (assuming 2 hours per activity on average)
        activities_count = len(day_info.get('activities', []))
        time_data['Activities'] += activities_count * 2
        
        # Count meals (assuming 1 hour per meal)
        meals_count = len(day_info.get('meals', []))
        time_data['Meals'] += meals_count * 1
        
        # Estimate travel time (1 hour between activities)
        if activities_count > 0:
            time_data['Travel'] += (activities_count - 1) * 1
        
        # Rest of the time is rest/free time
        total_accounted = time_data['Activities'] + time_data['Meals'] + time_data['Travel']
        time_data['Rest'] += max(0, 24 - (total_accounted / len(itinerary.get('daily_itinerary', []))))
    
    return time_data


def render_expense_chart(itinerary: dict, currency: str):
    """Render daily expense breakdown chart"""
    daily_expenses = calculate_daily_expenses(itinerary)
    
    if not daily_expenses:
        return
    
    df = pd.DataFrame(daily_expenses)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Activities',
        x=df['Day'],
        y=df['Activities'],
        marker_color='#667eea',
        hovertemplate='<b>Activities</b><br>%{y:.2f} ' + currency + '<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Meals',
        x=df['Day'],
        y=df['Meals'],
        marker_color='#764ba2',
        hovertemplate='<b>Meals</b><br>%{y:.2f} ' + currency + '<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name='Accommodation',
        x=df['Day'],
        y=df['Accommodation'],
        marker_color='#f093fb',
        hovertemplate='<b>Accommodation</b><br>%{y:.2f} ' + currency + '<extra></extra>'
    ))
    
    fig.update_layout(
        title='💰 Daily Expense Breakdown',
        xaxis_title='Days',
        yaxis_title=f'Cost ({currency})',
        barmode='stack',
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig, use_container_width=True)


def render_time_distribution_chart(itinerary: dict):
    """Render time distribution pie chart"""
    time_data = calculate_time_distribution(itinerary)
    
    # Prepare data
    categories = list(time_data.keys())
    values = list(time_data.values())
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe']),
        textposition='auto',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:.1f} hours<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='⏱️ Time Distribution Across Trip',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_expense_summary(itinerary: dict, currency: str):
    """Render expense category summary"""
    daily_expenses = calculate_daily_expenses(itinerary)
    
    if not daily_expenses:
        return
    
    # Calculate totals
    total_activities = sum([d['Activities'] for d in daily_expenses])
    total_meals = sum([d['Meals'] for d in daily_expenses])
    total_accommodation = sum([d['Accommodation'] for d in daily_expenses])
    grand_total = total_activities + total_meals + total_accommodation
    
    # Create horizontal bar chart
    categories = ['Activities', 'Meals', 'Accommodation']
    values = [total_activities, total_meals, total_accommodation]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(
            color=['#667eea', '#764ba2', '#f093fb'],
        ),
        text=[format_currency(v, currency) for v in values],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>%{x:.2f} ' + currency + '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'📊 Total Expense by Category (Grand Total: {format_currency(grand_total, currency)})',
        xaxis_title=f'Amount ({currency})',
        yaxis_title='Category',
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)


def render_itinerary(itinerary: dict):
    """Render the generated itinerary"""
    
    # Header
    st.markdown(f"# 🎉 Your Trip to {itinerary['destination']}")
    
    # Trip Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Duration", f"{itinerary['num_days']} Days")
    
    with col2:
        st.metric("Budget", format_currency(
            itinerary.get('total_estimated_cost', 0),
            st.session_state.get('plan_currency', 'USD')
        ))
    
    with col3:
        st.metric("Travelers", f"{st.session_state.get('plan_num_people', 1)} People")
    
    with col4:
        trip_types = st.session_state.get('plan_trip_types', ['Adventure'])
        trip_type_str = ', '.join(trip_types) if isinstance(trip_types, list) else trip_types
        st.markdown(f"**Type:** {get_trip_type_emoji(trip_types[0] if isinstance(trip_types, list) else trip_types)} {trip_type_str}")
    
    st.markdown("---")
    
    # Trip Overview
    if itinerary.get('trip_overview'):
        st.markdown("### 📖 Trip Overview")
        st.info(itinerary['trip_overview'])
        st.markdown("<br>", unsafe_allow_html=True)
    
    # NEW: Analytics Section
    st.markdown("### 📊 Trip Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        render_expense_chart(itinerary, st.session_state.get('plan_currency', 'USD'))
    
    with chart_col2:
        render_time_distribution_chart(itinerary)
    
    # Expense Summary
    render_expense_summary(itinerary, st.session_state.get('plan_currency', 'USD'))
    
    st.markdown("---")
    
    # Daily Itinerary
    st.markdown("### 📅 Day-by-Day Itinerary")
    
    for day_info in itinerary.get('daily_itinerary', []):
        render_day_card(day_info)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏨 Find Hotels", use_container_width=True, key="find_hotels_btn"):
            st.session_state.current_page = "Hotels"
            st.rerun()
    
    with col2:
        if st.button("🍽️ Explore Restaurants", use_container_width=True, key="explore_restaurants_btn"):
            st.session_state.current_page = "Foods"
            st.rerun()
    
    with col3:
        save_clicked = st.button("💾 Save Itinerary", use_container_width=True, type="primary", key="save_itinerary_main_btn")
    
    with col4:
        # Export PDF button
        if st.button("📄 Export PDF", use_container_width=True, type="secondary", key="export_pdf_btn"):
            st.session_state.export_pdf_clicked = True
    
    with col5:
        # Add to Favorites button
        trip_id = st.session_state.get('current_trip_id')
        user_id = st.session_state.get('user_id')
        is_favorited = False
        
        if user_id and trip_id:
            is_favorited = is_trip_favorited(user_id, trip_id=trip_id)
        
        if user_id and trip_id:
            # User is logged in and trip is saved
            if is_favorited:
                if st.button("❤️ Favorited", use_container_width=True, key="favorite_trip_plan_btn"):
                    if remove_favorite_trip(user_id, trip_id=trip_id):
                        st.success("Removed from favorites!")
                        st.rerun()
                    else:
                        st.error("Failed to remove from favorites")
            else:
                if st.button("🤍 Add to Favorites", use_container_width=True, key="add_favorite_trip_plan_btn"):
                    if add_favorite_trip(user_id, trip_id=trip_id):
                        st.success("Added to favorites! ❤️")
                        st.rerun()
                    else:
                        st.error("Failed to add to favorites")
        elif not user_id:
            # User is not logged in - show login prompt
            if st.button("🤍 Add to Favorites", use_container_width=True, key="favorite_login_required_btn"):
                st.session_state.favorite_login_required = True
                st.rerun()
        elif user_id and not trip_id:
            # User is logged in but trip not saved - button disabled with tooltip
            st.button("🤍 Add to Favorites", use_container_width=True, key="favorite_save_required_btn", disabled=True, help="Please save the itinerary first to add it to favorites")

    # Handle Export PDF button click
    if st.session_state.get('export_pdf_clicked', False):
        try:
            # Prepare trip data
            trip_data = {
                'start_date': st.session_state.get('plan_start_date', date.today()).isoformat(),
                'end_date': st.session_state.get('plan_end_date', date.today()).isoformat(),
                'budget': st.session_state.get('plan_budget', 0),
                'currency': st.session_state.get('plan_currency', 'USD'),
                'num_people': st.session_state.get('plan_num_people', 1),
                'trip_type': ', '.join(st.session_state.get('plan_trip_types', ['Adventure']))
            }
            
            # Generate PDF
            pdf_buffer = generate_trip_pdf(trip_data, itinerary)
            filename = generate_filename(itinerary['destination'])
            
            # Download button
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("✅ PDF generated successfully!")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="download_pdf_btn"
                )
            with col3:
                if st.button("✅ Done", use_container_width=True, key="done_pdf_export"):
                    st.session_state.export_pdf_clicked = False
                    st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to generate PDF: {str(e)}")
            if st.button("❌ Close", key="close_pdf_error"):
                st.session_state.export_pdf_clicked = False
                st.rerun()
    
    # Handle Add to Favorites - Login Required
    if st.session_state.get('favorite_login_required', False):
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("🔐 Please login or sign up to add trips to your favorites!")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔐 Login", use_container_width=True, type="primary", key="favorite_goto_login"):
                st.session_state.favorite_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "login"
                st.rerun()
        with col2:
            if st.button("📝 Sign Up", use_container_width=True, type="primary", key="favorite_goto_signup"):
                st.session_state.favorite_login_required = False
                st.session_state.current_page = "Login"
                st.session_state.auth_tab = "signup"
                st.rerun()
        with col3:
            if st.button("❌ Cancel", use_container_width=True, key="favorite_cancel_login"):
                st.session_state.favorite_login_required = False
                st.rerun()
    
    # Handle Save Itinerary button click
    if save_clicked:
        # Set a flag in session state
        st.session_state.save_itinerary_clicked = True
    
    # Check the flag
    if st.session_state.get('save_itinerary_clicked', False):
        # Check if user is logged in
        if not st.session_state.get('logged_in'):
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning("🔐 Please login or sign up to save your itinerary!")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔐 Login", use_container_width=True, type="primary", key="goto_login_from_save"):
                    st.session_state.save_itinerary_clicked = False
                    st.session_state.current_page = "Login"
                    st.session_state.auth_tab = "login"
                    st.rerun()
            with col2:
                if st.button("📝 Sign Up", use_container_width=True, type="primary", key="goto_signup_from_save"):
                    st.session_state.save_itinerary_clicked = False
                    st.session_state.current_page = "Login"
                    st.session_state.auth_tab = "signup"
                    st.rerun()
            with col3:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_save_itinerary"):
                    st.session_state.save_itinerary_clicked = False
                    st.rerun()
        else:
            # User is logged in
            trip_id = st.session_state.get('current_trip_id')
            
            if trip_id:
                st.markdown("<br>", unsafe_allow_html=True)
                st.success("✅ Your itinerary is already saved in 'Your Trips'!")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("📋 View My Trips", key="view_saved_trips_after_save", use_container_width=True):
                        st.session_state.save_itinerary_clicked = False
                        st.session_state.current_page = "Itineraries"
                        st.rerun()
                with col3:
                    if st.button("✅ OK", use_container_width=True, key="ok_already_saved"):
                        st.session_state.save_itinerary_clicked = False
                        st.rerun()
            else:
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💡 This itinerary was not saved because it's a duplicate of an existing trip in your account.")
                st.markdown("**Tip:** Modify the dates, budget, or destination to save it as a new trip.")
                
                col1, col2, col3 = st.columns([2, 1, 2])
                with col2:
                    if st.button("✅ OK", use_container_width=True, key="ok_duplicate_trip"):
                        st.session_state.save_itinerary_clicked = False
                        st.rerun()


def render_day_card(day_info: dict):
    """Render a single day's itinerary"""
    
    day_num = day_info.get('day', 1)
    day_date = day_info.get('date', '')
    day_title = day_info.get('title', f'Day {day_num}')
    day_summary = day_info.get('summary', '')
    
    # Get main activity/place for image
    activities = day_info.get('activities', [])
    main_activity = activities[0] if activities else None
    activity_name = main_activity.get('activity', day_title) if main_activity else day_title
    
    # Get city from session state for image search
    city = st.session_state.get('plan_city', '')
    country = st.session_state.get('plan_country', '')
    
    # Fetch image for the day's main attraction
    day_image_url = None
    if activity_name and city:
        try:
            from utils.image_service import get_image_service
            image_service = get_image_service()
            # Get image for the main activity/place
            day_image_url = image_service.get_place_image(activity_name, city, country)
        except Exception as e:
            pass
    
    # Expandable day card with image layout
    with st.expander(f"**Day {day_num}: {day_title}** ({day_date})", expanded=(day_num == 1)):
        
        # Day header with image if available
        if day_image_url:
            img_col, summary_col = st.columns([1, 2])
            with img_col:
                try:
                    st.image(day_image_url, use_container_width=True, caption=activity_name, output_format="PNG")
                except Exception as e:
                    # Show placeholder if image fails to load
                    st.markdown(f"""
                    <div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                        <div style="color: white; font-size: 3rem;">🗺️</div>
                    </div>
                    <p style="text-align: center; color: #666; margin-top: 5px; font-size: 0.9rem;">{activity_name}</p>
                    """, unsafe_allow_html=True)
        else:
            # Try to get a fallback image
            try:
                from utils.image_service import get_image_service
                image_service = get_image_service()
                # Use Lorem Picsum as fallback
                fallback_img = f"https://picsum.photos/seed/{hash(f'{activity_name}{city}') % 1000}/400/300"
                
                img_col, summary_col = st.columns([1, 2])
                with img_col:
                    try:
                        st.image(fallback_img, use_container_width=True, caption=activity_name)
                    except:
                        st.markdown(f"""
                        <div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                            <div style="color: white; font-size: 3rem;">🗺️</div>
                        </div>
                        <p style="text-align: center; color: #666; margin-top: 5px; font-size: 0.9rem;">{activity_name}</p>
                        """, unsafe_allow_html=True)
                with summary_col:
                    # Day Summary
                    if day_summary:
                        st.markdown(f"""
                        <div class="info-box" style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                                    border-left: 4px solid #667eea; margin-bottom: 1.5rem;">
                            <p style="color: #333; line-height: 1.6; margin: 0;">
                                <strong>📝 Day Overview:</strong><br>
                                {day_summary}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            except:
                # Day Summary without image (fallback if image generation fails)
                if day_summary:
                    st.markdown(f"""
                    <div class="info-box" style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                                border-left: 4px solid #667eea; margin-bottom: 1.5rem;">
                        <p style="color: #333; line-height: 1.6; margin: 0;">
                            <strong>📝 Day Overview:</strong><br>
                            {day_summary}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Activities
        st.markdown("#### 🎯 Activities")
        activities = day_info.get('activities', [])
        
        if activities:
            for activity in activities:
                render_activity(activity)
        else:
            st.info("No activities planned for this day")
        
        # Meals
        st.markdown("#### 🍽️ Meals")
        meals = day_info.get('meals', [])
        
        if meals:
            meal_cols = st.columns(len(meals))
            for idx, meal in enumerate(meals):
                with meal_cols[idx]:
                    render_meal(meal)
        else:
            st.info("No meals planned")
        
        # Accommodation
        accommodation = day_info.get('accommodation')
        if accommodation:
            st.markdown("#### 🏨 Accommodation")
            st.markdown(f"""
            <div class="info-box">
                <strong>{accommodation.get('hotel', 'Hotel')}</strong><br>
                📍 {accommodation.get('area', 'City Center')}<br>
                💰 {format_currency(accommodation.get('estimated_cost', 0), st.session_state.get('plan_currency', 'USD'))} per night
            </div>
            """, unsafe_allow_html=True)


def render_activity(activity: dict):
    """Render a single activity"""
    
    time_str = activity.get('time', '')
    activity_name = activity.get('activity', 'Activity')
    description = activity.get('description', '')
    location = activity.get('location', '')
    duration = activity.get('duration', '')
    cost = activity.get('estimated_cost', 0)
    maps_link = activity.get('maps_link', '#')
    
    st.markdown(f"""
    <div class="place-card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div style="font-size: 1.1rem; font-weight: bold; color: #667eea;">
                    {time_str} - {activity_name}
                </div>
                <p style="color: #666; margin: 0.5rem 0;">{description}</p>
                <div style="color: #888; font-size: 0.9rem;">
                    📍 {location} • ⏱️ {duration} • 💰 {format_currency(cost, st.session_state.get('plan_currency', 'USD'))}
                </div>
            </div>
        </div>
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button" style="margin-top: 0.5rem;">📍 View on Map</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


def render_meal(meal: dict):
    """Render a meal card"""
    
    meal_type = meal.get('type', 'Meal')
    restaurant = meal.get('restaurant', 'Restaurant')
    cuisine = meal.get('cuisine', '')
    cost = meal.get('estimated_cost', 0)
    maps_link = meal.get('maps_link', '#')
    
    food_emoji = {"Breakfast": "🍳", "Lunch": "🍱", "Dinner": "🍽️"}.get(meal_type, "🍴")
    
    st.markdown(f"""
    <div class="info-box">
        <div style="font-weight: bold; color: #333;">{food_emoji} {meal_type}</div>
        <div style="margin: 0.5rem 0;">{restaurant}</div>
        <div style="color: #666; font-size: 0.9rem;">{cuisine}</div>
        <div style="color: #667eea; font-weight: 600; margin-top: 0.5rem;">
            {format_currency(cost, st.session_state.get('plan_currency', 'USD'))}
        </div>
        <a href="{maps_link}" target="_blank" style="text-decoration: none;">
            <button class="map-button" style="margin-top: 0.5rem; font-size: 0.8rem; padding: 4px 12px;">📍 Map</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


def render():
    """Main render function for Plan Trip page"""
    
    # Initialize flags
    if 'save_itinerary_clicked' not in st.session_state:
        st.session_state.save_itinerary_clicked = False
    if 'export_pdf_clicked' not in st.session_state:
        st.session_state.export_pdf_clicked = False
    if 'favorite_login_required' not in st.session_state:
        st.session_state.favorite_login_required = False
    
    # Render the form
    form_data = render_trip_form()
    
    # Handle form submission
    if form_data['generate']:
        # Clear previous flags
        st.session_state.save_itinerary_clicked = False
        st.session_state.export_pdf_clicked = False
        
        # Validate inputs
        if not form_data['city'] or not form_data['country']:
            st.error("⚠️ Please enter both city and country!")
            return
        
        # For India, state is required
        if form_data['country'] and "india" in form_data['country'].lower():
            if not form_data.get('state'):
                st.error("⚠️ Please enter state for Indian destinations!")
                return
        
        if form_data['end_date'] < form_data['start_date']:
            st.error("⚠️ End date must be after start date!")
            return
        
        if form_data['budget'] <= 0:
            st.error("⚠️ Please enter a valid budget!")
            return
        
        if not form_data['trip_types']:
            st.error("⚠️ Please select at least one trip type!")
            return
        
        # Generate itinerary
        trip_type_str = ", ".join(form_data['trip_types'])
        with st.spinner(f"✨ Creating your perfect {trip_type_str.lower()} itinerary... This may take 20-30 seconds..."):
            try:
                agent = get_itinerary_agent()
                
                # Get user_id if logged in
                user_id = st.session_state.get('user_id')
                
                itinerary = agent.generate_itinerary(
                    city=form_data['city'],
                    state=form_data.get('state'),
                    country=form_data['country'],
                    start_date=form_data['start_date'],
                    end_date=form_data['end_date'],
                    budget=form_data['budget'],
                    currency=form_data['currency'],
                    trip_types=form_data['trip_types'],
                    food_preference=form_data['food_preference'],
                    num_people=form_data['num_people'],
                    user_id=user_id
                )
                
                if itinerary:
                    st.session_state.generated_itinerary = itinerary
                    st.session_state.current_trip_id = itinerary.get('trip_id')
                    
                    # Show appropriate success message
                    if itinerary.get('trip_id'):
                        st.success("✅ Your itinerary is ready and saved to 'Your Trips'!")
                    else:
                        st.success("✅ Your itinerary is ready!")
                        if st.session_state.get('logged_in'):
                            st.info("💡 This trip was not saved as it's similar to an existing trip in your account.")
                    
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Failed to generate itinerary. The AI response was invalid.")
                    st.info("💡 Tip: Try again with a different destination or date range.")
            
            except Exception as e:
                st.error(f"❌ Error generating itinerary: {str(e)}")
                import traceback
                with st.expander("🔍 Debug Info (for developers)"):
                    st.code(traceback.format_exc())
    
    # Display generated itinerary if available
    if st.session_state.get('generated_itinerary'):
        st.markdown("---")
        render_itinerary(st.session_state.generated_itinerary)