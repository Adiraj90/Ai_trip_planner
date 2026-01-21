# ✈️ AI Trip Planner

A comprehensive, intelligent travel planning system powered by multiple AI agents, built with **Streamlit**, **LangChain**, and **Groq LLM**. This application leverages a multi-agent architecture to provide personalized trip itineraries, hotel recommendations, restaurant suggestions, and complete travel planning with visual analytics and PDF export capabilities.

---

## 🌟 Key Highlights

### 🤖 Multi-Agent AI Architecture
Unlike traditional travel apps that use a single AI model, this project implements a **specialized multi-agent system** where each agent is an expert in its domain:

- **Destination Agent** - Researches cities, cultures, attractions, and local insights
- **Itinerary Agent** - Creates day-by-day travel plans with activities, meals, and accommodations
- **Hotel Agent** - Finds and recommends accommodations based on preferences and budget
- **Food Agent** - Discovers restaurants matching cuisine types and dietary preferences

This architecture provides:
- ✅ **Better Results** - Each agent specializes in its domain
- ✅ **Modular Design** - Easy to extend with new agents (flights, activities, etc.)
- ✅ **Scalability** - Agents work independently and can be optimized separately
- ✅ **Maintainability** - Clear separation of concerns

### 🧠 LangChain Integration
The project extensively uses **LangChain** for:
- **LLM Orchestration** - Managing interactions with Groq's Llama 3.3 70B model
- **Prompt Engineering** - Structured prompts for reliable JSON outputs
- **Chain of Thought** - Complex reasoning for itinerary generation
- **Context Management** - Maintaining conversation state across agent interactions
- **Structured Outputs** - Consistent data formats for UI rendering

---

## ✨ Features

### 🎯 Core Functionality

#### 1. 🏠 **Intelligent Destination Research**
- AI-powered destination insights with cultural information
- Popular attractions with coordinates and Google Maps integration
- Local cuisine recommendations
- Best time to visit and travel tips
- High-quality image galleries using Pexels/Unsplash APIs

#### 2. 🗺️ **Smart Itinerary Generation**
- **Day-by-day planning** with activities, meals, and accommodations
- **Budget-aware recommendations** respecting total trip budget
- **Multiple trip types** - Adventure, Cultural, Relaxation, Culinary, etc.
- **Dietary preferences** - Vegetarian, Vegan, Non-Veg, Halal, Kosher
- **Duplicate prevention** - Validates unique trips before saving
- **State-specific planning** for Indian destinations

#### 3. 🏨 **Hotel Discovery & Filtering**
- AI-generated hotel recommendations with real details
- **Advanced filtering**:
  - Price range (Budget/Medium/Luxury)
  - Star ratings (3★/4★/5★)
  - Room types (Single/Double/Suite)
  - Amenities (WiFi, Pool, Gym, Spa, etc.)
  - AC/Non-AC preferences
- **Smart pagination** - Load more hotels on demand (up to 30 for major cities)
- **Bookmark system** for saving favorite hotels

#### 4. 🍽️ **Restaurant Recommendations**
- Cuisine-specific searches (Italian, Chinese, Local, etc.)
- **Food type filtering** - Veg/Non-Veg/Vegan/Pescatarian
- **Dietary restrictions** - Gluten-free, Dairy-free, Nut-free, etc.
- **Service types** - Dine-in, Takeaway, Delivery
- **Ambiance filtering** - Casual, Fine Dining, Romantic, Family-friendly
- **Opening hours display** for planning meals
- **Bookmark system** for saving favorite restaurants

#### 5. 📊 **Trip Analytics & Visualization**
- **Daily expense breakdown** - Stacked bar charts with Plotly
- **Time distribution** - Pie charts showing activity allocation
- **Category-wise spending** - Activities, Meals, Accommodation
- **Interactive charts** with hover tooltips
- **Budget tracking** against planned expenses

#### 6. 📋 **Trip Management**
- **Your Trips** - View all saved itineraries
- **Popular Trips** - Pre-made trip ideas personalized by country
- **Favorites System** - Heart/bookmark trips for quick access
- **Bookmarks** - Save hotels and restaurants separately
- **PDF Export** - Professional trip reports with charts and analytics

