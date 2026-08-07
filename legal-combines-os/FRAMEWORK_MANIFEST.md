# Legal Combines OS - Framework Manifest
**Version:** 1.0.0  
**Generated:** 2026-08-06  
**Status:** FOUNDATION PHASE

---

## SECTION 1: FOLDER STRUCTURE OVERVIEW

### Total Folders: 26
### Total Files: 57

### Top-Level Folders (9)

| ID | Folder Name | Purpose |
|----|-------------|---------|
| F001 | backend | Core Python API server |
| F002 | frontend | Next.js web application |
| F003 | docker | Containerization configuration |
| F004 | docs | Documentation |
| F005 | scripts | Deployment & utility scripts |
| F006 | tests | Test suites |
| F007 | . | Root configuration files |

---

## SECTION 2: PERMANENT FOLDER ID SYSTEM

All folder IDs are permanent and MUST NOT be changed.

```
F001   ROOT PROJECT
├── F001-01  backend              # Python API
├── F001-02  backend/agents       # AI agent system
├── F001-03  backend/api         # REST API routes
├── F001-04  backend/models       # Data models
├── F001-05  backend/services     # Background services
├── F001-06  backend/skills       # AI skill definitions
├── F001-07  backend/tools        # Utility tools
├── F001-08  backend/utils        # Shared utilities
├── F002     frontend             # Next.js application
├── F002-01  frontend/src/app     # Next.js pages
├── F002-02  frontend/src/components  # React components
├── F002-03  frontend/src/lib     # Client utilities
├── F003     docker               # Container configs
├── F003-01  docker/backend       # Backend container
├── F003-02  docker/frontend      # Frontend container
├── F004     docs                 # Documentation
├── F005     scripts              # Automation scripts
├── F006     tests                # Test suites
└── F007     .                    # Root config (.env, README, etc)
```

---

## SECTION 3: DETAILED FOLDER CATALOG

