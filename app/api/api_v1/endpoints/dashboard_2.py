from fastapi import APIRouter
from api.api_v1.models.models import body_products
from api.api_v1.services.service import service_filter_product, service_cards_product, service_timel_line_product

router = APIRouter()

@router.post("/filter_product")
async def endpoint_filter_product(jsonBody: body_products):
    return service_filter_product(uuid=jsonBody.uuid, categories=jsonBody.categories)

@router.get("/cards_product/{uuid}/{id_product}")
async def endpoint_cards_product(uuid: str, id_product:str):
    return service_cards_product(uuid=uuid, id_product=id_product)

@router.get("/timel_line_product/{uuid}/{id_product}")
async def endpoint_timel_line_product(uuid: str, id_product:str):
    return service_timel_line_product(uuid=uuid, id_product=id_product)