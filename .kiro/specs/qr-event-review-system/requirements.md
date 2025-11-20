# Requirements Document

## Introduction

This document specifies the requirements for a dual-mode review system for the PicMe application. The system enables users to write event-specific reviews (requiring QR code verification) and general website reviews (no QR code required). The feature ensures secure, authenticated review submission with proper ownership controls for editing and deletion.

## Glossary

- **Review System**: The complete functionality allowing users to submit, view, edit, and delete reviews
- **Event Review**: A review specific to an event that requires QR code scanning for verification
- **General Review**: A review about the PicMe website/service that does not require QR code scanning
- **QR Scanner**: The existing QR code scanning functionality that extracts event identifiers
- **Event Attendee**: A user who has scanned a valid event QR code
- **Review Owner**: The user who created a specific review
- **My Reviews Dashboard**: The user interface section displaying all reviews created by the logged-in user

## Requirements

### Requirement 1: Event-Specific Review Submission

**User Story:** As an event attendee, I want to write a review for a specific event after scanning its QR code, so that I can share my experience about that particular event.

#### Acceptance Criteria

1. WHEN a user scans a valid event QR code, THE Review System SHALL extract the event_id from the QR code data
2. WHEN the event_id is successfully extracted, THE Review System SHALL display a review form specific to that event
3. WHEN a user submits an event review, THE Review System SHALL store the review with user_id, username, event_id, review_text, rating, and timestamp
4. WHEN a user attempts to submit an event review, THE Review System SHALL verify that the user has scanned the QR code for that event
5. IF a user has not scanned the event QR code, THEN THE Review System SHALL reject the review submission and display the message "You need a valid event QR code to write a review for this event"

### Requirement 2: General Website Review Submission

**User Story:** As a PicMe user, I want to write a general review about the PicMe website, so that I can share my overall experience with the service.

#### Acceptance Criteria

1. THE Review System SHALL provide a general review form accessible without QR code scanning
2. WHEN a user submits a general review, THE Review System SHALL store the review with user_id, username, review_text, rating, is_general_review flag set to 1, and event_id set to NULL
3. THE Review System SHALL allow each user to submit only one general website review
4. WHEN a user who has already submitted a general review attempts to submit another, THE Review System SHALL update the existing general review instead of creating a new one

### Requirement 3: Review Data Validation

**User Story:** As a system administrator, I want all reviews to meet quality standards, so that the review content is meaningful and properly formatted.

#### Acceptance Criteria

1. WHEN a user submits a review, THE Review System SHALL validate that the rating is an integer between 1 and 5 inclusive
2. WHEN a user submits a review, THE Review System SHALL validate that the review_text contains at least 10 characters
3. WHEN a user submits a review, THE Review System SHALL validate that the review_text does not exceed 500 characters
4. IF validation fails, THEN THE Review System SHALL reject the submission and display an appropriate error message

### Requirement 4: My Reviews Dashboard Display

**User Story:** As a user, I want to view all my reviews in one place, so that I can track what feedback I have provided.

#### Acceptance Criteria

1. THE Review System SHALL display a "My Reviews" section in the user dashboard
2. WHEN displaying reviews, THE Review System SHALL group event-specific reviews by event name
3. WHEN displaying reviews, THE Review System SHALL show the general website review separately if it exists
4. WHEN displaying each review, THE Review System SHALL show the review text, rating, event name (for event reviews), and timestamp
5. THE Review System SHALL display only reviews created by the currently logged-in user

### Requirement 5: Review Editing

**User Story:** As a user, I want to edit my own reviews, so that I can update my feedback if my opinion changes.

#### Acceptance Criteria

1. WHEN a user views their reviews in the My Reviews dashboard, THE Review System SHALL display an "Edit" option for each review
2. WHEN a user clicks the Edit option, THE Review System SHALL display a pre-filled form with the existing review data
3. WHEN a user submits an edited review, THE Review System SHALL verify that the user is the review owner
4. IF the user is not the review owner, THEN THE Review System SHALL reject the edit request
5. WHEN a valid edit is submitted, THE Review System SHALL update the review_text, rating, and timestamp fields

