-- =====================================================
-- SQL Migration Script: Create favorite_trips table
-- Purpose: Enable favorites/wishlist functionality
-- =====================================================

-- Drop table if exists (use only for fresh migration)
-- DROP TABLE IF EXISTS favorite_trips;

-- Create favorite_trips table
CREATE TABLE IF NOT EXISTS favorite_trips (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    trip_id INT NULL,
    is_popular_trip BOOLEAN DEFAULT 0 COMMENT '0 = saved trip, 1 = popular trip',
    popular_trip_title VARCHAR(255) NULL,
    popular_trip_destination VARCHAR(255) NULL,
    popular_trip_data JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    CONSTRAINT fk_favorite_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_favorite_trip 
        FOREIGN KEY (trip_id) 
        REFERENCES trips(trip_id) 
        ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_trip_id (trip_id),
    INDEX idx_popular_trip (user_id, popular_trip_title, popular_trip_destination),
    
    -- Unique constraint: prevent duplicate favorites
    -- A user can only favorite the same trip once
    UNIQUE KEY uk_user_saved_trip (user_id, trip_id),
    UNIQUE KEY uk_user_popular_trip (user_id, popular_trip_title, popular_trip_destination)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify table creation
SELECT 
    TABLE_NAME,
    ENGINE,
    TABLE_ROWS,
    CREATE_TIME
FROM 
    information_schema.TABLES
WHERE 
    TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'favorite_trips';
