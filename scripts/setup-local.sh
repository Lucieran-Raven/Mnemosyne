#!/bin/bash
set -e

echo "🧠 Mnemosyne Development Environment Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "${RED}Docker is required but not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "${RED}Docker Compose is required but not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "${RED}Python 3.9+ is required but not installed. Please install Python first.${NC}"
    exit 1
fi

echo "${GREEN}✓ Prerequisites met${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Mnemosyne Environment Configuration

# API Keys (fill these in)
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_HOST=your_pinecone_host_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Database (local development)
DATABASE_URL=postgresql+asyncpg://mnemosyne:mnemosyne_dev_password@localhost:5432/mnemosyne
REDIS_URL=redis://localhost:6379/0

# Optional
SENTRY_DSN=
EOF
    echo "${YELLOW}! Please edit .env file and add your API keys${NC}"
fi

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d .venv ]; then
    python -m venv .venv
fi

source .venv/bin/activate

# Install API dependencies
echo "Installing API dependencies..."
pip install -r api/requirements.txt

# Install SDK
echo "Installing SDK..."
pip install -e sdk/

# Install CLI
echo "Installing CLI..."
pip install -e cli/

# Start services
echo "Starting local services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
cd api
alembic upgrade head 2>/dev/null || echo "Note: Alembic migrations not set up yet"
cd ..

echo ""
echo "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your API keys"
echo "  2. Run: docker-compose up -d"
echo "  3. API will be available at http://localhost:8000"
echo "  4. Dashboard will be available at http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  mnemosyne status     - Check all services"
echo "  mnemosyne dev start  - Start all development services"
echo "  mnemosyne test       - Run all tests"
