from pydantic import BaseModel

from app.schemas.product import ProductResponse
from app.schemas.category import CategoryResponse
from app.schemas.brand import BrandResponse
from app.schemas.product_variant import ProductVariantResponse
from app.schemas.product_image import ProductImageResponse
from app.schemas.product_attribute import ProductAttributeResponse

class ProductCatalogDetailResponse(ProductResponse):

    category: CategoryResponse
    brand: BrandResponse
    variants: list[ProductVariantResponse]
    images: list[ProductImageResponse]
    attributes: list[ProductAttributeResponse]