#### 7. 👤 **User Profile & Preferences**
- **Profile management** with profile picture upload
- **Travel preferences** - Default currency, trip types, food preferences
- **Trip statistics** - Total trips, countries visited, budget spent
- **Password management** with security validation
- **Mobile number** support (optional, can be duplicate)

---

## 🏗️ Architecture & Design

### Multi-Agent System Design
```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                      │
│                      (Streamlit)                        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Destination  │    │  Itinerary   │    │    Hotel     │
│    Agent     │    │    Agent     │    │    Agent     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │     LLM      │
                    │   (Groq)     │
                    └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Database   │    │  Maps API    │    │  Image API   │
│   (MySQL)    │    │ (Nominatim)  │    │  (Pexels)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Agent Responsibilities

| Agent | Purpose | LangChain Usage |
|-------|---------|----------------|
| **Destination Agent** | Research cities, culture, attractions | Structured output parsing, Context caching |
| **Itinerary Agent** | Generate day-by-day plans | Chain of thought, Budget constraints |
| **Hotel Agent** | Find accommodations | JSON schema validation, Filtering logic |
| **Food Agent** | Discover restaurants | Cuisine classification, Dietary filtering |

---

## 🛠️ Tech Stack

### Frontend & UI
- **Streamlit** - Interactive web interface
- **Plotly** - Data visualization and charts
- **Custom CSS** - Enhanced UI/UX with gradients and animations
- **HTML/Markdown** - Rich content rendering

### Backend & AI
- **LangChain** - LLM orchestration and prompt engineering
- **Groq API** - Ultra-fast inference with Llama 3.3 70B
- **Python 3.10+** - Core application logic

### Data & Storage
- **MySQL** - User data, trips, preferences
- **Session State** - Real-time data management
- **JSON** - Itinerary storage and data exchange

### APIs & Services
- **Nominatim (OpenStreetMap)** - Free geocoding (no API key)
- **Google Maps** - Location links
- **Pexels/Unsplash** - High-quality travel images
- **Picsum Photos** - Fallback placeholder images

### Document Generation
- **ReportLab** - PDF generation
- **Plotly** - Chart exports for PDFs
- **Kaleido** - Static image rendering

---

## 📁 Project Structure
```
ai-trip-planner/
│
├── agents/                      # AI Agent modules
│   ├── __init__.py
│   ├── destination_agent.py     # Researches destinations
│   ├── itinerary_agent.py       # Generates trip plans
│   ├── hotel_agent.py           # Finds hotels
│   └── food_agent.py            # Discovers restaurants
│
├── pages/                       # Streamlit pages
│   ├── __init__.py
│   ├── home.py                  # Landing page with destination search
│   ├── plan_trip.py             # Trip planning interface
│   ├── hotels.py                # Hotel search and filtering
│   ├── foods.py                 # Restaurant discovery
│   ├── itineraries.py           # Trip management & favorites
│   ├── auth.py                  # Login/Signup
│   └── profile.py               # User profile & preferences
│
├── components/                  # Reusable UI components
│   ├── __init__.py
│   ├── header.py                # Navigation header
│   ├── cards.py                 # Card components
│   └── sidebar.py               # Sidebar components
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── llm_handler.py           # LangChain + Groq integration
│   ├── helpers.py               # General utilities
│   ├── maps_handler.py          # Geocoding & maps
│   ├── image_service.py         # Image fetching
│   └── pdf_generator.py         # PDF export
│
├── config/                      # Configuration
│   ├── __init__.py
│   └── database.py              # MySQL connection
│
├── database/                    # Database models & queries
│   ├── __init__.py
│   ├── models.py                # Data models
│   └── queries.py               # SQL operations
│
├── assets/                      # Static assets
│   └── styles.css               # Custom CSS
│
├── .streamlit/                  # Streamlit config
│   ├── config.toml              # App configuration
│   └── secrets.toml             # API keys (not in git)
│
├── app.py                       # Main application entry
├── database_schema.db           # database schema
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **MySQL 8.0+**
- **Groq API Key** (free tier available)
- **Pexels API Key** (optional, for images)
- **Unsplash API Key** (optional, for images)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-trip-planner.git
cd ai-trip-planner
```

### 2️⃣ Create Virtual Environment

**macOS / Linux**
```bash
python3 -m venv travel_venv
source travel_venv/bin/activate
```

**Windows**
```bash
python -m venv travel_venv
travel_venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Database

