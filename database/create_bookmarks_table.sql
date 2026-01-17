-- =====================================================
-- SQL Migration Script: Create bookmarks table
-- Purpose: Enable bookmark functionality for hotels and restaurants
-- =====================================================

-- Create bookmarks table
CREATE TABLE IF NOT EXISTS bookmarks (
    bookmark_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_type ENUM('hotel', 'restaurant') NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_location VARCHAR(255) NOT NULL,
    item_city VARCHAR(100) NULL,
    item_country VARCHAR(100) NULL,
    item_data JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_bookmark_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(user_id) 
        ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_item_type (item_type),
    INDEX idx_hotel_bookmark (user_id, item_type, item_name, item_location),
    INDEX idx_restaurant_bookmark (user_id, item_type, item_name, item_location),
    
    -- Unique constraint: prevent duplicate bookmarks
    UNIQUE KEY uk_user_hotel (user_id, item_type, item_name, item_location)
    
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
    AND TABLE_NAME = 'bookmarks';
