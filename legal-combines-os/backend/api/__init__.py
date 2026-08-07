"""
Legal Combines OS — API Routes Package
Contains all API route modules.
"""
from . import auth_routes
from . import payment_routes
from . import marketplace_routes
from . import document_routes
from . import workspace_routes

__all__ = [
    "auth_routes",
    "payment_routes",
    "marketplace_routes",
    "document_routes",
    "workspace_routes",
]
