"""
Database Utilities — SQLAlchemy Setup, Connection, Queries
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from ..config import Config


# Create base for models
Base = declarative_base()


# Create engine
engine = create_engine(
    Config.get_database_url(),
    poolclass=NullPool,
    echo=Config.DEBUG
)


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    """Database utility class"""

    @staticmethod
    def get_session() -> Session:
        """Get database session"""
        return SessionLocal()

    @staticmethod
    def init_db():
        """Initialize database (create tables)"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_db():
        """Drop all tables (use with caution)"""
        Base.metadata.drop_all(bind=engine)

    @staticmethod
    def get_session_context():
        """Get session as context manager"""
        return SessionLocal()


# Dependency for FastAPI
def get_db():
    """FastAPI dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Search utilities
def search_documents(db: Session, query: str, limit: int = 10):
    """Search documents using full-text search"""
    from sqlalchemy import text
    stmt = text("""
        SELECT id, filename, content, 
               ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', :query)) AS rank
        FROM documents
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC
        LIMIT :limit
    """)
    return db.execute(stmt, {"query": query, "limit": limit}).fetchall()


def get_stats(db: Session, user_id: str):
    """Get user statistics"""
    from sqlalchemy import func
    from ..models import Document, ComplianceReport, Booking
    
    doc_count = db.query(func.count(Document.id)).filter(Document.user_id == user_id).scalar()
    report_count = db.query(func.count(ComplianceReport.id)).filter(ComplianceReport.user_id == user_id).scalar()
    booking_count = db.query(func.count(Booking.id)).filter(Booking.user_id == user_id).scalar()
    
    return {
        "documents": doc_count or 0,
        "reports": report_count or 0,
        "bookings": booking_count or 0,
    }
