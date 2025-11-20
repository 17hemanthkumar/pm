import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def update_reviews_table():
    """Add event_id and is_general_review columns to reviews table"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add event_id column (nullable for general reviews)
        try:
            cursor.execute("""
                ALTER TABLE reviews 
                ADD COLUMN event_id VARCHAR(50) NULL AFTER user_name
            """)
            print("✓ Added event_id column")
        except mysql.connector.Error as err:
            if "Duplicate column name" in str(err):
                print("⚠ event_id column already exists")
            else:
                raise err
        
        # Add is_general_review column (1 = general website review, 0 = event-specific review)
        try:
            cursor.execute("""
                ALTER TABLE reviews 
                ADD COLUMN is_general_review TINYINT(1) DEFAULT 1 AFTER event_id
            """)
            print("✓ Added is_general_review column")
        except mysql.connector.Error as err:
            if "Duplicate column name" in str(err):
                print("⚠ is_general_review column already exists")
            else:
                raise err
        
        # Add index for event_id
        try:
            cursor.execute("""
                ALTER TABLE reviews 
                ADD INDEX idx_event_id (event_id)
            """)
            print("✓ Added index on event_id")
        except mysql.connector.Error as err:
            if "Duplicate key name" in str(err):
                print("⚠ Index on event_id already exists")
            else:
                raise err
        
        # Add index for is_general_review
        try:
            cursor.execute("""
                ALTER TABLE reviews 
                ADD INDEX idx_is_general (is_general_review)
            """)
            print("✓ Added index on is_general_review")
        except mysql.connector.Error as err:
            if "Duplicate key name" in str(err):
                print("⚠ Index on is_general_review already exists")
            else:
                raise err
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Reviews table updated successfully!")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    print("Updating reviews table...")
    update_reviews_table()
