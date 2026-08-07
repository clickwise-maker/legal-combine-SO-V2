"""
Legal Combines OS — FastAPI Application
"""


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os


from .config import Config
from .api import auth_routes, payment_routes, marketplace_routes, document_routes, workspace_routes


# Create FastAPI app
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.VERSION,
    description="AI-Powered Global Legal Compliance Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=Config.ALLOWED_HOSTS,
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Legal Combines OS API",
        "version": Config.VERSION,
        "status": "running",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": Config.VERSION,
        "environment": "production" if not Config.DEBUG else "development"
    }


# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(payment_routes.router, prefix="/api/payments", tags=["Payments"])
app.include_router(marketplace_routes.router, prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(document_routes.router, prefix="/api/documents", tags=["Documents"])
app.include_router(workspace_routes.router, prefix="/api/workspace", tags=["Workspace"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=Config.DEBUG
    )
