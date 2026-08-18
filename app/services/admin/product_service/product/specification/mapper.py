from app.schemas.product import SpecificationGroup, SpecificationSchema
from fastapi import HTTPException 

def map_specification(specification) -> SpecificationGroup:
    return SpecificationGroup(
        id = specification.id,
        group_name=specification.type,
        specification_value=[
            SpecificationSchema(label=value.key, value=value.value)
            for value in specification.specification_values
        ],
    )


def map_specifications(specifications) -> list[SpecificationGroup]:
    return [map_specification(specification) for specification in specifications]

def map_exception(status_code, message):
    raise HTTPException(status_code=status_code, detail=message)

