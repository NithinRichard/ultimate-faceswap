from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    gem_balance = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("SwapTask", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class SwapTask(Base):
    __tablename__ = "swap_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    type = Column(Enum(TaskType))
    cost = Column(Integer)
    source_url = Column(String, nullable=True)
    template_url = Column(String, nullable=True)
    result_url = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_id = Column(String, unique=True, index=True)
    amount_gems = Column(Integer)
    amount_usd = Column(Integer) # in cents
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
