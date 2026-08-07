import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pyotp
from jose import JWTError, jwt

from backend.models.user import User, UserRole


class JWTConfig:
    """JWT configuration settings."""

    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    OTP_TOKEN_EXPIRE_MINUTES = 5


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    OTP = "otp"


class JWTError(Exception):
    """Custom JWT error for token validation failures."""

    pass


class JWTManager:
    """Handles JWT token generation and validation."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.config = JWTConfig()

    def create_access_token(
        self, user: User, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT access token for authenticated user."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "type": TokenType.ACCESS,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.config.ALGORITHM)

    def create_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token for token renewal."""
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": user.id,
            "type": TokenType.REFRESH,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.config.ALGORITHM)

    def create_otp_token(self, user: User) -> Tuple[str, str]:
        """Generate OTP secret and OTP verification token."""
        otp_secret = pyotp.random_base32()
        expire = datetime.utcnow() + timedelta(
            minutes=self.config.OTP_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": user.id,
            "otp_secret": otp_secret,
            "type": TokenType.OTP,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.config.ALGORITHM)
        return otp_secret, token

    def verify_token(
        self, token: str, expected_type: str = TokenType.ACCESS
    ) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.config.ALGORITHM]
            )

            if payload.get("type") != expected_type:
                raise JWTError(f"Invalid token type: expected {expected_type}")

            return payload

        except JWTError as e:
            raise JWTError(f"Token validation failed: {str(e)}")

    def decode_token_unsafe(self, token: str) -> dict:
        """Decode token without verification (for debugging only)."""
        return jwt.decode(
            token, self.secret_key, algorithms=[self.config.ALGORITHM], options={"verify_signature": False}
        )

    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token from refresh token."""
        payload = self.verify_token(refresh_token, TokenType.REFRESH)
        return payload

    @staticmethod
    def generate_otp(secret: str) -> str:
        """Generate current OTP from secret."""
        totp = pyotp.TOTP(secret)
        return totp.now()

    @staticmethod
    def verify_otp(secret: str, otp: str) -> bool:
        """Verify OTP against secret."""
        totp = pyotp.TOTP(secret)
        return totp.verify(otp, valid_window=1)

    @staticmethod
    def get_otp_provisioning_uri(secret: str, email: str) -> str:
        """Get provisioning URI for authenticator apps."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name="Legal Combines OS")


class PasswordManager:
    """Secure password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        import bcrypt
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception:
            return False


def get_password_strength(password: str) -> dict:
    """Evaluate password strength."""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters")

    if len(password) >= 12:
        score += 1

    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
    else:
        feedback.append("Add special characters (!@#$%^&*)")

    strength_map = {
        0: "very_weak",
        1: "weak",
        2: "fair",
        3: "good",
        4: "strong",
        5: "very_strong",
        6: "excellent",
    }

    return {
        "score": score,
        "max_score": 6,
        "strength": strength_map.get(score, "unknown"),
        "feedback": feedback,
        "is_acceptable": score >= 3,
    }
