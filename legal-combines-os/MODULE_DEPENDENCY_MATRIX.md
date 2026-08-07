# MODULE_DEPENDENCY_MATRIX.md

**Version:** 1.0.0  
**Generated:** 2026-08-06

---

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MODULE DEPENDENCY MATRIX                         │
└─────────────────────────────────────────────────────────────────────────┘

MODULES (Rows) DEPEND ON (Columns)
                        │AUTH│PAY│MKT│SCR│AGT│SKL│TLS│UTL│MOD│SRV│API│
────────────────────────┼────┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
AUTH (Auth Routes)     │ -  │   │   │   │   │   │   │ X │ X │   │ X │
PAY (Payment Routes)    │    │ -  │   │   │   │   │   │   │ X │   │ X │
MKT (Marketplace)      │    │   │ -  │   │   │   │   │   │ X │   │ X │
SCR (Scraper Tools)    │    │   │   │ -  │   │   │   │ X │   │   │   │
AGT (AI Agents)        │    │   │   │   │ -  │ X │   │   │   │   │   │
SKL (AI Skills)        │    │   │   │   │ X │ - │   │   │   │   │   │
TLS (Tools)            │    │   │   │ X │   │   │ - │ X │   │   │   │
UTL (Utils)            │ X  │   │   │ X │   │   │ X │ - │   │   │   │
MOD (Models)           │ X  │ X │ X │   │   │   │   │ X │ - │   │   │
SRV (Services)         │    │   │   │ X │   │   │ X │   │   │ - │   │
API (Main App)         │ X  │ X │ X │ X │   │   │ X │   │ X │   │ - │
────────────────────────┴────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

---

## Detailed Dependency List

### AUTH Module (backend/api/auth_routes.py)
**Depends on:**
- `backend/utils/jwt_utils.py` - JWT generation, password hashing
- `backend/models/user.py` - User model
- `backend/main.py` - App registration

### PAY Module (backend/api/payment_routes.py)
**Depends on:**
- `backend/models/payment.py` - Subscription, Payment models
- `backend/main.py` - App registration

### MKT Module (backend/api/marketplace_routes.py)
**Depends on:**
- `backend/models/lawyer.py` - Lawyer profiles
- `backend/models/typist.py` - Typist profiles
- `backend/models/payment.py` - Commission calculations
- `backend/main.py` - App registration

### SCR Module (backend/tools/govt_scraper_tools.py)
**Depends on:**
- `backend/utils/database.py` - Document storage
- External: requests, beautifulsoup4, tenacity

### AGT Module (backend/agents/*.py)
**Depends on:**
- `backend/skills/*.md` - Skill definitions
- `backend/utils/jwt_utils.py` - Agent authentication

### SKL Module (backend/skills/*.md)
**Depends on:**
- `backend/agents/base_agent.py` - Agent execution context

### TLS Module (backend/tools/*.py)
**Depends on:**
- `backend/utils/jwt_utils.py` - Utility functions
- `backend/utils/database.py` - Data storage

### UTL Module (backend/utils/*.py)
**No internal dependencies**
- External: bcrypt, pyotp, jose, sqlalchemy

### MOD Module (backend/models/*.py)
**Depends on:**
- `backend/utils/database.py` - SQLAlchemy Base

### SRV Module (backend/services/*.py)
**Depends on:**
- `backend/tools/govt_scraper_tools.py` - Scraper factory
- `backend/utils/database.py` - Job history storage

### API Module (backend/main.py)
**Depends on:**
- `backend/api/*_routes.py` - All API routes
- `backend/models/*.py` - All models
- `backend/utils/*.py` - All utilities

---

## Frontend Dependencies

### Frontend/App (frontend/src/app/*)
**Depends on:**
- `frontend/src/lib/api.js` - API client
- `frontend/src/components/*` - React components
- Next.js framework

### Frontend/Components (frontend/src/components/*)
**Depends on:**
- `frontend/src/lib/api.js` - API client
- External: React, Tailwind CSS

### Frontend/Lib (frontend/src/lib/api.js)
**Depends on:**
- `backend/api/*_routes.py` - API endpoints
- External: fetch, localStorage

---

## Execution Order (Based on Dependencies)

```
Level 0 (No dependencies):
├── backend/utils (jwt_utils, database)
├── backend/models (user, payment, lawyer, typist)
└── Root config files

Level 1 (Depends on Level 0):
├── backend/api/auth_routes.py
├── backend/api/payment_routes.py
├── backend/api/marketplace_routes.py
├── backend/tools/govt_scraper_tools.py
└── backend/services/scraper_scheduler.py

Level 2 (Depends on Level 1):
├── backend/main.py (registers all routes)
├── frontend/src/lib/api.js
└── frontend/src/components/*

Level 3 (Depends on Level 2):
├── frontend/src/app/layout.js
├── frontend/src/app/page.js
└── Docker configuration

Level 4 (Depends on Level 3):
├── frontend production build
└── Docker compose

Level 5 (Independent):
├── backend/agents/*
├── backend/skills/*
└── Documentation
```

---

## Circular Dependency Check

✅ **No circular dependencies detected**

The dependency graph is a Directed Acyclic Graph (DAG).
