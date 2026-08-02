from dataclasses import dataclass

@dataclass(frozen=True)
class ImageValidationConfig:
    min_width: int
    min_height: int
    max_width: int
    max_height: int
    max_size_mb: int
    allowed_extensions: set[str]
    allowed_content_types: set[str]
    require_square: bool = False