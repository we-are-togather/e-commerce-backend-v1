from pydantic import (
    BaseModel,
    Field,
)
from app.schemas.base import BaseResponse
from datetime import date
class User(BaseModel):
    name:str
    email:str
    password:str
    mobile: str
    dob:date
    gender:str
    role:str = Field(default='patient', description='Role of the user. Roles are [admin, patient, doctor]')

class ShowUser(BaseModel):
    name: str
    email: str
    mobile:str
    dob:date
    gender:str
    role:str = Field(default='patient', description='Role of the user. Roles are [admin, patient, doctor]')

class ResponseUser(BaseResponse):
    data:ShowUser