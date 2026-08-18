import secrets
from fastapi import HTTPException, status
from app.repositories import admin as admin_repositories
from app.schemas.product import Variant, VariantAttribute, VariantData
from app.services.admin.product_service.product.image.mapper import map_image_groups


def map_variant(variant) -> Variant:
    return Variant(
        id=getattr(variant, "id", None),
        name=variant.name,
        price=variant.price,
        compare_at_price=variant.compare_at_price,
        inventory=variant.inventory,
        status=variant.status,
        sku=variant.sku,
        attributes=[VariantAttribute(id=attribute.id, key=attribute.key, value=attribute.value)
                    for attribute in variant.attributes],
    )


def map_variants(variants) -> list[Variant]:
    return [map_variant(variant) for variant in variants]


def map_variant_data(variant) -> VariantData:
    return VariantData(variant=map_variant(variant), image_groups=map_image_groups(variant.image_groups))



def build_variant_sku(base_code: str, attributes: dict[str, str]) -> str:
    # build_variant_sku("TSHIRT", {"color": "Black", "size": "XL"})
    # -> "TSHIRT-BLK-XL"  (color before size, alphabetically)
    parts = [base_code.upper()]
    for key in sorted(attributes.keys()):
        value = attributes[key]
        parts.append(value[:3].upper())
    return "-".join(parts)

async def generate_unique_variant_sku(
        db, 
        bse_code:str,
        attributes
):
    new_attributes = {}
    for attr in attributes:
        new_attributes["key"] = attr.key
        new_attributes["value"] = attr.value

    candidate = build_variant_sku(bse_code, new_attributes)
    exist = await admin_repositories.get_variant_id(db, candidate)
    if exist is None:
        return candidate
    # fallback: same attribute values collide on truncation(e.g.  "Blue" VS "Black" => both: "BL")
    for _ in range(5):
        suffixed  = f"{candidate}-{secrets.token_hex(2).upper()}"
        exist = await admin_repositories.get_variant_id(db, suffixed)
        if exist is None:
            return suffixed
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to generate unique SKU")
