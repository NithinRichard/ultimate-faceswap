from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/faceswap")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5433/faceswap",
)


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Ensure SSL is used for cloud databases (Supabase) - Fixed for comprehensive detection
connect_args = {}
if "supabase." in DATABASE_URL:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=300,
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
