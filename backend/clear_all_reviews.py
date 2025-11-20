import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def clear_all_reviews():
    """Delete all existing reviews from the database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CLEARING ALL REVIEWS")
        print("=" * 60)
        
        # Count existing reviews
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\n✓ No reviews found in database")
            cursor.close()
            conn.close()
            return True
        
        print(f"\nFound {count} review(s) in database")
        
        # Confirm deletion
        confirm = input(f"\nAre you sure you want to delete all {count} review(s)? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("\n✗ Operation cancelled")
            cursor.close()
            conn.close()
            return False
        
        # Delete all reviews
        cursor.execute("DELETE FROM reviews")
        conn.commit()
        
        deleted_count = cursor.rowcount
        
        print(f"\n✓ Successfully deleted {deleted_count} review(s)")
        
        # Also clear event_attendees if you want to reset QR scans
        cursor.execute("SELECT COUNT(*) FROM event_attendees")
        attendance_count = cursor.fetchone()[0]
        
        if attendance_count > 0:
            clear_attendance = input(f"\nAlso clear {attendance_count} QR scan record(s)? (yes/no): ")
            
            if clear_attendance.lower() == 'yes':
                cursor.execute("DELETE FROM event_attendees")
                conn.commit()
                print(f"✓ Successfully deleted {cursor.rowcount} QR scan record(s)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ CLEANUP COMPLETE!")
        print("=" * 60)
        print("\nAll reviews have been removed from the database.")
        print("Users can now write fresh reviews.")
        print("=" * 60)
        
        return True
        
    except mysql.connector.Error as err:
        print(f"\n✗ Database Error: {err}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == "__main__":
    clear_all_reviews()
