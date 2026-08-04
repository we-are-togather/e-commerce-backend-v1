from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.user import User

router = APIRouter()

@router.get("/order/order-list")
def all_order(show_per_page, page_num, filter, from_date, to_date, db: Session = Depends(get_db), user: User = Depends(get_current_user), role: User = Depends(require_role("admin"))):
    pass

@router.get("/order/order-info")
def get_order_info(db: Session = Depends(get_db), user: User = Depends(get_current_user), role: User = Depends(require_role("admin"))):
    pass

@router.put("/order/change-status")
def change_status(db: Session = Depends(get_db), user: User = Depends(get_current_user), role: User = Depends(require_role("admin"))):
    pass
