#!/bin/bash
#
# Genesis Engine - Stop Services
#

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Stopping Genesis Engine services..."

# Stop API server
if [ -f /tmp/genesis-api.pid ]; then
    PID=$(cat /tmp/genesis-api.pid)
    kill $PID 2>/dev/null && echo -e "${GREEN}✓ API server stopped${NC}"
    rm /tmp/genesis-api.pid
fi

# Stop dashboard
if [ -f /tmp/genesis-dashboard.pid ]; then
    PID=$(cat /tmp/genesis-dashboard.pid)
    kill $PID 2>/dev/null && echo -e "${GREEN}✓ Dashboard stopped${NC}"
    rm /tmp/genesis-dashboard.pid
fi

# Kill any remaining processes on ports
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

echo -e "${GREEN}All services stopped${NC}"
