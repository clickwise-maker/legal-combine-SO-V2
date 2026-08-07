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
