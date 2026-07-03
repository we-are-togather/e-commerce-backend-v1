from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
    func,
    Boolean
)
from sqlalchemy import Table, Column, Integer, ForeignKey

from sqlalchemy.orm import relationship
from app.db.base import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# =========================
# Product Table

# =========================

# class Attribute(Base):
#     '''
#     Product attributes like Color, Size, etc.
#     '''
#     __tablename__ = "attributes"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, unique=True)
#     value = relationship("AttributeValue", back_populates="attribute")

# class AttributeValue(Base):
#     '''
#     Values for attributes, e.g. Red, Blue for Color; S, M, L for Size. Memory 8GB, 16GB for RAM. Processor i5, i7 for Processor.'''
#     __tablename__ = "attribute_values"

#     id = Column(Integer, primary_key=True)

#     attribute_id = Column(
#         Integer,
#         ForeignKey("attributes.id")
#     )

#     value = Column(String)
#     attribute = relationship("Attribute", back_populates="value")

class Attribute(BaseModel):
    __tablename__ = "variant_attributes"
    key = Column(String)
    value = Column(String)
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    
    variant = relationship("ProductVariant", back_populates='attributes')

# class ProductVariantAttribute(Base):
#     '''
#     This table links product variants to their specific attribute values. For example, it would link the Red-S variant of a T-shirt to the "Red" value of the "Color" attribute and the "S" value of the "Size" attribute.'''
#     __tablename__ = "product_variant_attributes"

#     id = Column(Integer, primary_key=True)

#     product_variant_id = Column(
#         Integer,
#         ForeignKey("product_variants.id")
#     )

#     attribute_value_id = Column(
#         Integer,
#         ForeignKey("attribute_values.id")
#     )

#     # is_featured = Column(Boolean, default=False)
#     product_variant = relationship("ProductVariant", back_populates="attributes")

class ProductVariant(Base):
    '''
    Product variants represent specific combinations of attributes for a product. For example, a T-shirt product might have variants for each combination of size and color (e.g., Red-S, Red-M, Blue-S, Blue-M). Each variant can have its own price, stock level, and other properties.
    '''
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )
    color_name = Column(String(100))
    price = Column(Float)
    compare_at_price = Column(Float)
    inventory = Column(Integer, default=0)
    status = Column(String)

    sku = Column(String, unique=True)
    # Relationships
    product = relationship("Product", back_populates="variants", cascade="all, delete")
    image_groups = relationship("ImageGroup", back_populates="product_variant", cascade="all, delete")
    attributes = relationship("Attribute", back_populates="variant", cascade="all, delete")


class ImageGroup(BaseModel):
    '''
    This table stores images for each product. For example, a laptop product might have multiple images showing different angles of the laptop, close-ups of the keyboard, and images of the laptop in use. Each image is linked to a specific product.'''
    __tablename__ = "image_group"

    title = Column(String)
    group_type = Column(String)
    description = Column(String)

    product_id = Column(Integer, ForeignKey("products.id"))
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    # Relationships
    product = relationship("Product", back_populates="image_groups")
    image_links = relationship("Image", back_populates="group", cascade='all, delete')
    product_variant = relationship("ProductVariant", back_populates="image_groups")

class Image(BaseModel):
    __tablename__ = "images"
    image_url = Column(String)
    alt_text = Column(String(255))
    format = Column(String(50))
    group_id = Column(Integer, ForeignKey('image_group.id'))
    
    # relationship
    group = relationship("ImageGroup", back_populates="image_links")


class ProductVideos(BaseModel):
    '''
    This table stores videos for each product. For example, a laptop product might have a video showcasing its features and performance. Each video is linked to a specific product.'''
    __tablename__ = "product_videos"

    product_id = Column(Integer, ForeignKey("products.id"))

    video_url = Column(String)
    title = Column(String(255))
    platform = Column(String(50))  # e.g., YouTube, Vimeo


    # Relationships
    product = relationship("Product", back_populates="videos")


