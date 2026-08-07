# Contributing to Legal Combines OS

## Guidelines

### Code Style
- Python: PEP 8
- JavaScript: ESLint + Prettier
- Commit messages: Conventional Commits

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## Project Structure
```
backend/          # FastAPI backend
frontend/         # Next.js frontend
docker/           # Dockerfiles
docs/             # Documentation
scripts/           # Deployment scripts
```

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

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] PR description complete

## Security
- Never commit secrets
- Report vulnerabilities privately
- Use environment variables

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
