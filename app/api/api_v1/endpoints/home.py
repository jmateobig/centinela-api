from fastapi import APIRouter
from api.api_v1.services.service import service_categories, service_home_cards_values
from api.api_v1.models.models import  body_products

router = APIRouter()

@router.get("/categories/{uuid}")
async def endpoint_categories(uuid: str):
    return service_categories(uuid=uuid)

@router.post("/index_cards")
async def endpoint_home_cards_values(jsonBody: body_products):
    return service_home_cards_values(uuid=jsonBody.uuid, categories=jsonBody.categories)