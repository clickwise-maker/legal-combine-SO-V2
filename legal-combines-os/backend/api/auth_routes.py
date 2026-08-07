import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator

from backend.models.user import User, UserRole, UserStatus, OTPAttempt
from backend.utils.jwt_utils import (
    JWTManager,
    PasswordManager,
    get_password_strength,
    JWTError,
)


router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: Optional[str] = "client"

    @validator("password")
    def validate_password_strength(cls, v):
        strength = get_password_strength(v)
        if not strength["is_acceptable"]:
            raise ValueError(
                f"Password too weak: {'; '.join(strength['feedback'])}"
            )
        return v

    @validator("first_name", "last_name")
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip()

    @validator("role")
    def validate_role(cls, v):
        try:
            UserRole(v)
        except ValueError:
            raise ValueError(f"Invalid role: {v}. Must be one of: {[r.value for r in UserRole]}")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPVerifyRequest(BaseModel):
    user_id: str
    otp: str


class OTPInitRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

    @validator("new_password")
    def validate_password_strength(cls, v):
        strength = get_password_strength(v)
        if not strength["is_acceptable"]:
            raise ValueError(
                f"Password too weak: {'; '.join(strength['feedback'])}"
            )
        return v


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    role: str
    status: str
    otp_verified: bool


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class OTPResponse(BaseModel):
    message: str
    otp_sent: bool
    method: str = "email"


MOCK_USERS_DB = {}
MOCK_OTP_DB = {}
MOCK_OTP_ATTEMPTS = {}

JWT_SECRET = "your-secret-key-change-in-production"
jwt_manager = JWTManager(JWT_SECRET)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        payload = jwt_manager.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id not in MOCK_USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        return MOCK_USERS_DB[user_id]
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


def send_otp_email(email: str, otp: str) -> None:
    """Background task to send OTP via email."""
    print(f"[EMAIL] Sending OTP {otp} to {email}")


