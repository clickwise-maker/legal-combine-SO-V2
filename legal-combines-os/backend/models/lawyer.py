from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class LawyerStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class Specialty(str, Enum):
    CORPORATE = "corporate"
    CRIMINAL = "criminal"
    FAMILY = "family"
    PROPERTY = "property"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TAX = "tax"
    IMMIGRATION = "immigration"
    LABOR = "labor"
    CIVIL = "civil"
    CONSUMER = "consumer"


class Experience(str, Enum):
    JUNIOR = "junior"  # 0-3 years
    MID = "mid"  # 3-7 years
    SENIOR = "senior"  # 7-15 years
    EXPERT = "expert"  # 15+ years


class LawyerProfile:
    """Lawyer profile for marketplace."""

    def __init__(
        self,
        user_id: str,
        bar_license: str,
        specialties: List[Specialty],
        experience: Experience,
        hourly_rate: int,
        bio: Optional[str] = None,
        education: Optional[List[dict]] = None,
        languages: Optional[List[str]] = None,
        profile_id: Optional[str] = None,
        status: LawyerStatus = LawyerStatus.PENDING,
        is_available: bool = True,
        rating: float = 0.0,
        total_reviews: int = 0,
        total_cases: int = 0,
        completed_cases: int = 0,
        verified_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = profile_id or str(uuid.uuid4())
        self.user_id = user_id
        self.bar_license = bar_license
        self.specialties = specialties
        self.experience = experience
        self.hourly_rate = hourly_rate
        self.bio = bio
        self.education = education or []
        self.languages = languages or ["English", "Hindi"]
        self.status = status
        self.is_available = is_available
        self.rating = rating
        self.total_reviews = total_reviews
        self.total_cases = total_cases
        self.completed_cases = completed_cases
        self.verified_at = verified_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_verified(self) -> bool:
        return self.status == LawyerStatus.VERIFIED

    @property
    def hourly_rate_display(self) -> str:
        return f"₹{self.hourly_rate}/hour"

    @property
    def completion_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return (self.completed_cases / self.total_cases) * 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bar_license": self.bar_license,
            "specialties": [s.value for s in self.specialties],
            "experience": self.experience.value,
            "hourly_rate": self.hourly_rate,
            "hourly_rate_display": self.hourly_rate_display,
            "bio": self.bio,
            "education": self.education,
            "languages": self.languages,
            "status": self.status.value,
            "is_available": self.is_available,
            "is_verified": self.is_verified,
            "rating": self.rating,
            "total_reviews": self.total_reviews,
            "total_cases": self.total_cases,
            "completed_cases": self.completed_cases,
            "completion_rate": self.completion_rate,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LawyerProfile":
        return cls(
            profile_id=data.get("id"),
            user_id=data["user_id"],
            bar_license=data["bar_license"],
            specialties=[Specialty(s) for s in data["specialties"]],
            experience=Experience(data["experience"]),
            hourly_rate=data["hourly_rate"],
            bio=data.get("bio"),
            education=data.get("education"),
            languages=data.get("languages"),
            status=LawyerStatus(data.get("status", "pending")),
            is_available=data.get("is_available", True),
            rating=data.get("rating", 0.0),
            total_reviews=data.get("total_reviews", 0),
            total_cases=data.get("total_cases", 0),
            completed_cases=data.get("completed_cases", 0),
            verified_at=data.get("verified_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class LawyerReview:
    """Review for a lawyer."""

    def __init__(
        self,
        lawyer_id: str,
        client_id: str,
        rating: int,
        comment: Optional[str] = None,
        case_id: Optional[str] = None,
        review_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = review_id or str(uuid.uuid4())
        self.lawyer_id = lawyer_id
        self.client_id = client_id
        self.rating = min(5, max(1, rating))
        self.comment = comment
        self.case_id = case_id
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lawyer_id": self.lawyer_id,
            "client_id": self.client_id,
            "rating": self.rating,
            "comment": self.comment,
            "case_id": self.case_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LawyerBooking:
    """Booking for a lawyer consultation."""

    def __init__(
        self,
        lawyer_id: str,
        client_id: str,
        scheduled_at: datetime,
        duration_minutes: int = 30,
        notes: Optional[str] = None,
        booking_id: Optional[str] = None,
        status: str = "pending",
        amount: int = 0,
        commission: int = 0,
        created_at: Optional[datetime] = None,
    ):
        self.id = booking_id or str(uuid.uuid4())
        self.lawyer_id = lawyer_id
        self.client_id = client_id
        self.scheduled_at = scheduled_at
        self.duration_minutes = duration_minutes
        self.notes = notes
        self.status = status
        self.amount = amount
        self.commission = commission
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lawyer_id": self.lawyer_id,
            "client_id": self.client_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
            "status": self.status,
            "amount": self.amount,
            "commission": self.commission,
            "amount_display": f"₹{self.amount}",
            "commission_display": f"₹{self.commission}",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
