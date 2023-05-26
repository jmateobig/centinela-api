from api.api_v1.database.connection import query_execute
from sqlalchemy import text
from api.api_v1.enums.enums import ROLE
from api.api_v1.enums.enums import TYPE_FILTER


def get_my_marketplace(id_company):
    query = text('''
                    SELECT a.id_marketplace, b.name as marketplace
                FROM public.asignament a
                INNER JOIN marketplace b ON a.id_marketplace=b.id
                WHERE id_company=:id_company_param
    ''').bindparams(id_company_param=id_company)
    result = query_execute(query)
    row = result.fetchone()
    return row if row is not None else None


def get_compare_marketplace(id_company):
    query = text('''
                SELECT a.id_marketplace, b.name as marketplace
                FROM public.company_marketplace a
                INNER JOIN marketplace b ON a.id_marketplace=b.id
                WHERE id_company=:id_company_param
    ''').bindparams(id_company_param=id_company)
    result = query_execute(query)
    result = result.fetchall()
    return result


def get_filteres(filters):
    where=""
    for filter in filters:
        if filter.value != "":
            if filter.type_filter==TYPE_FILTER.TEXTO.value:
                where=where+filter.field+" "+filter.conector+" '"+filter.extra_value+""+filter.value+""+filter.extra_value+"' AND"
            if filter.type_filter==TYPE_FILTER.NUMERO.value:
                where=where+filter.field+" "+filter.conector+" "+filter.value+" AND"
    if (where!=''):
        where=where[:-4]
        where='WHERE '+where
    return where


def get_table_dashboard_heders_value(role, id_company):
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
    
    
def get_select_values(role,  my_marketplace, other_marketplaces):
    SELECT_VALUES='b."'+my_marketplace[1]+'", '
    MARKETPLACE_VALUES=''
    MARKETPLACE_IN=str(my_marketplace[0])
    n=1
    for marketplace in other_marketplaces:
        if (role==ROLE.ADMIN.value or role==ROLE.PLAN_3.value):
            SELECT_VALUES=SELECT_VALUES+'b."'+marketplace[1]+'", '
            MARKETPLACE_VALUES=MARKETPLACE_VALUES+' MAX(CASE WHEN mp.Id_marketplace = '+str(marketplace[0])+' THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "'+marketplace[1]+'", '
        elif (role==ROLE.PLAN_2.value):
            SELECT_VALUES=SELECT_VALUES+'b."Tienda_'+str(n)+'", '
            MARKETPLACE_VALUES=MARKETPLACE_VALUES+' MAX(CASE WHEN mp.Id_marketplace = '+str(marketplace[0])+' THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Tienda_'+str(n)+'", '
        MARKETPLACE_IN=MARKETPLACE_IN+", "+str(marketplace[0])
        n=n+1
        
    SELECT_VALUES=SELECT_VALUES+'b."Promedio", '
    MARKETPLACE_VALUES='''
                            MAX(CASE WHEN mp.Id_marketplace = '''+str(my_marketplace[0])+''' THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "'''+my_marketplace[1]+'''", 
                            ROUND(AVG(CASE WHEN mp.Id_marketplace NOT IN ('''+str(my_marketplace[0])+''') THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END), 2) AS "Promedio",
                        '''+ MARKETPLACE_VALUES
    return {'SELECT_VALUES':SELECT_VALUES, 'MARKETPLACE_VALUES':MARKETPLACE_VALUES, 'MARKETPLACE_IN':MARKETPLACE_IN}


def get_query_dashboard_data(role, id_company, page, filters):
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
    WHERE=get_filteres(filters)
    
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


def get_query_cards_data(id_company):
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