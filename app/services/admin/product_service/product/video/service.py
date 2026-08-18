from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.context import get_request_id
from app.repositories import admin as admin_repositories
from app.schemas.base import BaseResponse, Meta

from app.schemas.product import Video

async def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))

async def add_video(db, product_id, video):
    if not await admin_repositories.get_product(db, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Video of product id: {product_id} is not found")
    data = {
        "product_id": product_id,
        "video_url": video.url,
        "platform": video.platform,
        "title": video.title
    }
    await admin_repositories.add_videos(db, data)
    return await _response(status.HTTP_201_CREATED, f"Video added successfully of product: {product_id}", [])

async def get_videos(db, product_id):
    if not await admin_repositories.get_product(db, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Video of product id: {product_id} is not found")
    videos, _ = await admin_repositories.get_videos(db, product_id)
    videos = [
        Video(
            id=video.id,
            url=video.video_url,
            title=video.title,
            platform=video.platform
        )
        for video in videos
    ]
    return await _response(status.HTTP_200_OK, f"Videos of product: {product_id}", videos)

async def delete_video(db, video_id):
    if not await admin_repositories.get_video(db, video_id):

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Video of product id: {video_id} is not found")
    await admin_repositories.delete_video(db, video_id)
    return await _response(status.HTTP_200_OK, f"Video deleted successfully : {video_id}", [])

async def update_video(db, video_id, video):
    if not await admin_repositories.get_video(db, video_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Video of product id: {video_id} is not found")
    data = {}
    for source, target in (("url", "video_url"), ("title", "title"), ("platform", "platform")):
        value = getattr(video, source)
        if value is not None:
            data[target] = value

    await admin_repositories.update_video(db, data, video_id)
    return await _response(status.HTTP_200_OK, f"Video updated successfully : {video_id}", [])