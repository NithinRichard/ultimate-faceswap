import sys
import os
import shutil
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import schemas
from database import SessionLocal, engine
import models
import crud

# Make sure tables exist (and update schema if needed - SQLAlchemy won't auto-migrate columns though)
# Since we added a column, simpler way in dev is to let user know or use SQL.
# But for now let's hope the table recreation works or we might need to manually add column via SQL if table exists.
# models.Base.metadata.create_all(bind=engine) 

def ensure_column_exists():
    # Hacky migration for dev environment: Try to select source_url, if fail, add it.
    import sqlite3
    # We are using postgres...
    # Let's just run an ALTER TABLE command safely.
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE templates ADD COLUMN IF NOT EXISTS source_url VARCHAR"))
        db.commit()
        print("Ensured source_url column exists.")
    except Exception as e:
        print(f"Migration warning: {e}")
    finally:
        db.close()

def upload_template(file_path, title, type="VIDEO", cost=10, thumbnail_url=None):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Verify type
    if type.upper() not in ["IMAGE", "VIDEO"]:
        print("Error: Type must be IMAGE or VIDEO")
        return

    # 1. Copy file to backend/static/uploads
    filename = os.path.basename(file_path)
    # Add timestamp to avoid collisions
    timestamp = int(datetime.now().timestamp())
    target_filename = f"{timestamp}_{filename}"
    
    backend_static_dir = os.path.join("backend", "static", "uploads")
    os.makedirs(backend_static_dir, exist_ok=True)
    
    target_path = os.path.join(backend_static_dir, target_filename)
    
    print(f"Copying {file_path} to {target_path}...")
    shutil.copy(file_path, target_path)
    
    # 2. Add to DB
    # The URL should be relative path accessible via web or absolute internal path?
    # Worker expects either http URL OR local path relative to backend root?
    # Worker: "template_path = os.path.join(base_path, task.template_url.lstrip('/'))"
    # So we should store: "/static/uploads/filename"
    
    relative_url = f"/static/uploads/{target_filename}"
    
    # If thumbnail not provided for video, user should provide one. 
    # For now default to something generic if missing.
    if not thumbnail_url:
        if type.upper() == "VIDEO":
             thumbnail_url = "https://placehold.co/600x800/png?text=Video+Template" # Placeholder
             print("Warning: No thumbnail provided, using placeholder.")
        else:
             thumbnail_url = relative_url # For Image, thumbnail is source

    db = SessionLocal()
    try:
        t = schemas.TemplateCreate(
            title=title,
            type=type.upper(),
            thumbnail=thumbnail_url,
            source_url=relative_url,
            cost=cost
        )
        created = crud.create_template(db, t)
        print(f"Success! Template '{created.title}' added with ID: {created.id}")
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ensure_column_exists() # Run migration check
    
    if len(sys.argv) < 2:
        print("Usage: python upload_template.py <path_to_file> <title> [type] [cost]")
        print("Example: python upload_template.py C:/Downloads/myvideo.mp4 'My Cool Video' VIDEO 15")
    else:
        path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else "Uploaded Template"
        type = sys.argv[3] if len(sys.argv) > 3 else "VIDEO"
        cost = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        
        # Optional: Ask for thumbnail
        thumb = input("Enter thumbnail URL (or press Enter for placeholder): ").strip()
        
        upload_template(path, title, type, cost, thumb if thumb else None)
