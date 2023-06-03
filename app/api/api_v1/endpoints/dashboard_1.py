from fastapi import APIRouter
from api.api_v1.services.service import service_cards_data, service_table_comparative_heders, service_table_comparative_data
from api.api_v1.models.models import comparative_table_heders, comparative_table_data, body_products


router = APIRouter()

@router.post("/cards_comparative")
async def endpoint_cards_data(jsonBody: body_products):
    return service_cards_data(uuid=jsonBody.uuid, categories=jsonBody.categories)

@router.post("/table_comparative_heders")
async def endpoint_table_comparative_heders(jsonBody : comparative_table_heders):
    return service_table_comparative_heders(uuid=jsonBody.uuid)

@router.post("/table_comparative_data")
async def endpoint_table_comparative_data(jsonBody : comparative_table_data):
    return service_table_comparative_data(uuid=jsonBody.uuid, page=jsonBody.page, filters=jsonBody.filters, type_data=jsonBody.type_data, categories=jsonBody.categories)