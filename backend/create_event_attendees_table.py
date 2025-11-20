import mysql.connector
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def create_event_attendees_table():
    """Create event_attendees table for tracking QR code scans"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create event_attendees table
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
        
        print("✓ Event attendees table created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database migration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating event_attendees table...")
    create_event_attendees_table()