# =========================
# Product Tags 
# example: New Arrival, Best Seller, Discounted
# =========================
class ProductTag(BaseModel):
    '''
    Product tags are used to label products with specific attributes or characteristics that can help customers find and filter products. For example, tags like "New Arrival", "Best Seller", "Discounted", etc. can be used to highlight certain products and make them more discoverable. Each product can have multiple tags, and each tag can be associated with multiple products.'''
    __tablename__ = "product_tags"

    product_id = Column(Integer, ForeignKey("products.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))


    # Relationships
    # products = relationship(
    #     "Product",
    #     secondary="product_tag_association",
    #     back_populates="tags"
    # )
    # tags = relationship("Tag", back_populates="product_tag")

# =========================
# tags
# example: New Arrival, Best Seller, Discounted
# =========================
class Tag(BaseModel):
    '''
    The Tag table represents the different tags that can be associated with products. Each tag can be linked to multiple products, and each product can have multiple tags. For example, tags like "New Arrival", "Best Seller", "Discounted", etc. can be used to label products with specific attributes or characteristics that can help customers find and filter products.'''
    __tablename__ = "tags"

    name = Column(String(100), nullable=False)

    # Relationships
    products = relationship(
        "Product",
        secondary="product_tags",
        back_populates="tags"
    )



# product_tag_association = Table(
#     "product_tag_association",
#     Base.metadata,
#     Column("product_tag_id", Integer, ForeignKey("product_tags.id")),
#     Column("tag_id", Integer, ForeignKey("tags.id")),
#     Column('Product_id', Integer, ForeignKey('products.id'))
# )

#=============================
# Product Badges
# Example: New Arrival, Best Seller, Discounted
#=============================
class Badge(BaseModel):
    '''
    The Badge table represents the different badges that can be associated with products. Each badge can be linked to multiple products, and each product can have multiple badges. For example, badges like "New Arrival", "Best Seller", "Discounted", etc. can be used to label products with specific attributes or characteristics that can help customers find and filter products.'''
    __tablename__ = "badges"

    name = Column(String(100), nullable=False)

    # Relationships
    products = relationship(
        "Product",
        secondary="product_badges",
        back_populates="badges"
    )
class ProductBadge(BaseModel):
    '''
    Product badges are used to label products with specific attributes or characteristics that can help customers find and filter products. For example, badges like "New Arrival", "Best Seller", "Discounted", etc. can be used to highlight certain products and make them more discoverable. Each product can have multiple badges, and each badge can be associated with multiple products.'''
    __tablename__ = "product_badges"

    product_id = Column(Integer, ForeignKey("products.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))

    # Relationships
    # product = relationship(
    #     "Product",
    #     # secondary="product_badge_association",
    #     back_populates="badges"
    # )
    # badges = relationship("Badge", back_populates="products")

    
class Product(BaseModel):
    '''
    The main product table that contains general information about the product. Each product can have multiple variants (e.g., different sizes or colors) and multiple specifications (e.g., RAM, Storage).'''
    __tablename__ = "products"
    name = Column(String(255), nullable=False)

    status = Column(String(50))

    category = Column(Integer, ForeignKey("categories.id"))
    # subcategory = Column(Integer, ForeignKey("categories.id"), nullable=True)
    thumbnail_url = Column(String(255))
    search_boost = Column(Integer, default=0)
    
    min_price = Column(Float)
    max_price = Column(Float)


    slug = Column(String(255), unique=True)
    
    quantity = Column(Integer, default=0)

    product_code = Column(String(100), unique=True)

    brand = Column(Integer, ForeignKey("brands.id"))

    model = Column(String(100))

    short_description = Column(Text)


    # Relationships

    brand_table = relationship("Brand", back_populates="products")
    cat = relationship("Category",  back_populates="products")
    inventory_summary  = relationship("InventorySummary", back_populates="product", uselist=False, cascade="all, delete")
    seo = relationship("ProductSEO", back_populates="product", uselist=False, cascade="all, delete")
    seo_keywords = relationship("SEOKeyword", back_populates="product", cascade="all, delete")
    search_keywords = relationship("SearchKeyword", back_populates="product", cascade="all, delete")

    # subcategory = relationship("Category", foreign_keys=[subcategory], back_populates="products")
    specifications = relationship(
        "SpecificationType",
        back_populates="product",
        cascade="all, delete"
    )

    descriptions = relationship(
        "Description",
        back_populates="product",
        cascade="all, delete"
    )

    questions = relationship(
        "Question",
        back_populates="product",
        cascade="all, delete"
    )

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete"
    )
    image_groups = relationship(
        "ImageGroup",
        back_populates="product",
        cascade="all, delete"
    )


    videos = relationship(
        'ProductVideos',
        back_populates='product',
        cascade='all, delete'
    )
    
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete")
    tags = relationship(
        "Tag",
        secondary="product_tags",
        back_populates="products"
    )
    badges = relationship("Badge", secondary="product_badges", back_populates="products")

# ===========================
# Related Products Table
# Example: A laptop product might have related products such as laptop bags, external hard drives, or other laptops with similar specifications. Each related product is linked to a specific product. This allows customers to easily find complementary products or alternatives when viewing a product.'''
# ===========================
class RelatedProduct(BaseModel):
    '''
    The RelatedProduct table represents the relationships between products that are related to each other. For example, a laptop product might have related products such as laptop bags, external hard drives, or other laptops with similar specifications. Each related product is linked to a specific product. This allows customers to easily find complementary products or alternatives when viewing a product.'''
    __tablename__ = "related_products"

    product_id = Column(Integer, ForeignKey("products.id"))
    related_product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        foreign_keys=[product_id],
        backref="related_to"
    )
    related_product = relationship(
        "Product",
        foreign_keys=[related_product_id],
        backref="related_from"
    )


# ===========================
# Product Brand Table
# Example: Apple, Samsung, Dell
# ===========================
class Brand(BaseModel):
    '''
    The Brand table represents the different brands of products available in the store. Each brand can have multiple products associated with it. For example, if the store sells laptops, there might be brands like Apple, Samsung, Dell, etc. Each product can be linked to a specific brand, allowing customers to filter products by brand and providing additional information about the product's manufacturer.'''
    __tablename__ = "brands"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String(255))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    website_url = Column(String(255))

    # Relationships
    products = relationship(
        "Product",
        back_populates="brand_table",
        cascade="all, delete"
    )

# =========================
# Product Category Table
# Example: Electronics, Clothing, Home Appliances
# =========================
class Category(BaseModel):
    '''
    The Category table represents the different categories of products available in the store. Each category can have multiple products associated with it. For example, there might be categories like Electronics, Clothing, Home Appliances, etc. Each product can be linked to a specific category, allowing customers to filter products by category and providing additional information about the type of product.'''
    __tablename__ = "categories"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    logo_url = Column(String(255))

    # Relationships
    products = relationship(
        "Product",
        back_populates="cat",
        cascade="all, delete"
    )
    parent = relationship("Category", remote_side="Category.id", backref="subcategories")



# =========================
# Inventory Summary Table
# Example: Total stock available, number of variants in stock, number of variants out of stock
# =========================
class InventorySummary(BaseModel):
    '''
    The InventorySummary table provides a summary of the inventory for each product. It includes information such as the total stock available, the number of variants in stock, and the number of variants out of stock. This table can be used to quickly assess the inventory status of each product and make informed decisions about restocking and inventory management. Each inventory summary is linked to a specific product.'''
    __tablename__ = "inventory_summaries"

    product_id = Column(Integer, ForeignKey("products.id"))

    available = Column(Integer, default=0)
    reserved = Column(Integer, default=0)
    incoming = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)

    # Relationships
    product = relationship(
        "Product",
        back_populates="inventory_summary"
    )



