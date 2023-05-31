from fastapi import APIRouter
from api.api_v1.models.models import comparative_table_heders, comparative_table_data
from api.api_v1.services.service import get_table_dashboard_data, get_cards_dashboard_data
from api.api_v1.services.service import get_table_dashboard_heders, get_filter_dashboard_product

router = APIRouter()

@router.post("/table_comparative_heders")
async def get_table_heders(jsonBody : comparative_table_heders):
    return get_table_dashboard_heders(uuid=jsonBody.uuid)

@router.post("/table_comparative_data")
async def get_table_data(jsonBody : comparative_table_data):
    return get_table_dashboard_data(uuid=jsonBody.uuid, page=jsonBody.page, filters=jsonBody.filters, type_data=jsonBody.type_data)


@router.get("/cards_comparative/{uuid}")
async def get_cards_data(uuid: str):
    return get_cards_dashboard_data(uuid=uuid)


@router.get("/filter_product/{uuid}")
async def get_filter_product(uuid: str):
    return get_filter_dashboard_product(uuid=uuid)