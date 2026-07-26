from enum import Enum

class CustomerGroupType(str, Enum):
    RETAIL = "RETAIL"
    WHOLESALE = "WHOLESALE"
    CORPORATE = "CORPORATE"
    VIP = "VIP"
    EMPLOYEE = "EMPLOYEE"