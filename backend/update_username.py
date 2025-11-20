import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def update_username(email, new_name):
    """Update username for a specific user"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Update the user's name
        cursor.execute(
            "UPDATE users SET full_name = %s WHERE email = %s",
            (new_name, email)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✓ Successfully updated username to '{new_name}' for {email}")
        else:
            print(f"✗ No user found with email {email}")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        return False
    
    return True

if __name__ == "__main__":
    email = "hemanthbumrah@gmail.com"
    new_name = "hemanth"
    
    print(f"Updating username for {email}...")
    update_username(email, new_name)
    print("\n✓ Update complete! Your reviews will now show 'hemanth' as the author.")
