import requests
import sys
import os

# Add backend to sys.path to access database if needed, but using API is cleaner if server is running.
# OR we can just use SQL directly/CRUD if we want to bypass API.
# Let's use direct DB access to ensure it works even if API auth is tricky (though templates might be public).
# Actually, crud is easier since we have the functions.

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal, engine
import models
import crud
import schemas

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

TEMPLATES = [
    {
        "title": "Cyberpunk Warrior",
        "type": "IMAGE",
        "thumbnail": "https://images.unsplash.com/photo-1605810230434-7631ac76ec81",
        "cost": 1
    },
    {
        "title": "Viking Legend",
        "type": "IMAGE",
        "thumbnail": "https://images.unsplash.com/photo-1559526323-cb2f2fe2591b",
        "cost": 1
    },
    {
        "title": "Neon City Video",
        "type": "VIDEO",
        "thumbnail": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
        "cost": 10
    },
    {
        "title": "Forest Spirit",
        "type": "IMAGE",
        "thumbnail": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
        "cost": 1
    }
]

def seed_templates():
    db = SessionLocal()
    try:
        existing = crud.get_templates(db)
        if existing:
            print(f"Found {len(existing)} templates. Skipping seed.")
            return

        print("Seeding templates...")
        for t in TEMPLATES:
            # Create schema object
            template_create = schemas.TemplateCreate(
                title=t["title"],
                type=t["type"],
                thumbnail=t["thumbnail"],
                cost=t["cost"]
            )
            crud.create_template(db, template_create)
            print(f"Created template: {t['title']}")
            
        print("Seeding complete!")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_templates()
