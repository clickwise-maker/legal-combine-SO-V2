"""
Lawyer Models — Profiles, Bookings, Reviews
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..utils.database import Base


class BookingStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class LawyerProfile(Base):
    __tablename__ = "lawyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    bar_council_id = Column(String(255), unique=True, nullable=False)
    specialization = Column(String(255), nullable=False)
    experience_years = Column(Integer, default=0)
    hourly_rate = Column(Float, default=0.0)
    fixed_fee = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    total_cases = Column(Integer, default=0)
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="lawyer_profile")
    bookings = relationship("Booking", back_populates="lawyer")
    reviews = relationship("Review", back_populates="lawyer")

    def update_rating(self):
        if self.reviews:
            avg = sum(r.rating for r in self.reviews) / len(self.reviews)
            self.rating = round(avg, 1)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "bar_council_id": self.bar_council_id,
            "specialization": self.specialization,
            "experience_years": self.experience_years,
            "hourly_rate": self.hourly_rate,
            "fixed_fee": self.fixed_fee,
            "location": self.location,
            "bio": self.bio,
            "is_verified": self.is_verified,
            "is_available": self.is_available,
            "rating": self.rating,
            "total_cases": self.total_cases,
            "total_bookings": self.total_bookings,
            "total_revenue": self.total_revenue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    duration_hours = Column(Float, default=1.0)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(Text, nullable=True)
    meeting_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    lawyer = relationship("LawyerProfile", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "lawyer_id": str(self.lawyer_id) if self.lawyer_id else None,
            "date": self.date.isoformat() if self.date else None,
            "duration_hours": self.duration_hours,
            "total_amount": self.total_amount,
            "status": self.status.value if self.status else None,
            "notes": self.notes,
            "meeting_link": self.meeting_link,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), unique=True)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="review")
    lawyer = relationship("LawyerProfile", back_populates="reviews")
    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "booking_id": str(self.booking_id) if self.booking_id else None,
            "lawyer_id": str(self.lawyer_id) if self.lawyer_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
