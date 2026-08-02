from enum import Enum

class ImageType(str, Enum):
    CATEGORY = "category"
    PRODUCT = "product"
    BRAND = "brand"
    LOGO = "logo"
    BANNER = "banner"