from fastapi import status, HTTPException
from datetime import datetime, timezone

from app.schemas.base import BaseResponse, Meta
from app.core.context import get_request_id
from app.repositories import admin as admin_repositories


def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))


async def add_badges(db, product_id, badges):
    if isinstance(badges, list):
        for badge in badges:
            badge_row = await admin_repositories.get_badge(db, badge)
            if not badge_row:
                badge_row = await admin_repositories.add_badge(db, {"name": badge})
                await admin_repositories.add_product_badge(
                    db, {"product_id": product_id, "badge_id": badge_row.id}
                )
    else:
        badge_row = await admin_repositories.add_badge(db, {"name": badges})
        await admin_repositories.add_product_badge(
                            db, {"product_id": product_id, "badge_id": badge_row.id}
                        )
        return BaseResponse(
                status=status.HTTP_201_CREATED, success=True,
                message=f"Badge : {product_id} created successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )

async def add_product_badge(db, product_id, badge_id):
    badge = admin_repositories.get_badge_by_id(db, badge_id)
    if badge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Badge not found: {badge_id}")
    await admin_repositories.add_product_badge(
            db, {"product_id": product_id, "badge_id": badge_id}
        )
    return BaseResponse(
        status=status.HTTP_201_CREATED, success=True,
        message=f"Product Badge Added Successfully : {product_id} created successfully", lang="en",
        data=[],
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )

async def delete_product_badge(db, badge_id):
    is_deleted = await admin_repositories.delete_product_badge(db, badge_id)
    if is_deleted:
        return BaseResponse(
                status=status.HTTP_200_OK, success=True,
                message=f"Badge: {badge_id} deleted successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Badge not found with Badge: {badge_id}")
        

async def get_product_badges(db, product_id):
    badges, _ = await admin_repositories.get_product_badges(db, product_id)
    return [badge.name for badge in badges]


async def update_badges(db, product_id, badges):
    output = []
    for badge in badges:
        if badge.name is not None and badge.id is not None:
            existing = await admin_repositories.get_badge(db, badge.name)
            new_badge = existing or await admin_repositories.add_badge(db, {"name": badge.name})
            output.append({"id": badge.id, "product_id": product_id, "badge_id": new_badge.id})
    await admin_repositories.update_badges(db, output)

async def get_badge(db, badge_name):
    badges, _ = await admin_repositories.get_badges(db, badge_name)
    
    # if badges is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Badge not found with Badge: {badge_name}")
    return _response(status.HTTP_200_OK, f"Badge of Badge: {badge_name}", [{"id": badge.id, "name": badge.name} for badge in badges])