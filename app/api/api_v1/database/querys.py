from api.api_v1.database.connection import query_execute
from api.api_v1.database.helpers import get_my_marketplace, get_compare_marketplace, get_my_marketplace
from api.api_v1.database.helpers import get_compare_marketplace, get_filter_conditions, get_type_data_condition
from api.api_v1.database.helpers import get_where_clause, get_select_values, get_select_values_marketplace_out
from api.api_v1.database.helpers import subquery_card, subquery_card_2
from api.api_v1.database.helpers import get_select_values_chart
from api.api_v1.database.querys_app import get_user
from api.api_v1.enums.enums import ROLE
from sqlalchemy import text

#Metodo para obtener las categorias
def query_categories(uuid):
    user = get_user(uuid)
    id_company = user[0]
    
    my_marketplace = get_my_marketplace(id_company=id_company)
    if my_marketplace is None:
        return ''
    
    query=f'''
        SELECT c.id, concat(c.name, ' (',COUNT(a.id), ')') as category
            FROM public.category AS c
            LEFT JOIN (
                SELECT p.id, p.id_category
                FROM marketplace_product mp
                INNER JOIN product p on p.id = mp.id_product AND mp.id_marketplace = {my_marketplace[0]}
            ) a on c.id=a.id_category
            GROUP BY c.id, c.name
            ORDER BY c.name;
    '''
    return query

# Metodo para obtener los productos totales
def query_home_cards_values(uuid, categories):
    user=get_user(uuid)
    id_company=user[0]
    my_marketplace=get_my_marketplace(id_company=id_company)
    if my_marketplace is None:
        return ''
    
    query=f'''
        SELECT count(distinct id) as productos_totales
        FROM public.product
    '''
    result1 = query_execute(query).fetchone()
    
    query=f'''
        select count(distinct mp.id) as productos_propios
        from public.marketplace_product mp
        inner join product p on p.id=mp.id_product
        where mp.id_marketplace={my_marketplace[0]};
    '''
    result2 = query_execute(query).fetchone()
    
    query=f'''
        SELECT COUNT(DISTINCT mp.id) AS productos_match
        FROM public.marketplace_product mp
        INNER JOIN public.product p ON p.id = mp.id_product
        WHERE mp.id_marketplace = 5
        AND EXISTS (
            SELECT 1
            FROM public.marketplace_product mp2
            WHERE mp2.id_product = mp.id_product
            AND mp2.id_marketplace <> {my_marketplace[0]}
        );
    '''
    result3 = query_execute(query).fetchone()
    return {"data": [[(result1[0])],[(result2[0])],[(result3[0])]]}


#Metodo para obtener la infomracion de las cards
def query_cards_data(uuid, categories):
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
    
    categories = f"WHERE p.id_category IN ({','.join(str(category) for category in categories)})" if categories else ""

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
        INNER JOIN public.marketplace_product AS a ON a.id_product = b.id_product AND a.id_marketplace = {in_value}
        INNER JOIN public.product as p on p.id=a.id_product
        {categories};
    '''
    return text(query)


#Metodo para obtener los Encabezados de la  tabala
def query_table_comparative_heders(uuid):
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
    

#Metodo para obtner los datos de la tabla comparativa
def query_table_comparative_data(uuid, page, filters, type_data, categories):
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
    categories = f"AND pr.id_category IN ({','.join(str(category) for category in categories)})" if categories else ""
    
    query = f'''
            Select a.name, a.sku, {SELECT_VALUES} TO_CHAR(b."Fecha", 'DD/MM/YYYY') AS "Fecha"
            from 
            (Select mrp.id_product, mrp.name, mrp.sku from public.marketplace_product mrp
            inner join product pr on pr.id=mrp.id_product
            where id_marketplace={my_marketplace[0]} {categories}) as a
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


#Metodo para obtener todos los productos de un marketplace
def query_filter_product(uuid, categories):
    user=get_user(uuid)
    id_company=user[0]
    categories = f"AND p.id_category IN ({','.join(str(category) for category in categories)})" if categories else ""
    my_marketplace = get_my_marketplace(id_company=id_company)
    if not my_marketplace:
        return ''
    query = f'''
        SELECT p.id,concat('(', mp.sku, ') ', mp.name) as name, mp.description
        FROM public.marketplace_product mp
        inner join public.product p on p.id=mp.id_product
        where id_marketplace={my_marketplace[0]} {categories}
        order by mp.sku;
    '''
    return text(query)


#Metodo para obtener los valores minimo, maximo y promedio de un producto y su competencia
def query_cards_product(uuid, id_product):
    user = get_user(uuid)
    id_company = user[0]
    role = user[1]
    
    my_marketplace = get_my_marketplace(id_company=id_company)
    if my_marketplace is None:
        return ''
    other_marketplaces = get_compare_marketplace(id_company=id_company)
    if other_marketplaces is None:
        return ''
    values_in = get_select_values_marketplace_out(other_marketplaces=other_marketplaces)
    name = 'm.name' if role in [ROLE.ADMIN.value, ROLE.PLAN_3.value] else 'm.name_2'
    query_parts = []
    query_parts.append(subquery_card(order='asc', values_in=my_marketplace[0], product=id_product, name=name))
    query_parts.append(subquery_card(order='desc', values_in=my_marketplace[0], product=id_product, name=name))
    query_parts.append(subquery_card_2(values_in=my_marketplace[0], product=id_product, name=name))
    query_parts.append(subquery_card(order='asc', values_in=values_in, product=id_product, name=name))
    query_parts.append(subquery_card(order='desc', values_in=values_in, product=id_product, name=name))
    query_parts.append(subquery_card_2(values_in=values_in, product=id_product, name=name))
    query = ' UNION ALL '.join(query_parts)
    return query


#Metodo para obtener la linea de precios de un producto
def query_timel_line_product (uuid, id_product):
    user=get_user(uuid)
    id_company=user[0]
    role=user[1]
    
    my_marketplace=get_my_marketplace(id_company=id_company)
    if my_marketplace is None:
        return ''
    other_marketplaces=get_compare_marketplace(id_company=id_company)
    if other_marketplaces is None:
        return ''
    
    selects=get_select_values_chart(role=role, my_marketplace=my_marketplace, other_marketplaces=other_marketplaces)
    SELECT_VALUE=selects['SELECT_VALUE']
    MARKETPLACES_IN=selects['MARKETPLACES_IN']
    MARKETPLACES_OUT=selects['MARKETPLACES_OUT']
    query=f'''
       SELECT 
       {SELECT_VALUE}
        TO_CHAR(d.date_start, 'DD/MM/YYYY') AS formatted_date,
        LEAST(COALESCE(p.Price, p3.Price), COALESCE(p.Offer_Price, p3.Offer_Price)) AS Lowest_Price
        FROM
        marketplace_product mp
        CROSS JOIN (
            SELECT DISTINCT date_start
            FROM price
            WHERE Id_Marketplace_Product IN (
            SELECT mp2.Id
            FROM marketplace_product mp2
            WHERE mp2.Id_Product = {id_product}
                AND mp2.Id_Marketplace = {my_marketplace[0]}
            )
        ) d
        LEFT JOIN price p ON p.Id_Marketplace_Product = mp.Id
            AND p.date_start = d.date_start
        LEFT JOIN (
            SELECT
            mp3.Id_Product,
            mp3.Id_Marketplace,
            MAX(p3.date_start) AS max_date_start
            FROM
            marketplace_product mp3
            INNER JOIN price p3 ON p3.Id_Marketplace_Product = mp3.Id
            WHERE
            mp3.Id_Product = {id_product}
            AND mp3.Id_Marketplace IN ({MARKETPLACES_IN})
            GROUP BY
            mp3.Id_Product,
            mp3.Id_Marketplace
        ) m ON m.Id_Product = mp.Id_Product
            AND m.Id_Marketplace = mp.Id_Marketplace
            AND p.date_start IS NULL
        LEFT JOIN price p3 ON p3.Id_Marketplace_Product = mp.Id
            AND p3.date_start = m.max_date_start
        LEFT JOIN Marketplace mm ON mm.Id = mp.Id_Marketplace
        WHERE
        mp.Id_Product = {id_product}
        AND mp.Id_Marketplace IN ({MARKETPLACES_IN})

        UNION ALL

        SELECT
        a.name,
        a.formatted_date,
        ROUND(AVG(a.Lowest_Price), 2) AS Lowest_Price
        FROM
        (
            SELECT
            0 AS id,
            'Promedio' AS name,
            TO_CHAR(d.date_start, 'DD/MM/YYYY') AS formatted_date,
            LEAST(COALESCE(p.Price, p3.Price), COALESCE(p.Offer_Price, p3.Offer_Price)) AS Lowest_Price
            FROM
            marketplace_product mp
            CROSS JOIN (
                SELECT DISTINCT date_start
                FROM price
                WHERE Id_Marketplace_Product IN (
                SELECT mp2.Id
                FROM marketplace_product mp2
                WHERE mp2.Id_Product = {id_product}
                    AND mp2.Id_Marketplace = {my_marketplace[0]}
                )
            ) d
            LEFT JOIN price p ON p.Id_Marketplace_Product = mp.Id
                AND p.date_start = d.date_start
            LEFT JOIN (
                SELECT
                mp3.Id_Product,
                mp3.Id_Marketplace,
                MAX(p3.date_start) AS max_date_start
                FROM
                marketplace_product mp3
                INNER JOIN price p3 ON p3.Id_Marketplace_Product = mp3.Id
                WHERE
                mp3.Id_Product = {id_product}
                AND mp3.Id_Marketplace IN (1, 2)
                GROUP BY
                mp3.Id_Product,
                mp3.Id_Marketplace
            ) m ON m.Id_Product = mp.Id_Product
                AND m.Id_Marketplace = mp.Id_Marketplace
                AND p.date_start IS NULL
            LEFT JOIN price p3 ON p3.Id_Marketplace_Product = mp.Id
                AND p3.date_start = m.max_date_start
            LEFT JOIN Marketplace mm ON mm.Id = mp.Id_Marketplace
            WHERE
            mp.Id_Product = {id_product}
            AND mp.Id_Marketplace IN ({MARKETPLACES_OUT})
        ) AS a
        GROUP BY
        a.name,
        a.formatted_date

        ORDER BY
        name,
        formatted_date
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