from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router

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
