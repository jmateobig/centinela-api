from sqlalchemy import text
from api.api_v1.enums.enums import ROLE, TYPE_FILTER, TYPE_DATA
from api.api_v1.database.connection import query_execute

#Metodo para  obtener mi marketplace
def get_my_marketplace(id_company):
    query = text('''
        SELECT a.id_marketplace, b.name as marketplace
        FROM public.asignament a
        INNER JOIN marketplace b ON a.id_marketplace=b.id
        WHERE id_company=:id_company_param
    ''').bindparams(id_company_param=id_company)
    result = query_execute(query)
    return result.fetchone() or None


#Metodo para  obtener las  marketplaces con las  que compito
def get_compare_marketplace(id_company):
    query = text('''
        SELECT a.id_marketplace, b.name as marketplace
        FROM public.company_marketplace a
        INNER JOIN marketplace b ON a.id_marketplace=b.id
        WHERE id_company=:id_company_param
    ''').bindparams(id_company_param=id_company)
    result = query_execute(query)
    return result.fetchall() or None

#Metodo para serializar los filtros  en un array
def get_filter_conditions(filters):
    conditions = [] 
    for filter in filters:
        if filter.value:
            condition=''
            if filter.type_filter == TYPE_FILTER.TEXTO.value:
                condition = f"{filter.field} {filter.conector} '{filter.extra_value}{filter.value}{filter.extra_value}'"
            elif filter.type_filter == TYPE_FILTER.NUMERO.value:
                condition = f"{filter.field} {filter.conector} {filter.value}"
            conditions.append(condition)
    return conditions


#Metodo para filtrar por condicion respecto al promedio.
def get_type_data_condition(type_data, my_marketplace):
    if type_data == TYPE_DATA.UP.value:
        return [f'b."{my_marketplace[1]}" > b."Promedio"']
    elif type_data == TYPE_DATA.IN.value:
        return [f'b."{my_marketplace[1]}" = b."Promedio"']
    elif type_data == TYPE_DATA.DOWN.value:
        return [f'b."{my_marketplace[1]}" < b."Promedio"']
    return []


#Metodo que Serializa el Where
def get_where_clause(conditions, operator):
    where = "WHERE " + f" {operator} ".join(conditions) if (conditions) else ""
    return where


#Metodo para generar los encabezados dinamicos para el select
def get_select_values(role, my_marketplace, other_marketplaces):
    SELECT_VALUES = f'b."{my_marketplace[1]}", '
    MARKETPLACE_VALUES = []
    MARKETPLACE_IN = [str(my_marketplace[0])]
    n = 1

    for marketplace in other_marketplaces:
        if role == ROLE.ADMIN.value or role == ROLE.PLAN_3.value:
            SELECT_VALUES += f'b."{marketplace[1]}", '
            MARKETPLACE_VALUES.append(f'MAX(CASE WHEN mp.Id_marketplace = {marketplace[0]} THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "{marketplace[1]}", ')
        elif role == ROLE.PLAN_2.value:
            SELECT_VALUES += f'b."Tienda_{n}", '
            MARKETPLACE_VALUES.append(f'MAX(CASE WHEN mp.Id_marketplace = {marketplace[0]} THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Tienda_{n}", ')
        MARKETPLACE_IN.append(str(marketplace[0]))
        n += 1

    SELECT_VALUES += 'b."Promedio", '
    MARKETPLACE_VALUES.append(f'MAX(CASE WHEN mp.Id_marketplace = {my_marketplace[0]} THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "{my_marketplace[1]}", ')
    MARKETPLACE_VALUES.append(f'ROUND(AVG(CASE WHEN mp.Id_marketplace NOT IN ({my_marketplace[0]}) THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END), 2) AS "Promedio",')
    MARKETPLACE_VALUES = "\n".join(MARKETPLACE_VALUES)

    return {'SELECT_VALUES': SELECT_VALUES, 'MARKETPLACE_VALUES': MARKETPLACE_VALUES, 'MARKETPLACE_IN': ", ".join(MARKETPLACE_IN)}


#Metodos para obtener los marketplaces externos
def get_select_values_marketplace_out(other_marketplaces):
    marketplace_ids_out = [mp[0] for mp in other_marketplaces]
    return ','.join(str(id) for id in marketplace_ids_out)


#Metodos para obtener los marketplaces Externos, e Internos
def get_select_values_chart(role, my_marketplace, other_marketplaces):
    if  role == ROLE.ADMIN.value or role == ROLE.PLAN_3.value:
        marketplace_ids_in = [my_marketplace[0]] + [mp[0] for mp in other_marketplaces]
        marketplace_ids_out = [mp[0] for mp in other_marketplaces]
        select_value = "mm.name, "
    elif role == ROLE.PLAN_2.value:
        marketplace_ids_in = [my_marketplace[0]] + [mp[0] for mp in other_marketplaces]
        marketplace_ids_out = [mp[0] for mp in other_marketplaces]
        select_value = f"""
            CASE
                WHEN mp.Id_Marketplace = {my_marketplace[0]} THEN mm.name
                ELSE mm.name_2
            END AS name, 
        """
    elif role == ROLE.PLAN_1.value:
        marketplace_ids_in = [my_marketplace[0]]
        marketplace_ids_out = [mp[0] for mp in other_marketplaces]
        select_value = "mm.name, "
    
    return {
        'SELECT_VALUE': select_value,
        'MARKETPLACES_IN': ','.join(str(id) for id in marketplace_ids_in),
        'MARKETPLACES_OUT': ','.join(str(id) for id in marketplace_ids_out),
    }
    

#Obtener la subquery valores minimo y maximo
def subquery_card(order, values_in, product, name):
    return f'''
    (SELECT a.name AS marketplace, a.price AS value_product, a.formatted_date AS date_product
        FROM (
        SELECT a.id_product, {name} AS name,
        ROUND(LEAST(p.price, p.offer_price), 2) AS price,
            TO_CHAR(p.date_start, 'DD/MM/YYYY') AS formatted_date
            FROM public.marketplace_product a
            INNER JOIN public.price p ON p.id_marketplace_product = a.id
            INNER JOIN public.marketplace m ON m.id = a.id_marketplace
        WHERE m.id IN ({values_in}) AND a.id_product = {product}) a
        ORDER BY a.price {order}
        LIMIT 1)
    '''


#Obtener la subquery valores promedio
def subquery_card_2(values_in, product, name):
    return f'''
    (
    SELECT 'Promedio' AS marketplace, ROUND(AVG(a.price),2) AS value_product, '00/00/0000' AS date_product
            FROM (
                SELECT a.id_product, {name} AS name,
                ROUND(LEAST(p.price, p.offer_price), 2) AS price,
                TO_CHAR(p.date_start, 'DD/MM/YYYY') AS formatted_date
                FROM public.marketplace_product a
                INNER JOIN public.price p ON p.id_marketplace_product = a.id
                INNER JOIN public.marketplace m ON m.id = a.id_marketplace
                WHERE m.id IN ({values_in}) AND a.id_product = {product}
            ) a
        GROUP BY (marketplace, date_product)
    )
    '''