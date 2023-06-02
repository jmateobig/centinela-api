from api.api_v1.database.querys import get_table, get_table_dashboard_heders_value
from api.api_v1.database.querys import get_query_dashboard_data, get_query_cards_data, get_query_filter_product
from api.api_v1.database.querys import get_query_time_line_product, get_query_cards_product
from api.api_v1.database.querys import get_query_filter_categories


def get_table_dashboard_heders(uuid):
    return get_table_dashboard_heders_value(uuid=uuid)

def get_table_dashboard_data(uuid, page, filters, type_data, categories):
    query = get_query_dashboard_data(uuid=uuid, page=page, filters=filters, type_data=type_data, categories=categories)
    return get_table(query=query)

def get_cards_dashboard_data(uuid, categories):
    query = get_query_cards_data(uuid=uuid, categories=categories)
    return get_table(query=query)

def get_filter_dashboard_product(uuid, categories):
    query = get_query_filter_product(uuid=uuid, categories=categories)
    return get_table(query=query)

def get_timeline_product_data(uuid, id_product):
    query=get_query_time_line_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)

def get_cards_product_data(uuid, id_product):
    query=get_query_cards_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)

def get_filter_categories(uuid):
    query=get_query_filter_categories(uuid=uuid)
    return get_table(query=query)