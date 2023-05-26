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