from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"                     # Order placed, awaiting confirmation
    CONFIRMED = "CONFIRMED"                 # Order accepted by admin/system
    PROCESSING = "PROCESSING"               # Preparing the order
    ON_HOLD = "ON_HOLD"                     # Temporarily paused
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"  # Some items shipped
    COMPLETED = "COMPLETED"                 # Delivered and closed
    CANCELLED = "CANCELLED"                 # Order cancelled
    RETURN_REQUESTED = "RETURN_REQUESTED"   # Customer requested return
    RETURNED = "RETURNED"                   # All items returned
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED" # Some items returned
    REFUNDED = "REFUNDED"                   # Fully refunded
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED" # Partially refunded






class DeliveryType(str, Enum):
    INSIDE_DHAKA = "INSIDE_DHAKA"
    OUTSIDE_DHAKA = "OUTSIDE_DHAKA"

class AddressCategory(str, Enum):
    Home = "home"
    office = "office"

class DefaultShippingAddress(str, Enum):
    on = "on"
    off = "off"

class DefaultBillingAddress(str, Enum):
    on = "on"
    off = "off"

class TimelineEvent(str, Enum):
    ORDER_PLACED = "ORDER_PLACED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    PROCESSING = "PROCESSING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURN_REQUESTED = "RETURN_REQUESTED"
    RETURN_APPROVED = "RETURN_APPROVED"
    RETURN_REJECTED = "RETURN_REJECTED"
    RETURNED = "RETURNED"
    REFUND_INITIATED = "REFUND_INITIATED"
    REFUND_COMPLETED = "REFUND_COMPLETED"

class TimelineActor(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
    COURIER = "COURIER"
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"





class TransactionType(str, Enum):
    AUTHORIZE = "AUTHORIZE"
    CAPTURE = "CAPTURE"
    SALE = "SALE"
    REFUND = "REFUND"
    VOID = "VOID"
    CHARGEBACK = "CHARGEBACK"

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ShipmentStatus(str, Enum):
    PENDING = "PENDING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILED = "DELIVERY_FAILED"
    RETURN_IN_TRANSIT = "RETURN_IN_TRANSIT"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"

class ShippingMethod(str, Enum):
    STANDARD = "STANDARD"
    EXPRESS = "EXPRESS"
    SAME_DAY = "SAME_DAY"
    NEXT_DAY = "NEXT_DAY"
    PICKUP = "PICKUP"
    INTERNATIONAL = "INTERNATIONAL"

class Carrier(str, Enum):
    PATHAO = "PATHAO"
    REDX = "REDX"
    STEADFAST = "STEADFAST"
    PAPERFLY = "PAPERFLY"
    DHL = "DHL"
    FEDEX = "FEDEX"
    UPS = "UPS"

class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    FREE_SHIPPING = "FREE_SHIPPING"
    BUY_X_GET_Y = "BUY_X_GET_Y"
    BUNDLE = "BUNDLE"

class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"

class ReturnStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"

class ReturnResolution(str, Enum):
    REFUND = "REFUND"
    REPLACEMENT = "REPLACEMENT"
    EXCHANGE = "EXCHANGE"
    STORE_CREDIT = "STORE_CREDIT"

class RefundStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"



class OrderNoteType(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
    WAREHOUSE = "WAREHOUSE"


class NotificationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    WHATSAPP = "WHATSAPP"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class AllocationStatus(str, Enum):
    ALLOCATED = "ALLOCATED"
    PICKING = "PICKING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class FulfillmentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVARED = "DELIVERED"


class WarehouseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    CLOSED = "CLOSED"
