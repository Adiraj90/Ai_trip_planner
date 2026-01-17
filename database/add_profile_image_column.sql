-- Add profile_image_url column to users table
-- Run this migration if the column doesn't exist
-- This version works with MySQL 5.7+ (IF NOT EXISTS requires MySQL 8.0.19+)

-- Method 1: Check if column exists first, then add if needed
-- Run this query to check if the column exists:
-- SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_SCHEMA = 'ai_trip_planner' 
--   AND TABLE_NAME = 'users' 
--   AND COLUMN_NAME = 'profile_image_url';

-- If the query above returns no results, then run this:
ALTER TABLE users 
ADD COLUMN profile_image_url VARCHAR(500) NULL 
COMMENT 'URL to user profile picture';

-- Method 2: If column might already exist, use this stored procedure approach:
-- (Uncomment and run if you prefer this method)
/*
DELIMITER $$

CREATE PROCEDURE AddColumnIfNotExists()
BEGIN
    DECLARE column_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO column_exists
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'profile_image_url';
    
    IF column_exists = 0 THEN
        ALTER TABLE users 
        ADD COLUMN profile_image_url VARCHAR(500) NULL 
        COMMENT 'URL to user profile picture';
    END IF;
END$$

DELIMITER ;

CALL AddColumnIfNotExists();
DROP PROCEDURE AddColumnIfNotExists;
*/
