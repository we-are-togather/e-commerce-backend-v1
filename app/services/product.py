from pathlib import Path
from app.db.base import get_db

from app.models.product import (
    ProductVariant
)
def get_variant_id(db, variants, sku):
    return db.query(ProductVariant).filter_by(
        ProductVariant.sku == sku
    ).id
