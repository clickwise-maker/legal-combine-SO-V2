# CHANGELOG.md

**Legal Combines OS - Version History**

---

## [1.0.0] - 2026-08-06 - Framework Baseline

### Added
- **Framework Structure**
  - Permanent folder ID system (F001-F006)
  - Code placement matrix
  - Dependency tree
  - Implementation sequence

- **Backend Modules**
  - `backend/api/auth_routes.py` - JWT authentication with login, register, OTP
  - `backend/api/payment_routes.py` - Razorpay payment integration
  - `backend/api/marketplace_routes.py` - Lawyer/Typist marketplace with 12% commission
  - `backend/models/user.py` - User model with roles, OTP, lockout
  - `backend/models/payment.py` - Subscription plans, Payment, Commission models
  - `backend/models/lawyer.py` - LawyerProfile, Booking, Review
  - `backend/models/typist.py` - TypistProfile, DocumentOrder
  - `backend/tools/govt_scraper_tools.py` - Government website scrapers (RBI, SEBI, MCA, Gazette)
  - `backend/services/scraper_scheduler.py` - APScheduler-based weekly sync
  - `backend/utils/jwt_utils.py` - JWT generation, OTP, password hashing
  - `backend/utils/database.py` - SQLAlchemy models, search, stats

- **Frontend Modules**
  - `frontend/src/components/Auth/LoginForm.js` - Login form with validation
  - `frontend/src/components/Auth/RegisterForm.js` - Multi-step registration with OTP
  - `frontend/src/components/Payment/CheckoutButton.js` - Razorpay checkout
  - `frontend/src/lib/api.js` - API client with auth & payment methods

- **Configuration Files**
  - `requirements.txt` - Python dependencies
  - `setup.sh` - Environment setup

- **Documentation**
  - `FRAMEWORK_MANIFEST.md` - Complete framework structure
  - `MASTER_FOLDER_INDEX.md` - Folder catalog
  - `FILE_INDEX.md` - File catalog
  - `MODULE_DEPENDENCY_MATRIX.md` - Dependency graph
  - `IMPLEMENTATION_SEQUENCE.md` - Development order
  - `ROADMAP.md` - Phase-by-phase plan

### Placeholder Files (To Be Implemented)
- `docker-compose.yml` - Docker orchestration
- `docker/backend/Dockerfile` - Backend container
- `docker/frontend/Dockerfile` - Frontend container
- `frontend/package.json` - Node dependencies
- `frontend/next.config.js` - Next.js config
- `frontend/tailwind.config.js` - Tailwind config
- `frontend/postcss.config.js` - PostCSS config
- `frontend/src/app/layout.js` - Next.js layout
- `frontend/src/app/page.js` - Home page
- `frontend/src/app/globals.css` - Global styles
- `backend/__init__.py` - Package init
- `backend/config.py` - App configuration
- `backend/agents/*.py` - AI agent system
- `backend/skills/*/SKILL.md` - AI skill definitions
- `backend/tools/web_tools.py` - Web utilities
- `backend/tools/document_tools.py` - Document processing
- `backend/tools/form_filler_tools.py` - Form auto-fill
- `docs/architecture.md` - Architecture docs
- `tests/test_api.py` - Integration tests
- `README.md` - Project documentation
- `LICENSE` - License file
- `.env.example` - Environment template

### Known Issues
- None

### Dependencies Added
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1
pyotp==2.9.0
pydantic[email]==2.5.0
razorpay==1.4.2
python-multipart==0.0.6
requests==2.31.0
beautifulsoup4==4.12.2
lxml==5.0.0
tenacity==8.2.3
APScheduler==3.10.4
SQLAlchemy==2.0.23
```

---

## [0.0.0] - 2026-08-06 - Project Initialization

### Added
- Initial folder structure
- Docker configuration templates
- Placeholder files for all modules

---

## Version Format

Format: `[MAJOR.MINOR.PATCH]`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Schedule
- Version 0.1: MVP with core modules
- Version 0.2: Frontend completion
- Version 0.3: Testing & CI/CD
- Version 1.0: Production ready

---

## Contact

For questions about this changelog, contact the Legal Combines OS development team.
