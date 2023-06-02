from fastapi import APIRouter
from api.api_v1.models.models import comparative_table_heders, comparative_table_data, body_products
from api.api_v1.services.service import get_table_dashboard_data, get_cards_dashboard_data
from api.api_v1.services.service import get_table_dashboard_heders, get_filter_dashboard_product
from api.api_v1.services.service import get_timeline_product_data, get_cards_product_data
from api.api_v1.services.service import get_filter_categories

router = APIRouter()

@router.post("/table_comparative_heders")
async def get_table_heders(jsonBody : comparative_table_heders):
    return get_table_dashboard_heders(uuid=jsonBody.uuid)

@router.post("/table_comparative_data")
async def get_table_data(jsonBody : comparative_table_data):
    return get_table_dashboard_data(uuid=jsonBody.uuid, page=jsonBody.page, filters=jsonBody.filters, type_data=jsonBody.type_data, categories=jsonBody.categories)

@router.post("/cards_comparative")
async def get_cards_data(jsonBody: body_products):
    return get_cards_dashboard_data(uuid=jsonBody.uuid, categories=jsonBody.categories)

@router.post("/filter_product")
async def get_filter_product(jsonBody: body_products):
    return get_filter_dashboard_product(uuid=jsonBody.uuid, categories=jsonBody.categories)

@router.get("/get_timel_line_product/{uuid}/{id_product}")
async def get_time_line_product(uuid: str, id_product:str):
    return get_timeline_product_data(uuid=uuid, id_product=id_product)

@router.get("/get_cards_product/{uuid}/{id_product}")
async def get_cards_product(uuid: str, id_product:str):
    return get_cards_product_data(uuid=uuid, id_product=id_product)

@router.get("/get_categories/{uuid}")
async def get_categories(uuid: str):
    return get_filter_categories(uuid=uuid)