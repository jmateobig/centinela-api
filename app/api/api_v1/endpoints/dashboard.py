from fastapi import APIRouter
from api.api_v1.models.models import comparative_table_heders, comparative_table_data
from api.api_v1.services.service import get_table_dashboard_data, get_cards_dashboard_data
from api.api_v1.services.service import get_table_dashboard_heders

router = APIRouter()

@router.post("/table_comparative_heders")
async def get_table_heders(jsonBody : comparative_table_heders):
    return get_table_dashboard_heders(role=jsonBody.role_name, id_company=jsonBody.id_company)

@router.post("/table_comparative_data")
async def get_table_data(jsonBody : comparative_table_data):
    return get_table_dashboard_data(role=jsonBody.role_name, id_company=jsonBody.id_company, page=jsonBody.page, filters=jsonBody.filters)


@router.get("/cards_comparative/{id_company}")
async def get_cards_data(id_company: int):
    return get_cards_dashboard_data(id_company=id_company)
