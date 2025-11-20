# Quick Start: Reviews System

## 🚀 Setup (2 minutes)

### Windows
```bash
setup_reviews.bat
```

### Manual
```bash
cd backend
python setup_reviews_system.py
```

## ✅ What You Get

### 1. Homepage Reviews
- Bottom of homepage
- "Write a Review" button
- Top 3 reviews displayed
- General website feedback

### 2. Event Reviews
- Event detail page
- "Scan Event QR Code" button
- Write review after scanning
- Event-specific feedback

### 3. My Reviews Page
- New "My Reviews" link in navigation
- View all your reviews
- Edit any review
- Delete any review

## 📝 How to Use

### Write a General Review
1. Go to homepage
2. Scroll to bottom
3. Click "Write a Review"
4. Rate 1-5 stars
5. Write review (10-500 chars)
6. Submit

### Write an Event Review
1. Go to event detail page
2. Click "Scan Event QR Code"
3. Scan QR (or use manual entry for testing)
4. Return to event page
5. Click "Write Event Review"
6. Submit review

### Manage Your Reviews
1. Click "My Reviews" in navigation
2. See all your reviews
3. Click "Edit" to modify
4. Click "Delete" to remove

## 🧪 Testing

### Test General Review
```
1. Login → Homepage
2. Click "Write a Review"
3. Submit review
4. Check homepage (should appear)
5. Check "My Reviews" (should appear)
```

### Test Event Review
```
1. Login → Event page
2. Click "Scan Event QR Code"
3. Use manual entry: enter event_id
4. Return to event page
5. Click "Write Event Review"
6. Submit review
7. Check event page (should appear)
8. Check "My Reviews" (should appear)
```

## 🔧 Troubleshooting

### Reviews not showing?
```bash
# Check if tables exist
mysql -u root picme_db
SHOW TABLES LIKE 'reviews';
SHOW TABLES LIKE 'event_attendees';

# If not, run setup again
python backend/setup_reviews_system.py
```

### Can't write event review?
- Make sure you scanned the QR code first
- Try manual entry with the event_id
- Check browser console for errors

### QR scanner not working?
- Allow camera permissions
- Try "Upload QR Image" tab
- Use manual entry for testing

## 📚 Full Documentation

See `REVIEWS_SYSTEM_SETUP.md` for complete documentation.

## 🎯 Key Points

- ✅ General reviews = homepage feedback
- ✅ Event reviews = require QR scan
- ✅ My Reviews = manage all reviews
- ✅ One general review per user
- ✅ One event review per user per event
- ✅ Edit/delete anytime

## 🔐 Security

- Users can only edit their own reviews
- Event reviews require QR verification
- All inputs validated
- SQL injection protected

## 💡 Tips

1. **For Testing**: Use manual QR entry with event_id
2. **For Production**: Users scan actual QR codes
3. **Navigation**: "My Reviews" link added to all pages
4. **Editing**: Click edit, change rating/text, submit
5. **Deleting**: Click delete, confirm, done

## ✨ That's It!

You now have a complete reviews system with:
- Homepage reviews
- Event-specific reviews
- QR code verification
- Review management page

**Start the server and try it out!**

```bash
cd backend
python app.py
```

Then visit: `http://127.0.0.1:5000/homepage`
