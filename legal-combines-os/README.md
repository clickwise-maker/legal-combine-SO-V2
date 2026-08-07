# Legal Combines OS Deep V2

AI-Powered Global Legal Compliance Platform — Deep Edition

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/clickwise-maker/legal-combines-os.git
cd legal-combines-os

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run with Docker
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [API Endpoints](#-api-endpoints)
- [Development](#-development)
- [Deployment](#-deployment)
- [License](#-license)

## ✨ Features

### 🔐 Authentication
- JWT-based authentication
- Two-factor OTP verification (TOTP)
- Account lockout protection
- Role-based access control (Admin, Lawyer, Client, Guest)

### 💳 Payments
- Razorpay integration
- Subscription plans (Basic, Professional, Enterprise)
- Commission tracking (12% marketplace)
- Webhook support

### 🏛️ Marketplace
- **Lawyers**: Specializations, hourly rates, ratings, bookings
- **Typists**: Typing speed, document types, order management

### 🔍 Government Scraper
- India Gazette integration
- RBI, SEBI, MCA, DGTR support
- Weekly automated sync
- BeautifulSoup4 + async HTTP

### 🤖 AI Agents
- Document Review skill
- Legal Research skill
- Compliance Check skill
- Agent orchestration framework

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14 + Tailwind CSS |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| AI/LLM | DeepSeek + Ollama + OpenRouter |
| Auth | JWT + OTP + 2FA |
| Payments | Razorpay |
| Deployment | Docker Compose + Nginx |

## 🏗️ Architecture

```
legal-combines-os/
├── backend/
│   ├── api/           # Routes (auth, payments, marketplace)
│   ├── models/        # SQLAlchemy models
│   ├── tools/         # Scrapers, document tools
│   ├── services/      # Scheduler, LLM clients
│   └── utils/         # JWT, database, security
├── frontend/
│   ├── src/
│   │   ├── app/       # Next.js pages
│   │   ├── components/ # Auth, Payment components
│   │   └── lib/       # API client
│   └── package.json
├── docker/            # Dockerfiles
├── docs/              # Architecture, setup guides
└── scripts/           # Setup and deployment scripts
```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/verify-otp` | OTP verification |
| POST | `/api/auth/refresh` | Token refresh |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments/plans` | List subscription plans |
| POST | `/api/payments/create-order` | Create payment order |
| POST | `/api/payments/confirm` | Confirm subscription |
| POST | `/api/payments/webhook` | Razorpay webhook |

### Marketplace
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/marketplace/lawyers` | List lawyers |
| GET | `/api/marketplace/lawyers/{id}` | Lawyer details |
| POST | `/api/marketplace/book-lawyer` | Book consultation |
| GET | `/api/marketplace/typists` | List typists |
| POST | `/api/marketplace/order` | Create document order |

### Scraper
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scrape/trigger` | Trigger scrape job |
| GET | `/api/scrape/status` | Get scrape status |

## 🖥️ Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose

### Local Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=sqlite:///legal_combines.db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Razorpay
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RAZORPAY_KEY=your-public-key
```

## 🚀 Deployment

### Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Deployment

```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Frontend
cd frontend
npm run build
npm start
```

## 📄 License

MIT © clickwise-maker

## 🤝 Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.
