from unittest import skip

from app.models.product import (
    Brand,
    Category,
    Product,
    ProductVariant,
    Attribute,
    ImageGroup,
    Image,
    ProductVideos,

    Description,
    SpecificationType,
    SpecificationValue,

    Tag,
    ProductTag,
    ProductBadge,
    Badge,

    SEOKeyword,
    ProductSEO,
    SearchKeyword
)

class BaseRepository:
    def __init__(self, model):
        self.model = model
    
    def create(self, db, data):
        obj = self.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    

def create_brand(db, brand:Brand):
    return BaseRepository(Brand).create(db, brand)

def remove_brand(db, brand_id:int) -> bool:
    brand = db.query(Brand).filter_by(id=brand_id).first()
    if not brand:
        return False
    db.delete(brand)
    db.commit()
    return True

def list_brand(db):
    return db.query(Brand).all()

def get_brand_name(db, name:str):
    return db.query(Brand).filter_by(Brand.name == name).first()



# ===========================================
#                   Category
# ===========================================
def create_category(db, category):
    return BaseRepository(Category).create(db, category)

def list_category(db):
    return db.query(Category).all()

def get_category_by_name(db, name:str = None, cat_id= None):
    if name:
        return db.query(Category).filter_by(Category.name == name).first()
    if cat_id:
        return db.query(Category).filter_by(Category.id==cat_id).first()



# ===========================================
#               Add Product
# ===========================================
def add_product(db, product):
    return BaseRepository(Product).create(db, product)

def add_variant_attribute(db, variant_attribute):
    return BaseRepository(Attribute).create(db, variant_attribute)

def add_variant(db, variant):
    return BaseRepository(ProductVariant).create(db, variant)

def get_variant_id(db, key):
    return db.query(ProductVariant).filter_by(ProductVariant.sku == key).id


def add_image_group(db, image_group):
    return BaseRepository(ImageGroup).create(db, image_group)

def add_image(db, image):
    return BaseRepository(Image).create(db, image)

def add_videos(db, video):
    return BaseRepository(ProductVideos).create(db, video)


def add_description(db, description):
    return BaseRepository(Description).create(db, description)

def add_specification_type(db, specification_type):
    return BaseRepository(SpecificationType).create(db, specification_type)

def add_specification_value(db, specification_value):
    return BaseRepository(SpecificationValue).create(db, specification_value)


def add_tag(db, tag):
    return BaseRepository(Tag).create(db, tag)

def add_product_tag(db, product_tag):
    return BaseRepository(ProductTag).create(db, product_tag)

def get_tag(db, tag):
    return db.query(Tag).filter_by(Tag.name==tag).first()

def add_badge(db, badge):
    return BaseRepository(Badge).create(db, badge)

def add_product_badge(db, product_badge):
    return BaseRepository(ProductBadge).create(db, product_badge)

def get_badge(db, badge):
    return db.query(Badge).filter_by(Badge.name==badge).first()


def add_seo(db, seo):
    return BaseRepository(ProductSEO).create(db, seo)

def add_seo_keyword(db, seo_keyword):
    return BaseRepository(SEOKeyword).create(db, seo_keyword)