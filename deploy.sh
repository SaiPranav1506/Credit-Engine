#!/bin/bash
# Deploy script for Linux/Mac
# Usage: ./deploy.sh [dev|docker|test]

set -e

MODE="${1:-dev}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Credit Engine Full Stack Deployment${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Helper functions
info() {
    echo -e "${BLUE}➜ $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Check prerequisites
info "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 not found. Please install Python 3.9+"
fi
success "Python found: $(python3 --version)"

# Check Node/npm
if ! command -v node &> /dev/null; then
    error "Node.js not found. Please install Node 18+"
fi
success "Node found: $(node --version), npm: $(npm --version)"

# Main deployment logic
case $MODE in
    dev)
        echo ""
        echo -e "${YELLOW}Starting in DEVELOPMENT mode${NC}"
        echo ""

        # Check virtual environment
        if [ ! -d "venv" ]; then
            info "Creating Python virtual environment..."
            python3 -m venv venv
            success "Virtual environment created"
        fi

        # Activate venv
        info "Activating Python virtual environment..."
        source venv/bin/activate

        # Install Python dependencies
        info "Installing Python dependencies..."
        pip install -r credit_engine/requirements.txt -q
        success "Python dependencies installed"

        # Install frontend dependencies
        info "Installing frontend dependencies..."
        cd frontend
        npm ci --quiet
        cd ..
        success "Frontend dependencies installed"

        echo ""
        echo -e "${GREEN}=====================================${NC}"
        echo -e "${GREEN}Running in Development Mode${NC}"
        echo -e "${GREEN}=====================================${NC}"
        echo ""
        
        echo -e "${BLUE}Backend will start at: http://localhost:5000${NC}"
        echo -e "${BLUE}Frontend will start at: http://localhost:5173${NC}"
        echo ""

        read -p "Start services now? (yes/no) " response
        if [ "$response" = "yes" ]; then
            echo ""
            echo -e "${YELLOW}Starting services...${NC}"
            echo ""

            # Start backend
            (cd . && python api.py) &
            BACKEND_PID=$!

            # Start frontend
            (cd frontend && npm run dev) &
            FRONTEND_PID=$!

            success "Services started"
            echo -e "${YELLOW}Backend PID: $BACKEND_PID${NC}"
            echo -e "${YELLOW}Frontend PID: $FRONTEND_PID${NC}"
            echo "Press Ctrl+C to stop"

            wait
        fi
        ;;

    docker)
        echo ""
        echo -e "${YELLOW}Starting in DOCKER mode (Production)${NC}"
        echo ""

        # Check Docker
        if ! command -v docker &> /dev/null; then
            error "Docker not found. Please install Docker"
        fi
        success "Docker found: $(docker --version)"

        if ! command -v docker-compose &> /dev/null; then
            error "Docker Compose not found. Please install Docker Compose"
        fi
        success "Docker Compose found: $(docker-compose --version)"

        info "Building Docker images..."
        docker-compose build

        success "Docker images built successfully"

        echo ""
        echo -e "${GREEN}=====================================${NC}"
        echo -e "${GREEN}Running in Docker Mode${NC}"
        echo -e "${GREEN}=====================================${NC}"
        echo ""

        echo -e "${BLUE}Backend will be at: http://localhost:5000${NC}"
        echo -e "${BLUE}Frontend will be at: http://localhost:3000${NC}"
        echo ""

        read -p "Start Docker containers? (yes/no) " response
        if [ "$response" = "yes" ]; then
            info "Starting Docker containers..."
            docker-compose up -d

            sleep 3

            success "Containers started"
            echo ""
            echo "Container Status:"
            docker-compose ps
            echo ""
            echo -e "${BLUE}View logs: docker-compose logs -f${NC}"
            echo -e "${BLUE}Stop containers: docker-compose down${NC}"
        fi
        ;;

    test)
        echo ""
        echo -e "${YELLOW}Starting in TEST mode${NC}"
        echo ""

        info "Testing backend API..."
        if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
            success "Backend API is responding"
        else
            error "Backend API is not responding. Make sure it's running on port 5000"
        fi

        info "Testing frontend..."
        if curl -s http://localhost:3000 | grep -q "html"; then
            success "Frontend is responding"
        else
            error "Frontend is not responding. Make sure it's running on port 3000"
        fi

        info "Testing model loader..."
        python3 -c "from credit_engine.model_loader import load_production_model; loader = load_production_model(); print('✓ Model loaded successfully')"
        ;;

    *)
        echo "Usage: $0 [dev|docker|test]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Deployment Setup Complete${NC}"
echo -e "${GREEN}=====================================${NC}"
