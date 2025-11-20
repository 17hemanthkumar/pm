import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def update_reviews_schema():
    """Update reviews table to support both general and event-specific reviews"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add event_id column (NULL for general reviews, event ID for event-specific reviews)
        cursor.execute("""
            ALTER TABLE reviews 
            ADD COLUMN event_id INT NULL,
            ADD COLUMN review_type ENUM('general', 'event') DEFAULT 'general',
            ADD INDEX idx_event_id (event_id),
            ADD INDEX idx_review_type (review_type)
        """)
        
        print("✓ Added event_id and review_type columns to reviews table")
        
        # Drop the old unique constraint on user_id (if it exists)
        try:
            cursor.execute("ALTER TABLE reviews DROP INDEX user_id")
            print("✓ Removed old unique constraint on user_id")
        except:
            print("  (No unique constraint to remove)")
        
        # Add new unique constraint: one general review per user, one review per user per event
        cursor.execute("""
            ALTER TABLE reviews 
            ADD UNIQUE KEY unique_user_event (user_id, event_id, review_type)
        """)
        
        print("✓ Added unique constraint for user-event-type combination")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database schema updated successfully!")
        print("  - Users can now write one general review about PicMe")
        print("  - Users can write one review per event they attend")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    print("Updating reviews table schema...")
    update_reviews_schema()
