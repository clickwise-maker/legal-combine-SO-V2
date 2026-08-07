"""
Workspace API Routes
Handles workspace management and user settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()


# Pydantic Models
class WorkspaceCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_type: str = "personal"  # "personal", "team", "enterprise"


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None


class WorkspaceResponse(BaseModel):
    workspace_id: str
    name: str
    description: Optional[str]
    workspace_type: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


class MemberAddRequest(BaseModel):
    user_id: str
    role: str = "member"  # "owner", "admin", "member", "viewer"


class WorkspaceListResponse(BaseModel):
    workspaces: List[dict]
    total: int


# Routes
@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(request: WorkspaceCreateRequest, user_id: str = "demo"):
    """Create a new workspace."""
    workspace_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    return {
        "workspace_id": workspace_id,
        "name": request.name,
        "description": request.description,
        "workspace_type": request.workspace_type,
        "owner_id": user_id,
        "created_at": now,
        "updated_at": now
    }


@router.get("/", response_model=WorkspaceListResponse)
async def list_workspaces(
    page: int = 1,
    per_page: int = 20,
    user_id: Optional[str] = None
):
    """List all workspaces for the current user."""
    return {
        "workspaces": [],
        "total": 0
    }


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str):
    """Get workspace details."""
    return {
        "workspace_id": workspace_id,
        "name": "Demo Workspace",
        "description": "Workspace description",
        "workspace_type": "personal",
        "owner_id": "demo",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    request: WorkspaceUpdateRequest
):
    """Update workspace settings."""
    return {
        "workspace_id": workspace_id,
        "name": request.name or "Updated Workspace",
        "description": request.description,
        "workspace_type": "personal",
        "owner_id": "demo",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """Delete a workspace."""
    return {"status": "deleted", "workspace_id": workspace_id}


@router.post("/{workspace_id}/members")
async def add_member(
    workspace_id: str,
    request: MemberAddRequest
):
    """Add a member to the workspace."""
    return {
        "workspace_id": workspace_id,
        "user_id": request.user_id,
        "role": request.role,
        "added_at": datetime.utcnow().isoformat()
    }


@router.get("/{workspace_id}/members")
async def list_members(workspace_id: str):
    """List workspace members."""
    return {"members": [], "total": 0}


@router.delete("/{workspace_id}/members/{member_id}")
async def remove_member(workspace_id: str, member_id: str):
    """Remove a member from workspace."""
    return {"status": "removed", "member_id": member_id}
