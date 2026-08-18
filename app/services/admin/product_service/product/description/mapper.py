from app.schemas.product import DescriptionSchema


def map_description(description) -> DescriptionSchema:
    return DescriptionSchema(
        id=getattr(description, "id", None),
        title=description.title,
        text=description.text,
    )


def map_descriptions(descriptions) -> list[DescriptionSchema]:
    return [map_description(description) for description in descriptions]
