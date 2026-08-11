from pathlib import Path
from typing import Annotated, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.admin import ListByFilter
from app.schemas.base import BaseResponse, Meta
from app.schemas.product import ProductCreateResponseSchema, ProductCreateSchema, ProductFilter, DescriptionSchema, SpecificationGroup
from app.schemas.user import User
from app.services.admin import product_service
from app.utils.logger import logging
from app.core.context import get_request_id

router = APIRouter()
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/product", response_model=ProductCreateResponseSchema)
async def create_product(payload: Annotated[str, Form(...)], files: Annotated[List[UploadFile], File(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    logging.info("Product creating session started successfully")
    return await product_service.add_product(db, ProductCreateSchema.model_validate_json(payload), files)

@router.get("/product")
async def list_product(filters:Annotated[ProductFilter, Depends()], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await product_service.get_list_product(db, filters)

@router.get("/product/{id}")
async def get_product(id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await product_service.get_product(db, id)

@router.delete("/product/{id}")
async def remove_product(id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    if await product_service.product_delete(db, id):
        return BaseResponse(status=status.HTTP_200_OK,success=True, message="product deleted successfully", lang="eng", data=[], meta=Meta(request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)))
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product is not available with the id {id}")

@router.patch("/product/{id}")
async def update_product(id:int,payload:ProductCreateSchema, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.update_product(db, id, payload)
    return response


# =======================================================
#               Image
# =======================================================

@router.patch("/product/{id}/image")
async def update_product_image():
    pass

@router.delete("/product/{id}/image")
async def delete_image():
    pass


@router.post("/product/{id}/image")
async def add_image():
    pass

@router.post("/product/{id}/image/group")
async def add_image_group():
    pass


# =======================================================
#                   Description
# =======================================================
@router.post("/product/{product_id}/description")
async def add_description(
    product_id:int, payload:DescriptionSchema, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]
):
    response = product_service.add_description(db, product_id , payload)
    return response

@router.get("product/{desc_id}/description")
async def get_descriptions(desc_id:int,  db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_description(db, desc_id)
    return response

@router.get("product/{product_id}/description")
async def get_full_desc(product_id:int,  db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_description_list(db, product_id)
    return response

@router.delete('product/{desc_id}/description')
async def delete_description(desc_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.delete_description(db, desc_id)
    return response

@router.patch("product/{desc_id}/description")
async def update_description(desc_id:int,payload:DescriptionSchema,  db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.update_description(db, payload, desc_id)
    return response

# =======================================================
#                   Specification
# =======================================================
@router.post("/product/{product_id}/specification")
async def add_specification(product_id:int, payload:SpecificationGroup, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.add_specification(db, product_id, payload)
    return response

@router.get("product/{spec_id}/specification")
async def get_specification(spec_id:int,db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_specification(db, spec_id)
    return response

@router.get("product/{product_id}/specification")
async def get_full_specification(product_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_specification_list(db, product_id)
    return response

@router.delete('product/{spec_id}/specification')
async def delete_specification(spec_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.delete_specification(db,spec_id)
    return response

@router.patch("product/{spec_id}/specification")
async def update_specification(spec_id:int,payload:SpecificationGroup, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.update_specification(db, payload, spec_id)
    return response


# =======================================================
#                   Variants
# =======================================================
@router.get("product/{product_id}/variants")
async def get_variants(product_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_variants(db, product_id)
    return response

@router.get("product/{variant_id}/variant")
async def get_variant(variant_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.get_variant(db, variant_id)
    return response

@router.delete("product/{variant_id}/variant")
async def delete_variant(variant_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.delete_variant(db, variant_id)
    return response

@router.patch("product/{variant_id}/variant")
async def update_variant(variant_id:int, payload:SpecificationGroup, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.update_variant(db, payload, variant_id)
    return response

@router.post("product/{product_id}/variant")
async def add_variant(product_id:int, payload:SpecificationGroup, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    response = await product_service.add_variant(db, product_id, payload)
    return response

# =======================================================
#                   Tags
# =======================================================



# =======================================================
#                   Badges
# =======================================================



# =======================================================
#                   SEO
# =======================================================


# =======================================================
#                   Related Product
# =======================================================


# =======================================================
#                   Video
# =======================================================


