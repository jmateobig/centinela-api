from pydantic import BaseModel
from typing import Any, List,Optional,Dict


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
    like:Optional[str]
    page:Optional[int]
    category:Optional[str]
    brand:Optional[str]
    filters:List[filter]