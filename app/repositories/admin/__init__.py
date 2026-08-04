"""Admin repository facade."""

from .brands import create_brand, get_brand, list_brand, remove_brand, update_brand
from .categories import create_category, get_category_by_name, list_category, update_category
from .products import *
from .promotions import *
