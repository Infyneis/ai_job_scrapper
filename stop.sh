#!/bin/bash

# ============================================================
# 🛑 Job Scraper Application Stopper
# ============================================================
# This script stops all services:
# - 🐍 Backend (FastAPI on port 8000)
# - ⚛️  Frontend (Next.js on port 3000)
# - 🦙 Ollama (optional)
# ============================================================

# 🎨 Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo -e "${RED}════════════════════════════════════════════════════════${NC}"
echo -e "${RED}  🛑 Stopping Job Scraper Services${NC}"
echo -e "${RED}════════════════════════════════════════════════════════${NC}"
echo ""

# 🐍 Stop Backend (port 8000)
print_step "Stopping backend (port 8000)..."
BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
    print_success "Backend stopped"
else
    print_warning "Backend was not running"
fi

# ⚛️  Stop Frontend (port 3000)
print_step "Stopping frontend (port 3000)..."
FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    print_success "Frontend stopped"
else
    print_warning "Frontend was not running"
fi

# 🦙 Optionally stop Ollama
if [ "$1" == "--all" ] || [ "$1" == "-a" ]; then
    print_step "Stopping Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services stop ollama 2>/dev/null
    else
        pkill ollama 2>/dev/null
    fi
    print_success "Ollama stopped"
else
    print_warning "Ollama left running (use --all to stop it too)"
fi

echo ""
print_success "All services stopped! 👋"
echo ""
