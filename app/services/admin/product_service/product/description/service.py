from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.context import get_request_id
from app.repositories import admin as admin_repositories
from app.schemas.base import BaseResponse, Meta
from app.services.admin.product_service.product.description.mapper import map_description, map_descriptions


def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))


async def add_description(db, product_id, descriptions):
    items = descriptions if isinstance(descriptions, list) else [descriptions]
    for description in items:
        await admin_repositories.add_description(db, {
            "product_id": product_id, "title": description.title, "text": description.text
        })
    if not isinstance(descriptions, list):
        return _response(status.HTTP_201_CREATED, f"Description Created successfully of product: {product_id}", [])


async def get_description(db, desc_id):
    description = await admin_repositories.get_description(db, desc_id)
    if description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"description id: {desc_id} is not found")
    return _response(status.HTTP_201_CREATED, "Description Created successfully", map_description(description))


async def get_description_list(db, product_id):
    descriptions, _ = await admin_repositories.get_description_list(db, product_id)
    return _response(status.HTTP_200_OK, f"Descriptions of product: {product_id}", map_descriptions(descriptions))


async def delete_description(db, desc_id):
    if await admin_repositories.delete_description(db, desc_id):
        return _response(status.HTTP_200_OK, "Description Deleted successfully.", [])
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Can not deleted desc:{desc_id}. May be its not existed")


async def update_description(db, descriptions, desc_id=None):
    if isinstance(descriptions, list):
        output = []
        for description in descriptions:
            data = {"id": description.id}
            if description.title is not None:
                data["title"] = description.title
            if description.text is not None:
                data["text"] = description.text
            output.append(data)
        await admin_repositories.update_descriptions(db, output)
        return None

    data = {}
    if descriptions.title is not None:
        data["title"] = descriptions.title
    if descriptions.text is not None:
        data["text"] = descriptions.text
    await admin_repositories.update_descriptions(db, data, desc_id=desc_id)
    return _response(status.HTTP_200_OK,
                     f"Description Updated successfully of description id: {desc_id}", [])
