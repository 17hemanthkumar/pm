import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def setup_reviews_system():
    """Complete setup for reviews system"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("SETTING UP REVIEWS SYSTEM")
        print("=" * 60)
        
        # 1. Create reviews table
        print("\n1. Creating reviews table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    user_name VARCHAR(255) NOT NULL,
                    event_id VARCHAR(50) NULL,
                    is_general_review TINYINT(1) DEFAULT 1,
                    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_rating (rating),
                    INDEX idx_created_at (created_at),
                    INDEX idx_event_id (event_id),
                    INDEX idx_is_general (is_general_review)
                )
            """)
            print("   ✓ Reviews table created")
        except mysql.connector.Error as err:
            if "already exists" in str(err):
                print("   ⚠ Reviews table already exists")
            else:
                raise err
        
        # 2. Create event_attendees table
        print("\n2. Creating event_attendees table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_attendees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    event_id VARCHAR(50) NOT NULL,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_attendance (user_id, event_id),
                    INDEX idx_user_event (user_id, event_id)
                )
            """)
            print("   ✓ Event attendees table created")
        except mysql.connector.Error as err:
            if "already exists" in str(err):
                print("   ⚠ Event attendees table already exists")
            else:
                raise err
        
        # 3. Update existing reviews table if needed
        print("\n3. Updating reviews table schema...")
        
        # Check if event_id column exists
        cursor.execute("SHOW COLUMNS FROM reviews LIKE 'event_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reviews ADD COLUMN event_id VARCHAR(50) NULL AFTER user_name")
            print("   ✓ Added event_id column")
        else:
            print("   ⚠ event_id column already exists")
        
        # Check if is_general_review column exists
        cursor.execute("SHOW COLUMNS FROM reviews LIKE 'is_general_review'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE reviews ADD COLUMN is_general_review TINYINT(1) DEFAULT 1 AFTER event_id")
            print("   ✓ Added is_general_review column")
        else:
            print("   ⚠ is_general_review column already exists")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ REVIEWS SYSTEM SETUP COMPLETE!")
        print("=" * 60)
        print("\nYou can now:")
        print("  • Write general website reviews on the homepage")
        print("  • Scan event QR codes to unlock event-specific reviews")
        print("  • View and manage all your reviews in 'My Reviews' page")
        print("=" * 60)
        
    except mysql.connector.Error as err:
        print(f"\n✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    setup_reviews_system()
