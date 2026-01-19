from fastapi import APIRouter, Request, Header, HTTPException, Depends, Body
from sqlalchemy.orm import Session
import razorpay
import os
import hmac
import hashlib
from database import get_db
import crud, models, auth
from pydantic import BaseModel

router = APIRouter()

# Initialize Razorpay Client
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder")
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class OrderCreate(BaseModel):
    package_name: str
    gems: int
    price_inr: int # Price in INR (e.g., 9 for ₹9)

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    gems: int # Pass this from frontend for verification simplicity in MVP

@router.post("/create-order")
def create_order(
    request: OrderCreate,
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        amount_paise = request.price_inr * 100 # Razorpay takes amount in paise
        
        data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"receipt_user_{current_user.id}",
            "notes": {
                "user_id": current_user.id,
                "gems": request.gems,
                "package": request.package_name
            }
        }
        
        order = client.order.create(data=data)
        return order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-payment")
def verify_payment(
    verification: PaymentVerify,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verify Signature
        params_dict = {
            'razorpay_order_id': verification.razorpay_order_id,
            'razorpay_payment_id': verification.razorpay_payment_id,
            'razorpay_signature': verification.razorpay_signature
        }
        
        # Verify signature using the client utility or manual HMAC
        # client.utility.verify_payment_signature(params_dict) # This method can raise errors if invalid
        
        # Manual verification to be safe and explicit
        msg = f"{verification.razorpay_order_id}|{verification.razorpay_payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != verification.razorpay_signature:
             raise HTTPException(status_code=400, detail="Invalid payment signature")
             
        # Check if transaction already exists to effect idempotency
        existing_tx = db.query(models.Transaction).filter(models.Transaction.stripe_id == verification.razorpay_payment_id).first()
        if existing_tx:
             return {"status": "already_processed"}

        # Success! Add Gems
        crud.update_user_gems(db, current_user.id, verification.gems)
        
        # Record transaction (Reusing stripe_id field for razorpay_payment_id for now)
        new_tx = models.Transaction(
            user_id=current_user.id,
            stripe_id=verification.razorpay_payment_id, # Storing Payment ID here
            amount_gems=verification.gems,
            amount_usd=0, # Assuming INR, can store 0 or convert roughly
            status="completed"
        )
        db.add(new_tx)
        db.commit()
        
        return {"status": "success", "new_balance": current_user.gem_balance + verification.gems} # Approximate, or re-fetch

    except Exception as e:
        print(f"Payment verification failed: {e}")
        raise HTTPException(status_code=400, detail="Payment verification failed")
