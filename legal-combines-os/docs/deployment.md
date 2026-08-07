# Legal Combines OS — Deployment Guide

## Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git
- 2GB+ RAM

## Quick Deploy

### 1. Clone Repository
```bash
git clone https://github.com/clickwise-maker/legal-combines-os.git
cd legal-combines-os
```

### 2. Environment Setup
```bash
cp .env.example .env
nano .env
```

**Required Environment Variables:**
- `DB_PASSWORD`: Database password
- `SECRET_KEY`: JWT secret key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `RAZORPAY_KEY_ID`: Razorpay public key
- `RAZORPAY_KEY_SECRET`: Razorpay private key

### 3. Deploy
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

### 4. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### AWS EC2
1. Launch Ubuntu 22.04 instance
2. Install Docker and Docker Compose
3. Clone repository
4. Configure .env
5. Run `docker-compose up -d`

## Security Checklist
- [ ] SSL Certificate configured
- [ ] Environment variables secured
- [ ] Database password changed
- [ ] Debug mode disabled
- [ ] Rate limiting enabled

## Troubleshooting

### Database connection failed
```bash
docker-compose logs postgres
```

### Backend not starting
```bash
docker-compose logs backend
```

## Updates
```bash
git pull
docker-compose down
docker-compose up -d --build
```
