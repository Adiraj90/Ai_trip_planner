# Image Service Setup Guide

This guide explains how to set up free image APIs for the AI Trip Planner application.

## Available Image APIs

The application supports three image sources (in order of preference):

1. **Pexels API** (Recommended) - Free, 200 requests/hour
2. **Unsplash API** - Free, 50 requests/hour  
3. **Unsplash Source** (Fallback) - No API key needed, but less reliable

## Setting Up API Keys

### Option 1: Pexels API (Recommended)

1. Visit https://www.pexels.com/api/
2. Create a free account
3. Generate an API key
4. Add to `.streamlit/secrets.toml`:

```toml
PEXELS_API_KEY = "your_pexels_api_key_here"
```

### Option 2: Unsplash API

1. Visit https://unsplash.com/developers
2. Create a free account  
3. Create a new application
4. Get your API key (Client ID)
5. Add to `.streamlit/secrets.toml`:

```toml
UNSPLASH_API_KEY = "your_unsplash_api_key_here"
```

### Option 3: Use Fallback (No Setup Required)

If you don't want to set up API keys, the app will automatically use Unsplash Source (no key needed). Images may be less reliable but will still work.

## Example secrets.toml Configuration

```toml
# Database Configuration
[DB_CONFIG]
DB_HOST = "localhost"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
DB_NAME = "your_database"

# Image APIs (Optional - app works without these)
PEXELS_API_KEY = "your_pexels_key_here"  # Recommended
UNSPLASH_API_KEY = "your_unsplash_key_here"  # Alternative

# Other secrets...
```

## Image Usage in the App

### Home Page
- **City Exploration**: Shows 4 images of the destination city
- Images are fetched when user explores a destination

### Hotels Tab
- Each hotel card displays one image
- Images are fetched for specific hotels

### Foods Tab  
- Each restaurant card displays one image
- Images are fetched for specific restaurants

### Day-by-Day Itinerary
- Each day card shows an image of the main attraction/activity
- Image appears on the right side of the day overview

### Profile Page
- Users can upload their profile picture
- Image URL is stored in the database

## Database Migration

If you want to enable profile images, run this SQL migration:

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_image_url VARCHAR(500) NULL 
COMMENT 'URL to user profile picture';
```

The migration file is located at: `database/add_profile_image_column.sql`

## Notes

- **Rate Limits**: Pexels allows 200 requests/hour, Unsplash allows 50/hour
- **Fallback**: If API keys aren't set, the app uses Unsplash Source (no limits but less reliable)
- **Image Quality**: Pexels and Unsplash provide high-quality, royalty-free images
- **Free Tier**: Both Pexels and Unsplash offer free tiers suitable for development

## Testing

After setting up API keys, test the image service by:

1. Exploring a destination on the Home page - you should see 4 images
2. Searching for hotels - each hotel card should have an image
3. Searching for restaurants - each restaurant card should have an image
4. Generating a trip itinerary - each day should have an image
5. Uploading a profile picture - profile page should display your image
