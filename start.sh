#!/bin/bash

# ============================================================
# 🚀 Job Scraper Application Launcher
# ============================================================
# This script starts all services needed for the job scraper:
# - 🦙 Ollama (local AI model)
# - 🐍 Backend (FastAPI)
# - ⚛️  Frontend (Next.js)
# ============================================================

set -e  # Exit on any error

# 🎨 Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 📁 Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 📝 Log file for debugging
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# ============================================================
# 🛠️  Helper Functions
# ============================================================

print_header() {
    echo ""
    echo -e "${PURPLE}════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================
# 🧹 Cleanup function (runs on exit)
# ============================================================

cleanup() {
    print_header "🧹 Shutting down services..."

    # Kill background processes started by this script
    if [ ! -z "$BACKEND_PID" ]; then
        print_step "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        print_step "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    print_success "All services stopped. Goodbye! 👋"
    exit 0
}

# Set up trap to catch Ctrl+C and other exit signals
trap cleanup SIGINT SIGTERM EXIT

# ============================================================
# 🔍 Pre-flight Checks
# ============================================================

print_header "🔍 Running pre-flight checks..."

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found at $BACKEND_DIR"
    exit 1
fi
print_success "Backend directory found"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi
print_success "Frontend directory found"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+"
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm"
    exit 1
fi
print_success "npm found: $(npm --version)"

# ============================================================
# 🦙 Step 1: Start Ollama (Local AI)
# ============================================================

print_header "🦙 Step 1: Setting up Ollama (Local AI)..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama is not installed."
    print_info "Installing Ollama via Homebrew..."

    if command -v brew &> /dev/null; then
        brew install ollama
    else
        print_error "Homebrew not found. Please install Ollama manually:"
        print_info "  curl -fsSL https://ollama.ai/install.sh | sh"
        exit 1
    fi
fi
print_success "Ollama is installed"

# Check if Ollama service is running
print_step "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_warning "Ollama is not running. Starting it..."

    # Start Ollama in background
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use brew services
        brew services start ollama 2>/dev/null || ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    else
        # Linux - start directly
        ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    fi

    # Wait for Ollama to be ready
    print_step "Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
fi
print_success "Ollama is running"

# Check if llama3.2 model is available
print_step "Checking for llama3.2 model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.2"; then
    print_warning "llama3.2 model not found. Downloading..."
    print_info "This may take a few minutes (2GB download)..."
    ollama pull llama3.2
fi
print_success "llama3.2 model is ready"

# ============================================================
# 🐍 Step 2: Start Backend (FastAPI)
# ============================================================

print_header "🐍 Step 2: Starting Backend (FastAPI)..."

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_step "Creating Python virtual environment..."
    python3 -m venv venv
fi
print_success "Virtual environment ready"

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
print_step "Installing Python dependencies..."
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Check if .env file exists (optional - only needed for OpenRouter fallback)
if [ ! -f ".env" ]; then
    print_info ".env file not found (optional - Ollama doesn't need it)"
    print_info "To enable OpenRouter fallback, create .env with OPEN_ROUTER_API_KEY"
fi

# Install Playwright browsers if needed
print_step "Checking Playwright browsers..."
python -m playwright install chromium > /dev/null 2>&1 || true
print_success "Playwright browsers ready"

# Start the backend server
print_step "Starting FastAPI backend on http://localhost:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
print_step "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        break
    fi
    sleep 1
    echo -n "."
done
echo ""
print_success "Backend is running (PID: $BACKEND_PID)"
print_info "API docs available at: http://localhost:8000/docs"

# ============================================================
# ⚛️  Step 3: Start Frontend (Next.js)
# ============================================================

print_header "⚛️  Step 3: Starting Frontend (Next.js)..."

cd "$FRONTEND_DIR"

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    print_step "Installing npm dependencies..."
    npm install
fi
print_success "npm dependencies ready"

# Start the frontend
print_step "Starting Next.js frontend on http://localhost:3000..."
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
print_step "Waiting for frontend to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        break
    fi
    sleep 1
    echo -n "."
done
echo ""
print_success "Frontend is running (PID: $FRONTEND_PID)"

# ============================================================
# 🎉 All systems go!
# ============================================================

print_header "🎉 All services are running!"

echo -e "${GREEN}┌─────────────────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│                                                         │${NC}"
echo -e "${GREEN}│  🦙 Ollama:    http://localhost:11434                   │${NC}"
echo -e "${GREEN}│  🐍 Backend:   http://localhost:8000                    │${NC}"
echo -e "${GREEN}│  📚 API Docs:  http://localhost:8000/docs               │${NC}"
echo -e "${GREEN}│  ⚛️  Frontend:  http://localhost:3000                    │${NC}"
echo -e "${GREEN}│                                                         │${NC}"
echo -e "${GREEN}│  📝 Logs are saved in: $LOG_DIR             │${NC}"
echo -e "${GREEN}│                                                         │${NC}"
echo -e "${GREEN}│  Press Ctrl+C to stop all services                      │${NC}"
echo -e "${GREEN}│                                                         │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────────────────┘${NC}"
echo ""

# Open the browser (optional)
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_info "Opening browser..."
    sleep 2
    open http://localhost:3000
fi

# Keep the script running and show logs
print_header "📋 Live Logs (Backend)"
print_info "Showing backend logs. Press Ctrl+C to stop all services."
echo ""

tail -f "$LOG_DIR/backend.log"
