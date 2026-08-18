from fastapi import status, HTTPException
from datetime import datetime, timezone

from app.schemas.base import BaseResponse, Meta
from app.core.context import get_request_id

from app.repositories import admin as admin_repositories


async def add_seo(db, product_id, seo):
    if isinstance(seo, list):
        for seo_data in seo:
            await admin_repositories.add_seo(db, {
                "product_id": product_id,
                "meta_title": seo_data.meta_title,
                "meta_description": seo_data.meta_description,
                "canonical_url": seo_data.canonical_url,
                "og_image": seo_data.open_graph_image,
                "no_index": not seo_data.index,
            })
    
    else:
        await admin_repositories.add_seo(db, {
            "product_id": product_id,
            "meta_title": seo.meta_title,
            "meta_description": seo.meta_description,
            "canonical_url": seo.canonical_url,
            "og_image": seo.open_graph_image,
            "no_index": not seo.index,
        })
        return BaseResponse(
                status=status.HTTP_201_CREATED, success=True,
                message=f"SEO Created successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )


async def add_seo_keyword(db, product, seos):
    for item in seos:  
        for keyword in item.meta_keywords:
            await admin_repositories.add_seo_keyword(db, {"product_id": product.id, "keyword": keyword})

async def delete_seo(db, seo_id):
    is_deleted = await admin_repositories.delete_seo(db, seo_id)
    if is_deleted:
        return BaseResponse(
                status=status.HTTP_200_OK, success=True,
                message=f"Seo: {seo_id} deleted successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )
    else: HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Seo not foud with this id: {seo_id}")



async def update_seo(db, seos, seo_id=None):
    if isinstance(seos, list):
        output = []
        for seo in seos:
            data = {"id": seo.id}
            fields = (("meta_title", "meta_title"), ("meta_description", "meta_description"),
                    ("canonical_url", "canonical_url"), ("open_graph_image", "og_image"))
            for source, target in fields:
                value = getattr(seo, source)
                if value is not None:
                    data[target] = value
            if seo.index is not None:
                data["no_index"] = not seo.index
            output.append(data)
        await admin_repositories.update_seos(db, output)
    else:
        data = {}
        fields = (("meta_title", "meta_title"), ("meta_description", "meta_description"),
                ("canonical_url", "canonical_url"), ("open_graph_image", "og_image"))
        for source, target in fields:
            value = getattr(seos, source)
            if value is not None:
                data[target] = value
        if seos.index is not None:
            data["no_index"] = not seos.index
        await admin_repositories.update_seo(db, data, seo_id)
        return BaseResponse(
                status=status.HTTP_200_OK, success=True,
                message=f"SEO: {seo_id} updated successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )
