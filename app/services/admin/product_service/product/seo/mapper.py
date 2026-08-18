from app.schemas.product import SEO


def map_seo(seo) -> SEO:
    return SEO(
        meta_title=seo.meta_title,
        canonical_url=seo.canonical_url,
        meta_description=seo.meta_description,
        open_graph_image=seo.og_image,
        index=seo.no_index,
    )
