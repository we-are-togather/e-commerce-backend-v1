from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.schemas.order import PlaceOrder, PlaceOrderResponse, PlaceOrderData
from app.schemas.base import Meta


from app.repositories import order_repositories
from app.repositories.payment_repositories import create_payment

from app.services.orders.helper import evaluate_items, check_first_order
from app.services.orders.data_class import OrderContext, ShippingDetail
from app.services.orders.pricing import get_discount, get_delivary_charge, get_currency_rate

from app.repositories.user_repositories import get_address

from app.enums.order_enums import OrderStatus, FulfillmentStatus
from app.enums.payment_enums import PaymentProvider, PaymentStatus

from app.services.gateways.sslCommerz import SSLCommerzGateway

async def place_order(db, payload, request_id):
    payload = PlaceOrder.model_validate_json(payload)
    exchange_rate = await get_currency_rate(payload.payment.currency, "BDT")
    async with db.begin():
        is_first_order, customer_group = check_first_order(db, payload.customer_id)
        order_item_info = evaluate_items(db, payload.items)
        order = OrderContext(
            customer_id=payload.customer_id,
            customer_group=customer_group,
            subtotal=order_item_info.subtotal,
            total_quantity=order_item_info.quantity,
            payment_method=payload.payment.payment_method,
            shipping_zone=payload.shipping.shipping_zone,
            is_first_order=is_first_order,
            product_ids=order_item_info.product_ids,
            category_ids=order_item_info.category_ids,
            brand_ids=order_item_info.brand_ids
        )

        result = get_discount(db, order, payload.coupon_code)
        if result:
            discount = result["discount"] + result["shipping_discount"]
        else:
            discount  = 0
        
        address = get_address(db, payload.shipping.address_id, payload.customer_id)
        shipping_detail = ShippingDetail(
            name = address.recipient_name,
            phone=address.recipient_contact,
            alternative_phone=address.recipient_backup_contact,
            recipient_email=address.recipient_email,
            address=address.address,
            district=address.district,
            thana = address.thana,
            cod_amount=order_item_info.subtotal - discount,
            invoice=None,
            item_description=None,
            note=None,
            weight=order_item_info.weight,
            is_exchange=None,
            is_home=None
        )

        delivary_charge = get_delivary_charge(shipping_detail)
        order = {
            "customer_id":payload.customer_id,
            "order_number":payload.order_info.order_id,
            "status": OrderStatus.PENDING,
            "fulfillment_status":FulfillmentStatus.PENDING,
            
            "subtotal":order_item_info.subtotal,
            "discount_total":discount,
            "shipping_total":delivary_charge,
            "tax_total": 0,
            "grand_total":order_item_info.subtotal - discount + delivary_charge,

            "refunded_amount":0,
            "coupon_code":payload.coupon_code,
            "customer_note":payload.customer_note,
            "admin_note": None,
            "is_guest_order": False,
            "placed_at": datetime.now(tz=timezone.utc)
        }
        new_order = await order_repositories.create_order(db, order)
        payment_method = payload.payment.payment_method
        payment = {
            "order_id": new_order.id,
            "payment_provider": PaymentProvider.SSLCOMMERZ if payment_method == 'ONLINE' else None,
            "payment_method":payment_method,
            "payment_status":PaymentStatus.PENDING,
            "currency":payload.payment.currency,
            "amount":order_item_info.subtotal - discount + delivary_charge,
            "paid_amount":0,
            "due_amount": order_item_info.subtotal - discount + delivary_charge,
            "refunded_amount":0,
            "gateway_reference":None,
            "exchange_rate": exchange_rate,
            "gateway_order_id":None,
            "payment_url":None,
            "is_test" :False
        }
        new_payment = await create_payment(db, payment)
        payment_url = None
        if new_payment.method == PaymentProvider.SSLCOMMERZ:
            gateway = SSLCommerzGateway()
            session = await gateway.create_session(
                payment=payment,
                customer=payload.customer_id
            )
            payment.gateway_url = session["GatewayPageURL"]
            payment.gateway_response = session
            payment_url = payment.gateway_rul

    if new_order:
        payment_url = ''
        data = PlaceOrderData(
            order_id = new_order.id,
            order_number=payload.order_info.order_id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            fulfillment_status=FulfillmentStatus.PENDING,
            currency=payload.payment.currency,
            exchange_rate=exchange_rate,

            subtotal = order_item_info.subtotal,
            discount_total=discount,
            shipping_total=delivary_charge,
            tax_total=0,
            grand_total=order_item_info.subtotal - discount + delivary_charge,

            payment_method=payment_method,
            payment_required=True if not payment_method == "COD" else False,
            payment_url=None if payment_method == "COD" else payment_url,

            placed_at = datetime.now(tz=timezone.utc),
            expires_at=datetime.now().date,

            invoice_url=None,
            tracking_url=None,
        )
        return PlaceOrderResponse(
            status = 200,
            success=True,
            message="Order Placed Successfully",
            lang='en',
            data=data,
            meta = Meta(
                request_id=request_id,
                timestamp=datetime.now(tz=timezone.utc)
            )
        )
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="order is not placed")