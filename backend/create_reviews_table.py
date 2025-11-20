import mysql.connector
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def create_reviews_table():
    """Create reviews table for user reviews"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                user_name VARCHAR(255) NOT NULL,
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_rating (rating),
                INDEX idx_created_at (created_at)
            )
        """)
        
        print("✓ Reviews table created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database migration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating reviews table...")
    create_reviews_table()
