from fastapi import APIRouter

from api.api_v1.endpoints import dashboard

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

