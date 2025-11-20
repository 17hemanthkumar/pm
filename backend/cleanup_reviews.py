import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def cleanup_reviews():
    """Delete all reviews from the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Delete all reviews
        cursor.execute("DELETE FROM reviews")
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Successfully deleted {deleted_count} review(s)")
        print("✓ Reviews table is now empty")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

def show_users():
    """Show all users in the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, full_name, email FROM users")
        users = cursor.fetchall()
        
        print("\n=== Current Users ===")
        for user in users:
            print(f"ID: {user['id']}, Name: {user['full_name']}, Email: {user['email']}")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")

if __name__ == "__main__":
    print("Cleaning up reviews...")
    cleanup_reviews()
    print("\nShowing current users:")
    show_users()
    print("\n✓ Cleanup complete! You can now create new reviews with the correct username.")
