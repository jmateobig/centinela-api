from pydantic import BaseModel
from typing import   List,Optional

class filter(BaseModel):
    field:str
    conector:str
    type_filter:int
    value:Optional[str]
    extra_value:str


class comparative_table_heders(BaseModel):
    uuid:str


class comparative_table_data(BaseModel):
    uuid:str
    type_data:int
    like:Optional[str]
    page:Optional[int]
    category:Optional[str]
    brand:Optional[str]
    filters:List[filter]
    categories:List[int]
    
    
class body_products(BaseModel):
    uuid:str
    categories:List[int]