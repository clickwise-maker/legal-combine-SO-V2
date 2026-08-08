"""
Authentication Routes — JWT, OTP, Login/Register
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field

from ..models import User, UserRole
from ..utils.database import get_db
from ..utils.jwt_utils import JWTUtils, create_otp, hash_password, verify_password
from ..utils.security import rate_limit, Security
from ..config import Config

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    role: str = "user"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OTPRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPGenerateRequest(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=TokenResponse)
@rate_limit(requests=10, period=60)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        id=uuid.uuid4(), email=request.email, name=request.name, phone=request.phone,
        role=UserRole(request.role) if request.role in [r.value for r in UserRole] else UserRole.USER,
        is_verified=False,
    )
    user.set_password(request.password)
    user.generate_otp()
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = JWTUtils.create_access_token(token_data)
    refresh_token = JWTUtils.create_refresh_token(token_data)
    
    return {
        "access_token": access_token, "refresh_token": refresh_token,
        "user_id": str(user.id), "email": user.email, "role": user.role.value,
    }

@router.post("/login", response_model=TokenResponse)
@rate_limit(requests=20, period=60)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    if user.is_locked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is locked")
    
    if not user.verify_password(request.password):
        user.increment_failed_attempts()
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    user.reset_failed_attempts()
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    return {
        "access_token": JWTUtils.create_access_token(token_data),
        "refresh_token": JWTUtils.create_refresh_token(token_data),
        "user_id": str(user.id), "email": user.email, "role": user.role.value,
    }

@router.post("/otp/generate")
@rate_limit(requests=5, period=60)
async def generate_otp(request: OTPGenerateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.generate_otp()
    db.commit()
    return {"message": "OTP sent to your email", "expires_in": f"{Config.OTP_EXPIRE_MINUTES} minutes"}

@router.post("/otp/verify")
async def verify_otp(request: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not user.verify_otp(request.otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")
    db.commit()
    return {"message": "OTP verified successfully"}

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = JWTUtils.decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    return {"access_token": JWTUtils.create_access_token(token_data), "token_type": "bearer"}

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = JWTUtils.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": str(user.id), "email": user.email, "name": user.name,
        "role": user.role.value, "is_verified": user.is_verified,
        "is_active": user.is_active, "last_login": user.last_login_at,
    }

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}
