from app.schemas.order import PlaceOrder
from app.repositories import order_repositories


import operator
from app.services.orders.helper import (
    check_first_order
)



def get_delivary_charge(db, zone_id):
    charge = order_repositories.get_delivary_charge(db, zone_id)
    return charge.delivery_charge

def get_discount_price():
    pass

def get_shipping_price():
    pass



