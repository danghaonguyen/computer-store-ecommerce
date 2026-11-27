from datetime import datetime
from pydantic import BaseModel, Field


# CREATE REVIEW
class ReviewImageCreate(BaseModel):

    image_url: str = Field(min_length=1, max_length=500)


class ReviewCreate(BaseModel):

    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    images: list[ReviewImageCreate] = Field(default_factory=list)


# OUTPUT REVIEW
class ReivewImageResponse(BaseModel):

    id: int
    review_id: int
    image_url: str
    created_at: datetime

    model_config = {"from_attributes" : True}


class ReviewResponse(BaseModel):

    id: int
    user_id: int
    product_id: int
    order_id: int | None
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime
    images: list[ReivewImageResponse]

    model_config = {"from_attributes" : True}


# UPDATE REVIEW
class ReviewUpdate(BaseModel):

    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None

