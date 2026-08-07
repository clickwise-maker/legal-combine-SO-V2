from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.models.lawyer import (
    LawyerProfile,
    LawyerReview,
    LawyerBooking,
    Specialty,
    Experience,
    LawyerStatus,
)
from backend.models.typist import (
    TypistProfile,
    TypistReview,
    DocumentOrder,
    DocumentType,
    TypistStatus,
)
from backend.models.payment import Commission


router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])


MOCK_LAWYERS_DB = {}
MOCK_TYPISTS_DB = {}
MOCK_LAWYER_BOOKINGS_DB = {}
MOCK_DOCUMENT_ORDERS_DB = {}
MOCK_LAWYER_REVIEWS_DB = {}
MOCK_TYPIST_REVIEWS_DB = {}


class LawyerProfileCreate(BaseModel):
    bar_license: str
    specialties: List[str]
    experience: str
    hourly_rate: int
    bio: Optional[str] = None
    education: Optional[List[dict]] = None
    languages: Optional[List[str]] = None


class LawyerProfileUpdate(BaseModel):
    specialties: Optional[List[str]] = None
    hourly_rate: Optional[int] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None


class TypistProfileCreate(BaseModel):
    typing_speed_wpm: int
    specialties: List[str]
    per_page_rate: int
    bio: Optional[str] = None
    languages: Optional[List[str]] = None


class TypistProfileUpdate(BaseModel):
    specialties: Optional[List[str]] = None
    per_page_rate: Optional[int] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None


class LawyerBookingCreate(BaseModel):
    lawyer_id: str
    scheduled_at: datetime
    duration_minutes: int = 30
    notes: Optional[str] = None


class LawyerReviewCreate(BaseModel):
    lawyer_id: str
    rating: int
    comment: Optional[str] = None
    case_id: Optional[str] = None


class DocumentOrderCreate(BaseModel):
    typist_id: str
    document_type: str
    pages: int
    content: str
    notes: Optional[str] = None


class TypistReviewCreate(BaseModel):
    typist_id: str
    rating: int
    comment: Optional[str] = None
    order_id: Optional[str] = None


def get_current_user_id() -> str:
    """Mock function to get current authenticated user ID."""
    return "user_123"