Create a MySQL database:
```sql
CREATE DATABASE ai_trip_planner;
```

Import the schema (create tables as defined in `database/models.py`):
```
For reference you can go through sql queries in database_schema.db
```

### 5️⃣ Configure Secrets

Create `.streamlit/secrets.toml`:
```toml
# Database Configuration
DB_HOST = "localhost"
DB_USER = "your_mysql_user"
DB_PASSWORD = "your_mysql_password"
DB_NAME = "ai_trip_planner"

# LLM API Keys
GROQ_API_KEY = "your_groq_api_key"

# Image APIs (Optional)
PEXELS_API_KEY = "your_pexels_key"
UNSPLASH_API_KEY = "your_unsplash_key"
```

**Get API Keys:**
- **Groq**: https://console.groq.com/ (Free tier: 30 requests/min)
- **Pexels**: https://www.pexels.com/api/ (Free: 200 requests/hour)
- **Unsplash**: https://unsplash.com/developers (Free: 50 requests/hour)

### 6️⃣ Run the Application
```bash
streamlit run app.py
```

The app will open at your local host for example `http://localhost:8501`

---

## 🎯 Usage Guide

### Step 1: Explore Destinations
1. Go to **Home** page
2. Enter a city and country (e.g., "Paris, France")
3. View destination insights, attractions, and cuisine
4. Click "Plan My Trip" to start planning

### Step 2: Create Trip Itinerary
1. Navigate to **Plan Trip**
2. Enter trip details:
   - Destination (city, country, state for India)
   - Travel dates
   - Budget and currency
   - Number of travelers
   - Trip types (multiple selections)
   - Food preferences
3. Click "Generate Itinerary"
4. View day-by-day plan with:
   - Activities with timings and costs
   - Meals (breakfast, lunch, dinner)
   - Accommodation recommendations
   - Interactive analytics charts
5. Export to PDF or save to your account

### Step 3: Find Hotels
1. Go to **Hotels** page
2. Search by city and country
3. Apply filters:
   - Budget category
   - Price range
   - Star rating
   - Room type
   - Amenities (WiFi, Pool, Gym, etc.)
   - AC preference
4. View hotel cards with ratings and prices
5. Bookmark favorites (requires login)
6. Load more hotels for comprehensive search

### Step 4: Discover Restaurants
1. Navigate to **Foods** page
2. Search by destination
3. Filter by:
   - Food types (Veg/Non-Veg/Vegan)
   - Cuisine (Italian, Chinese, Local, etc.)
   - Price range
   - Rating
   - Dietary restrictions
   - Service types
   - Ambiance
4. Check opening hours
5. Bookmark favorites

### Step 5: Manage Trips
1. Go to **Itineraries**
2. View **Your Trips** tab for saved itineraries
3. Browse **Popular Trips** for inspiration
4. Check **Your Favorites** for hearted trips
5. Access **Bookmarks** for saved hotels/restaurants
6. Actions available:
   - View details
   - Modify trip
   - Export PDF
   - Add to favorites
   - Delete trip

### Step 6: Profile Management
1. Click **Profile** in navigation
2. View travel statistics
3. Edit personal information
4. Upload profile picture (file or URL)
5. Update travel preferences
6. Change password securely

---

## 🧠 LangChain Implementation Details

### How LangChain Powers This Application

1. **LLM Initialization & Configuration**
2. **Structured Output Generation**
  - LangChain principles are used to enforce JSON schemas:
3. **Agent-Specific Prompts**
  - **Destination Agent:**
  - **Itinerary Agent:**
4. **Context Management**
5. **Error Handling & Retry Logic**
6. **Token Optimization**
---

## 🎨 UI/UX Features

### Visual Design
- **Gradient Backgrounds** - Modern purple-blue color scheme
- **Card Layouts** - Clean, organized information display
- **Responsive Design** - Works on desktop and mobile
- **Smooth Animations** - Hover effects and transitions
- **Custom CSS** - Professional styling with `assets/styles.css`

