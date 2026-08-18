from app.repositories import admin as admin_repositories


async def update_publishing(db, publishing):
    output = []
    for item in publishing:
        data = {"id": item.id}
        for field in ("search_boost", "status", "feature_product"):
            value = getattr(item, field)
            if value is not None:
                data[field] = value
        output.append(data)
    await admin_repositories.update_publishing(db, output)