@router.get("/lawyers")
async def list_lawyers(
    specialty: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_hourly_rate: Optional[int] = None,
    max_hourly_rate: Optional[int] = None,
    available_only: bool = True,
    page: int = 1,
    limit: int = 10,
):
    """List all lawyers with filtering."""
    lawyers = list(MOCK_LAWYERS_DB.values())

    if specialty:
        lawyers = [l for l in lawyers if specialty in [s.value for s in l.specialties]]

    if min_rating is not None:
        lawyers = [l for l in lawyers if l.rating >= min_rating]

    if min_hourly_rate is not None:
        lawyers = [l for l in lawyers if l.hourly_rate >= min_hourly_rate]

    if max_hourly_rate is not None:
        lawyers = [l for l in lawyers if l.hourly_rate <= max_hourly_rate]

    if available_only:
        lawyers = [l for l in lawyers if l.is_available]

    lawyers = sorted(lawyers, key=lambda x: x.rating, reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paginated = lawyers[start:end]

    return {
        "lawyers": [l.to_dict() for l in paginated],
        "total": len(lawyers),
        "page": page,
        "limit": limit,
    }


@router.get("/lawyers/{lawyer_id}")
async def get_lawyer(lawyer_id: str):
    """Get lawyer profile details."""
    if lawyer_id not in MOCK_LAWYERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    return {"lawyer": MOCK_LAWYERS_DB[lawyer_id].to_dict()}


@router.post("/lawyers", status_code=status.HTTP_201_CREATED)
async def create_lawyer_profile(request: LawyerProfileCreate):
    """Create lawyer profile."""
    user_id = get_current_user_id()

    if user_id in [l.user_id for l in MOCK_LAWYERS_DB.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    lawyer = LawyerProfile(
        user_id=user_id,
        bar_license=request.bar_license,
        specialties=[Specialty(s) for s in request.specialties],
        experience=Experience(request.experience),
        hourly_rate=request.hourly_rate,
        bio=request.bio,
        education=request.education,
        languages=request.languages,
    )

    MOCK_LAWYERS_DB[lawyer.id] = lawyer
    return {"lawyer": lawyer.to_dict()}


@router.patch("/lawyers/profile")
async def update_lawyer_profile(request: LawyerProfileUpdate):
    """Update own lawyer profile."""
    user_id = get_current_user_id()

    lawyer = None
    for l in MOCK_LAWYERS_DB.values():
        if l.user_id == user_id:
            lawyer = l
            break

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if request.specialties is not None:
        lawyer.specialties = [Specialty(s) for s in request.specialties]
    if request.hourly_rate is not None:
        lawyer.hourly_rate = request.hourly_rate
    if request.bio is not None:
        lawyer.bio = request.bio
    if request.is_available is not None:
        lawyer.is_available = request.is_available

    lawyer.updated_at = datetime.utcnow()

    return {"lawyer": lawyer.to_dict()}


@router.post("/lawyers/book")
async def create_booking(request: LawyerBookingCreate):
    """Book a lawyer consultation."""
    client_id = get_current_user_id()

    if request.lawyer_id not in MOCK_LAWYERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )

    lawyer = MOCK_LAWYERS_DB[request.lawyer_id]

    if not lawyer.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lawyer is not available"
        )

    commission_amount = Commission.calculate(lawyer.hourly_rate * request.duration_minutes // 60 * 100)
    amount = commission_amount["gross_amount"]
    commission = commission_amount["commission_amount"]

    booking = LawyerBooking(
        lawyer_id=request.lawyer_id,
        client_id=client_id,
        scheduled_at=request.scheduled_at,
        duration_minutes=request.duration_minutes,
        notes=request.notes,
        amount=amount,
        commission=commission,
    )

    MOCK_LAWYER_BOOKINGS_DB[booking.id] = booking
    lawyer.total_cases += 1

    return {"booking": booking.to_dict()}


@router.get("/lawyers/bookings")
async def get_my_bookings(status: Optional[str] = None):
    """Get current user's bookings."""
    user_id = get_current_user_id()

    bookings = [
        b.to_dict()
        for b in MOCK_LAWYER_BOOKINGS_DB.values()
        if b.client_id == user_id or b.lawyer_id == user_id
    ]

    if status:
        bookings = [b for b in bookings if b["status"] == status]

    return {"bookings": bookings}


@router.post("/lawyers/review")
async def create_lawyer_review(request: LawyerReviewCreate):
    """Create a review for a lawyer."""
    user_id = get_current_user_id()

    if request.lawyer_id not in MOCK_LAWYERS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )

    review = LawyerReview(
        lawyer_id=request.lawyer_id,
        client_id=user_id,
        rating=request.rating,
        comment=request.comment,
        case_id=request.case_id,
    )

    MOCK_LAWYER_REVIEWS_DB[review.id] = review

    lawyer = MOCK_LAWYERS_DB[request.lawyer_id]
    lawyer.total_reviews += 1
    lawyer.rating = sum(r.rating for r in MOCK_LAWYER_REVIEWS_DB.values() if r.lawyer_id == request.lawyer_id) / lawyer.total_reviews

    return {"review": review.to_dict()}


@router.get("/lawyers/{lawyer_id}/reviews")
async def get_lawyer_reviews(lawyer_id: str):
    """Get reviews for a lawyer."""
    reviews = [
        r.to_dict()
        for r in MOCK_LAWYER_REVIEWS_DB.values()
        if r.lawyer_id == lawyer_id
    ]
    return {"reviews": reviews}


@router.get("/typists")
async def list_typists(
    specialty: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_rate: Optional[int] = None,
    max_rate: Optional[int] = None,
    available_only: bool = True,
    page: int = 1,
    limit: int = 10,
):
    """List all typists with filtering."""
    typists = list(MOCK_TYPISTS_DB.values())

    if specialty:
        typists = [t for t in typists if specialty in [s.value for s in t.specialties]]

    if min_rating is not None:
        typists = [t for t in typists if t.rating >= min_rating]

    if min_rate is not None:
        typists = [t for t in typists if t.per_page_rate >= min_rate]

    if max_rate is not None:
        typists = [t for t in typists if t.per_page_rate <= max_rate]

    if available_only:
        typists = [t for t in typists if t.is_available]

    typists = sorted(typists, key=lambda x: x.rating, reverse=True)

    start = (page - 1) * limit
    end = start + limit
    paginated = typists[start:end]

    return {
        "typists": [t.to_dict() for t in paginated],
        "total": len(typists),
        "page": page,
        "limit": limit,
    }


