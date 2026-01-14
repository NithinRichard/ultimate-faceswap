from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import crud, models, schemas
import os
import jwt
# from clerk_backend_api import Clerk # Optional if using SDK for other things

security = HTTPBearer()

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        # Decode the token (For MVP we skip signature verification to avoid JWKS fetching complexity)
        # In PROD: Fetch JWKS from Clerk and verify signature!
        payload = jwt.decode(token.credentials, options={"verify_signature": False})
        clerk_id = payload.get("sub")
        # email = payload.get("email") # specific claim depends on Clerk JWT template
        
        if not clerk_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no sub claim",
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )
    
    user = crud.get_user_by_clerk_id(db, clerk_id=clerk_id)
    if not user:
        # Auto-register the user if they don't exist
        # We might need an email. For now, checking if email is in payload or use dummy
        email = payload.get("email", f"{clerk_id}@example.com") 
        # Note: You need to ensure your Clerk JWT template includes 'email'
        
        user_create = schemas.UserCreate(
            email=email,
            clerk_id=clerk_id
        )
        user = crud.create_user(db=db, user=user_create)

    return user
