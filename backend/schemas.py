from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import TaskStatus, TaskType

class UserBase(BaseModel):
    email: EmailStr
    clerk_id: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    gem_balance: int
    created_at: datetime

    class Config:
        from_attributes = True

class SwapTaskBase(BaseModel):
    type: TaskType
    source_url: str
    template_url: str

class SwapTaskCreate(SwapTaskBase):
    pass

class SwapTask(SwapTaskBase):
    id: int
    user_id: int
    status: TaskStatus
    cost: int
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    amount_gems: int
    amount_usd: int

class Transaction(TransactionBase):
    id: int
    user_id: int
    stripe_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class GemBalance(BaseModel):
    gem_balance: int
