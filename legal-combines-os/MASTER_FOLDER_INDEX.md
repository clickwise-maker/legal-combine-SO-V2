# MASTER_FOLDER_INDEX.md

**Version:** 1.0.0  
**Generated:** 2026-08-06

---

## Folder Index

| Folder ID | Folder Name | Parent Folder | Description | Owner | Phase | Status |
|-----------|-------------|--------------|-------------|-------|-------|--------|
| F007 | root | - | Project root - README, LICENSE, env, git | Project Lead | Phase 1 | 30% |
| F001-01 | backend | F007 | Python FastAPI server, REST API, business logic | Backend Team | Phase 3 | 70% |
| F001-02 | agents | F001-01 | AI agent orchestration, skill routing, agent loops | AI Team | Phase 5 | 10% |
| F001-03 | api | F001-01 | REST API route handlers (Auth, Payments, Marketplace, Scraper) | Backend Team | Phase 3 | 85% |
| F001-04 | models | F001-01 | SQLAlchemy data models, Pydantic schemas | Backend Team | Phase 3 | 80% |
| F001-05 | services | F001-01 | Background workers, schedulers, async tasks | Backend Team | Phase 4 | 70% |
| F001-06 | skills | F001-01 | AI skill definitions (review, research, compliance) | AI Team | Phase 5 | 5% |
| F001-07 | tools | F001-01 | Government scrapers, document tools, web tools | Backend Team | Phase 4 | 60% |
| F001-08 | utils | F001-01 | JWT utilities, database helpers, shared functions | Backend Team | Phase 3 | 75% |
| F002 | frontend | F007 | Next.js 14 web application, React components | Frontend Team | Phase 2 | 30% |
| F002-01 | app | F002 | Next.js App Router pages and layouts | Frontend Team | Phase 2 | 0% |
| F002-02 | components | F002 | React components (Auth, Payment, Dashboard, etc.) | Frontend Team | Phase 2 | 50% |
| F002-03 | lib | F002 | API client, utilities, constants | Frontend Team | Phase 2 | 70% |
| F003 | docker | F007 | Docker containerization configuration | DevOps Team | Phase 6 | 0% |
| F003-01 | backend | F003 | Backend Python container Dockerfile | DevOps Team | Phase 6 | 0% |
| F003-02 | frontend | F003 | Frontend Node container Dockerfile | DevOps Team | Phase 6 | 0% |
| F004 | docs | F007 | Project documentation, architecture diagrams | Documentation Team | Phase 1 | 0% |
| F005 | scripts | F007 | Setup scripts, deployment automation | DevOps Team | Phase 6 | 50% |
| F006 | tests | F007 | Unit tests, integration tests, E2E tests | QA Team | Phase 5 | 0% |

**Total Folders: 19**

---

## Folder Purpose Summary

### Foundation Folders (Phase 1)
- F007 (root) - Project root configuration
- F004 (docs) - Documentation structure

### Core Implementation Folders
- F001-01 (backend) - Python API server
- F002 (frontend) - Next.js application
- F005 (scripts) - Automation scripts

### Service Folders
- F001-05 (services) - Background services
- F001-07 (tools) - Utility tools
- F001-08 (utils) - Shared utilities

### AI Folders (Phase 5)
- F001-02 (agents) - AI orchestration
- F001-06 (skills) - AI skill definitions

### Infrastructure Folders (Phase 6)
- F003 (docker) - Containerization
- F006 (tests) - Testing suite
