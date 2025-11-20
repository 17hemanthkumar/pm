-- Clear All Reviews Script
-- Run this in MySQL to delete all reviews

USE picme_db;

-- Show current review count
SELECT COUNT(*) as 'Total Reviews' FROM reviews;
SELECT COUNT(*) as 'General Reviews' FROM reviews WHERE is_general_review = 1;
SELECT COUNT(*) as 'Event Reviews' FROM reviews WHERE is_general_review = 0;

-- Show current QR scan count
SELECT COUNT(*) as 'Total QR Scans' FROM event_attendees;

-- Uncomment the lines below to delete all reviews
-- DELETE FROM reviews;
-- SELECT 'All reviews deleted!' as Status;

-- Uncomment the line below to also delete QR scan records
-- DELETE FROM event_attendees;
-- SELECT 'All QR scan records deleted!' as Status;

-- Verify deletion
-- SELECT COUNT(*) as 'Remaining Reviews' FROM reviews;
-- SELECT COUNT(*) as 'Remaining QR Scans' FROM event_attendees;
