
from sqlalchemy import Enum as SAEnum
from enum import Enum

def sa_enum(enum_cls: type, name: str):
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        validate_strings=True,
        values_callable=lambda x: [e.value for e in x],
    )

class Status(Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"