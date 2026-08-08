import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.lawyer import (
    LawyerProfile,
    Booking,
    Review,
    BookingStatus,
)
from ..models.typist import (
    TypistProfile,
    DocumentOrder,
    OrderStatus,
)
from ..models.payment import Commission
from ..utils.database import get_db


router = APIRouter(tags=["Marketplace"])


# ----------------------------- Schemas -----------------------------

class LawyerProfileCreate(BaseModel):
    bar_council_id: str
    specialization: str
    experience_years: int = 0
    hourly_rate: float = 0.0
    fixed_fee: Optional[float] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class LawyerProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    hourly_rate: Optional[float] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None


class TypistProfileCreate(BaseModel):
    specialization: str
    experience_years: int = 0
    rate_per_page: float = 0.0
    rate_per_hour: float = 0.0
    bio: Optional[str] = None


class TypistProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    rate_per_page: Optional[float] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None


class LawyerBookingCreate(BaseModel):
    lawyer_id: str
    date: datetime
    duration_hours: float = 1.0
    notes: Optional[str] = None


class LawyerReviewCreate(BaseModel):
    lawyer_id: str
    rating: int
    comment: Optional[str] = None


class DocumentOrderCreate(BaseModel):
    typist_id: str
    order_type: str
    page_count: int = 1
    instructions: Optional[str] = None


class TypistReviewCreate(BaseModel):
    typist_id: str
    rating: int
    comment: Optional[str] = None


# ----------------------------- Helpers -----------------------------

def get_current_user_id() -> str:
    """Mock function to get current authenticated user ID."""
    return "user_123"


def _user_uuid(user_id: str):
    """Convert user_id string to UUID if valid, else None."""
    try:
        return uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        return None


def _update_rating(db: Session, model_cls, id_field, owner_id):
    """Recompute average rating for a lawyer/typist from their reviews."""
    reviews = db.query(Review).filter(Review.lawyer_id == owner_id).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
        db.query(model_cls).filter(model_cls.id == owner_id).update(
            {"rating": round(avg, 1)}
        )


# ----------------------------- Lawyer Routes -----------------------------

