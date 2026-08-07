from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class UserRole(str, Enum):
    ADMIN = "admin"
    LAWYER = "lawyer"
    CLIENT = "client"
    GUEST = "guest"


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class User:
    """User model for Legal Combines OS authentication system."""

    def __init__(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.CLIENT,
        phone: Optional[str] = None,
        user_id: Optional[str] = None,
        status: UserStatus = UserStatus.PENDING,
        otp_secret: Optional[str] = None,
        otp_verified: bool = False,
        otp_expiry: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        failed_login_attempts: int = 0,
        locked_until: Optional[datetime] = None,
    ):
        self.id = user_id or str(uuid.uuid4())
        self.email = email.lower().strip()
        self.password_hash = password_hash
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.role = role
        self.phone = phone
        self.status = status
        self.otp_secret = otp_secret
        self.otp_verified = otp_verified
        self.otp_expiry = otp_expiry
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary for API responses."""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role.value,
            "phone": self.phone,
            "status": self.status.value,
            "otp_verified": self.otp_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        if include_sensitive:
            data["otp_secret"] = self.otp_secret
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user instance from dictionary."""
        return cls(
            user_id=data.get("id"),
            email=data["email"],
            password_hash=data["password_hash"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=UserRole(data.get("role", "client")),
            phone=data.get("phone"),
            status=UserStatus(data.get("status", "pending")),
            otp_secret=data.get("otp_secret"),
            otp_verified=data.get("otp_verified", False),
            otp_expiry=data.get("otp_expiry"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            last_login=data.get("last_login"),
            failed_login_attempts=data.get("failed_login_attempts", 0),
            locked_until=data.get("locked_until"),
        )


class OTPAttempt:
    """Track OTP verification attempts for rate limiting."""

    MAX_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    def __init__(
        self,
        user_id: str,
        attempts: int = 0,
        locked_until: Optional[datetime] = None,
        last_attempt: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.attempts = attempts
        self.locked_until = locked_until
        self.last_attempt = last_attempt

    @property
    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_failure(self) -> None:
        """Record a failed OTP attempt."""
        self.attempts += 1
        self.last_attempt = datetime.utcnow()
        if self.attempts >= self.MAX_ATTEMPTS:
            self.locked_until = datetime.utcnow().replace(
                minute=datetime.utcnow().minute + self.LOCKOUT_MINUTES
            )

    def reset(self) -> None:
        """Reset attempts after successful verification."""
        self.attempts = 0
        self.locked_until = None
        self.last_attempt = None
