from pathlib import Path

from slugify import slugify

from app.repositories import admin as admin_repositories


async def add_images(db, product_id, image_groups, variants_output):
    for image_group in image_groups:
        group = await admin_repositories.add_image_group(db, {
            "title": image_group.title,
            "group_type": image_group.group_type,
            "description": image_group.description,
            "product_id": product_id,
            "variant_id": variants_output[image_group.temp_key],
        })
        for image in image_group.images:
            await admin_repositories.add_image(db, {
                "group_id": group.id,
                "image_url": Path("uploads/products").joinpath(
                    str(product_id), slugify(image.image_name)
                ).as_posix(),
                "alt_text": image.alt_text,
            })


async def update_image_group(db, image_groups):
    output = []
    for group in image_groups:
        data = {"id": group.id}
        for source, target in (("title", "title"), ("group_type", "group_type"),
                               ("description", "description"), ("product_id", "product_id"),
                               ("variant_id", "variant_id")):
            value = getattr(group, source)
            if value is not None:
                data[target] = value
        output.append(data)
    await admin_repositories.update_image_group(db, output)