@router.get("/lawyers")
async def list_lawyers(
    specialization: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_hourly_rate: Optional[float] = None,
    max_hourly_rate: Optional[float] = None,
    available_only: bool = True,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """List all lawyers with filtering."""
    query = db.query(LawyerProfile)

    if specialization:
        query = query.filter(LawyerProfile.specialization.ilike(f"%{specialization}%"))

    if min_rating is not None:
        query = query.filter(LawyerProfile.rating >= min_rating)

    if min_hourly_rate is not None:
        query = query.filter(LawyerProfile.hourly_rate >= min_hourly_rate)

    if max_hourly_rate is not None:
        query = query.filter(LawyerProfile.hourly_rate <= max_hourly_rate)

    if available_only:
        query = query.filter(LawyerProfile.is_available == True)  # noqa: E712

    query = query.order_by(LawyerProfile.rating.desc())

    total = query.count()
    start = (page - 1) * limit
    end = start + limit
    paginated = query.offset(start).limit(limit).all()

    return {
        "lawyers": [l.to_dict() for l in paginated],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/lawyers/{lawyer_id}")
async def get_lawyer(lawyer_id: str, db: Session = Depends(get_db)):
    """Get lawyer profile details."""
    lawyer = db.query(LawyerProfile).filter(LawyerProfile.id == lawyer_id).first()
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    return {"lawyer": lawyer.to_dict()}


@router.post("/lawyers", status_code=status.HTTP_201_CREATED)
async def create_lawyer_profile(
    request: LawyerProfileCreate,
    db: Session = Depends(get_db),
):
    """Create lawyer profile."""
    user_id = get_current_user_id()

    existing = db.query(LawyerProfile).filter(
        LawyerProfile.user_id == _user_uuid(user_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    lawyer = LawyerProfile(
        user_id=_user_uuid(user_id),
        bar_council_id=request.bar_council_id,
        specialization=request.specialization,
        experience_years=request.experience_years,
        hourly_rate=request.hourly_rate,
        fixed_fee=request.fixed_fee,
        location=request.location,
        bio=request.bio,
    )

    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)
    return {"lawyer": lawyer.to_dict()}


@router.patch("/lawyers/profile")
async def update_lawyer_profile(
    request: LawyerProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update own lawyer profile."""
    user_id = get_current_user_id()

    lawyer = db.query(LawyerProfile).filter(
        LawyerProfile.user_id == _user_uuid(user_id)
    ).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if request.specialization is not None:
        lawyer.specialization = request.specialization
    if request.hourly_rate is not None:
        lawyer.hourly_rate = request.hourly_rate
    if request.bio is not None:
        lawyer.bio = request.bio
    if request.is_available is not None:
        lawyer.is_available = request.is_available

    lawyer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lawyer)

    return {"lawyer": lawyer.to_dict()}


@router.post("/lawyers/book")
async def create_booking(
    request: LawyerBookingCreate,
    db: Session = Depends(get_db),
):
    """Book a lawyer consultation."""
    client_id = get_current_user_id()

    lawyer = db.query(LawyerProfile).filter(LawyerProfile.id == request.lawyer_id).first()
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )

    if not lawyer.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lawyer is not available"
        )

    total_amount = lawyer.hourly_rate * request.duration_hours
    commission_amount = Commission.calculate(total_amount)

    booking = Booking(
        user_id=_user_uuid(client_id),
        lawyer_id=lawyer.id,
        date=request.date,
        duration_hours=request.duration_hours,
        total_amount=total_amount,
        status=BookingStatus.PENDING,
        notes=request.notes,
    )

    db.add(booking)
    lawyer.total_bookings = (lawyer.total_bookings or 0) + 1
    db.commit()
    db.refresh(booking)

    return {
        "booking": booking.to_dict(),
        "commission": commission_amount,
    }


@router.get("/lawyers/bookings")
async def get_my_bookings(
    booking_status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get current user's bookings."""
    user_id = get_current_user_id()

    query = db.query(Booking).filter(
        (Booking.user_id == _user_uuid(user_id)) |
        (Booking.lawyer_id == _user_uuid(user_id))
    )

    if booking_status:
        try:
            query = query.filter(Booking.status == BookingStatus(booking_status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )

    bookings = query.order_by(Booking.created_at.desc()).all()
    return {"bookings": [b.to_dict() for b in bookings]}


@router.post("/lawyers/review")
async def create_lawyer_review(
    request: LawyerReviewCreate,
    db: Session = Depends(get_db),
):
    """Create a review for a lawyer."""
    user_id = get_current_user_id()

    lawyer = db.query(LawyerProfile).filter(LawyerProfile.id == request.lawyer_id).first()
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )

    review = Review(
        lawyer_id=lawyer.id,
        user_id=_user_uuid(user_id),
        rating=request.rating,
        comment=request.comment,
    )

    db.add(review)
    db.flush()
    _update_rating(db, LawyerProfile, LawyerProfile.id, lawyer.id)
    db.commit()
    db.refresh(review)

    return {"review": review.to_dict()}


@router.get("/lawyers/{lawyer_id}/reviews")
async def get_lawyer_reviews(lawyer_id: str, db: Session = Depends(get_db)):
    """Get reviews for a lawyer."""
    reviews = db.query(Review).filter(Review.lawyer_id == lawyer_id).all()
    return {"reviews": [r.to_dict() for r in reviews]}


# ----------------------------- Typist Routes -----------------------------

@router.get("/typists")
async def list_typists(
    specialization: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_rate: Optional[float] = None,
    max_rate: Optional[float] = None,
    available_only: bool = True,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """List all typists with filtering."""
    query = db.query(TypistProfile)

    if specialization:
        query = query.filter(TypistProfile.specialization.ilike(f"%{specialization}%"))

    if min_rating is not None:
        query = query.filter(TypistProfile.rating >= min_rating)

    if min_rate is not None:
        query = query.filter(TypistProfile.rate_per_page >= min_rate)

    if max_rate is not None:
        query = query.filter(TypistProfile.rate_per_page <= max_rate)

    if available_only:
        query = query.filter(TypistProfile.is_available == True)  # noqa: E712

    query = query.order_by(TypistProfile.rating.desc())

    total = query.count()
    start = (page - 1) * limit
    end = start + limit
    paginated = query.offset(start).limit(limit).all()

    return {
        "typists": [t.to_dict() for t in paginated],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/typists/{typist_id}")
async def get_typist(typist_id: str, db: Session = Depends(get_db)):
    """Get typist profile details."""
    typist = db.query(TypistProfile).filter(TypistProfile.id == typist_id).first()
    if not typist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )
    return {"typist": typist.to_dict()}


@router.post("/typists", status_code=status.HTTP_201_CREATED)
async def create_typist_profile(
    request: TypistProfileCreate,
    db: Session = Depends(get_db),
):
    """Create typist profile."""
    user_id = get_current_user_id()

    existing = db.query(TypistProfile).filter(
        TypistProfile.user_id == _user_uuid(user_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    typist = TypistProfile(
        user_id=_user_uuid(user_id),
        specialization=request.specialization,
        experience_years=request.experience_years,
        rate_per_page=request.rate_per_page,
        rate_per_hour=request.rate_per_hour,
        bio=request.bio,
    )

    db.add(typist)
    db.commit()
    db.refresh(typist)
    return {"typist": typist.to_dict()}


@router.patch("/typists/profile")
async def update_typist_profile(
    request: TypistProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update own typist profile."""
    user_id = get_current_user_id()

    typist = db.query(TypistProfile).filter(
        TypistProfile.user_id == _user_uuid(user_id)
    ).first()

    if not typist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if request.specialization is not None:
        typist.specialization = request.specialization
    if request.rate_per_page is not None:
        typist.rate_per_page = request.rate_per_page
    if request.bio is not None:
        typist.bio = request.bio
    if request.is_available is not None:
        typist.is_available = request.is_available

    typist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(typist)

    return {"typist": typist.to_dict()}


@router.post("/documents/order")
async def create_document_order(
    request: DocumentOrderCreate,
    db: Session = Depends(get_db),
):
    """Create a document typing order."""
    client_id = get_current_user_id()

    typist = db.query(TypistProfile).filter(TypistProfile.id == request.typist_id).first()
    if not typist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )

    if not typist.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Typist is not available"
        )

    total_amount = typist.rate_per_page * request.page_count
    commission_amount = Commission.calculate(total_amount)

    order = DocumentOrder(
        user_id=_user_uuid(client_id),
        typist_id=typist.id,
        order_type=request.order_type,
        page_count=request.page_count,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        instructions=request.instructions,
    )

    db.add(order)
    typist.total_orders = (typist.total_orders or 0) + 1
    db.commit()
    db.refresh(order)

    return {
        "order": order.to_dict(),
        "commission": commission_amount,
    }


@router.get("/documents/orders")
async def get_my_orders(
    order_status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get current user's document orders."""
    user_id = get_current_user_id()

    query = db.query(DocumentOrder).filter(
        (DocumentOrder.user_id == _user_uuid(user_id)) |
        (DocumentOrder.typist_id == _user_uuid(user_id))
    )

    if order_status:
        try:
            query = query.filter(DocumentOrder.status == OrderStatus(order_status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )

    orders = query.order_by(DocumentOrder.created_at.desc()).all()
    return {"orders": [o.to_dict() for o in orders]}


@router.post("/typists/review")
async def create_typist_review(
    request: TypistReviewCreate,
    db: Session = Depends(get_db),
):
    """Create a review for a typist.

    Reviews are stored in the lawyers 'reviews' table linked to the typist's
    user_id, since the schema defines a single Review model. The typist's
    rating is recomputed from orders rated by the client.
    """
    user_id = get_current_user_id()

    typist = db.query(TypistProfile).filter(TypistProfile.id == request.typist_id).first()
    if not typist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Typist not found"
        )

    review = Review(
        lawyer_id=typist.id,
        user_id=_user_uuid(user_id),
        rating=request.rating,
        comment=request.comment,
    )

    db.add(review)
    db.flush()

    reviews = db.query(Review).filter(Review.lawyer_id == typist.id).all()
    if reviews:
        avg = sum(r.rating for r in reviews) / len(reviews)
        typist.rating = round(avg, 1)

    db.commit()
    db.refresh(review)

    return {"review": review.to_dict()}


@router.get("/typists/{typist_id}/reviews")
async def get_typist_reviews(typist_id: str, db: Session = Depends(get_db)):
    """Get reviews for a typist."""
    reviews = db.query(Review).filter(Review.lawyer_id == typist_id).all()
    return {"reviews": [r.to_dict() for r in reviews]}


@router.get("/commission/calculate")
async def calculate_service_commission(
    service_type: str,
    amount: float,
    db: Session = Depends(get_db),
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
