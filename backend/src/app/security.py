from datetime import datetime, timedelta
from typing import Optional, Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import BaseAPIConfig
from app.models import User
from app.database import get_db

# Password hashing context using the robust BCrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Tells FastAPI where the client should fetch the token in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/access-token")

class AuthHandler:
    """
    Core handler for JWT Encoding/Decoding and Password Hashing.
    """
    def __init__(self):
        self.settings = BaseAPIConfig.get_settings()
        self.secret_key = self.settings.jwt_secret_key
        self.algorithm = self.settings.jwt_algorithm
        self.expire_minutes = self.settings.access_token_expire_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies if the plaintext password matches the stored bcrypt hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Returns the bcrypt hash for a new user password."""
        return pwd_context.hash(password)

    def create_access_token(self, subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a JWT Token containing the User ID (subject) and expiration claims.
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
            
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


class SecurityDependencies:
    """
    FastAPI Dependencies to inject secure contexts into routes.
    """
    @staticmethod
    async def get_current_user(
        db: AsyncSession = Depends(get_db), 
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """
        Validates the parsed Token from the Authorization header,
        extracts the User ID, checks if user exists in DB, and returns it.
        Raises 401 Unauthorized otherwise.
        """
        settings = BaseAPIConfig.get_settings()
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        # Verify user actually exists in the transactional graph
        result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
        user = result.scalars().first()
        
        if user is None:
            raise credentials_exception
            
        # Define the context variable globally for this request so 
        # all subsequent database queries are locked to this tenant
        from app.tenant import set_current_tenant
        set_current_tenant(user.tenant_id)
            
        return user
