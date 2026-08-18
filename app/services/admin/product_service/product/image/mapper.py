from app.schemas.product import Image, ImageGroup


def map_image(image) -> Image:
    return Image(image_url=image.image_url, alt_text=image.alt_text)


def map_image_group(group) -> ImageGroup:
    variant = getattr(group, "product_variant", None)
    return ImageGroup(
        id=group.id,
        product_id=group.product_id,
        variant_id=group.variant_id,
        title=group.title,
        group_type=group.group_type,
        description=group.description,
        variant_sku=variant.sku if variant else None,
        images=[map_image(image) for image in group.image_links],
    )


def map_image_groups(groups) -> list[ImageGroup]:
    return [map_image_group(group) for group in groups]
