import os
from supabase import create_client, Client
import shutil

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use service role for backend operations

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Warning: Supabase credentials not found.")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

import mimetypes

def upload_file(file_path: str, bucket_name: str, destination_path: str) -> str:
    """
    Uploads a file to Supabase Storage and returns the public URL.
    """
    supabase = get_supabase()
    if not supabase:
        return None

    try:
        # Guess MIME type
        content_type, _ = mimetypes.guess_type(destination_path)
        if not content_type:
            content_type = "application/octet-stream"

        with open(file_path, 'rb') as f:
            supabase.storage.from_(bucket_name).upload(
                file=f,
                path=destination_path,
                file_options={"content-type": content_type}
            )
        
        # Get Public URL
        # For public buckets, we can construct it manually or ask SDK
        # Public URL format: <SUPABASE_URL>/storage/v1/object/public/<bucket>/<path>
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{destination_path}"
        return public_url
    except Exception as e:
        print(f"Supabase Upload Error: {e}")
        # Identify if it's already there?
        return None

def download_file(url: str, save_path: str):
    """
    Downloads a file from a URL to a local path.
    """
    import requests
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        return True
    return False
