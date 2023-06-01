from api.api_v1.database.querys import get_table, get_table_dashboard_heders_value
from api.api_v1.database.querys import get_query_dashboard_data, get_query_cards_data, get_query_filter_product
from api.api_v1.database.querys import get_query_time_line_product, get_query_cards_product


def get_table_dashboard_heders(uuid):
    return get_table_dashboard_heders_value(uuid=uuid)

def get_table_dashboard_data(uuid, page, filters, type_data):
    query = get_query_dashboard_data(uuid=uuid, page=page, filters=filters, type_data=type_data)
    return get_table(query=query)

def get_cards_dashboard_data(uuid):
    query = get_query_cards_data(uuid=uuid)
    return get_table(query=query)

def get_filter_dashboard_product(uuid):
    query = get_query_filter_product(uuid=uuid)
    return get_table(query=query)

def get_timeline_product_data(uuid, id_product):
    query=get_query_time_line_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)

def get_cards_product_data(uuid, id_product):
    query=get_query_cards_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)