def send_welcome_email(email: str, first_name: str) -> None:
    """Background task to send welcome email."""
    print(f"[EMAIL] Sending welcome email to {email}")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    """Register a new user account."""
    email = request.email.lower().strip()

    if email in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    password_hash = PasswordManager.hash_password(request.password)

    user = User(
        email=email,
        password_hash=password_hash,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
        role=UserRole(request.role),
        status=UserStatus.PENDING,
    )

    MOCK_USERS_DB[email] = user

    otp_secret, otp_token = jwt_manager.create_otp_token(user)
    MOCK_OTP_DB[user.id] = {
        "secret": otp_secret,
        "expires": datetime.utcnow() + timedelta(minutes=5),
        "verified": False,
    }

    otp_code = JWTManager.generate_otp(otp_secret)
    background_tasks.add_task(send_otp_email, email, otp_code)
    background_tasks.add_task(send_welcome_email, email, user.first_name)

    access_token = jwt_manager.create_access_token(user)
    refresh_token = jwt_manager.create_refresh_token(user)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,
        user=user.to_dict(),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate user and return tokens."""
    email = request.email.lower().strip()

    if email not in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = MOCK_USERS_DB[email]

    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to too many failed attempts",
        )

    if not PasswordManager.verify_password(request.password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()

    access_token = jwt_manager.create_access_token(user)
    refresh_token = jwt_manager.create_refresh_token(user)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,
        user=user.to_dict(),
    )


@router.post("/otp/init", response_model=OTPResponse)
async def init_otp(request: OTPInitRequest, background_tasks: BackgroundTasks):
    """Initialize OTP setup for a user."""
    email = request.email.lower().strip()

    if email not in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = MOCK_USERS_DB[email]
    otp_secret, otp_token = jwt_manager.create_otp_token(user)
    
    MOCK_OTP_DB[user.id] = {
        "secret": otp_secret,
        "expires": datetime.utcnow() + timedelta(minutes=5),
        "verified": False,
    }

    otp_code = JWTManager.generate_otp(otp_secret)
    background_tasks.add_task(send_otp_email, email, otp_code)

    return OTPResponse(
        message="OTP sent to your email",
        otp_sent=True,
        method="email",
    )


@router.post("/otp/verify", response_model=MessageResponse)
async def verify_otp(request: OTPVerifyRequest):
    """Verify OTP code and activate user account."""
    user_id = request.user_id

    if user_id not in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_id in MOCK_OTP_ATTEMPTS:
        attempt = MOCK_OTP_ATTEMPTS[user_id]
        if attempt.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Too many failed attempts. Please try again later.",
            )

    if user_id not in MOCK_OTP_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not initialized. Please request a new OTP.",
        )

    otp_data = MOCK_OTP_DB[user_id]

    if datetime.utcnow() > otp_data["expires"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )

    user = MOCK_USERS_DB[user_id]
    
    if not JWTManager.verify_otp(otp_data["secret"], request.otp):
        if user_id not in MOCK_OTP_ATTEMPTS:
            MOCK_OTP_ATTEMPTS[user_id] = OTPAttempt(user_id=user_id)
        
        MOCK_OTP_ATTEMPTS[user_id].record_failure()
        
        if MOCK_OTP_ATTEMPTS[user_id].is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Too many failed attempts. Account locked for 15 minutes.",
            )
        
        remaining = OTPAttempt.MAX_ATTEMPTS - MOCK_OTP_ATTEMPTS[user_id].attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining} attempts remaining.",
        )

    user.otp_verified = True
    user.otp_secret = otp_data["secret"]
    user.status = UserStatus.ACTIVE
    otp_data["verified"] = True
    
    if user_id in MOCK_OTP_ATTEMPTS:
        MOCK_OTP_ATTEMPTS[user_id].reset()

    return MessageResponse(
        message="OTP verified successfully",
        detail="Your account is now active",
    )


@router.post("/otp/resend", response_model=OTPResponse)
async def resend_otp(email: OTPInitRequest, background_tasks: BackgroundTasks):
    """Resend OTP to user's email."""
    return await init_otp(email, background_tasks)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        payload = jwt_manager.verify_token(
            request.refresh_token, expected_type="refresh"
        )
        user_id = payload.get("sub")

        if user_id not in MOCK_USERS_DB:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        user = MOCK_USERS_DB[user_id]
        access_token = jwt_manager.create_access_token(user)
        refresh_token = jwt_manager.create_refresh_token(user)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,
            user=user.to_dict(),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(user: User = Depends(get_current_user)):
    """Logout user (invalidate session)."""
    return MessageResponse(message="Successfully logged out")


@router.post("/password/reset", response_model=MessageResponse)
async def request_password_reset(
    request: PasswordResetRequest, background_tasks: BackgroundTasks
):
    """Request password reset email."""
    email = request.email.lower().strip()

    if email not in MOCK_USERS_DB:
        return MessageResponse(
            message="If the email exists, a reset link has been sent",
            detail=None,
        )

    user = MOCK_USERS_DB[email]
    reset_token = jwt_manager.create_access_token(
        user, expires_delta=timedelta(minutes=15)
    )

    background_tasks.add_task(
        send_otp_email, email, f"Password reset token: {reset_token[:8]}..."
    )

    return MessageResponse(
        message="If the email exists, a reset link has been sent",
        detail=None,
    )


@router.post("/password/change", response_model=MessageResponse)
async def change_password(
    request: PasswordChangeRequest,
    user: User = Depends(get_current_user),
):
    """Change user's password."""
    if not PasswordManager.verify_password(
        request.old_password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.password_hash = PasswordManager.hash_password(request.new_password)
    user.updated_at = datetime.utcnow()

    return MessageResponse(
        message="Password changed successfully",
        detail="Please login again with your new password",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(**user.to_dict())


@router.get("/otp/setup-qr")
async def get_otp_setup_qr(user: User = Depends(get_current_user)):
    """Get QR code for authenticator app setup."""
    if not user.otp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please initialize OTP first",
        )

    uri = JWTManager.get_otp_provisioning_uri(user.otp_secret, user.email)

    return {
        "uri": uri,
        "secret": user.otp_secret,
        "email": user.email,
    }
