import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
import crud
import schemas

def add_template():
    db = SessionLocal()
    try:
        # Video URL (Mixkit preview)
        video_url = "https://assets.mixkit.co/videos/preview/mixkit-urban-model-walking-in-slow-motion-1556-large.mp4"
        
        # Thumbnail URL (Unsplash - Urban walking)
        # Using a reliable one
        thumb_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600"

        print(f"Checking video URL: {video_url}...")
        try:
            r = requests.head(video_url)
            if r.status_code != 200:
                print(f"Warning: Video URL returned status {r.status_code}")
            else:
                print("Video URL is valid.")
        except Exception as e:
            print(f"Warning: Could not verify URL: {e}")

        t = schemas.TemplateCreate(
            title="Urban Model Walk",
            type="VIDEO",
            thumbnail=thumb_url,
            cost=15 # Premium video
        )
        
        created = crud.create_template(db, t)
        print(f"Successfully added template: {created.title} (ID: {created.id})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_template()
