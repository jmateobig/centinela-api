from api.api_v1.database.connection import query_execute
from api.api_v1.database.querys_app import get_user
from sqlalchemy import text
from api.api_v1.enums.enums import ROLE, TYPE_FILTER, TYPE_DATA

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


#Metodo para obtener los Encabezados de la  tabala
def get_table_dashboard_heders_value(uuid):
    #Get User
    user=get_user(uuid)
    id_company=user[0]
    role=user[1]
    
    my_marketplace = get_my_marketplace(id_company=id_company)
    if my_marketplace is None:
        return {'cols': []}
    other_marketplaces = get_compare_marketplace(id_company=id_company)
    if other_marketplaces is None:
        return {'cols': []}
    cols = ['Producto', 'Sku', my_marketplace[1]]
    for i, marketplace in enumerate(other_marketplaces):
        if (role == ROLE.ADMIN.value or role == ROLE.PLAN_3.value):
            cols.append(marketplace[1])
        elif (role == ROLE.PLAN_2.value):
            cols.append('Tienda_' + str(i + 1))
    cols += ['Promedio', 'Fecha']    
    return {'cols': cols}
    

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


#Metodo para obtner los datos de la tabla comparativa
def get_query_dashboard_data(uuid, page, filters, type_data):
    user=get_user(uuid)
    id_company=user[0]
    role=user[1]
    
    my_marketplace=get_my_marketplace(id_company=id_company)
    
    if my_marketplace is None:
        return ''
    other_marketplaces=get_compare_marketplace(id_company=id_company)
    if other_marketplaces is None:
        return ''
    
    selects=get_select_values(role=role, my_marketplace=my_marketplace, other_marketplaces=other_marketplaces)
    SELECT_VALUES=selects['SELECT_VALUES']
    MARKETPLACE_VALUES=selects['MARKETPLACE_VALUES']
    MARKETPLACE_IN=selects['MARKETPLACE_IN']
    
    conditions = get_filter_conditions(filters=filters)
    type_data_condition = get_type_data_condition(type_data=type_data, my_marketplace=my_marketplace)
    conditions.extend(type_data_condition)
    WHERE = get_where_clause(conditions=conditions, operator='AND')
    
    query = f'''
            Select a.name, a.sku, {SELECT_VALUES} TO_CHAR(b."Fecha", 'DD/MM/YYYY') AS "Fecha"
            from 
            (Select id_product, name, sku from public.marketplace_product
            where id_marketplace={my_marketplace[0]}) as a
            inner join (
                SELECT
                mp.Id_product, {MARKETPLACE_VALUES}
                MAX(p.Date_Start) AS "Fecha"
                FROM
                Marketplace_Product mp
                INNER JOIN (
                    SELECT
                    pp.Id_Marketplace_Product,
                    pp.Price,
                    pp.Offer_Price,
                    pp.Date_Start
                    FROM
                    Price pp
                    INNER JOIN (
                        SELECT
                        Id_Marketplace_Product,
                        MAX(Date_Start) AS Max_Date_Start
                        FROM
                        Price
                        GROUP BY
                        Id_Marketplace_Product
                    ) sub ON pp.Id_Marketplace_Product = sub.Id_Marketplace_Product
                    AND pp.Date_Start = sub.Max_Date_Start
                ) p ON p.Id_Marketplace_Product = mp.Id
                WHERE
                mp.Id_marketplace IN ({MARKETPLACE_IN})
                GROUP BY
                mp.Id_product
            ) as b on a.id_product= b.id_product
            {WHERE}
            ORDER BY a.sku
            LIMIT 10
            OFFSET {page};
        '''
    return text(query)


#Metodo para obtener la infomracion de las cards
def get_query_cards_data(uuid):
    user=get_user(uuid)
    id_company=user[0]
    
    my_marketplace = get_my_marketplace(id_company=id_company)
    if not my_marketplace:
        return ''

    other_marketplaces = get_compare_marketplace(id_company=id_company)
    if not other_marketplaces:
        return ''

    select_value = f'b."{my_marketplace[1]}"'
    in_value = str(my_marketplace[0])
    ex_values = ', '.join(str(marketplace[0]) for marketplace in other_marketplaces)

    query = f'''
        SELECT 
            COUNT(CASE WHEN {select_value} < b."Promedio" THEN 1 END) AS abajo,
            COUNT(CASE WHEN {select_value} = b."Promedio" THEN 1 END) AS en,
            COUNT(CASE WHEN {select_value} > b."Promedio" THEN 1 END) AS arriba
        FROM (
            SELECT mp.Id_product,
                MAX(CASE WHEN mp.Id_marketplace = {in_value} THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Way",
                ROUND(AVG(CASE WHEN mp.Id_marketplace <> {in_value} THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END), 2) AS "Promedio"
            FROM Marketplace_Product mp
            INNER JOIN (
                SELECT pp.Id_Marketplace_Product, pp.Price, pp.Offer_Price
                FROM Price pp
                INNER JOIN (
                    SELECT Id_Marketplace_Product, MAX(Date_Start) AS Max_Date_Start
                    FROM Price
                    GROUP BY Id_Marketplace_Product
                ) sub ON pp.Id_Marketplace_Product = sub.Id_Marketplace_Product AND pp.Date_Start = sub.Max_Date_Start
            ) p ON p.Id_Marketplace_Product = mp.Id
            WHERE mp.Id_marketplace IN ({in_value}, {ex_values})
            GROUP BY mp.Id_product
        ) AS b
        INNER JOIN public.marketplace_product AS a ON a.id_product = b.id_product AND a.id_marketplace = {in_value};
    '''
    return text(query)
    

#Metodo para serealizar una tabla  y enviarla al front
def get_table(query):
    rows = []
    # cols = []
    try:
        res=query_execute(query)
        rows = res.fetchall()
        # cols = [str(col) for col in res.keys()]
    except:
        rows = []
    response = {}
    # response['cols']=cols
    response['data']=[]    
    for row in rows:
        temp=[]
        for atribut in row:
            temp.append(str(atribut))
        response['data'].append(temp)
    return response