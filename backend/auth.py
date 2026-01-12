from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import crud, models
import os
from clerk_backend_api import Clerk

security = HTTPBearer()

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    # In a real app, you'd verify the JWT with Clerk's public key
    # For now, we'll implement a placeholder that expects the Clerk ID in the token or as a mock
    # clerk = Clerk(bearer_token=os.getenv("CLERK_SECRET_KEY"))
    
    # We'll assume the token *is* the clerk_id for simplicity in this MVP 
    # OR you'd actually use clerk.verify_token(token.credentials)
    
    clerk_id = token.credentials # THIS IS A PLACEHOLDER. Replace with real JWT verification.
    
    user = crud.get_user_by_clerk_id(db, clerk_id=clerk_id)
    if not user:
        # If user doesn't exist in our DB but is authenticated in Clerk, create them
        # (Usually handled via a webhook or first-login check)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in local database",
        )
    return user
