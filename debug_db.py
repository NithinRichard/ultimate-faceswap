import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
url = os.getenv('DATABASE_URL')
print(f"DEBUG_CHECK_URL: {url}")
