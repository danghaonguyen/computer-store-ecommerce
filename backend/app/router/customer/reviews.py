from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.security import require_role
from app.database.database import get_db

from app.model_database.users.user import User
from app.model_database.products.product import Product
from app.model_database.products.product_variant import ProductVariant
from app.model_database.orders.order import Order
from app.model_database.orders.order_item import OrderItem
from app.model_database.reviews.review import Review
from app.model_database.reviews.review_image import ReviewImage

from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse


customer = APIRouter(tags=["Reivews - Customer"])


# CUSTOMER ============================
# CREATE REVIEW
@customer.post("/reivews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review_data: ReviewCreate, 
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("CUSTOMER"))
                        ):

    # Check product
    query = select(Product).where(Product.id == review_data.product_id)

    product_result = await db.execute(query)

    product_id = product_result.scalar_one_or_none()

    if product_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")


    # Check deliverd order containing product
    query = select(Order.id).join(OrderItem, 
                                  OrderItem.order_id == Order.id).join(
                                      ProductVariant, ProductVariant.id == OrderItem.product_variant_id
                                  ).where(
                                      Order.user_id == current_user.id,
                                      Order.status == "DELIVERED",
                                      ProductVariant.product_id == review_data.product_id
                                  ).limit(1)

    order_result = await db.execute(query)

    order_id = order_result.scalar_one_or_none()

    if order_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only review products from delivered orders")


    # Check existing review
    query = select(Review.id).where(Review.user_id == current_user.id,
                                    Review.product_id == review_data.product_id)

    result = await db.execute(query)

    existing_reivew = result.scalar_one_or_none()

    if existing_reivew is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="You have already reviewed this product")

    # Create review
    new_review = Review(

        user_id=current_user.id,
        product_id=review_data.product_id,
        order_id=order_id,
        rating=review_data.rating,
        comment=review_data.comment,
        images=[

            ReviewImage(image_url=image.image_url)
            for image in review_data.images
        ]
    )

    try:
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review, attribute_names=["images"])

    except Exception:
        await db.rollback()
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to created review")

    return new_review

# SEE REVIEWS PRODUCT
@customer.get("/product/{product_id}/reviews", response_model=list[ReviewResponse])
async def see_reivew(product_id: int, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(require_role("CUSTOMER"))
                     ):

    query = select(Product.id).where(Product.id == product_id)

    product_result = await db.execute(query)

    product_id = product_result.scalar_one()

    if product_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found")

    # Get reviews
    query = select(Review).options(

        selectinload(Review.images)

    ).where(Review.product_id == product_id).order_by(Review.created_at.desc())

    result = await db.execute(query)

    reviews = result.scalars().all()

    return reviews

# SEE VIEWS ME
@customer.get("/me", response_model=list[ReviewResponse])
async def see_my_reviews(db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(require_role("CUSTOMER"))
                         ):

    query = select(Review).options(

        selectinload(Review.images)

    ).where(Review.user_id == current_user.id).order_by(Review.created_at.desc())

    result = await db.execute(query)

    reviews = result.scalars().all()

    return reviews


# UPDATE MY VIEW
@customer.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, review_data: ReviewUpdate,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("CUSTOMER"))
                        ):

    # Check review ownership
    query = select(Review).options(

        selectinload(Review.images)

    ).where(Review.id == review_id, Review.user_id == current_user.id)

    result = await db.execute(query)

    review = result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found")

    update_data = review_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No data provided for update")

    if "rating" in update_data and update_data["rating"] is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Rating cannot be null")

    for key, value in update_data.items():
        setattr(review, key, value)

    try:
        await db.commit()

        # load time update_at
        await db.refresh(review)

        # load relationship images
        await db.refresh(review, attribute_names=["images"])

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update review")

    return review
    

# DELETE MY VIEW
@customer.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("CUSTOMER"))
                        ):

    # Check review ownership
    query = select(Review).where(Review.id == review_id,
                                 Review.user_id == current_user.id)


    result = await db.execute(query)

    review = result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found")

    try:
        await db.delete(review)
        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to delete review")

    return {"message" : " Review deleted successfully"}