### Interactive Elements
- **Expandable Day Cards** - Show/hide detailed itineraries
- **Filter Panels** - Sticky sidebar for hotel/restaurant filtering
- **Loading Indicators** - Spinners with progress messages
- **Success/Error Toasts** - User feedback for actions
- **Balloons Animation** - Celebration on account creation

### Data Visualization
- **Plotly Charts**:
  - Stacked bar charts for daily expenses
  - Pie charts for time distribution
  - Horizontal bar charts for category totals
- **Interactive Tooltips** - Hover for detailed information
- **Responsive Sizing** - Charts adapt to screen width

---

## 🔐 Security & Privacy

### Authentication
- **Password Hashing** - SHA-256 encryption
- **Email Validation** - Regex pattern matching
- **Username Uniqueness** - Database constraints
- **Password Strength** - Minimum 8 characters

### Data Protection
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - HTML escaping in user inputs
- **Session Management** - Streamlit session state
- **API Key Security** - Secrets stored in `.streamlit/secrets.toml`

### Privacy Features
- **Optional Mobile Numbers** - Can be duplicate or omitted
- **Profile Image Compression** - Reduces data size
- **User Data Isolation** - Foreign key constraints
- **Cascade Deletion** - Removes user data on account deletion

---

## 📊 Database Schema

### Entity Relationship
```
users (1) ──── (N) trips
  │                  │
  │                  ├── (N) hotels
  │                  └── (N) restaurants
  │
  ├── (1) user_preferences
  ├── (N) favorite_trips
  └── (N) bookmarks

destinations_cache (independent)
```

### Key Tables
- **users** - Authentication and profile data
- **trips** - Trip itineraries with JSON storage
- **hotels** - Hotel recommendations
- **restaurants** - Restaurant suggestions
- **favorite_trips** - User favorites (saved + popular)
- **bookmarks** - Hotel and restaurant bookmarks
- **destinations_cache** - Cached destination research

---

## 🚧 Advanced Features

- Duplicate Trip Prevention
- Smart Pagination
- Multi-Select Trip Types
- Profile Image Upload
- PDF Generation with Charts

---

## 💡 Use Cases

### For Travelers
- 🌍 **Solo Travelers** - Personalized itineraries with safety tips
- 👨‍👩‍👧‍👦 **Family Trips** - Kid-friendly activities and restaurants
- 💑 **Honeymoon Planning** - Romantic destinations and experiences
- 🎒 **Backpackers** - Budget-conscious recommendations
- 🍽️ **Food Enthusiasts** - Culinary-focused trip planning

### For Travel Agencies
- 📋 **Quick Proposals** - Generate client itineraries in seconds
- 💼 **Corporate Travel** - Business trip planning
- 🏢 **Group Tours** - Multi-traveler budgeting
- 📊 **Analytics** - Budget breakdowns for clients

### For Students/Researchers
- 🎓 **Study AI Agents** - Multi-agent architecture example
- 🧪 **LangChain Projects** - Practical LLM integration
- 📚 **Database Design** - Normalized schema reference
- 🎨 **UI/UX Patterns** - Streamlit best practices

---

## 🐛 Known Limitations

1. **LLM Accuracy** - AI may occasionally generate non-existent hotels/restaurants
2. **Image Loading** - External image URLs may fail; fallback placeholders used
3. **Geocoding Rate Limits** - Nominatim allows 1 request/second
4. **PDF Chart Rendering** - Requires Kaleido package (may fail without it)
5. **Mobile Responsiveness** - Best experienced on desktop (1920x1080+)

---

## 👨‍💻 Author

**Aditya Raj**  
Computer Engineering Student  
Passionate about: Generative AI, Multi-Agent Systems, LangChain, Applied ML

📧 Email: your.email@example.com  
🔗 LinkedIn: [Your Profile](https://www.linkedin.com/in/theadityaraj91/)  
🐙 GitHub: [Your Username](https://github.com/Adiraj90)

---

## ⭐ Star This Project

If you found this project helpful, please give it a ⭐ on GitHub!

It helps others discover this work and motivates continued development.

---

**Built with ❤️ using Python, LangChain, and Streamlit**
