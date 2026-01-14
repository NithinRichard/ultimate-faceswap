from fastapi import APIRouter
from api.v1.endpoints import users, swaps, payments, templates

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(swaps.router, prefix="/swaps", tags=["swaps"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
