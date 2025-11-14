# Implementation Plan

- [ ] 1. Remove testimonials section from homepage
  - Locate and delete the entire "What People Are Saying" section from homepage.html
  - Remove the section container, all three testimonial cards, and associated HTML
  - Verify proper spacing remains between "How PicMe Works" and "CTA Section"
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2. Implement dynamic hero image carousel
  - [ ] 2.1 Create hero carousel JavaScript functions
    - Write `loadHeroEvents()` function to fetch events from `/api/events` endpoint
    - Implement event filtering logic to select events with valid images (prioritize `cover_thumbnail`, fallback to `image`)
    - Add sorting by `created_at` to show most recent events first
    - Limit carousel to maximum 10 events
    - _Requirements: 1.1, 1.2_
  
  - [ ] 2.2 Implement carousel display and rotation logic
    - Write `updateHeroImage(index)` function to update image and metadata overlay
    - Implement smooth fade transitions using CSS opacity
    - Create `startHeroRotation()` function with 5-second auto-rotation interval
    - Add logic to handle single event (no rotation) and zero events (default image)
    - _Requirements: 1.3, 1.4, 1.5_
  
  - [ ] 2.3 Update hero section HTML structure
    - Replace static Unsplash image with dynamic image element (id="heroEventImage")
    - Add dynamic metadata elements (ids: heroEventCategory, heroEventName, heroEventPhotos)
    - Maintain existing Tailwind CSS classes for styling consistency
    - Add transition classes for smooth image changes
    - _Requirements: 1.2, 1.4_
  
  - [ ] 2.4 Implement error handling and fallback logic
    - Add try-catch blocks for API fetch errors
    - Implement fallback to default placeholder image when no events available
    - Handle individual image load failures by skipping to next event
    - Add console logging for debugging (no user-facing error messages)
    - _Requirements: 1.5_
  
  - [ ] 2.5 Initialize carousel on page load
    - Add event listener for `DOMContentLoaded` to trigger `loadHeroEvents()`
    - Ensure carousel initialization doesn't block page rendering
    - Add cleanup logic to clear interval on page unload
    - _Requirements: 1.1, 1.3_

- [ ] 3. Test and verify implementation
  - [ ] 3.1 Test carousel functionality with various event counts
    - Test with 0 events (should show default image)
    - Test with 1 event (should display without rotation)
    - Test with 3+ events (should auto-rotate every 5 seconds)
    - Verify smooth transitions between images
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [ ] 3.2 Verify testimonials removal and page layout
    - Confirm testimonials section is completely removed
    - Check spacing between remaining sections looks natural
    - Test responsive design on mobile and tablet viewports
    - Verify all other homepage sections remain functional
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 3.3 Test error scenarios
    - Test with network disconnected (API failure)
    - Test with events that have invalid image URLs
    - Verify graceful degradation in all error cases
    - _Requirements: 1.5_
