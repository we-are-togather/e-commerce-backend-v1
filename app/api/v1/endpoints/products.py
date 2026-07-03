from fastapi import APIRouter, Depends, Query
# from sqlalchemy.orm import Session
# from app.core.outh2 import get_current_user
# from app.db.base import get_db
# from app.schemas.base import BaseResponse
# from app.schemas.product import (ProductColorSchema, ProductListItemSchema, 
#                                  ProductCreateResponseSchema,
#                                  ProductListResponseSchema,
#                                  ProductListItemSchema,
#                                  ProductSchema,
#                                  ReviewsSchema,
#                                  QuestionSchema,
#                                  Variant,

#                                  ProductDetailResponseSchema,
#                                  ProductColorReponseSchema,
#                                  VariantChangeResponseSchema,
#                                 VariantChangeRequestSchema,
#                                 VariantAttributeSchema
# )
# from app.models.product import (
#     Product,
#     ProductVariantAttribute,
#     ProductVariantImage, 
#     Review, 
#     Question, 
#     ProductVariant,
#     AttributeValue

# )
# from app.schemas.user import User

router = APIRouter(
    tags=['products']
)


# @router.get("/{category}/{brand}", response_model=ProductListResponseSchema)
# def get_products(
#     category: str = None,
#     brand: str = None,
#     min_price: float = None,
#     max_price: float = None,
#     weight: float = None,
#     size: str = None,

#     page: int = Query(1, ge=1),
#     limit: int = Query(10, ge=1, le=100),

#     sort_by: str = "created_at",
#     sort_order: str = "desc",

#     db: Session = Depends(get_db)
# ):
    
#     query = db.query(Product)

#     if category:
#         query = query.filter(Product.category == category)
#     if brand:
#         query = query.filter(Product.brand == brand)
#     if min_price is not None:
#         query = query.filter(Product.price >= min_price)
#     if max_price is not None:
#         query = query.filter(Product.price <= max_price)
#     if weight is not None:
#         query = query.filter(Product.weight == weight)
#     if size:
#         query = query.filter(Product.size == size)

#     total = query.count()

#     if sort_order.lower() == "desc":
#         query = query.order_by(getattr(Product, sort_by).desc())
#     else:
#         query = query.order_by(getattr(Product, sort_by))

#     products = query.offset((page - 1) * limit).limit(limit).all()
#     product_list = []
#     for product in products:
#         product_list.append(
#             ProductListItemSchema(
#                 id=product.id,
#                 name=product.name,
#                 short_description=product.short_description.split("\n") if product.short_description else [],
#                 slug=product.slug,
#                 regular_price=product.variants[0].regular_price if product.variants else 0.0,
#                 price=product.variants[0].price if product.variants else 0.0
#             )
#         )

#     return ProductListResponseSchema(
#         status="200",
#         message="Products retrieved successfully",
#         lang="en",
#         data=product_list,
#         total=total,
#         page=page,
#         limit=limit
#     )


# @router.get("/{slug}", response_model=ProductDetailResponseSchema)
# def get_product_by_slug(slug: str,id: int,  db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == id).first()

#     if not product:
#         return ProductDetailResponseSchema(
#             status="404",
#             message="Product not found",
#             lang="en",
#             data=None
#         )
#     variants = []
#     default_variant = True
#     for var in product.variants:
#         attributes = db.query(ProductVariantAttribute).filter(ProductVariantAttribute.product_variant_id == var.id).all()
#         variant_attributes = []

#         for attr in attributes:
#             attribute_value = db.query(AttributeValue).filter(AttributeValue.id == attr.attribute_value_id).first()
#             variant_attributes.append(
#                 VariantAttributeSchema(
#                     variant_attribute_id=attr.id,
#                     variant_attribute_value_id=attr.attribute_value_id,

#                     variant_attribute_name=attribute_value.attribute.name,
#                     variant_attribute_value=attribute_value.value
#                 )

#             )
#         variants.append(
#             Variant(
#                 variant_id=var.id,
#                 is_default=True if default_variant else False,
#                 param=variant_attributes,
#                 price=var.price,
#                 regular_price=var.regular_price,
#                 stock=var.stock,
#                 color_name=var.color_name,
#                 image_url=var.images[0].image_url if var.images else None
#             )
#         )
#         default_variant = False


#     desc = {}
#     for d in product.descriptions:
#         desc[d.title] = d.text
    
