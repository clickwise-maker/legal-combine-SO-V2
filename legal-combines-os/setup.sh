#!/bin/bash

echo "🚀 Setting up Legal Combines OS..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Create .env from example
cp .env.example .env

echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "1. Edit .env with your API keys"
echo "2. docker-compose up -d"