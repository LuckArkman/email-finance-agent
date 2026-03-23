from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.security import AuthHandler, SecurityDependencies

from app.schemas import UserRegister, UserResponse
from app.models import User, Tenant

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
auth_handler = AuthHandler()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Onboarding: Creates a new Tenant and a User associated with it.
    """
    # 1. Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system."
        )

    # 2. Create Tenant
    new_tenant = Tenant(name=user_in.tenant_name)
    db.add(new_tenant)
    await db.flush() # Get tenant ID

    # 3. Create User
    new_user = User(
        email=user_in.email,
        hashed_password=auth_handler.get_password_hash(user_in.password),
        tenant_id=new_tenant.id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/access-token")
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    Expects form-data: username and password.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not auth_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Issue JWT Token
    access_token = auth_handler.create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "tenant_id": user.tenant_id
    }

@router.get("/me")
async def read_users_me(current_user: User = Depends(SecurityDependencies.get_current_user)):
    """
    Test endpoint. Will only answer if a valid JWT token is passed in headers.
    Returns the current active user info.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active
    }
