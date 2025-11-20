# Reviews System Setup Guide

## Overview
The PicMe reviews system allows users to:
1. **Write general website reviews** on the homepage
2. **Write event-specific reviews** after scanning event QR codes
3. **View and manage all their reviews** in the "My Reviews" page

## Database Setup

### Step 1: Run the Setup Script
```bash
cd backend
python setup_reviews_system.py
```

This will create:
- `reviews` table - stores all reviews (general and event-specific)
- `event_attendees` table - tracks which users have scanned QR codes for which events

### Step 2: Verify Tables
Check that the following tables exist in your `picme_db` database:

```sql
-- Reviews table
CREATE TABLE reviews (
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
);

-- Event attendees table
CREATE TABLE event_attendees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id VARCHAR(50) NOT NULL,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (user_id, event_id),
    INDEX idx_user_event (user_id, event_id)
);
```

## Features

### 1. General Website Reviews (Homepage)
- **Location**: Homepage bottom section
- **Access**: Any logged-in user
- **Behavior**:
  - Users can write one general review about the PicMe website
  - If they already have a review, it will be updated (not duplicated)
  - Top 3 reviews are displayed on the homepage

### 2. Event-Specific Reviews
- **Location**: Event detail page
- **Access**: Users who have scanned the event QR code
- **Workflow**:
  1. User visits event detail page
  2. Sees "Scan Event QR Code" button
  3. Scans QR code using QR scanner page
  4. Returns to event detail page
  5. "Write Event Review" button now appears
  6. Can write review specific to that event

### 3. My Reviews Page
- **Location**: `/my_reviews` (accessible from navigation)
- **Features**:
  - View all your reviews (general + event-specific)
  - Edit any review (updates rating and text)
  - Delete any review
  - Reviews are organized by type (general vs event)

## API Endpoints

### Get General Reviews
```
GET /api/reviews?top=true
```
Returns top 3 general website reviews

### Get Event Reviews
```
GET /api/reviews/event/<event_id>
```
Returns all reviews for a specific event

### Get User's Reviews
```
GET /api/reviews/user
```
Returns all reviews by the current logged-in user

### Create/Update Review
```
POST /api/reviews
Body: {
    "rating": 1-5,
    "review_text": "Your review text",
    "event_id": "event_abc123" (optional, for event reviews),
    "is_general_review": true/false
}
```

### Delete Review
```
DELETE /api/reviews/<review_id>
```

### Scan Event QR Code
```
POST /api/scan-event-qr
Body: {
    "event_id": "event_abc123"
}
```

### Check Event Attendance
```
GET /api/check-event-attendance?event_id=event_abc123
```

## User Flow Examples

### Example 1: Writing a General Review
1. User logs in
2. Scrolls to bottom of homepage
3. Clicks "Write a Review"
4. Selects rating (1-5 stars)
5. Writes review text (10-500 characters)
6. Submits
7. Review appears on homepage and in "My Reviews"

### Example 2: Writing an Event Review
1. User logs in
2. Visits event detail page
3. Clicks "Scan Event QR Code"
4. Scans QR code (camera or upload)
5. Returns to event detail page
6. Clicks "Write Event Review"
7. Selects rating and writes review
8. Submits
9. Review appears on event page and in "My Reviews"

### Example 3: Managing Reviews
1. User clicks "My Reviews" in navigation
2. Sees all their reviews organized by type
3. Can click "Edit" to modify a review
4. Can click "Delete" to remove a review
5. Changes are immediate

## Navigation Updates

The "My Reviews" link has been added to:
- Homepage navigation
- Event detail page navigation
- All other user pages

## Testing

### Test General Reviews
1. Log in as a user
2. Go to homepage
3. Click "Write a Review"
4. Submit a review
5. Verify it appears on homepage
6. Go to "My Reviews" and verify it's there

### Test Event Reviews
1. Create an event as admin
2. Log in as a user
3. Go to event detail page
4. Click "Scan Event QR Code"
5. Use manual entry to enter the event_id
6. Return to event detail page
7. Click "Write Event Review"
8. Submit review
9. Verify it appears on event page
10. Go to "My Reviews" and verify it's there

### Test Edit/Delete
1. Go to "My Reviews"
2. Click "Edit" on a review
3. Change rating and text
4. Submit
5. Verify changes are saved
6. Click "Delete" on a review
7. Confirm deletion
8. Verify review is removed

## Troubleshooting

### Reviews not loading
- Check database connection
- Verify tables exist: `SHOW TABLES LIKE 'reviews';`
- Check browser console for errors

### Can't write event review
- Verify you've scanned the event QR code
- Check `event_attendees` table: `SELECT * FROM event_attendees WHERE user_id = YOUR_ID;`
- Try scanning QR code again

### QR scanner not working
- Allow camera permissions in browser
- Try upload method instead
- Use manual entry for testing

### Reviews not appearing
- Check if `is_general_review` flag is set correctly
- Verify `event_id` is correct for event reviews
- Check database: `SELECT * FROM reviews WHERE user_id = YOUR_ID;`

## Security Notes

- Users can only edit/delete their own reviews
- Event reviews require QR code scan (prevents fake reviews)
- General reviews are limited to one per user
- All inputs are validated (rating 1-5, text 10-500 chars)
- SQL injection protection via parameterized queries

## Future Enhancements

- Review moderation for admins
- Review replies/comments
- Helpful/unhelpful voting
- Review photos/images
- Review verification badges
- Email notifications for new reviews
