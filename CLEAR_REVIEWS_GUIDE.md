# Clear All Reviews Guide

## Overview
This guide explains how to remove all existing reviews from your PicMe database.

## ⚠️ Warning
**This action is IRREVERSIBLE!** All reviews will be permanently deleted from the database.

## Methods to Clear Reviews

### Method 1: Windows Batch File (Easiest)
```bash
clear_reviews.bat
```

This will:
1. Show how many reviews exist
2. Ask for confirmation
3. Delete all reviews
4. Optionally delete QR scan records

### Method 2: Python Script
```bash
cd backend
python clear_all_reviews.py
```

Same as Method 1, but run directly.

### Method 3: SQL Script (Direct Database)
```bash
# Open MySQL
mysql -u root picme_db

# Run the SQL file
source backend/clear_reviews.sql
```

Then uncomment the DELETE statements in the SQL file to actually delete.

### Method 4: MySQL Command Line (Quick)
```sql
-- Connect to database
mysql -u root picme_db

-- Delete all reviews
DELETE FROM reviews;

-- Delete all QR scan records (optional)
DELETE FROM event_attendees;

-- Verify
SELECT COUNT(*) FROM reviews;
SELECT COUNT(*) FROM event_attendees;
```

## What Gets Deleted

### Reviews Table
- All general website reviews
- All event-specific reviews
- User ratings and review text
- Review timestamps

### Event Attendees Table (Optional)
- All QR code scan records
- Users will need to re-scan QR codes to write event reviews

## What Does NOT Get Deleted

- User accounts
- Events
- Photos
- Downloads
- Admin accounts
- Any other data

## Step-by-Step Instructions

### Using the Batch File

1. **Open Command Prompt**
   ```
   Right-click on clear_reviews.bat → Run as Administrator
   ```

2. **Review the Information**
   - Script shows how many reviews exist
   - Shows breakdown of general vs event reviews

3. **Confirm Deletion**
   - Type `yes` to confirm
   - Type `no` to cancel

4. **Optional: Clear QR Scans**
   - Script asks if you want to clear QR scan records
   - Type `yes` to clear (users must re-scan QR codes)
   - Type `no` to keep (users can still write event reviews)

5. **Done!**
   - All reviews are deleted
   - Database is clean

### Using Python Script

```bash
# Navigate to backend folder
cd backend

# Run the script
python clear_all_reviews.py

# Follow the prompts
# Type 'yes' to confirm deletion
```

### Using SQL

```sql
-- Connect to MySQL
mysql -u root -p

-- Switch to database
USE picme_db;

-- Check current reviews
SELECT COUNT(*) FROM reviews;

-- Delete all reviews
DELETE FROM reviews;

-- Verify deletion
SELECT COUNT(*) FROM reviews;
-- Should show 0

-- Optional: Delete QR scans
DELETE FROM event_attendees;
```

## Verification

After clearing reviews, verify the deletion:

### Check Database
```sql
mysql -u root picme_db
SELECT COUNT(*) FROM reviews;
-- Should return 0

SELECT COUNT(*) FROM event_attendees;
-- Should return 0 if you cleared QR scans
```

### Check Website
1. Visit homepage
   - Reviews section should show "No reviews yet"
   
2. Visit "My Reviews" page
   - Should show "No Reviews Yet"
   
3. Visit event detail page
   - Event reviews should show "No reviews yet"

## After Clearing Reviews

### Users Can:
- Write new general reviews on homepage
- Scan QR codes (if you cleared event_attendees)
- Write new event reviews
- See their new reviews in "My Reviews"

### What Happens:
- Homepage shows "No reviews yet"
- Event pages show "No reviews yet"
- "My Reviews" page is empty for all users
- Fresh start for the reviews system

## Troubleshooting

### Script says "No reviews found"
- Reviews table is already empty
- Nothing to delete

### "Table doesn't exist" error
- Run `setup_reviews_system.py` first
- Creates the necessary tables

### Permission denied
- Run as Administrator (Windows)
- Check MySQL user permissions

### Can't connect to database
- Verify MySQL is running
- Check DB_CONFIG in script
- Verify database name is 'picme_db'

## Backup Before Clearing (Optional)

If you want to backup reviews before deleting:

```sql
-- Backup reviews
CREATE TABLE reviews_backup AS SELECT * FROM reviews;

-- Backup QR scans
CREATE TABLE event_attendees_backup AS SELECT * FROM event_attendees;

-- Now you can safely delete
DELETE FROM reviews;
DELETE FROM event_attendees;

-- To restore later (if needed)
INSERT INTO reviews SELECT * FROM reviews_backup;
INSERT INTO event_attendees SELECT * FROM event_attendees_backup;
```

## Quick Reference

| Method | Command | Confirmation Required |
|--------|---------|----------------------|
| Batch File | `clear_reviews.bat` | Yes |
| Python | `python backend/clear_all_reviews.py` | Yes |
| SQL File | `source backend/clear_reviews.sql` | No (must uncomment) |
| Direct SQL | `DELETE FROM reviews;` | No |

## Safety Features

The Python script includes:
- ✅ Shows count before deleting
- ✅ Requires explicit "yes" confirmation
- ✅ Separate confirmation for QR scans
- ✅ Success/error messages
- ✅ Can be cancelled anytime

## When to Clear Reviews

Clear reviews when you want to:
- Start fresh with the reviews system
- Remove test reviews
- Clean up before production launch
- Reset after major changes
- Remove inappropriate content (all at once)

## Alternative: Delete Individual Reviews

Instead of clearing all reviews, users can:
1. Go to "My Reviews" page
2. Click "Delete" on specific reviews
3. Confirm deletion

This is better for:
- Removing specific reviews
- Letting users manage their own content
- Keeping other reviews intact

## Summary

**Easiest Method:**
```bash
clear_reviews.bat
```

**What It Does:**
- Deletes all reviews
- Optionally deletes QR scans
- Requires confirmation
- Shows results

**Result:**
- Clean database
- No reviews
- Users can write new reviews
- Fresh start

## Need Help?

If you encounter issues:
1. Check MySQL is running
2. Verify database exists
3. Check table names
4. Review error messages
5. Try SQL method directly

## Important Notes

- ⚠️ **Irreversible**: Cannot undo deletion
- 💾 **Backup**: Consider backing up first
- 🔒 **Users**: User accounts are NOT deleted
- 📸 **Photos**: Photos are NOT deleted
- 🎫 **Events**: Events are NOT deleted
- ✅ **Safe**: Only reviews are affected

---

**Ready to clear reviews? Run:**
```bash
clear_reviews.bat
```
