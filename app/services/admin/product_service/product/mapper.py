from app.schemas.admin import ProductResponse
from app.schemas.product import Video


def map_product_list_item(product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        status=product.status,
        category=product.cat.name,
        min_price=product.min_price,
        max_price=product.max_price,
        quantitiy=product.quantity,
        product_code=product.product_code,
        brand=product.brand_table.name,
        model=product.model,
    )


def map_videos(videos) -> list[Video]:
    return [Video(url=video.video_url, title=video.title, platform=video.platform) for video in videos]

def build_base_code(category_prefix: str, seq_val: int) -> str:
    return f"{category_prefix.upper()}-{seq_val:06d}"
