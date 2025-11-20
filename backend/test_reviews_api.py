import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'picme_db'
}

def test_reviews():
    """Test if reviews are being stored correctly"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 60)
        print("TESTING REVIEWS")
        print("=" * 60)
        
        # Get all reviews
        cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
        reviews = cursor.fetchall()
        
        print(f"\nTotal reviews in database: {len(reviews)}")
        
        if len(reviews) == 0:
            print("\n✗ No reviews found!")
            cursor.close()
            conn.close()
            return
        
        print("\nReviews:")
        print("-" * 60)
        for review in reviews:
            print(f"\nID: {review['id']}")
            print(f"User ID: {review['user_id']}")
            print(f"User Name: {review['user_name']}")
            print(f"Rating: {review['rating']} stars")
            print(f"Review: {review['review_text']}")
            print(f"Event ID: {review.get('event_id', 'N/A')}")
            print(f"Is General: {review.get('is_general_review', 'N/A')}")
            print(f"Created: {review['created_at']}")
            print("-" * 60)
        
        cursor.close()
        conn.close()
        
        print("\n✓ Reviews test complete!")
        
    except mysql.connector.Error as err:
        print(f"\n✗ Database Error: {err}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    test_reviews()
