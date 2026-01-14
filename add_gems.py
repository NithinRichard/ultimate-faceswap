import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import User

def add_gems(user_id=1, amount=100):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            print(f"User {user.email} (ID: {user.id}) currently has {user.gem_balance} gems.")
            user.gem_balance += amount
            db.commit()
            db.refresh(user)
            print(f"Added {amount} gems. New balance: {user.gem_balance}")
        else:
            print(f"User ID {user_id} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_gems()
