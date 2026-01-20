from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router
from database import engine
from models import Base

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import sys
    error_msg = str(e)
    if "Tenant or user not found" in error_msg:
        print("\n" + "="*80)
        print("CRITICAL DATABASE CONFIGURATION ERROR")
        print("="*80)
        print("You are using the Supavisor connection pooler (port 6543) but the username is incorrect.")
        print("When using the pooler, the username MUST be in the format: user.project_ref")
        print("Example: postgres.nidwhonclawjduojrntq")
        print("\nPlease update your DATABASE_URL in Render to use the correct username.")
        print("="*80 + "\n")
    raise e

app = FastAPI(title="Ultimate Faceswap API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/results", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Ultimate Faceswap API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
