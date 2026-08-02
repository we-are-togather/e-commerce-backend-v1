from app.utils.helper.data_class import ImageValidationConfig

COMMON_ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

COMMON_ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

IMAGE_CONFIGS = {
    "category": ImageValidationConfig(
        min_width=600,
        min_height=600,
        max_width=3000,
        max_height=3000,
        max_size_mb=5,
        require_square=True,
        allowed_extensions=COMMON_ALLOWED_EXTENSIONS,
        allowed_content_types=COMMON_ALLOWED_CONTENT_TYPES,
    ),
    "product": ImageValidationConfig(
        min_width=1000,
        min_height=1000,
        max_width=5000,
        max_height=5000,
        max_size_mb=8,
        require_square=False,
        allowed_extensions=COMMON_ALLOWED_EXTENSIONS,
        allowed_content_types=COMMON_ALLOWED_CONTENT_TYPES,
    ),
    "brand": ImageValidationConfig(
        min_width=300,
        min_height=300,
        max_width=2000,
        max_height=2000,
        max_size_mb=3,
        require_square=True,
        allowed_extensions=COMMON_ALLOWED_EXTENSIONS,
        allowed_content_types=COMMON_ALLOWED_CONTENT_TYPES,
    ),
    "logo": ImageValidationConfig(
        min_width=128,
        min_height=128,
        max_width=1024,
        max_height=1024,
        max_size_mb=2,
        require_square=True,
        allowed_extensions={".png", ".webp", ".svg"},
        allowed_content_types={
            "image/png",
            "image/webp",
            "image/svg+xml",
        },
    ),
    "banner": ImageValidationConfig(
        min_width=1200,
        min_height=400,
        max_width=5000,
        max_height=3000,
        max_size_mb=8,
        require_square=False,
        allowed_extensions=COMMON_ALLOWED_EXTENSIONS,
        allowed_content_types=COMMON_ALLOWED_CONTENT_TYPES,
    ),
}
