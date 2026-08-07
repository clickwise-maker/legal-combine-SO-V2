# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 1

# System Architecture

## Overview

Legal Combines OS is a microservices-based legal compliance platform built with:
- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 (React)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Queue**: Celery for background tasks

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                   Next.js 14 + Tailwind                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       API GATEWAY                            │
│                     FastAPI + Uvicorn                        │
├─────────────────────────────────────────────────────────────┤
│  /auth    │  /payments   │  /marketplace  │  /scrape      │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │    Redis     │  │   Government     │
│   (Data)        │  │   (Cache)    │  │   Scrapers       │
└─────────────────┘  └──────────────┘  └──────────────────┘
```

## Components

### Backend Services
- Auth Service: JWT + OTP authentication
- Payment Service: Razorpay integration
- Marketplace Service: Lawyer/Typist bookings
- Scraper Service: Government website sync

### Frontend Pages
- Landing page
- Authentication (Login/Register)
- Subscription plans
- Lawyer marketplace
- Typist marketplace
- User dashboard

## Data Flow

1. User request → Next.js frontend
2. API call → FastAPI backend
3. Validation → Service layer
4. Database operation → PostgreSQL
5. Response → Frontend update
