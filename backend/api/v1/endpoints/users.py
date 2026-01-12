from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas, auth
from database import get_db

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@router.get("/balance", response_model=schemas.GemBalance)
def get_balance(current_user: schemas.User = Depends(auth.get_current_user)):
    return {"gem_balance": current_user.gem_balance}
