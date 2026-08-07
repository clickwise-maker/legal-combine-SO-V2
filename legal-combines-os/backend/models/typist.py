from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class TypistStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class DocumentType(str, Enum):
    AGREEMENT = "agreement"
    CONTRACT = "contract"
    PETITION = "petition"
    AFFIDAVIT = "affidavit"
    PLAINT = "plaint"
    WRIT = "writ"
    APPEAL = "appeal"
    ORDER = "order"
    JUDGMENT = "judgment"
    LEGAL_NOTICE = "legal_notice"
    POWER_OF_ATTORNEY = "power_of_attorney"
    WILL = "will"
    OTHER = "other"


class TypistProfile:
    """Typist profile for marketplace."""

    def __init__(
        self,
        user_id: str,
        typing_speed_wpm: int,
        specialties: List[DocumentType],
        per_page_rate: int,
        bio: Optional[str] = None,
        languages: Optional[List[str]] = None,
        profile_id: Optional[str] = None,
        status: TypistStatus = TypistStatus.PENDING,
        is_available: bool = True,
        rating: float = 0.0,
        total_reviews: int = 0,
        total_documents: int = 0,
        completed_documents: int = 0,
        verified_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = profile_id or str(uuid.uuid4())
        self.user_id = user_id
        self.typing_speed_wpm = typing_speed_wpm
        self.specialties = specialties
        self.per_page_rate = per_page_rate
        self.bio = bio
        self.languages = languages or ["English", "Hindi"]
        self.status = status
        self.is_available = is_available
        self.rating = rating
        self.total_reviews = total_reviews
        self.total_documents = total_documents
        self.completed_documents = completed_documents
        self.verified_at = verified_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_verified(self) -> bool:
        return self.status == TypistStatus.VERIFIED

    @property
    def per_page_rate_display(self) -> str:
        return f"₹{self.per_page_rate}/page"

    @property
    def completion_rate(self) -> float:
        if self.total_documents == 0:
            return 0.0
        return (self.completed_documents / self.total_documents) * 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "typing_speed_wpm": self.typing_speed_wpm,
            "specialties": [s.value for s in self.specialties],
            "per_page_rate": self.per_page_rate,
            "per_page_rate_display": self.per_page_rate_display,
            "bio": self.bio,
            "languages": self.languages,
            "status": self.status.value,
            "is_available": self.is_available,
            "is_verified": self.is_verified,
            "rating": self.rating,
            "total_reviews": self.total_reviews,
            "total_documents": self.total_documents,
            "completed_documents": self.completed_documents,
            "completion_rate": self.completion_rate,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TypistProfile":
        return cls(
            profile_id=data.get("id"),
            user_id=data["user_id"],
            typing_speed_wpm=data["typing_speed_wpm"],
            specialties=[DocumentType(s) for s in data["specialties"]],
            per_page_rate=data["per_page_rate"],
            bio=data.get("bio"),
            languages=data.get("languages"),
            status=TypistStatus(data.get("status", "pending")),
            is_available=data.get("is_available", True),
            rating=data.get("rating", 0.0),
            total_reviews=data.get("total_reviews", 0),
            total_documents=data.get("total_documents", 0),
            completed_documents=data.get("completed_documents", 0),
            verified_at=data.get("verified_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class TypistReview:
    """Review for a typist."""

    def __init__(
        self,
        typist_id: str,
        client_id: str,
        rating: int,
        comment: Optional[str] = None,
        order_id: Optional[str] = None,
        review_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = review_id or str(uuid.uuid4())
        self.typist_id = typist_id
        self.client_id = client_id
        self.rating = min(5, max(1, rating))
        self.comment = comment
        self.order_id = order_id
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "typist_id": self.typist_id,
            "client_id": self.client_id,
            "rating": self.rating,
            "comment": self.comment,
            "order_id": self.order_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DocumentOrder:
    """Document typing order."""

    def __init__(
        self,
        typist_id: str,
        client_id: str,
        document_type: DocumentType,
        pages: int,
        content: str,
        notes: Optional[str] = None,
        order_id: Optional[str] = None,
        status: str = "pending",
        amount: int = 0,
        commission: int = 0,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self.id = order_id or str(uuid.uuid4())
        self.typist_id = typist_id
        self.client_id = client_id
        self.document_type = document_type
        self.pages = pages
        self.content = content
        self.notes = notes
        self.status = status
        self.amount = amount
        self.commission = commission
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "typist_id": self.typist_id,
            "client_id": self.client_id,
            "document_type": self.document_type.value,
            "pages": self.pages,
            "content": self.content,
            "notes": self.notes,
            "status": self.status,
            "amount": self.amount,
            "commission": self.commission,
            "amount_display": f"₹{self.amount}",
            "commission_display": f"₹{self.commission}",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
