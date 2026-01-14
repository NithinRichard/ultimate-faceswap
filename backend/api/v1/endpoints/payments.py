from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
import os
from database import get_db
import crud, models, auth

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, endpoint_secret
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        client_id = session.get('client_reference_id')
        if not client_id:
            return {"status": "ignored", "reason": "no client_reference_id"}

        # Extract amount of gems from metadata or line items
        # For this MVP, we'll assume a fixed amount for now or check metadata
        gems_to_add = int(session.get('metadata', {}).get('gems', 0))
        
        user = crud.get_user_by_clerk_id(db, clerk_id=client_id)
        if user:
            crud.update_user_gems(db, user.id, gems_to_add)
            
            # Record transaction
            new_tx = models.Transaction(
                user_id=user.id,
                stripe_id=session.id,
                amount_gems=gems_to_add,
                amount_usd=session.amount_total,
                status="completed"
            )
            db.add(new_tx)
            db.commit()

    return {"status": "success"}

@router.post("/create-checkout-session")
def create_checkout_session(
    package_name: str,
    gems: int,
    price_cents: int, # e.g. 900 for $9.00
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    # In a real app, strictly validate package_name/price on backend
    domain_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"{gems} Gems ({package_name})",
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain_url + '/buy-gems?success=true',
            cancel_url=domain_url + '/buy-gems?canceled=true',
            client_reference_id=current_user.clerk_id,
            metadata={
                'gems': gems,
                'user_id': current_user.id
            }
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
