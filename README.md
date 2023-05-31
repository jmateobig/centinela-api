# centinela-api
# API 
.\venv\Scripts\activate
uvicorn app:app --reload --port 8080
python .\src\manage.py makemigrations
python .\src\manage.py migrate


{
   "dataset":"mantenimiento_mantenimiento_dic",
   "type": 2,
   "columns": [
     {
       "field":"central"
    },
    {
       "field":"unidad_equipo"
    },
    {
       "field":"tiempo_mantenimiento_dias"
    },
    {
       "field":"fecha_inicio"
    },
    {
       "field":"fecha_fin"
    },
    {
       "field":"potencia_fuera_servicio_mw"
    },
    {
       "field":"energia_fuera_servicio_gwh"
    },
    {
       "field":"motivo_mantenimiento"
    }
   ],
   "filters": [
     {
       "type_filter":3,
       "field":"fecha_inicio",
       "equal":">=",
       "value":"'20221200'"
    },
    {
       "type_filter":3,
       "field":"fecha_inicio",
       "equal":"<=",
       "value":"'20230523'"
    },
    {
       "type_filter":11,
       "field":"central",
       "equal":"=",
       "value":"CHIXOY"
    },
    {
       "type_filter":100,
       "equal":"=",
       "field":"nones",
       "value":"'True'"
    }
   ],
   "length": 10,
   "start": 10,
   "column_order": 1  
 }


 Query
 SELECT a.name, a.sku, b."Way", b."Gallo", b."Max", b."Promedio", TO_CHAR(b."Fecha", 'DD/MM/YYYY') AS "Fecha"
FROM
    (SELECT id_product, name, sku FROM public.marketplace_product WHERE id_marketplace = 5) AS a
INNER JOIN (
    SELECT
        mp.Id_product,
        MAX(CASE WHEN mp.Id_marketplace = 5 THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Way",
        MAX(CASE WHEN mp.Id_marketplace = 1 THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Gallo",
        MAX(CASE WHEN mp.Id_marketplace = 2 THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END) AS "Max",
        ROUND(AVG(CASE WHEN mp.Id_marketplace NOT IN (5) THEN COALESCE(LEAST(p.Price, p.Offer_Price), 0) END), 2) AS "Promedio",
        p.Date_Start AS "Fecha"
    FROM
        Marketplace_Product mp
    INNER JOIN Price p ON p.Id_Marketplace_Product = mp.Id
    WHERE
        mp.Id_marketplace IN (5, 1, 2)
    GROUP BY
        mp.Id_product, p.Date_Start
) AS b ON a.id_product = b.id_product
ORDER BY
    a.name, b."Fecha";