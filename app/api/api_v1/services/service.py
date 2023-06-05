from api.api_v1.database.querys import get_table
from api.api_v1.database.querys import query_categories, query_home_cards_values, query_home_chart
from api.api_v1.database.querys import query_cards_data, query_table_comparative_heders, query_table_comparative_data
from api.api_v1.database.querys import query_filter_product, query_cards_product, query_timel_line_product

def service_categories(uuid):
    query=query_categories(uuid=uuid)
    return get_table(query=query)

def service_home_cards_values(uuid, categories):
    return query_home_cards_values(uuid=uuid,categories=categories)

def service_home_chart(uuid, categories):
    query=query_home_chart(uuid=uuid,categories=categories)
    return get_table(query=query)

def service_cards_data(uuid, categories):
    query = query_cards_data(uuid=uuid, categories=categories)
    return get_table(query=query)

def service_table_comparative_heders(uuid):
    return query_table_comparative_heders(uuid=uuid)

def service_table_comparative_data(uuid, page, filters, type_data, categories):
    query = query_table_comparative_data(uuid=uuid, page=page, filters=filters, type_data=type_data, categories=categories)
    return get_table(query=query)

def service_filter_product(uuid, categories):
    query = query_filter_product(uuid=uuid, categories=categories)
    return get_table(query=query)

def service_cards_product(uuid, id_product):
    query=query_cards_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)

def service_timel_line_product(uuid, id_product):
    query=query_timel_line_product(uuid=uuid, id_product=id_product)
    return get_table(query=query)