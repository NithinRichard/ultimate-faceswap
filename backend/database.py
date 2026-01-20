from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/faceswap")

import socket
from urllib.parse import urlparse, urlunparse

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5433/faceswap",
)

# Fix for Render/Supabase IPv6 issues: Force IPv4 resolution
if "supabase.co" in DATABASE_URL:
    try:
        parsed = urlparse(DATABASE_URL)
        hostname = parsed.hostname
        if hostname:
            # Resolve to IPv4 address
            ip_address = socket.gethostbyname(hostname)
            print(f"Resolved {hostname} to {ip_address} for IPv4 connectivity")
            
            # Replace hostname with IP in the URL
            if parsed.netloc:
                new_netloc = parsed.netloc.replace(hostname, ip_address)
                DATABASE_URL = urlunparse(parsed._replace(netloc=new_netloc))
    except Exception as e:
        print(f"Warning: Failed to force IPv4 resolution: {e}")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