# =========================
# Specification Type Table
# Example:
# RAM, Storage, Color
# =========================
class SpecificationType(BaseModel):
    '''
    Specification types represent the categories of specifications for a product. For example, for a laptop product, specification types might include RAM, Storage, Color, etc. Each specification type can have multiple values (e.g., 8GB, 16GB for RAM; 256GB, 512GB for Storage; Red, Blue for Color).'''
    __tablename__ = "specification_types"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String(100), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="specifications"
    )

    specification_values = relationship(
        "SpecificationValue",
        back_populates="specification_type",
        cascade="all, delete"
    )


# =========================
# Specification Value Table
# Example:
# 8GB, 256GB, Black
# =========================
class SpecificationValue(BaseModel):
    '''
    Specification values represent the specific values for each specification type. For example, if the specification type is RAM, the specification values might be 8GB, 16GB, etc. If the specification type is Color, the specification values might be Red, Blue, etc. Each specification value is linked to a specific specification type.'''
    __tablename__ = "specification_values"

    key = Column(String(100), nullable=False)

    value = Column(String(255), nullable=False)

    specification_type_id = Column(
        Integer,
        ForeignKey("specification_types.id")
    )

    # Relationships
    specification_type = relationship(
        "SpecificationType",
        back_populates="specification_values"
    )


