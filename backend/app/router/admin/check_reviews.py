from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.core.security import require_role

from app.model_database.users.user import User
from app.model_database.reviews.review import Review

from app.schemas.review import ReviewResponse


admin = APIRouter(prefix="/admin/reviews", tags=["Reviews Management"])


# GET ALL REVIEWS
@admin.get("", response_model=list[ReviewResponse])
async def get_all_reviews(db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(require_role("ADMIN"))
                          ):

    query = select(Review).options(

        selectinload(Review.images)

    ).order_by(Review.created_at.desc())

    result = await db.execute(query)

    reviews = result.scalars().all()

    return reviews

# GET REVIEW DETAIL
@admin.get("/{review_id}", response_model=ReviewResponse)
async def get_review_detail(review_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(require_role("ADMIN"))
                            ):

    query = select(Review).options(

        selectinload(Review.images)

    ).where(Review.id == review_id)

    result = await db.execute(query)

    review = result.scalar_one_or_none()

    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found")

    return review


# DELETE REVIEW
@admin.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(require_role("ADMIN"))
                        ):

    query = select(Review).where(Review.id == review_id)

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

    return {"message" : "Review deleted successfully"}