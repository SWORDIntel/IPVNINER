#!/bin/bash
# Start IPv9 API Server

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}IPv9 Scanner API Server${NC}"
echo "======================================"
echo ""

# Check if Python dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing API dependencies...${NC}"
    pip3 install fastapi uvicorn pydantic aiosqlite requests
fi

# Check configuration
CONFIG_PATH="/etc/ipv9tool/ipv9tool.yml"
if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${YELLOW}Warning: Configuration not found at $CONFIG_PATH${NC}"
    echo "Using default configuration"
fi

# Create database directory
mkdir -p ~/.ipv9tool

# Start server
HOST="${IPV9_API_HOST:-0.0.0.0}"
PORT="${IPV9_API_PORT:-8000}"
WORKERS="${IPV9_API_WORKERS:-4}"

echo "Starting API server..."
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo ""
echo -e "${GREEN}API Documentation:${NC} http://localhost:$PORT/docs"
echo -e "${GREEN}ReDoc Documentation:${NC} http://localhost:$PORT/redoc"
echo ""

exec uvicorn ipv9tool.api.server:create_api_app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info
