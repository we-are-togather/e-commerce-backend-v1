from pydantic import(BaseModel, 
                     Field
                    )
from typing import  Optional, List, Dict


class BaseResponse(BaseModel):
    status: str = Field(description='status code of the request')
    message: str = Field(description='message of the status')
    lang: str = Field(description='language which you are return')
    data:List[Optional[Dict]]