from fastapi import APIRouter

from api.api_v1.endpoints import home, dashboard_1, dashboard_2

api_router = APIRouter()
api_router.include_router(home.router,        prefix="/home", tags=["home"])
api_router.include_router(dashboard_1.router, prefix="/dashboard_1", tags=["dashboard"])
api_router.include_router(dashboard_2.router, prefix="/dashboard_2", tags=["dashboard"])

