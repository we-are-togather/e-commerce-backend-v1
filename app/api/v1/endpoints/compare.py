from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.schemas.cart import CartCreateSchema, CartItemCreateSchema, CartResponseSchema

router = APIRouter(prefix="/compare", tags=["Compare"])

@router.post("/", response_model=List[ProductVariantSchema])
def compare_products(variant_ids: List[int], db: Session = Depends(get_db)):    
    variants = db.query(ProductVariant).filter(ProductVariant.id.in_(variant_ids)).all()
    if not variants:
        raise HTTPException(status_code=404, detail="No product variants found for the provided IDs")
    
    return [
        ProductVariantSchema(
            id=var.id,
            product_id=var.product_id,
            name=var.name,
            price=var.price,
            description=var.description
        ) for var in variants
    ]

@router.get("/compare-list")
def get_compare_list(db: Session = Depends(get_db)):
    # This is a placeholder implementation. In a real application, you would likely want to store the compare list in the user's session or database.
    compare_list = db.query(ProductVariant).filter(ProductVariant.is_featured == True).all()
    return compare_list



@router.get("/compare-list")
def get_compare_list(db: Session = Depends(get_db)):
    # This is a placeholder implementation. In a real application, you would likely want to store the compare list in the user's session or database.
    compare_list = db.query(ProductVariant).filter(ProductVariant.is_featured == True).all()
    return compare_list

@router.get("/compare-amount")
def get_compare_amount(db: Session = Depends(get_db)):
    # This is a placeholder implementation. In a real application, you would likely want to calculate the total amount of items in the compare list.
    compare_amount = db.query(ProductVariant).filter(ProductVariant.is_featured == True).count()
    return {"compare_amount": compare_amount}
