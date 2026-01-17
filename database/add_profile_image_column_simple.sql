-- Simple version: Add profile_image_url column to users table
-- First check if column exists, then run this only if it doesn't

-- Step 1: Check if column exists (run this first to check)
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'ai_trip_planner' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'profile_image_url';

-- Step 2: If the query above returns NO results, then run this:
ALTER TABLE users 
ADD COLUMN profile_image_url VARCHAR(500) NULL 
COMMENT 'URL to user profile picture';
