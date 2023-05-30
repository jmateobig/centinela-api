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
    
    
class TYPE_DATA(Enum):
    ALL  = 1
    DOWN = 2
    IN   = 3
    UP   = 4