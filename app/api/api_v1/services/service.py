from api.api_v1.database.querys import get_table, get_table_dashboard_heders_value
from api.api_v1.database.querys import get_query_dashboard_data, get_query_cards_data


def get_table_dashboard_heders(role, id_company):
    return get_table_dashboard_heders_value(role=role, id_company=id_company)

def get_table_dashboard_data(role, id_company, page, filters):
    query = get_query_dashboard_data(role=role, id_company=id_company, page=page, filters=filters)
    return get_table(query=query)

def get_cards_dashboard_data(id_company):
    query = get_query_cards_data(id_company=id_company)
    return get_table(query=query)


    