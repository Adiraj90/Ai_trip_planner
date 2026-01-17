"""
PDF Generator for Trip Itineraries
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def _calculate_daily_expenses(itinerary: dict):
    """Calculate expenses for each day"""
    daily_expenses = []
    
    for day_info in itinerary.get('daily_itinerary', []):
        day_num = day_info.get('day', 0)
        
        # Calculate total expenses for the day
        activities_cost = sum([float(activity.get('estimated_cost', 0)) for activity in day_info.get('activities', [])])
        meals_cost = sum([float(meal.get('estimated_cost', 0)) for meal in day_info.get('meals', [])])
        accommodation_cost = float(day_info.get('accommodation', {}).get('estimated_cost', 0))
        
        daily_expenses.append({
            'Day': f'Day {day_num}',
            'Activities': activities_cost,
            'Meals': meals_cost,
            'Accommodation': accommodation_cost,
            'Total': activities_cost + meals_cost + accommodation_cost
        })
    
    return daily_expenses


def _calculate_time_distribution(itinerary: dict):
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
        if len(itinerary.get('daily_itinerary', [])) > 0:
            time_data['Rest'] += max(0, 24 - (total_accounted / len(itinerary.get('daily_itinerary', []))))
    
    return time_data


def _create_expense_chart_image(itinerary: dict, currency: str) -> BytesIO:
    """Create expense chart and return as image bytes"""
    daily_expenses = _calculate_daily_expenses(itinerary)
    
    if not daily_expenses:
        return None
    
    df = pd.DataFrame(daily_expenses)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Activities',
        x=df['Day'],
        y=df['Activities'],
        marker_color='#667eea'
    ))
    
    fig.add_trace(go.Bar(
        name='Meals',
        x=df['Day'],
        y=df['Meals'],
        marker_color='#764ba2'
    ))
    
    fig.add_trace(go.Bar(
        name='Accommodation',
        x=df['Day'],
        y=df['Accommodation'],
        marker_color='#f093fb'
    ))
    
    fig.update_layout(
        title='💰 Daily Expense Breakdown',
        xaxis_title='Days',
        yaxis_title=f'Cost ({currency})',
        barmode='stack',
        height=400,
        width=600,
        showlegend=True,
        font=dict(size=10)
    )
    
    # Convert to image bytes
    try:
        img_bytes = fig.to_image(format="png", width=600, height=400, scale=2)
        return BytesIO(img_bytes)
    except Exception as e:
        # If kaleido is not available, return None
        return None


def _create_time_chart_image(itinerary: dict) -> BytesIO:
    """Create time distribution chart and return as image bytes"""
    time_data = _calculate_time_distribution(itinerary)
    
    categories = list(time_data.keys())
    values = list(time_data.values())
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker=dict(colors=['#667eea', '#764ba2', '#f093fb', '#4facfe'])
    )])
    
    fig.update_layout(
        title='⏱️ Time Distribution Across Trip',
        height=400,
        width=600,
        showlegend=True,
        font=dict(size=10)
    )
    
    # Convert to image bytes
    try:
        img_bytes = fig.to_image(format="png", width=600, height=400, scale=2)
        return BytesIO(img_bytes)
    except Exception as e:
        # If kaleido is not available, return None
        return None


def _create_expense_summary_chart_image(itinerary: dict, currency: str) -> BytesIO:
    """Create expense summary chart and return as image bytes"""
    daily_expenses = _calculate_daily_expenses(itinerary)
    
    if not daily_expenses:
        return None
    
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
        marker=dict(color=['#667eea', '#764ba2', '#f093fb']),
        text=[f"{v:.2f} {currency}" for v in values],
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f'📊 Total Expense by Category (Grand Total: {grand_total:.2f} {currency})',
        xaxis_title=f'Amount ({currency})',
        yaxis_title='Category',
        height=300,
        width=600,
        showlegend=False,
        font=dict(size=10)
    )
    
    # Convert to image bytes
    try:
        img_bytes = fig.to_image(format="png", width=600, height=300, scale=2)
        return BytesIO(img_bytes)
    except Exception as e:
        # If kaleido is not available, return None
        return None


def generate_trip_pdf(trip_data: dict, itinerary: dict) -> BytesIO:
    """
    Generate PDF for trip itinerary
    
    Args:
        trip_data: Trip basic information
        itinerary: Full itinerary with daily plans
        
    Returns:
        BytesIO object containing PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    # Title
    title = Paragraph(f"✈️ Trip to {itinerary.get('destination', 'Destination')}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Trip Overview Table
    overview_data = [
        ['Duration', f"{itinerary.get('num_days', 'N/A')} Days"],
        ['Dates', f"{trip_data.get('start_date', 'N/A')} to {trip_data.get('end_date', 'N/A')}"],
        ['Budget', f"{trip_data.get('currency', 'USD')} {trip_data.get('budget', 0):,.2f}"],
        ['Travelers', f"{trip_data.get('num_people', 1)} People"],
        ['Trip Type', trip_data.get('trip_type', 'N/A')]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(overview_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Trip Overview
    if itinerary.get('trip_overview'):
        elements.append(Paragraph("Trip Overview", heading_style))
        elements.append(Paragraph(itinerary['trip_overview'], normal_style))
        elements.append(Spacer(1, 0.2*inch))
    
    # Trip Analytics Section with Charts
    currency = trip_data.get('currency', 'USD')
    
    # Expense Chart
    expense_chart_img = _create_expense_chart_image(itinerary, currency)
    if expense_chart_img:
        elements.append(PageBreak())
        elements.append(Paragraph("Trip Analytics", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("Daily Expense Breakdown", subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        try:
            expense_chart_img.seek(0)
            chart_img = Image(expense_chart_img, width=5.5*inch, height=3.7*inch)
            elements.append(chart_img)
            elements.append(Spacer(1, 0.2*inch))
        except:
            # If image loading fails, skip chart
            elements.append(Paragraph("Chart unavailable", normal_style))
    
    # Time Distribution Chart
    time_chart_img = _create_time_chart_image(itinerary)
    if time_chart_img:
        elements.append(Paragraph("Time Distribution", subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        try:
            time_chart_img.seek(0)
            chart_img = Image(time_chart_img, width=5.5*inch, height=3.7*inch)
            elements.append(chart_img)
            elements.append(Spacer(1, 0.2*inch))
        except:
            # If image loading fails, skip chart
            elements.append(Paragraph("Chart unavailable", normal_style))
    
    # Expense Summary Chart
    expense_summary_img = _create_expense_summary_chart_image(itinerary, currency)
    if expense_summary_img:
        elements.append(Paragraph("Total Expense by Category", subheading_style))
        elements.append(Spacer(1, 0.1*inch))
        try:
            expense_summary_img.seek(0)
            chart_img = Image(expense_summary_img, width=5.5*inch, height=2.8*inch)
            elements.append(chart_img)
            elements.append(Spacer(1, 0.2*inch))
        except:
            # If image loading fails, skip chart
            elements.append(Paragraph("Chart unavailable", normal_style))
    
    # Daily Itinerary
    elements.append(PageBreak())
    elements.append(Paragraph("Day-by-Day Itinerary", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    for day_info in itinerary.get('daily_itinerary', []):
        day_num = day_info.get('day', 1)
        day_title = day_info.get('title', f'Day {day_num}')
        day_date = day_info.get('date', '')
        day_summary = day_info.get('summary', '')
        
        # Day header
        elements.append(Paragraph(f"Day {day_num}: {day_title} ({day_date})", subheading_style))
        
        if day_summary:
            elements.append(Paragraph(day_summary, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Activities
        activities = day_info.get('activities', [])
        if activities:
            elements.append(Paragraph("<b>Activities:</b>", normal_style))
            for activity in activities:
                activity_text = f"• <b>{activity.get('time', '')}</b> - {activity.get('activity', '')}"
                elements.append(Paragraph(activity_text, normal_style))
                if activity.get('description'):
                    elements.append(Paragraph(f"  {activity.get('description', '')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Meals
        meals = day_info.get('meals', [])
        if meals:
            elements.append(Paragraph("<b>Meals:</b>", normal_style))
            for meal in meals:
                meal_text = f"• {meal.get('type', '')}: {meal.get('restaurant', '')} ({meal.get('cuisine', '')})"
                elements.append(Paragraph(meal_text, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Accommodation
        accommodation = day_info.get('accommodation')
        if accommodation:
            elements.append(Paragraph("<b>Accommodation:</b>", normal_style))
            hotel_text = f"{accommodation.get('hotel', '')} - {accommodation.get('area', '')}"
            elements.append(Paragraph(hotel_text, normal_style))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(PageBreak())
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Generated by AI Trip Planner", footer_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generate_filename(destination: str) -> str:
    """Generate filename for PDF"""
    safe_destination = destination.replace(',', '').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"Trip_{safe_destination}_{timestamp}.pdf"