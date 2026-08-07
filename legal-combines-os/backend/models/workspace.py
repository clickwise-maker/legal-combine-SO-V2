"""
Workspace Models — Collaboration, Sharing, Members
"""


import uuid
from datetime import datetime


from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


from ..utils.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Relationships
    owner = relationship("User")
    documents = relationship("Document", back_populates="workspace")
    members = relationship("WorkspaceMember", back_populates="workspace")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String(50), default="viewer")  # owner, admin, editor, viewer
    joined_at = Column(DateTime, default=datetime.utcnow)


    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")