# =========================
# Product Description Table
# =========================
class Description(BaseModel):
    '''
    Product descriptions provide detailed information about the product. This can include multiple sections, each with its own title and text. For example, a laptop product might have descriptions for "Overview", "Technical Specifications", "Features", etc. Each description is linked to a specific product.'''
    __tablename__ = "descriptions"

    title = Column(String(255))

    text = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="descriptions"
    )


# =========================
# Product Question Table
# =========================
class Question(BaseModel):
    '''
    Product questions allow customers to ask questions about the product, and for the store to provide answers. Each question is linked to a specific product and can have an answer provided by the store. For example, a customer might ask "Does this laptop have a backlit keyboard?" and the store can answer "Yes, it does." Each question is linked to a specific product.'''
    __tablename__ = "questions"

    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    question = Column(Text)

    answer = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="questions"
    )


# =========================
# Product Review Table
# =========================
class Review(BaseModel):
    '''
    Product reviews allow customers to rate and review the product. Each review is linked to a specific product and can have a rating (e.g., 1-5 stars) and a written review. For example, a customer might rate a laptop 5 stars and write "Great laptop for gaming!"'''
    __tablename__ = "reviews"
    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    star = Column(Integer)

    review = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="reviews"
    )


# =========================
# product compare table
# =========================
class CompareItem(Base):
    '''
    The CompareItem table allows users to add products to a comparison list. Each entry in this table represents a product that a user has added for comparison. This can be used to display a side-by-side comparison of product features, specifications, and prices for the products that the user is interested in comparing. Each compare item is linked to a specific user and a specific product.'''
    __tablename__ = "compare_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=func.now())
    # Relationships
    product = relationship("Product")   
    user = relationship("User")


# =========================
# Product SEO Table
# example: Meta title, meta description, meta keywords
# =========================
class ProductSEO(BaseModel):
    '''
    The ProductSEO table stores SEO-related information for each product. This includes fields such as meta title, meta description, and meta keywords, which are used to optimize the product's visibility in search engine results. Each SEO entry is linked to a specific product, allowing for customized SEO settings for each product in the store.'''
    __tablename__ = "product_seo"

    product_id = Column(Integer, ForeignKey("products.id"))

    meta_title = Column(String(255))
    meta_description = Column(Text)
    canonical_url = Column(String(255))
    og_image = Column(String(255))
    no_index = Column(Boolean, default=False)

    # Relationships
    product = relationship(
        "Product",
        back_populates="seo"
    )


# =========================
# Product SEO Keyword Table
# example: laptop, gaming laptop, 16GB RAM laptop
# =========================

class SEOKeyword(BaseModel):
    '''
    The SEOKeyword table stores individual SEO keywords for each product. These keywords can be used to further optimize the product's visibility in search engine results. Each keyword is linked to a specific product, allowing for a list of relevant keywords that can help improve the product's search ranking.'''
    __tablename__ = "seo_keywords"

    product_id = Column(Integer, ForeignKey("products.id"))

    keyword = Column(String(255))

    # Relationships
    product = relationship(
        "Product",
        back_populates="seo_keywords"
    )


# =========================
# Product Search Keyword Table
# example: laptop, gaming laptop, 16GB RAM laptop
# =========================


class SearchKeyword(BaseModel):
    '''
    The SearchKeyword table stores keywords that customers have used to search for products. This information can be used to analyze search trends and optimize product listings based on popular search terms. Each search keyword is linked to a specific product, allowing for insights into which products are being searched for with specific keywords.'''
    __tablename__ = "search_keywords"

    product_id = Column(Integer, ForeignKey("products.id"))

    keyword = Column(String(255))

    # Relationships
    product = relationship(
        "Product",
        back_populates="search_keywords"
    )
