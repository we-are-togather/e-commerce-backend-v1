from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.context import get_request_id
from app.repositories import admin as admin_repositories
from app.schemas.base import BaseResponse, Meta
from app.services.admin.product_service.product.specification.mapper import map_specification, map_specifications, map_exception


def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))



async def add_specification(db, product_id, specifications):
    # items = specifications if isinstance(specifications, list) else [specifications]
    if isinstance(specifications, list):
        for item in specifications:
            specification = await admin_repositories.add_specification_type(
                db, {"product_id": product_id, "type": item.group_name}
            )
            for value in item.specification_value:
                await admin_repositories.add_specification_value(db, {
                    "specification_type_id": specification.id, "key": value.label, "value": value.value
                })
    else:
        specification = await admin_repositories.add_specification_type(
            db, {"product_id": product_id, "type": specifications.group_name}
        )
        for value in specifications.specification_value:
            await admin_repositories.add_specification_value(db, {
                "specification_type_id": specification.id, "key": value.label if value.label is not None else map_exception(status.HTTP_409_CONFLICT, "input should'nt be null") , "value": value.value
            })

        return _response(status.HTTP_201_CREATED,
                         f"Specification Created successfully of product: {product_id}", [])


async def get_specification(db, spec_id):
    specification = await admin_repositories.get_specification(db, spec_id)
    if specification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Specification Not found wiht the id {spec_id}")
    return _response(status.HTTP_200_OK, f"Specification of spec if: {spec_id}",
                     map_specification(specification))


async def get_specification_list(db, product_id):
    specifications, _ = await admin_repositories.get_specifications(db, product_id)
    return _response(status.HTTP_200_OK, f"Specification of product: {product_id}",
                     map_specifications(specifications))


async def delete_specification(db, spec_id):
    if await admin_repositories.delete_specification(db, spec_id):
        return _response(status.HTTP_200_OK, f"Specification id:{spec_id} deleted successfully", [])
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Specification with id{spec_id} not found")


async def update_spec_value(db, spec_values):
    output = []
    for specification in spec_values:
        if specification.id is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Specification value id should not be null")
        data = {"id": specification.id}
        if specification.label is not None:
            data["key"] = specification.label
        if specification.value is not None:
            data["value"] = specification.value
        output.append(data)
    await admin_repositories.update_specification_value(db, output)


async def update_specification(db, specifications, spec_id=None):
    if isinstance(specifications, list):
        output = []
        for specification in specifications:
            data = {"id": specification.id}
            if specification.group_name is not None:
                data["type"] = specification.group_name
            output.append(data)
            if specification.specification_value:
                await update_spec_value(db, specification.specification_value)
        await admin_repositories.update_specification(db, output)
        return None
    data = {"id": spec_id}
    if specifications.group_name is not None:
        data["type"] = specifications.group_name
    if specifications.specification_value:

        await update_spec_value(db, specifications.specification_value)
    await admin_repositories.update_specification(db, data, spec_id)
    return _response(status.HTTP_200_OK, "Specification Updated successfully.", [])
