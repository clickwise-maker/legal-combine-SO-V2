import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///legal_combines.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class GovtDocument(Base):
    """Model for storing scraped government documents."""
    
    __tablename__ = "govt_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    document_type = Column(String(50), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_url = Column(String(1000), nullable=False)
    source_name = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    jurisdiction = Column(String(100), default="India")
    ministry = Column(String(200), nullable=True)
    act_number = Column(String(100), nullable=True)
    gazette_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    keywords = Column(String(1000), nullable=True)
    metadata = Column(JSON, nullable=True)
    content_hash = Column(String(64), unique=True, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_source_type", "source_type"),
        Index("idx_document_type", "document_type"),
        Index("idx_gazette_date", "gazette_date"),
        Index("idx_content_hash", "content_hash"),
    )


class ScrapeHistory(Base):
    """Model for tracking scrape history."""
    
    __tablename__ = "scrape_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False)
    task_name = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False)
    sources_processed = Column(Integer, default=0)
    documents_found = Column(Integer, default=0)
    documents_saved = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)


class ScrapeTask(Base):
    """Model for scrape task configuration."""
    
    __tablename__ = "scrape_tasks"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    sources = Column(JSON, nullable=False)
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON, nullable=False)
    status = Column(String(50), default="pending")
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session() -> Session:
    """Get a database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """Get database session for FastAPI dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def record_scrape_history(
    task_id: str,
    task_name: str,
    status: str,
    sources_processed: int,
    documents_found: int,
    documents_saved: int,
    errors: list,
    started_at: datetime,
    completed_at: Optional[datetime],
    duration_seconds: int,
):
    """Record a scrape run to history."""
    with get_db_session() as session:
        history = ScrapeHistory(
            task_id=task_id,
            task_name=task_name,
            status=status,
            sources_processed=sources_processed,
            documents_found=documents_found,
            documents_saved=documents_saved,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )
        session.add(history)


def search_documents(
    query: Optional[str] = None,
    source_type: Optional[str] = None,
    document_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
):
    """Search documents with filters."""
    with get_db_session() as session:
        q = session.query(GovtDocument)

        if query:
            q = q.filter(
                (GovtDocument.title.ilike(f"%{query}%")) |
                (GovtDocument.content.ilike(f"%{query}%")) |
                (GovtDocument.keywords.ilike(f"%{query}%"))
            )

        if source_type:
            q = q.filter(GovtDocument.source_type == source_type)

        if document_type:
            q = q.filter(GovtDocument.document_type == document_type)

        if date_from:
            q = q.filter(GovtDocument.gazette_date >= date_from)

        if date_to:
            q = q.filter(GovtDocument.gazette_date <= date_to)

        total = q.count()
        documents = q.order_by(GovtDocument.gazette_date.desc()).offset(offset).limit(limit).all()

        return {
            "documents": [doc.__dict__ for doc in documents],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def get_document_stats():
    """Get statistics about stored documents."""
    with get_db_session() as session:
        from sqlalchemy import func

        stats = {
            "total_documents": session.query(func.count(GovtDocument.id)).scalar(),
            "by_source": {},
            "by_type": {},
            "recent_count": session.query(func.count(GovtDocument.id))
                .filter(GovtDocument.scraped_at >= datetime.utcnow().replace(hour=0, minute=0, second=0))
                .scalar(),
        }

        for source_type, count in session.query(
            GovtDocument.source_type, func.count(GovtDocument.id)
        ).group_by(GovtDocument.source_type).all():
            stats["by_source"][source_type] = count

        for doc_type, count in session.query(
            GovtDocument.document_type, func.count(GovtDocument.id)
        ).group_by(GovtDocument.document_type).all():
            stats["by_type"][doc_type] = count

        return stats
