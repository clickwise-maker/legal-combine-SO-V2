"""
Document Models — Uploads, Analysis, Compliance Reports
"""


import uuid
from datetime import datetime
from enum import Enum as PyEnum


from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Integer, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


from ..utils.database import Base


class DocumentType(str, PyEnum):
    CONTRACT = "contract"
    LEGAL_NOTICE = "legal_notice"
    AFFIDAVIT = "affidavit"
    PLEADING = "pleading"
    AGREEMENT = "agreement"
    OTHER = "other"


class DocumentStatus(str, PyEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    REVIEWED = "reviewed"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    ERROR = "error"


class Document(Base):
    __tablename__ = "documents"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(100), nullable=False)  # pdf, docx, txt, etc.
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    doc_metadata = Column("metadata", JSON, nullable=True)  # extracted metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Relationships
    user = relationship("User", back_populates="documents")
    workspace = relationship("Workspace", back_populates="documents")
    analysis = relationship("Analysis", back_populates="document", uselist=False)
    compliance_reports = relationship("ComplianceReport", back_populates="document")


class Analysis(Base):
    __tablename__ = "analyses"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), unique=True)
    entity_classification = Column(JSON, nullable=True)
    geo_scope = Column(JSON, nullable=True)
    compliance_score = Column(Float, nullable=True)
    missing_laws = Column(JSON, nullable=True)
    red_flags = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    document = relationship("Document", back_populates="analysis")


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    report_type = Column(String(50), default="auto")  # auto, manual
    score = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    findings = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    document = relationship("Document", back_populates="compliance_reports")