#     specs = {}
#     for spec in product.specifications:
#         spec_values = {}
#         for value in spec.specification_values:
#             spec_values[value.key] = value.value
#         specs[spec.type] = spec_values
    
#     reviews = db.query(Review).filter(Review.product_id == product.id).all()
#     review_list = []
#     for review in reviews:
#         review_list.append(
#             ReviewsSchema(
#                 user_name=review.user.name,
#                 star=review.star,
#                 review_text=review.review_text,
#                 review_at=review.created_at
#             )
#         )

#     questions = db.query(Question).filter(Question.product_id == product.id).all()
#     question_list = []
#     for question in questions:
#         question_list.append(
#             QuestionSchema(
#                 user_name=question.user.name,
#                 question=question.question_text,
#                 asked_at=question.created_at,
#                 answer=question.answer

#             )
#         )

#     return ProductDetailResponseSchema(
#         status="200",
#         message="Product retrieved successfully",
#         lang="en",
#         data=ProductSchema(
#             id=product.id,
#             name=product.name,
#             short_description=product.short_description.split("\n") if product.short_description else [],
#             slug=product.slug,
#             regular_price=product.variants[0].regular_price if product.variants else 0.0,
#             price=product.variants[0].price if product.variants else 0.0,
#             description=desc,
#             specification=specs,
#             reviews=review_list,
#             questions=question_list,
#             variants=variants
#         )
#     )


# @router.get("/change-color")
# def change_color(
#     color_id: int = Query(..., description="The attribute value ID for the selected color which provide the image url for that color variant"),
#     db: Session = Depends(get_db)
# ):
#     image = db.query(ProductVariantImage).filter(ProductVariantImage.product_variant_id == color_id).first()
#     if not image:
#         return BaseResponse(
#             status="404",
#             message="Product variant image not found",
#             lang="en"
#         )
#     return ProductColorReponseSchema(
#         status="200",
#         message="Color options retrieved successfully",
#         lang="en",
#         data=
#             ProductColorSchema(
#                 color_name=image.image_url.split("/")[-1].split(".")[0],  # Assuming color name is part of the image filename
#                 image_url=image.image_url
#             )
        
#     )


# @router.get("variants/change-variant")
# def change_variant(
#     product_id:int,
#     variant_id: int,
#     variant_attribute_id: int = Query(..., description="The attribute value ID that determines the variant change. For example, if changing based on color, this would be the attribute value ID for the selected color."),
#     db: Session = Depends(get_db)
# ):

    
#     variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id, ProductVariant.product_id == product_id).first()
#     if not variant:
#         return BaseResponse(
#             status="404",
#             message="Variant not found",
#             lang="en"
#         )
#     attribut = db.query(AttributeValue).filter(AttributeValue.id == variant_attribute_id).first()
#     if not attribut:
#         return BaseResponse(
#             status="404",
#             message="Attribute value not found",
#             lang="en"
#         )
    
    
#     return VariantChangeResponseSchema(
#         status="200",
#         message="Variant changed successfully",
#         lang="en",
#         data=VariantChangeRequestSchema(
#             product_id=product_id,
#             variant_id=variant_id,
#             variant_attribute_id=variant_attribute_id,
#             price=variant.price,
#             regular_price=variant.regular_price,
#             stock=variant.stock
#         )
#     )


# # ============================================
# #      Ask question and submit review endpoints
# # ============================================

# @router.get("/ask-question/{product_id}")
# def ask_question(
#     product_id: int,
#     question: str = Query(..., min_length=5),
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         return BaseResponse(
#             status="404",
#             message="Product not found",
#             lang="en"
#         )
    
#     new_question = Question(
#         product_id=product_id,
#         user_id=user.id,
#         question_text=question
#     )
#     db.add(new_question)
#     db.commit()
#     db.refresh(new_question)

#     return BaseResponse(
#         status="200",
#         message="Question submitted successfully",
#         lang="en"
#     )

# @router.get("/submit-review/{product_id}")
# def submit_review(
#     product_id: int,
#     review_text: str = Query(..., min_length=10),
#     star: int = Query(..., ge=1, le=5),
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         return BaseResponse(
#             status="404",
#             message="Product not found",
#             lang="en"
#         )
    
#     new_review = Review(
#         product_id=product_id,
#         user_id=user.id,
#         review_text=review_text,
#         star=star
#     )
#     db.add(new_review)
#     db.commit()
#     db.refresh(new_review)

#     return BaseResponse(
#         status="200",
#         message="Review submitted successfully",
#         lang="en"
#     )

