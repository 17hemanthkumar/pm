"""
Script to reprocess all uploaded photos with new tolerance settings.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import process_images, UPLOAD_FOLDER

def reprocess_all_events():
    """Reprocess all events that have uploaded photos"""
    print("=" * 60)
    print("REPROCESSING ALL EVENTS WITH NEW TOLERANCE (0.65)")
    print("=" * 60)
    
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"Upload folder not found: {UPLOAD_FOLDER}")
        return
    
    # Find all event folders
    event_folders = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.startswith('event_') and os.path.isdir(os.path.join(UPLOAD_FOLDER, f))
    ]
    
    if not event_folders:
        print("No events found to reprocess")
        return
    
    print(f"\nFound {len(event_folders)} events to reprocess:")
    for event_id in event_folders:
        print(f"  - {event_id}")
    
    print("\nStarting reprocessing...\n")
    
    for event_id in event_folders:
        print(f"\n{'='*60}")
        print(f"Processing: {event_id}")
        print(f"{'='*60}")
        
        try:
            process_images(event_id)
            print(f"✓ Successfully processed {event_id}")
        except Exception as e:
            print(f"✗ Error processing {event_id}: {e}")
    
    print("\n" + "=" * 60)
    print("REPROCESSING COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    reprocess_all_events()
