from fastapi import status, HTTPException
from datetime import datetime, timezone

from app.repositories import admin as admin_repositories
from app.schemas.base import BaseResponse, Meta
from app.core.context import get_request_id

def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))

async def add_tag(db, product_id, tags):
    if isinstance(tags, list):
        for tag in tags:
            tag_row = await admin_repositories.get_tag(db, tag)
            if not tag_row:
                tag_row = await admin_repositories.add_tag(db, {"name": tag})
                await admin_repositories.add_product_tag(db, {"product_id": product_id, "tag_id": tag_row.id})
    else:
        tag_row = await admin_repositories.add_tag(db, {"name": tags})
        await admin_repositories.add_product_tag(db, {"product_id": product_id, "tag_id":tag_row.id})
        return BaseResponse(
                status=status.HTTP_201_CREATED, success=True,
                message=f"Tag of : {product_id} created successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )
    
async def add_product_tag(db, product_id, tag_id):
    tag = admin_repositories.get_tag(db, tag_id)
    if tag is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag not found with id:{tag_id}")
    await admin_repositories.add_product_tag(db, {"product_id": product_id, "tag_id":tag_id})
    return BaseResponse(
            status=status.HTTP_201_CREATED, success=True,
            message=f"Tag of : {product_id} created successfully", lang="en",
            data=[],
            meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
        )


async def get_product_tags(db, product_id):
    tags, _ = await admin_repositories.get_product_tags(db, product_id)
    return [tag.name for tag in tags]


async def update_tags(db, product_id, tags):
    output = []
    for tag in tags:
        if tag.name is not None and tag.id is not None:
            existing = await admin_repositories.get_tag(db, tag.name)
            new_tag = existing or await admin_repositories.add_tag(db, {"name": tag.name})
            output.append({"id": tag.id, "product_id": product_id, "tag_id": new_tag.id})
    await admin_repositories.updated_product_tag(db, output)

async def delete_product_tag(db, tag_id):
    is_deleted = await admin_repositories.delete_product_tag(db, tag_id)
    if is_deleted:
        return BaseResponse(
            status=status.HTTP_200_OK, success=True,
            message=f"Product Tag: {tag_id} deleted successfully", lang="en",
            data=[],
            meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
        )
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product Tag {tag_id} not found to delete")

async def get_tags(db, tag_name):
    tags, _ = await admin_repositories.get_tags(db, tag_name)
    
    return _response(status.HTTP_200_OK, f"Tags from searching Keyword", [{"id": tag.id, "name": tag.name} for tag in tags])

