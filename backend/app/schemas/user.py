from pydantic import EmailStr, BaseModel, Field

# REGISTER USER
class UserCreate(BaseModel):

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)
    full_name: str = Field(min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)

# OUTPUT USER
class UserResponse(BaseModel):

    id: int
    username: str
    email: EmailStr
    full_name: str
    phone: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


# LOGIN USER
class UserLogin(BaseModel):

    email: EmailStr
    password: str



# UPDATE USER
class UserUpdate(BaseModel):

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)


# UPDATE STATUS USER
class UserStatusUpdate(BaseModel):

    is_active: bool


# UPDATE ROLES USER
class UserRolesUpdate(BaseModel):

    roles: list[str]
    