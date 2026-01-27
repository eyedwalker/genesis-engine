#!/bin/bash
#
# Genesis Engine - One-Click Start
# Usage: ./start.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║                                               ║"
echo "║   ⚡ GENESIS ENGINE                           ║"
echo "║      Factory-as-a-Service Platform           ║"
echo "║                                               ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for required tools
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is required${NC}"
        exit 1
    fi

    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is required${NC}"
        echo "Install from: https://nodejs.org/"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        echo -e "${RED}Error: npm is required${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ All requirements met${NC}"
}

# Install Python dependencies
setup_python() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"

    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install -q --upgrade pip

    # Use minimal requirements for quick start (avoids numpy compilation issues on Python 3.13)
    pip install -q -r requirements-minimal.txt

    # Install package in editable mode without dependencies
    pip install -q --no-deps -e .

    echo -e "${GREEN}✓ Python dependencies installed${NC}"
}

# Install dashboard dependencies
setup_dashboard() {
    echo -e "${YELLOW}Setting up dashboard...${NC}"

    cd dashboard
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    cd ..

    echo -e "${GREEN}✓ Dashboard dependencies installed${NC}"
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting services...${NC}"

    # Kill any existing processes on our ports
    lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

    # Load .env if exists (for API keys)
    if [ -f "$SCRIPT_DIR/.env" ]; then
        export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
        echo -e "${GREEN}✓ Loaded environment from .env${NC}"
    fi

    # Start API server in background
    echo -e "${BLUE}Starting API server on http://localhost:8000${NC}"
    # Run server directly with full paths to avoid genesis/__init__.py (has pydantic_ai dep)
    "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/genesis-engine/genesis/api/server.py" &> /tmp/genesis-api.log &
    API_PID=$!
    echo $API_PID > /tmp/genesis-api.pid

    # Start dashboard in background
    echo -e "${BLUE}Starting dashboard on http://localhost:3000${NC}"
    cd dashboard
    npm run dev &> /tmp/genesis-dashboard.log &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > /tmp/genesis-dashboard.pid
    cd ..

    # Wait for services to start
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 3

    # Check if services are running
    if ! kill -0 $API_PID 2>/dev/null; then
        echo -e "${RED}API server failed to start. Check /tmp/genesis-api.log${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Services started${NC}"
}

# Open browser
open_browser() {
    echo -e "${YELLOW}Opening browser...${NC}"
    sleep 2

    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:3000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in your browser"
    else
        echo "Open http://localhost:3000 in your browser"
    fi
}

# Show status
show_status() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Genesis Engine is running!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BLUE}Dashboard:${NC}  http://localhost:3000"
    echo -e "  ${BLUE}API:${NC}        http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}   http://localhost:8000/docs"
    echo ""
    echo -e "  ${YELLOW}To stop:${NC}    ./stop.sh"
    echo -e "  ${YELLOW}CLI:${NC}        source venv/bin/activate && genesis --help"
    echo ""
}

# Main
main() {
    check_requirements
    setup_python
    setup_dashboard
    start_services
    open_browser
    show_status

    # Keep script running and show logs
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""

    # Trap Ctrl+C to cleanup
    trap 'echo ""; echo "Stopping services..."; ./stop.sh; exit 0' INT

    # Tail logs
    tail -f /tmp/genesis-api.log /tmp/genesis-dashboard.log 2>/dev/null
}

main
