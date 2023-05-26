from enum import Enum

class ROLE(Enum):
    ADMIN =     'Admin'
    PLAN_1 =    'Plan_1'
    PLAN_2 =    'Plan_2'
    PLAN_3 =    'Plan_3'
    PLAN_f=     'Plan_F'
    
class TYPE_FILTER(Enum):
    TEXTO = 1
    NUMERO= 2
    FECHA = 3