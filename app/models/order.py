from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Enum,
    DateTime,
    Numeric,
    BigInteger,
    Text,
    JSON
)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.enums.order_enums import *
from app.enums.payment_enums import PaymentStatus

from app.models.base import BaseModel
from app.enums.base_enums import sa_enum

# from app.models.user import OrderAdresses




class Order(BaseModel):
    __tablename__ = "orders"

    # -------------------------
    # Primary Key
    # -------------------------


    # -------------------------
    # Customer
    # -------------------------
    customer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True
    )

    address_id = Column(
        Integer, 
        ForeignKey("order_addresses.id", ondelete="CASCADE"),
        nullable=True
    )
    
    # -------------------------
    # Order Information
    # -------------------------
    order_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    status = Column(
        sa_enum(OrderStatus, "order_status"),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )

    fulfillment_status = Column(
        sa_enum(FulfillmentStatus, "fullfillment_status"),
        default=FulfillmentStatus.PENDING,
        nullable=False,
        index=True,
    )  # Tracks whether the products have been prepared and delivered.{Pending, Processing,Packed, Shipped, Delivered }


    # -------------------------
    # Price Summary
    # -------------------------
    subtotal = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    discount_total = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    shipping_total = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    tax_total = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    grand_total = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )  # total amount 




    # -------------------------
    # Promotion
    # -------------------------
    coupon_code = Column(String(100))

    # -------------------------
    # Customer
    # -------------------------
    customer_note = Column(Text)

    admin_note = Column(Text)

    # -------------------------
    # Flags
    # -------------------------
    is_guest_order = Column(
        Boolean,
        nullable=False,
        default=False,
    )


    # -------------------------
    # Dates
    # -------------------------
    placed_at = Column(DateTime(timezone=True))

    confirmed_at = Column(DateTime(timezone=True))

    shipped_at = Column(DateTime(timezone=True))

    delivered_at = Column(DateTime(timezone=True))

    cancelled_at = Column(DateTime(timezone=True))

    completed_at = Column(DateTime(timezone=True))


    # -------------------------
    # Relationships
    # -------------------------
    customer = relationship("User")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    addresses = relationship(
        "OrderAdresses",
        back_populates="order"
    )

    timeline = relationship(
        "OrderTimeline",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    shipments = relationship(
        "Shipment",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    discounts = relationship(
        "OrderDiscount",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    invoices = relationship(
        "Invoice",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    returns = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    delivery = relationship(
        "DeliveryDetail",
        back_populates="order"
    )


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    variant_id = Column(String)

    name = Column(String, nullable=False)
    sku = Column(String)

    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    image = Column(String)

    order = relationship(
        "Order",
        back_populates="items"
    )


class OrderTimeline(BaseModel):
    __tablename__ = "order_timelines"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event = Column(
        String(100),
        nullable=False,
        index=True,
    )

    previous_status = Column(
        String(50),
        nullable=True,
    )

    current_status = Column(
        String(50),
        nullable=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    actor_type = Column(
        String(30),
        nullable=False,
    )

    actor_id = Column(
        BigInteger,
        nullable=True,
    )

    actor_name = Column(
        String(255),
        nullable=True,
    )

    ip_address = Column(
        String(45),
        nullable=True,
    )

    metadata_ = Column(
        JSON,
        nullable=True,
    )
    # --------------------
    # Relationships
    # --------------------

    order = relationship(
        "Order",
        back_populates="timeline",
    )



class Payment(BaseModel):
    __tablename__ = "payments"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    payment_method = Column(
        String(50),
        nullable=False,
        index=True,
    )

    payment_provider = Column(
        String(50),
        nullable=False,
        index=True,
    )

    payment_status = Column(
        sa_enum(PaymentStatus, "payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="BDT",
    )
    exchange_rate = Column(
            Numeric(12, 6),
            nullable=False,
            default=1,
    )  # current exchanange rate of selected currency

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    paid_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    due_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    refunded_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    gateway_reference = Column(
        String(255),
        nullable=True,
    )

    gateway_order_id = Column(
        String(255),
        nullable=True,
    )

    payment_url = Column(
        Text,
        nullable=True,
    )

    is_test = Column(
        Boolean,
        default=False,
    )

    paid_at = Column(DateTime(timezone=True))

    expires_at = Column(DateTime(timezone=True))

    # ---------------- Relationships ----------------

    order = relationship(
        "Order",
        back_populates="payments",
    )

    transactions = relationship(
        "PaymentTransaction",
        back_populates="payment",
        cascade="all, delete-orphan",
    )


class PaymentTransaction(BaseModel):
    __tablename__ = "payment_transactions"



    payment_id = Column(
        BigInteger,
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    transaction_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    transaction_status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    gateway_transaction_id = Column(
        String(255),
        nullable=True,
        unique=True,
    )

    gateway_reference = Column(
        String(255),
        nullable=True,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="BDT",
    )

    gateway_response = Column(
        JSON,
        nullable=True,
    )

    failure_reason = Column(
        Text,
        nullable=True,
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    payment = relationship(
        "Payment",
        back_populates="transactions",
    )

    
class DeliveryDetail(BaseModel):
    __tablename__ = "delivery_details"


    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True
    )

    type = Column(
        sa_enum(DeliveryType, "delivery_type"),
        nullable=False
    )

    address = Column(Integer, ForeignKey('order_addresses.id', ondelete='CASCADE'))

    courier = Column(String)

    tracking_id = Column(String)

    order = relationship(
        "Order",
        back_populates="delivery"
    )
    order_address = relationship("OrderAdresses", back_populates="deliveries")


class ShippingRate(BaseModel):
    __tablename__ = "shipping_rates"



    name = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    description = Column(Text)

    shipping_method = Column(
        String(50),
        nullable=False,
        index=True,
    )

    carrier = Column(
        String(100),
        nullable=True,
        index=True,
    )

    service_level = Column(
        String(50),
        nullable=True,
    )

    zone_id = Column(
        Integer,
        ForeignKey("shipping_zones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    minimum_order_amount = Column(
        Numeric(12,2),
        default=0,
        nullable=False,
    )

    maximum_order_amount = Column(
        Numeric(12,2),
        nullable=True,
    )

    minimum_weight = Column(
        Numeric(10,2),
        default=0,
        nullable=False,
    )

    maximum_weight = Column(
        Numeric(10,2),
        nullable=True,
    )

    base_rate = Column(
        Numeric(12,2),
        nullable=False,
    )

    additional_rate_per_kg = Column(
        Numeric(12,2),
        default=0,
        nullable=False,
    )

    free_shipping = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    estimated_delivery_days = Column(
        Integer,
        nullable=False,
    )

    priority = Column(
        Integer,
        default=0,
        nullable=False,
    )

    currency = Column(
        String(10),
        default="BDT",
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    zone = relationship("ShippingZone", back_populates="rates")

class ShippingZone(BaseModel):
    __tablename__ = "shipping_zones"

    zone_code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    zone_name = Column(
        String(100),
        nullable=False,
        index=True,
    )

    country = Column(
        String(100),
        nullable=False,
    )

    state = Column(
        String(100),
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    postal_code = Column(
        String(20),
        nullable=True,
    )

    priority = Column(
        Integer,
        default=0,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )


    rates = relationship(
        "ShippingRate",
        back_populates="zone",
        cascade="all, delete-orphan",
    )

class Shipment(BaseModel):

    __tablename__ = "shipments"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    shipment_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    carrier = Column(
        String(100),
        nullable=False,
        index=True,
    )

    shipping_service = Column(
        String(100),
        nullable=True,
    )

    tracking_number = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    tracking_url = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    shipping_cost = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    estimated_delivery_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    shipped_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    returned_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivery_attempts = Column(
        BigInteger,
        nullable=False,
        default=0,
    )

    is_return_shipment = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    note = Column(
        Text,
        nullable=True,
    )

    # ---------------- Relationships ----------------

    order = relationship(
        "Order",
        back_populates="shipments",
    )

    warehouse = relationship("Warehouse",
                             back_populates="shipment")
    

    items = relationship(
        "ShipmentItem",
        back_populates="shipment",
        cascade="all, delete-orphan",
    )


class ShipmentItem(BaseModel):
    __tablename__ = "shipment_items"



    shipment_id = Column(
        BigInteger,
        ForeignKey("shipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_item_id = Column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )
    shipment = relationship(
        "Shipment",
        back_populates="items",
    )

    order_item = relationship("OrderItem")



class OrderDiscount(BaseModel):
    __tablename__ = "order_discounts"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    promotion_id = Column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    coupon_code = Column(
        String(100),
        nullable=True,
        index=True,
    )

    discount_name = Column(
        String(255),
        nullable=False,
    )

    discount_type = Column(
        String(50),
        nullable=False,
    )

    discount_value = Column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )
    # ---------------- Relationships ---------------- #

    order = relationship(
        "Order",
        back_populates="discounts",
    )

    promotion = relationship("Promotions")




class OrderItemDiscount(BaseModel):
    __tablename__ = "order_item_discounts"



    order_item_id = Column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    promotion_id = Column(
        BigInteger,
        ForeignKey("promotions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    discount_name = Column(
        String(255),
        nullable=False,
    )

    discount_type = Column(
        String(50),
        nullable=False,
    )

    discount_value = Column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )
    # ---------------- Relationships ---------------- #

    order_item = relationship("OrderItem")

    promotion = relationship("Promotions")


class InventoryReservation(BaseModel):
    __tablename__ = "inventory_reservations"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_item_id = Column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_variant_id = Column(
        BigInteger,
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    reservation_status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    released_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    order = relationship("Order")

    order_item = relationship("OrderItem")

    product_variant = relationship("ProductVariant")


class Invoice(BaseModel):
    __tablename__ = "invoices"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    invoice_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="BDT",
    )

    subtotal = Column(
        Numeric(12,2),
        nullable=False,
    )

    discount_total = Column(
        Numeric(12,2),
        nullable=False,
    )

    shipping_total = Column(
        Numeric(12,2),
        nullable=False,
    )

    tax_total = Column(
        Numeric(12,2),
        nullable=False,
    )

    grand_total = Column(
        Numeric(12,2),
        nullable=False,
    )

    paid_amount = Column(
        Numeric(12,2),
        nullable=False,
    )

    due_amount = Column(
        Numeric(12,2),
        nullable=False,
    )

    pdf_url = Column(
        Text,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    issued_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    order = relationship(
        "Order",
        back_populates="invoices",
    )


class ReturnRequest(BaseModel):
    __tablename__ = "return_requests"



    return_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    reason = Column(
        Text,
        nullable=False,
    )

    customer_comment = Column(Text)

    admin_comment = Column(Text)

    requested_refund_amount = Column(
        Numeric(12,2),
        nullable=False,
        default=0,
    )

    approved_refund_amount = Column(
        Numeric(12,2),
        nullable=False,
        default=0,
    )

    approved_at = Column(DateTime(timezone=True))

    rejected_at = Column(DateTime(timezone=True))

    completed_at = Column(DateTime(timezone=True))

    is_closed = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    order = relationship(
        "Order",
        back_populates="returns",
    )

    customer = relationship("User")

    items = relationship(
        "ReturnItem",
        back_populates="return_request",
        cascade="all, delete-orphan",
    )

    refunds = relationship(
        "Refund",
        back_populates="return_request",
    )


class ReturnItem(BaseModel):
    __tablename__ = "return_items"



    return_request_id = Column(
        BigInteger,
        ForeignKey("return_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_item_id = Column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    reason = Column(
        String(255),
        nullable=False,
    )

    condition = Column(
        String(100),
        nullable=True,
    )

    resolution = Column(
        String(50),
        nullable=True,
    )

    refund_amount = Column(
        Numeric(12,2),
        nullable=False,
        default=0,
    )

    customer_note = Column(Text)
    return_request = relationship(
        "ReturnRequest",
        back_populates="items",
    )

    order_item = relationship("OrderItem")


class Refund(BaseModel):
    __tablename__ = "refunds"



    refund_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    payment_id = Column(
        BigInteger,
        ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    return_request_id = Column(
        BigInteger,
        ForeignKey("return_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    refund_method = Column(
        String(50),
        nullable=False,
    )

    gateway_refund_id = Column(
        String(255),
        nullable=True,
        unique=True,
    )

    amount = Column(
        Numeric(12,2),
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="BDT",
    )

    reason = Column(Text)

    processed_at = Column(DateTime(timezone=True))
    payment = relationship("Payment")

    return_request = relationship(
        "ReturnRequest",
        back_populates="refunds",
    )




class OrderNote(BaseModel):
    __tablename__ = "order_notes"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    note_type = Column(
        String(30),
        nullable=False,
        index=True,
    )

    note = Column(
        Text,
        nullable=False,
    )

    is_customer_visible = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    # ---------------- Relationships ---------------- #

    order = relationship("Order")

    user = relationship("User")




class OrderNotification(BaseModel):
    __tablename__ = "order_notifications"



    order_id = Column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    notification_type = Column(
        String(30),
        nullable=False,
        index=True,
    )

    recipient = Column(
        String(255),
        nullable=False,
    )

    subject = Column(
        String(255),
        nullable=True,
    )

    message = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    provider = Column(
        String(100),
        nullable=True,
    )

    provider_message_id = Column(
        String(255),
        nullable=True,
        unique=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    # ---------------- Relationships ---------------- #

    order = relationship("Order")




class OrderAllocation(BaseModel):
    __tablename__ = "order_allocations"



    order_item_id = Column(
        BigInteger,
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    allocated_quantity = Column(
        Integer,
        nullable=False,
    )

    picked_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    packed_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    shipped_quantity = Column(
        Integer,
        nullable=False,
        default=0,
    )

    allocation_status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    allocated_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    order_item = relationship("OrderItem")

    warehouse = relationship("Warehouse", back_populates='allocation')

class Warehouse(BaseModel):
    __tablename__ = "warehouses"

    warehouse_code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    contact_person = Column(
        String(150),
        nullable=True,
    )

    phone = Column(
        String(30),
        nullable=True,
    )

    email = Column(
        String(150),
        nullable=True,
    )

    address_line1 = Column(
        String(255),
        nullable=False,
    )

    address_line2 = Column(
        String(255),
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=False,
    )

    state = Column(
        String(100),
        nullable=True,
    )

    postal_code = Column(
        String(20),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=False,
    )

    latitude = Column(
        Numeric(10, 7),
        nullable=True,
    )

    longitude = Column(
        Numeric(10, 7),
        nullable=True,
    )

    timezone = Column(
        String(50),
        nullable=True,
    )

    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    status = Column(
        sa_enum(WarehouseStatus, "warehouse_status"),
        nullable=True,
        default = WarehouseStatus.ACTIVE
    )

    notes = Column(
        Text,
        nullable=True,
    )

    allocation = relationship("OrderAllocation", cascade="all, delete-orphan", back_populates="warehouse")
    shipment = relationship("Shipment", cascade="all, delete-orphan", back_populates="warehouse")





