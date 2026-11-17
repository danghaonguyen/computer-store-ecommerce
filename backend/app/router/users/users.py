from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.model_database.users.user import User
from app.model_database.users.role import Role
from app.schemas.user import UserResponse, UserUpdate, UserStatusUpdate, UserRolesUpdate
from app.core.security import require_role


router = APIRouter(prefix="/users", tags=["Users"])

# GET USER
@router.get("", response_model=list[UserResponse])
async def get_user(db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(require_role("ADMIN"))
                   ):

    query = select(User)

    data = await db.execute(query)

    user = data.scalars().all()

    return user

# GET USER_ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_id(user_id: int, db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_role("ADMIN"))
                      ):

    query = select(User).where(User.id == user_id)

    data = await db.execute(query)

    user = data.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    return user

# UPATE USER
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate,
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_role("ADMIN"))
                      ):

    query = select(User).where(User.id == user_id)

    data = await db.execute(query)

    user = data.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


# UPDATE STATUS USER
@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(user_id: int, user_data: UserStatusUpdate, 
                             db: AsyncSession = Depends(get_db), 
                             current_user: User = Depends(require_role("ADMIN"))
                             ):

    query = select(User).where(User.id == user_id)

    data = await db.execute(query)

    user = data.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return user

# UPDATE ROLES USER
@router.patch("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(user_id: int, user_data: UserRolesUpdate, 
                            db: AsyncSession = Depends(get_db), 
                            current_user: User = Depends(require_role("ADMIN"))
                            ):

    query = select(User).where(User.id == user_id)

    data = await db.execute(query)

    user = data.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    query_role = select(Role).where(Role.name.in_(user_data.roles))

    result = await db.execute(query_role)

    roles = result.scalars().all()

    if len(roles) != len(set(user_data.roles)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="One or more roles not found")

    user.roles = roles

    await db.commit()
    await db.refresh(user)

    return user