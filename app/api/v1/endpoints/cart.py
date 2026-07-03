from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.schemas.cart import CartCreateSchema, CartItemCreateSchema, CartResponseSchema


router = APIRouter(prefix="/cart", tags=["Cart"])
@router.post("/", response_model=CartResponseSchema)
def add_to_cart(cart_data: CartCreateSchema, db: Session = Depends(get_db)):
    # Create a new cart
    if cart_data.user_id:
        cart = Cart(owner_type='user', owner_id=cart_data.user_id)
    else:
        cart = Cart(owner_type='guest', owner_id= 0)  # You can use session ID or any unique identifier for guests
    
    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Add items to the cart
    for item in cart_data.items:
        # Check if the product variant exists
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Product variant with ID {item.product_variant_id} not found")

        cart_item = CartItem(
            cart_id=cart.id,
            product_variant_id=item.product_variant_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    return CartResponseSchema(
        id=cart.id,
        user_id=cart.owner_id,
        items=[
            CartItemCreateSchema(
                product_variant_id=item.product_variant_id,
                quantity=item.quantity
            ) for item in cart.items
        ]
    )




@router.get("/carts")
def get_carts(db: Session = Depends(get_db)):
    carts = db.query(Cart).all()
    return carts

@router.delete("/carts/{cart_id}")
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db.delete(cart)
    db.commit()
    return {"detail": "Cart deleted successfully"}


@router.get("/amount")
def get_cart_amount(db: Session = Depends(get_db)):
    # This is a placeholder implementation. In a real application, you would likely want to calculate the total amount of items in the cart.
    total_amount = db.query(CartItem).count()
    return {"total_amount": total_amount}