### Requirement 6: Review Deletion

**User Story:** As a user, I want to delete my own reviews, so that I can remove feedback I no longer want to share.

#### Acceptance Criteria

1. WHEN a user views their reviews in the My Reviews dashboard, THE Review System SHALL display a "Delete" option for each review
2. WHEN a user clicks the Delete option, THE Review System SHALL prompt for confirmation
3. WHEN a user confirms deletion, THE Review System SHALL verify that the user is the review owner
4. IF the user is not the review owner, THEN THE Review System SHALL reject the deletion request
5. WHEN a valid deletion is confirmed, THE Review System SHALL permanently remove the review from the database

### Requirement 7: Review Ownership Security

**User Story:** As a system administrator, I want to ensure users can only modify their own reviews, so that review integrity is maintained.

#### Acceptance Criteria

1. WHEN a user attempts to edit a review, THE Review System SH
ALL verify the user_id matches the review's user_id
2. WHEN a user attempts to delete a review, THE Review System SHALL verify the user_id matches the review's user_id
3. IF ownership verification fails, THEN THE Review System SHALL return a 403 Forbidden error
4. THE Review System SHALL prevent User A from viewing, editing, or deleting User B's reviews

### Requirement 8: QR Code Event Attendance Tracking

**User Story:** As a system administrator, I want to track which users have scanned event QR codes, so that I can verify eligibility for event-specific reviews.

#### Acceptance Criteria

1. WHEN a user scans an event QR code, THE Review System SHALL record the user_id and event_id in the event_attendees table
2. THE Review System SHALL record the scan timestamp for audit purposes
3. WHEN a user scans the same event QR code multiple times, THE Review System SHALL maintain only one attendance record per user per event
4. WHEN a user attempts to submit an event review, THE Review System SHALL query the event_attendees table to verify attendance

### Requirement 9: Review Retrieval and Display

**User Story:** As a user, I want to see reviews for events and the website, so that I can make informed decisions about attending events or using the service.

#### Acceptance Criteria

1. THE Review System SHALL provide an API endpoint to retrieve all reviews for a specific event
2. THE Review System SHALL provide an API endpoint to retrieve all general website reviews
3. WHEN retrieving reviews, THE Review System SHALL include the reviewer's username, rating, review text, and timestamp
4. THE Review System SHALL order reviews by creation timestamp in descending order (newest first)
5. THE Review System SHALL calculate and display the average rating for events and the website

### Requirement 10: Database Schema Integrity

**User Story:** As a database administrator, I want a properly structured database schema, so that review data is stored consistently and efficiently.

#### Acceptance Criteria

1. THE Review System SHALL store reviews in a table with columns: id, user_id, username, event_id, review_text, rating, is_general_review, created_at, updated_at
2. THE Review System SHALL store event attendance in a table with columns: id, user_id, event_id, scanned_at
3. THE Review System SHALL enforce a foreign key constraint between reviews.user_id and users.id
4. THE Review System SHALL create an index on event_id for efficient event review queries
5. THE Review System SHALL create a unique constraint on (user_id, event_id) in the event_attendees table to prevent duplicate attendance records

### Requirement 11: Existing Feature Preservation

**User Story:** As a system administrator, I want all existing features to remain functional, so that the new review system does not disrupt current operations.

#### Acceptance Criteria

1. THE Review System SHALL NOT modify the existing QR scanning functionality
2. THE Review System SHALL NOT modify the existing event display functionality
3. THE Review System SHALL NOT modify the existing user/admin login systems
4. THE Review System SHALL NOT modify the existing photo display functionality
5. THE Review System SHALL NOT modify the existing admin dashboard functionality