@router.get("/typists/{typist_id}")
async def get_typist(typist_id: str):
    """Get typist profile details."""
    if typist_id not in MOCK_TYPISTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )
    return {"typist": MOCK_TYPISTS_DB[typist_id].to_dict()}


@router.post("/typists", status_code=status.HTTP_201_CREATED)
async def create_typist_profile(request: TypistProfileCreate):
    """Create typist profile."""
    user_id = get_current_user_id()

    if user_id in [t.user_id for t in MOCK_TYPISTS_DB.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    typist = TypistProfile(
        user_id=user_id,
        typing_speed_wpm=request.typing_speed_wpm,
        specialties=[DocumentType(s) for s in request.specialties],
        per_page_rate=request.per_page_rate,
        bio=request.bio,
        languages=request.languages,
    )

    MOCK_TYPISTS_DB[typist.id] = typist
    return {"typist": typist.to_dict()}


@router.patch("/typists/profile")
async def update_typist_profile(request: TypistProfileUpdate):
    """Update own typist profile."""
    user_id = get_current_user_id()

    typist = None
    for t in MOCK_TYPISTS_DB.values():
        if t.user_id == user_id:
            typist = t
            break

    if not typist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if request.specialties is not None:
        typist.specialties = [DocumentType(s) for s in request.specialties]
    if request.per_page_rate is not None:
        typist.per_page_rate = request.per_page_rate
    if request.bio is not None:
        typist.bio = request.bio
    if request.is_available is not None:
        typist.is_available = request.is_available

    typist.updated_at = datetime.utcnow()

    return {"typist": typist.to_dict()}


@router.post("/documents/order")
async def create_document_order(request: DocumentOrderCreate):
    """Create a document typing order."""
    client_id = get_current_user_id()

    if request.typist_id not in MOCK_TYPISTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )

    typist = MOCK_TYPISTS_DB[request.typist_id]

    if not typist.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Typist is not available"
        )

    base_amount = typist.per_page_rate * request.pages
    commission_amount = Commission.calculate(base_amount * 100)
    amount = commission_amount["gross_amount"]
    commission = commission_amount["commission_amount"]

    order = DocumentOrder(
        typist_id=request.typist_id,
        client_id=client_id,
        document_type=DocumentType(request.document_type),
        pages=request.pages,
        content=request.content,
        notes=request.notes,
        amount=amount,
        commission=commission,
    )

    MOCK_DOCUMENT_ORDERS_DB[order.id] = order
    typist.total_documents += 1

    return {"order": order.to_dict()}


@router.get("/documents/orders")
async def get_my_orders(status: Optional[str] = None):
    """Get current user's document orders."""
    user_id = get_current_user_id()

    orders = [
        o.to_dict()
        for o in MOCK_DOCUMENT_ORDERS_DB.values()
        if o.client_id == user_id or o.typist_id == user_id
    ]

    if status:
        orders = [o for o in orders if o["status"] == status]

    return {"orders": orders}


@router.post("/typists/review")
async def create_typist_review(request: TypistReviewCreate):
    """Create a review for a typist."""
    user_id = get_current_user_id()

    if request.typist_id not in MOCK_TYPISTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )

    review = TypistReview(
        typist_id=request.typist_id,
        client_id=user_id,
        rating=request.rating,
        comment=request.comment,
        order_id=request.order_id,
    )

    MOCK_TYPIST_REVIEWS_DB[review.id] = review

    typist = MOCK_TYPISTS_DB[request.typist_id]
    typist.total_reviews += 1
    typist.rating = sum(r.rating for r in MOCK_TYPIST_REVIEWS_DB.values() if r.typist_id == request.typist_id) / typist.total_reviews

    return {"review": review.to_dict()}


@router.get("/typists/{typist_id}/reviews")
async def get_typist_reviews(typist_id: str):
    """Get reviews for a typist."""
    reviews = [
        r.to_dict()
        for r in MOCK_TYPIST_REVIEWS_DB.values()
        if r.typist_id == typist_id
    ]
    return {"reviews": reviews}


@router.get("/commission/calculate")
async def calculate_service_commission(
    service_type: str,
    amount: int,
):
    """Calculate commission for a marketplace service."""
    if service_type not in ["lawyer", "typist"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service type"
        )

    commission = Commission.calculate(amount)
    return {
        "service_type": service_type,
        "commission_rate": 0.12,
        **commission,
    }
