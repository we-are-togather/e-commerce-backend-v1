from enum import Enum

class PromotionType(str, Enum):
    AUTOMATIC_DISCOUNT = "AUTOMATIC_DISCOUNT"
    COUPON_CAMPAIGN = "COUPON_CAMPAIGN"
    FLASH_SALE = "FLASH_SALE"
    BUY_X_GET_Y = "BUY_X_GET_Y"
    BUNDLE_DISCOUNT = "BUNDLE_DISCOUNT"
    FREE_SHIPPING = "FREE_SHIPPING"
    GIFT_WITH_PURCHASE = "GIFT_WITH_PURCHASE"
    LOYALTY_PROMOTION = "LOYALTY_PROMOTION"

class RewardType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"
    FREE_PRODUCT = "free_product"
    BUY_X_GET_Y = "buy_x_get_y"
    GIFT_PRODUCT = "gift_product"
    BUNDLE_PRICE = "bundle_price"
    LOYALTY_POINTS = "loyalty_points"
    CASHBACK = "cashback"


class PromotionTargetType(str, Enum):
    ORDER = "order"
    PRODUCT = "product"
    VARIANT = "variant"
    CATEGORY = "category"
    BRAND = "brand"
    COLLECTION = "collection"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    CUSTOMER_GROUP = "customer_group"
    SHIPPING_ZONE = "shipping_zone"
    WAREHOUSE = "warehouse"


class PromotionStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    ARCHIVED = "archived"

class TargetType(str, Enum):
    PRODUCT = "PRODUCT"
    CATEGORY = "CATEGORY"
    BRAND = "BRAND"
    CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT"
    ALL = "ALL"

class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"

 
class CouponGenerationType(str, Enum):
    SINGLE_CODE = "SINGLE_CODE"
    BULK_UNIQUE = "BULK_UNIQUE"

class RewardDiscountType(str, Enum):
    FREE = "FREE"
    PERCENTAGE_OFF = "PERCENTAGE_OFF"
    FIXED_OFF = "FIXED_OFF"

class BundleDiscountType(str, Enum):
    FIXED_BUNDLE_PRICE = "FIXED_BUNDLE_PRICE"
    PERCENTAGE_OFF = "PERCENTAGE_OFF"

class RuleType(str, Enum):
    MINIMUM_ORDER_AMOUNT = "minimum_order_amount"
    MINIMUM_QUANTITY = "minimum_quantity"
    MAXIMUM_QUANTITY = "maximum_quantity"
    CUSTOMER_GROUP = "customer_group"
    CUSTOMER = "customer"
    BRAND = "brand"
    CATEGORY = "category"
    COLLECTION = "collection"
    PRODUCT = "product"
    VARIANT = "variant"
    PAYMENT_METHOD = "payment_method"
    SHIPPING_ZONE = "shipping_zone"
    SHIPPING_COUNTRY = "shipping_country"
    FIRST_ORDER = "first_order"
    CUSTOMER_TOTAL_SPENT = "customer_total_spent"
    CUSTOMER_ORDER_COUNT = "customer_order_count"
    WEEKDAY = "weekday"
    TIME_RANGE = "time_range"


class TargetRole(str, Enum):
    QUALIFIER = "qualifier"   # Customer must buy
    REWARD = "reward"         # Customer receives
    DISCOUNT = "discount"     # Discount is applied to these items
    EXCLUDED = "excluded"     # Explicitly excluded from promotion

class CouponStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    DISABLED = "disabled"

class RuleOperator(str, Enum):
    # Equality
    EQUAL = "eq"
    NOT_EQUAL = "ne"

    # Numeric comparison
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"

    # Collection comparison
    IN = "in"
    NOT_IN = "not_in"

    # String comparison
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

    # Range comparison
    BETWEEN = "between"

    # Boolean
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"