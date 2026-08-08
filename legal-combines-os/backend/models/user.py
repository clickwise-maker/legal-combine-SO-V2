"""
User Model — Authentication, Authorization, OTP
"""


import uuid
from datetime import datetime, timedelta
from enum import Enum as PyEnum


from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from passlib.context import CryptContext


from ..utils.database import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, PyEnum):
    USER = "user"
    LAWYER = "lawyer"
    TYPIST = "typist"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # OTP fields
    otp = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    otp_verified = Column(Boolean, default=False)


    # Relationships
    lawyer_profile = relationship("LawyerProfile", back_populates="user", uselist=False)
    typist_profile = relationship("TypistProfile", back_populates="user", uselist=False)
    documents = relationship("Document", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    bookings = relationship("Booking", back_populates="user")


    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = pwd_context.hash(password)


    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(password, self.hashed_password)


    def generate_otp(self, length: int = 6) -> str:
        """Generate and store OTP"""
        import random
        otp = ''.join(random.choices('0123456789', k=length))
        self.otp = otp
        self.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
        self.otp_verified = False
        return otp


    def verify_otp(self, otp: str) -> bool:
        """Verify OTP"""
        if not self.otp or not self.otp_expires_at or self.otp_expires_at < datetime.utcnow():
            return False
        if self.otp == otp:
            self.otp_verified = True
            self.is_verified = True
            return True
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.is_locked = True
        return False


    def increment_failed_attempts(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.is_locked = True


    def reset_failed_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0


    def __repr__(self):
        return f"<User {self.email}>"
