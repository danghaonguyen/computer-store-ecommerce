from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from app.model_database.users.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user,
    require_role
    )
from app.model_database.users.role import Role

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ROUTER REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    query = select(User).where(or_(User.email == user_data.email,
                               User.username == user_data.username))

    data = await db.execute(query)

    exist_user = data.scalar_one_or_none()

    if exist_user:
        if exist_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    hashed_password = hash_password(user_data.password)

    new_user = user_data.model_dump(exclude=["password"])

    new_user["password_hash"] = hashed_password

    new_user = User(**new_user)

    customer_role = await db.execute(
        select(Role).where(Role.name == "CUSTOMER")
    )

    new_user.roles.append(customer_role.scalar_one())


    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                                    detail="Failed to register")

    return new_user    


# ROUTER LOGIN
@router.post("/login")
async def login_user(user_data: UserLogin, db: AsyncSession = Depends(get_db)):

    query = select(User).options(
        selectinload(User.roles)
        ).where(User.email == user_data.email)

    data = await db.execute(query)

    user = data.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account is disabled")

    access_token = create_access_token({"sub": str(user.id)})

    roles = [role.name for role in user.roles]

    return {"access_token": access_token, 
            "token_type": "bearer", 
            "roles": roles}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):

    return current_user


@router.get("/admin/test")
async def admin_test(current_user: User = Depends(require_role("ADMIN"))):

    return {
        "message" : "Welcome Admin",
        "username": current_user.username
    }

@router.get("/customer/test")
async def customer_test(
    current_user: User = Depends(require_role("CUSTOMER"))
):
    return {
        "message": "Welcome Customer",
        "username": current_user.username
    }