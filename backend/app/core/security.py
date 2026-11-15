from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.database import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.model_database.users.user import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()

# HASHED PASSWORD
password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)


# CREATE JSON WEB TOKEN
def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt

# VERIFY TOKEN
def verify_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None

# GET CURRENT USER
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = credentials.credentials

    user_id = verify_access_token(token)

    if not user_id:
        raise credentials_exception

    query = select(User).options(
        selectinload(User.roles)
        ).where(User.id == int(user_id))

    result = await db.execute(query)

    current_user = result.scalar_one_or_none()

    if current_user is None or not current_user.is_active:
        raise credentials_exception

    return current_user


# REQUIRE_ROLE
def require_role(role_name: str):

    async def check_role(current_user: User = Depends(get_current_user)):

        user_roles = [role.name for role in current_user.roles]

        if role_name not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )

        return current_user

    return check_role