### F001-01 | backend
| Attribute | Value |
|-----------|-------|
| **Name** | backend |
| **Full Path** | `./backend/` |
| **Purpose** | Python FastAPI server - REST API, business logic, integrations |
| **Current Status** | IMPLEMENTATION (70%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 3: Backend Core |
| **Dependencies** | FastAPI, SQLAlchemy, Pydantic |
| **Owner** | Backend Team |
| **Files** | 11 (.py files, 1 __init__) |

### F001-02 | backend/agents
| Attribute | Value |
|-----------|-------|
| **Name** | agents |
| **Full Path** | `./backend/agents/` |
| **Purpose** | AI agent orchestration, skill routing, agent loops |
| **Current Status** | FOUNDATION (10%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 5: AI Integration |
| **Dependencies** | F001-01, F001-06 |
| **Owner** | AI Team |
| **Files** | 3 (placeholders) |

### F001-03 | backend/api
| Attribute | Value |
|-----------|-------|
| **Name** | api |
| **Full Path** | `./backend/api/` |
| **Purpose** | REST API route handlers (Auth, Payments, Marketplace, Scraper) |
| **Current Status** | IMPLEMENTATION (85%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 3: Backend Core |
| **Dependencies** | F001-01, F001-04, F001-08 |
| **Owner** | Backend Team |
| **Files** | 3 route modules |

### F001-04 | backend/models
| Attribute | Value |
|-----------|-------|
| **Name** | models |
| **Full Path** | `./backend/models/` |
| **Purpose** | SQLAlchemy data models, Pydantic schemas |
| **Current Status** | IMPLEMENTATION (80%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 3: Backend Core |
| **Dependencies** | F001-01, F001-08 |
| **Owner** | Backend Team |
| **Files** | 4 models |

### F001-05 | backend/services
| Attribute | Value |
|-----------|-------|
| **Name** | services |
| **Full Path** | `./backend/services/` |
| **Purpose** | Background workers, schedulers, async tasks |
| **Current Status** | IMPLEMENTATION (70%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 4: Background Services |
| **Dependencies** | F001-01, F001-07 |
| **Owner** | Backend Team |
| **Files** | 1 service (scraper_scheduler) |

### F001-06 | backend/skills
| Attribute | Value |
|-----------|-------|
| **Name** | skills |
| **Full Path** | `./backend/skills/` |
| **Purpose** | AI skill definitions (review, research, compliance) |
| **Current Status** | FOUNDATION (5%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 5: AI Integration |
| **Dependencies** | F001-02 |
| **Owner** | AI Team |
| **Files** | 3 SKILL.md (empty) |

### F001-07 | backend/tools
| Attribute | Value |
|-----------|-------|
| **Name** | tools |
| **Full Path** | `./backend/tools/` |
| **Purpose** | Government scrapers, document tools, web tools |
| **Current Status** | IMPLEMENTATION (60%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 4: Background Services |
| **Dependencies** | F001-01 |
| **Owner** | Backend Team |
| **Files** | 4 tool modules |

### F001-08 | backend/utils
| Attribute | Value |
|-----------|-------|
| **Name** | utils |
| **Full Path** | `./backend/utils/` |
| **Purpose** | JWT utilities, database helpers, shared functions |
| **Current Status** | IMPLEMENTATION (75%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 3: Backend Core |
| **Dependencies** | F001-01 |
| **Owner** | Backend Team |
| **Files** | 2 utility modules |

### F002 | frontend
| Attribute | Value |
|-----------|-------|
| **Name** | frontend |
| **Full Path** | `./frontend/` |
| **Purpose** | Next.js 14 web application, React components |
| **Current Status** | FOUNDATION (30%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 2: Frontend Foundation |
| **Dependencies** | Node.js 18+, React 18 |
| **Owner** | Frontend Team |
| **Files** | 4 config files (empty) |

### F002-01 | frontend/src/app
| Attribute | Value |
|-----------|-------|
| **Name** | app |
| **Full Path** | `./frontend/src/app/` |
| **Purpose** | Next.js App Router pages and layouts |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 2: Frontend Foundation |
| **Dependencies** | F002 |
| **Owner** | Frontend Team |
| **Files** | 4 (empty placeholders) |

### F002-02 | frontend/src/components
| Attribute | Value |
|-----------|-------|
| **Name** | components |
| **Full Path** | `./frontend/src/components/` |
| **Purpose** | React components (Auth, Payment, Dashboard, etc.) |
| **Current Status** | IMPLEMENTATION (50%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 2: Frontend Foundation |
| **Dependencies** | F002, F002-03 |
| **Owner** | Frontend Team |
| **Files** | 3 implemented components |

### F002-03 | frontend/src/lib
| Attribute | Value |
|-----------|-------|
| **Name** | lib |
| **Full Path** | `./frontend/src/lib/` |
| **Purpose** | API client, utilities, constants |
| **Current Status** | IMPLEMENTATION (70%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 2: Frontend Foundation |
| **Dependencies** | F002 |
| **Owner** | Frontend Team |
| **Files** | 1 API client |

### F003 | docker
| Attribute | Value |
|-----------|-------|
| **Name** | docker |
| **Full Path** | `./docker/` |
| **Purpose** | Docker containerization configuration |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 6: DevOps |
| **Dependencies** | F001-01, F002 |
| **Owner** | DevOps Team |
| **Files** | 3 files (empty) |

### F003-01 | docker/backend
| Attribute | Value |
|-----------|-------|
| **Name** | backend |
| **Full Path** | `./docker/backend/` |
| **Purpose** | Backend Python container Dockerfile |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 6: DevOps |
| **Dependencies** | F003 |
| **Owner** | DevOps Team |
| **Files** | 1 Dockerfile (empty) |

### F003-02 | docker/frontend
| Attribute | Value |
|-----------|-------|
| **Name** | frontend |
| **Full Path** | `./docker/frontend/` |
| **Purpose** | Frontend Node container Dockerfile |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 6: DevOps |
| **Dependencies** | F003 |
| **Owner** | DevOps Team |
| **Files** | 1 Dockerfile (empty) |

### F004 | docs
| Attribute | Value |
|-----------|-------|
| **Name** | docs |
| **Full Path** | `./docs/` |
| **Purpose** | Project documentation, architecture diagrams |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 1: Foundation |
| **Dependencies** | None |
| **Owner** | Documentation Team |
| **Files** | 1 (empty) |

### F005 | scripts
| Attribute | Value |
|-----------|-------|
| **Name** | scripts |
| **Full Path** | `./scripts/` |
| **Purpose** | Setup scripts, deployment automation |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 6: DevOps |
| **Dependencies** | F001-01, F002 |
| **Owner** | DevOps Team |
| **Files** | 1 script |

### F006 | tests
| Attribute | Value |
|-----------|-------|
| **Name** | tests |
| **Full Path** | `./tests/` |
| **Purpose** | Unit tests, integration tests, E2E tests |
| **Current Status** | FOUNDATION (0%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 3: Testing |
| **Dependencies** | F001-01, F002 |
| **Owner** | QA Team |
| **Files** | 1 (empty placeholder) |

### F007 | Root Configuration
| Attribute | Value |
|-----------|-------|
| **Name** | Root |
| **Full Path** | `./` |
| **Purpose** | Project root - README, LICENSE, env, git |
| **Current Status** | FOUNDATION (30%) |
| **Planned Status** | PRODUCTION |
| **Phase** | Phase 1: Foundation |
| **Dependencies** | None |
| **Owner** | Project Lead |
| **Files** | 6 config files |

---

## SECTION 4: CODE PLACEMENT MATRIX

### AUTH SYSTEM
```
BACKEND AUTH
└── F001-03/backend/api/auth_routes.py     # Login, Register, OTP, JWT
└── F001-04/backend/models/user.py           # User model with roles
└── F001-08/backend/utils/jwt_utils.py       # JWT generation, OTP, bcrypt

FRONTEND AUTH
└── F002-02/frontend/src/components/Auth/LoginForm.js
└── F002-02/frontend/src/components/Auth/RegisterForm.js
└── F002-03/frontend/src/lib/api.js           # Auth API methods
```

### PAYMENTS SYSTEM
```
BACKEND PAYMENTS
└── F001-03/backend/api/payment_routes.py   # Razorpay integration
└── F001-04/backend/models/payment.py        # Subscription, Payment models

FRONTEND PAYMENTS
└── F002-02/frontend/src/components/Payment/CheckoutButton.js
└── F002-03/frontend/src/lib/api.js           # Payment API methods
```

### MARKETPLACE SYSTEM
```
BACKEND MARKETPLACE
└── F001-03/backend/api/marketplace_routes.py  # Lawyer/Typist endpoints
└── F001-04/backend/models/lawyer.py            # Lawyer profiles, bookings
└── F001-04/backend/models/typist.py           # Typist profiles, orders
```

### SCRAPER SYSTEM
```
BACKEND SCRAPER
└── F001-07/backend/tools/govt_scraper_tools.py  # Government website scrapers
└── F001-05/backend/services/scraper_scheduler.py  # APScheduler-based jobs
└── F001-08/backend/utils/database.py              # Document storage
```

### AI AGENTS
```
BACKEND AI
└── F001-02/backend/agents/base_agent.py        # Base agent class
└── F001-02/backend/agents/agent_loop.py        # Agent execution loop
└── F001-02/backend/agents/skill_router.py      # Skill routing
└── F001-06/backend/skills/review/SKILL.md      # Review skill
└── F001-06/backend/skills/research/SKILL.md    # Research skill
└── F001-06/backend/skills/compliance/SKILL.md  # Compliance skill
```

### INFRASTRUCTURE
```
DOCKER
└── F003/docker/docker-compose.yml              # Service orchestration
└── F003-01/docker/backend/Dockerfile          # Backend container
└── F003-02/docker/frontend/Dockerfile         # Frontend container

CONFIGURATION
└── F007/.env.example                          # Environment template
└── F007/.gitignore                            # Git exclusions
└── F007/requirements.txt                      # Python dependencies
└── F002/frontend/package.json                  # Node dependencies
```

---

## SECTION 5: PHASE CLASSIFICATION

### FRAMEWORK (Folders that define the project structure)
```
F001   backend
F002   frontend
F003   docker
F004   docs
F005   scripts
F006   tests
F007   . (root)
```

### FOUNDATION (Phase 1 - Must complete first)
```
F007   Root configuration (README, LICENSE, .env)
F004   docs/architecture.md
F005   scripts/setup.sh
```

### IMPLEMENTATION (Phase 2-4 - Core development)
```
F001-01   backend (main.py, __init__.py, config.py)
F001-03   backend/api (auth, payment, marketplace routes)
F001-04   backend/models (user, payment, lawyer, typist)
F001-07   backend/tools (govt_scraper_tools)
F001-08   backend/utils (jwt_utils, database)
F001-05   backend/services (scraper_scheduler)
F002      frontend (package.json, configs)
F002-01   frontend/src/app (pages, layouts)
F002-02   frontend/src/components (Auth, Payment)
F002-03   frontend/src/lib (api.js)
```

### TESTING (Phase 5)
```
F006   tests/test_api.py
```

### PRODUCTION (Phase 6 - Deployment)
```
F003   docker (Dockerfiles, compose)
F001-02   backend/agents (AI orchestration)
F001-06   backend/skills (AI skills)
```

---

## SECTION 6: COMPLETE DEPENDENCY TREE

```
legal-combines-os (F007)
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── docker-compose.yml
│
├── backend (F001-01)
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   │
│   ├── agents (F001-02) ⚠️ AI Module
│   │   ├── base_agent.py
│   │   ├── agent_loop.py
│   │   └── skill_router.py
│   │   └── [DEPENDS ON: F001-06]
│   │
│   ├── api (F001-03)
│   │   ├── auth_routes.py
│   │   │   └── [DEPENDS ON: F001-04, F001-08]
│   │   ├── payment_routes.py
│   │   │   └── [DEPENDS ON: F001-04]
│   │   └── marketplace_routes.py
│   │       └── [DEPENDS ON: F001-04]
│   │
│   ├── models (F001-04)
│   │   ├── user.py
│   │   ├── payment.py
│   │   ├── lawyer.py
│   │   └── typist.py
│   │   └── [DEPENDS ON: F001-08]
│   │
│   ├── services (F001-05)
│   │   └── scraper_scheduler.py
│   │       └── [DEPENDS ON: F001-07]
│   │
│   ├── skills (F001-06) ⚠️ AI Module
│   │   ├── review/SKILL.md
│   │   ├── research/SKILL.md
│   │   └── compliance/SKILL.md
│   │   └── [DEPENDS ON: F001-02]
│   │
│   ├── tools (F001-07)
│   │   ├── govt_scraper_tools.py
│   │   │   └── [DEPENDS ON: F001-08]
│   │   ├── web_tools.py ⚠️ PLACEHOLDER
│   │   ├── document_tools.py ⚠️ PLACEHOLDER
│   │   └── form_filler_tools.py ⚠️ PLACEHOLDER
│   │
│   └── utils (F001-08)
│       ├── jwt_utils.py
│       └── database.py
│
├── frontend (F002)
│   ├── package.json ⚠️ EMPTY
│   ├── next.config.js ⚠️ EMPTY
│   ├── tailwind.config.js ⚠️ EMPTY
│   ├── postcss.config.js ⚠️ EMPTY
│   │
│   └── src (F002-00)
│       ├── app (F002-01)
│       │   ├── layout.js ⚠️ EMPTY
│       │   ├── page.js ⚠️ EMPTY
│       │   └── globals.css ⚠️ EMPTY
│       │
│       ├── components (F002-02)
│       │   ├── Auth/
│       │   │   ├── LoginForm.js ✅
│       │   │   └── RegisterForm.js ✅
│       │   └── Payment/
│       │       └── CheckoutButton.js ✅
│       │
│       └── lib (F002-03)
│           └── api.js ✅
│
├── docker (F003)
│   ├── docker-compose.yml ⚠️ EMPTY
│   ├── backend/ (F003-01)
│   │   └── Dockerfile ⚠️ EMPTY
│   └── frontend/ (F003-02)
│       └── Dockerfile ⚠️ EMPTY
│
├── docs (F004)
│   └── architecture.md ⚠️ EMPTY
│
├── scripts (F005)
│   └── setup.sh
│
└── tests (F006)
    └── test_api.py ⚠️ EMPTY
```

---

## SECTION 7: EXECUTION ORDER

### Phase 1: Foundation (Week 1)
```
1.1  Create F007 root config files
1.2  Create F004 docs structure
1.3  Create F005 scripts
     ↓
[CHECKPOINT: Basic project structure complete]
```

### Phase 2: Frontend Foundation (Week 2)
```
2.1  Populate F002 package.json
2.2  Create F002-01 app pages (layout, page)
2.3  Create F002-02 Auth components
2.4  Create F002-02 Payment components
2.5  Create F002-03 api.js client
     ↓
[CHECKPOINT: Frontend UI ready for backend]
```

### Phase 3: Backend Core (Week 3)
```
3.1  Implement F001-01 main.py
3.2  Implement F001-03 auth_routes.py
3.3  Implement F001-03 payment_routes.py
3.4  Implement F001-04 all models
3.5  Implement F001-08 jwt_utils.py
3.6  Implement F001-08 database.py
3.7  Implement F002-03 api.js complete
     ↓
[CHECKPOINT: Core API functional]
```

### Phase 4: Background Services (Week 4)
```
4.1  Implement F001-07 govt_scraper_tools.py
4.2  Implement F001-05 scraper_scheduler.py
4.3  Implement F001-03 marketplace_routes.py
4.4  Implement F001-04 lawyer/typist models
     ↓
[CHECKPOINT: Scraper & marketplace ready]
```

### Phase 5: Testing (Week 5)
```
5.1  Populate F006 test_api.py
5.2  Create integration tests
5.3  Create E2E tests
     ↓
[CHECKPOINT: All features tested]
```

### Phase 6: DevOps (Week 6)
```
6.1  Create F003-01 backend Dockerfile
6.2  Create F003-02 frontend Dockerfile
6.3  Create F003 docker-compose.yml
6.4  Implement F001-02 agents
6.5  Create F001-06 SKILL.md files
     ↓
[CHECKPOINT: Production ready]
```

---

## SECTION 8: FOLDER NUMBERING SYSTEM

Permanent IDs that NEVER change:

```
F001-01   backend
F001-02   backend/agents
F001-03   backend/api
F001-04   backend/models
F001-05   backend/services
F001-06   backend/skills
F001-07   backend/tools
F001-08   backend/utils
F002      frontend
F002-01   frontend/src/app
F002-02   frontend/src/components
F002-03   frontend/src/lib
F003      docker
F003-01   docker/backend
F003-02   docker/frontend
F004      docs
F005      scripts
F006      tests
F007      . (root)
```

### Numbering Rules:
1. **F** prefix = Folder
2. **First 3 digits** = Top-level category
3. **Hyphenated digits** = Subdirectories (max depth: 2)
4. **IDs are permanent** - never reassign

---

## SECTION 9: FRAMEWORK MAP

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    LEGAL COMBINES OS - FRAMEWORK MAP                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║   ┌─────────────────────────────────────────────────────────────────┐    ║
║   │ F007 ROOT (F001-08, F002-03, F003, F004, F005, F006)            │    ║
║   └─────────────────────────────────────────────────────────────────┘    ║
║                              │                                           ║
║              ┌──────────────┼──────────────┐                           ║
║              ▼              ▼              ▼                           ║
║   ┌─────────────────┐ ┌───────────┐ ┌─────────────┐                     ║
║   │ F001 BACKEND    │ │ F002      │ │ F003 DOCKER │                     ║
║   │ (Python API)    │ │ FRONTEND  │ │ (Containers)│                     ║
║   │                 │ │ (Next.js) │ │             │                     ║
║   │ ┌─────────────┐ │ │           │ │ ┌─────────┐ │                     ║
║   │ │ F001-02     │ │ │ ┌───────┐ │ │ │F003-01  │ │                     ║
║   │ │ AGENTS (AI) │ │ │ │F002-01│ │ │ │BACKEND  │ │                     ║
║   │ └─────────────┘ │ │ │  APP  │ │ │ └─────────┘ │                     ║
║   │ ┌─────────────┐ │ │ └───────┘ │ │ ┌─────────┐ │                     ║
║   │ │ F001-03 API │ │ │ ┌───────┐ │ │ │F003-02  │ │                     ║
║   │ │ Routes      │ │ │ │F002-02│ │ │ │FRONTEND │ │                     ║
║   │ └─────────────┘ │ │ │COMPS  │ │ │ └─────────┘ │                     ║
║   │ ┌─────────────┐ │ │ └───────┘ │ └─────────────┘                     ║
║   │ │ F001-04     │ │ │ ┌───────┐ │                                    ║
║   │ │ MODELS      │ │ │ │F002-03│ │                                    ║
║   │ └─────────────┘ │ │ │  LIB  │ │                                    ║
║   │ ┌─────────────┐ │ │ └───────┘ │                                    ║
║   │ │ F001-05     │ │ └───────────┘                                    ║
║   │ │ SERVICES    │ │                                                  ║
║   │ └─────────────┘ │                                                  ║
║   │ ┌─────────────┐ │                                                  ║
║   │ │ F001-06     │ │                                                  ║
║   │ │ SKILLS (AI) │ │                                                  ║
║   │ └─────────────┘ │                                                  ║
║   │ ┌─────────────┐ │                                                  ║
║   │ │ F001-07     │ │                                                  ║
║   │ │ TOOLS       │ │                                                  ║
║   │ └─────────────┘ │                                                  ║
║   │ ┌─────────────┐ │                                                  ║
║   │ │ F001-08     │ │                                                  ║
║   │ │ UTILS       │ │                                                  ║
║   │ └─────────────┘ │                                                  ║
║   └─────────────────┘                                                  ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

LEGEND:
┌─────┐ = Folder
│     │ = Dependency connection
▼     │ = Execution direction
```

---

## SECTION 10: STATUS SUMMARY

| Folder | ID | Status | Priority |
|--------|----|--------|----------|
| Root Config | F007 | 30% | P1 |
| Backend | F001-01 | 70% | P1 |
| Backend/Agents | F001-02 | 10% | P3 |
| Backend/API | F001-03 | 85% | P1 |
| Backend/Models | F001-04 | 80% | P1 |
| Backend/Services | F001-05 | 70% | P2 |
| Backend/Skills | F001-06 | 5% | P3 |
| Backend/Tools | F001-07 | 60% | P2 |
| Backend/Utils | F001-08 | 75% | P1 |
| Frontend | F002 | 30% | P1 |
| Frontend/App | F002-01 | 0% | P1 |
| Frontend/Components | F002-02 | 50% | P1 |
| Frontend/Lib | F002-03 | 70% | P1 |
| Docker | F003 | 0% | P3 |
| Docker/Backend | F003-01 | 0% | P3 |
| Docker/Frontend | F003-02 | 0% | P3 |
| Docs | F004 | 0% | P2 |
| Scripts | F005 | 50% | P2 |
| Tests | F006 | 0% | P2 |

**Overall Progress: 45%**

---

## SECTION 11: OWNERSHIP MATRIX

| Team | Folders | Priority Work |
|------|---------|---------------|
| Backend Team | F001-01, F001-03, F001-04, F001-08 | API, Models, Utils |
| AI Team | F001-02, F001-06 | Agents, Skills |
| Frontend Team | F002, F002-01, F002-02, F002-03 | UI, Components |
| DevOps Team | F003, F003-01, F003-02, F005 | Docker, Scripts |
| QA Team | F006 | Tests |
| Documentation | F004 | Docs |

---

**END OF FRAMEWORK MANIFEST**
**Document ID:** LCO-FM-001
**Version:** 1.0.0
