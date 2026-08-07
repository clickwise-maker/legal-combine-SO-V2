"""
JWT Utilities — Token Generation, OTP, Password Hashing
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import Config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTUtils:
    """JWT token utilities"""

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            return jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        except JWTError:
            return {}

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        payload = JWTUtils.decode_token(token)
        if not payload:
            return None
        if payload.get("exp") < datetime.utcnow().timestamp():
            return None
        return payload


def create_otp(length: int = 6) -> str:
    """Generate numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)
