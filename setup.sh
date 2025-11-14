#!/bin/bash
# IPv9 Scanner - Unified Installation Script
# One-command installation for complete IPv9 network intelligence platform

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
  _____ _______      ___    _____
 |_   _|  __ \ \    / / |  / ____|
   | | | |__) \ \  / /| |_| (___   ___ __ _ _ __  _ __   ___ _ __
   | | |  ___/ \ \/ / | __|\___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
  _| |_| |      \  /  | |_ ____) | (_| (_| | | | | | | |  __/ |
 |_____|_|       \/    \__|_____/ \___\__,_|_| |_|_| |_|\___|_|

 IPv9 Network Intelligence Platform - Unified Installer
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run as root. Run as normal user with sudo access.${NC}"
    exit 1
fi

echo -e "${GREEN}=== IPv9 Scanner Installation ===${NC}\n"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}Error: Cannot detect OS${NC}"
    exit 1
fi

echo -e "${BLUE}Detected OS:${NC} $OS $VER\n"

# Confirm installation
echo -e "${YELLOW}This will install:${NC}"
echo "  • Python dependencies (FastAPI, Rich, textual, etc.)"
echo "  • System tools (nmap, masscan, dnsmasq)"
echo "  • IPv9 Scanner with TUI"
echo "  • IPv9 API server"
echo "  • System services"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Update package lists
echo -e "\n${GREEN}[1/7] Updating package lists...${NC}"
sudo apt-get update -qq

# Install system dependencies
echo -e "${GREEN}[2/7] Installing system dependencies...${NC}"
sudo apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    dnsmasq \
    nmap \
    masscan \
    dnsutils \
    iputils-ping \
    net-tools \
    iptables \
    git \
    curl \
    wget \
    sqlite3 \
    build-essential \
    > /dev/null 2>&1

echo -e "${CYAN}  ✓ System dependencies installed${NC}"

# Install Python dependencies
echo -e "${GREEN}[3/7] Installing Python dependencies...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip -qq > /dev/null 2>&1
pip install -r requirements.txt -qq

echo -e "${CYAN}  ✓ Python dependencies installed${NC}"

# Install IPv9 package
echo -e "${GREEN}[4/7] Installing IPv9 Scanner...${NC}"
pip install -e . -qq

echo -e "${CYAN}  ✓ IPv9 Scanner installed${NC}"

# Create system directories
echo -e "${GREEN}[5/7] Creating system directories...${NC}"
sudo mkdir -p /etc/ipv9tool
sudo mkdir -p /var/log/ipv9tool
sudo mkdir -p /var/lib/ipv9tool

# Create user directories
mkdir -p ~/.ipv9tool
mkdir -p ~/.ipv9tool/scans
mkdir -p ~/.ipv9tool/reports
mkdir -p ~/.ipv9tool/logs

# Copy configuration files
if [ ! -f /etc/ipv9tool/ipv9tool.yml ]; then
    sudo cp config/ipv9tool.yml /etc/ipv9tool/
fi

# Set permissions
sudo chown -R $USER:$USER ~/.ipv9tool
sudo chmod 755 /var/log/ipv9tool
sudo chmod 755 /var/lib/ipv9tool

echo -e "${CYAN}  ✓ Directories created${NC}"

# Configure DNS
echo -e "${GREEN}[6/7] Configuring DNS...${NC}"

read -p "Configure IPv9 DNS forwarding? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo ./scripts/setup-dns.sh
    echo -e "${CYAN}  ✓ DNS configured${NC}"
else
    echo -e "${YELLOW}  ⊘ DNS configuration skipped${NC}"
fi

# Create launcher scripts
echo -e "${GREEN}[7/7] Creating launcher scripts...${NC}"

# Create ipv9scan launcher
cat > ~/.local/bin/ipv9scan << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")/../.." || exit
source venv/bin/activate
python -m ipv9tool.tui.main "$@"
LAUNCHER

# Create ipv9api launcher
cat > ~/.local/bin/ipv9api << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")/../.." || exit
source venv/bin/activate
uvicorn ipv9tool.api.server:create_api_app --host 0.0.0.0 --port 8000
LAUNCHER

chmod +x ~/.local/bin/ipv9scan
chmod +x ~/.local/bin/ipv9api

echo -e "${CYAN}  ✓ Launchers created${NC}"

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo -e "${YELLOW}  ! Added ~/.local/bin to PATH (restart shell or run: source ~/.bashrc)${NC}"
fi

# Installation complete
echo -e "\n${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}     Installation Complete! 🚀${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}Quick Start:${NC}"
echo -e "  ${YELLOW}ipv9scan${NC}              - Launch TUI scanner"
echo -e "  ${YELLOW}ipv9api${NC}               - Start API server"
echo -e "  ${YELLOW}ipv9tool --help${NC}       - CLI help"
echo ""

echo -e "${CYAN}Features:${NC}"
echo "  • Real-time TUI with streaming logs"
echo "  • Full network enumeration (masscan)"
echo "  • Comprehensive 6-phase auditing"
echo "  • REST API with OpenAPI docs"
echo "  • Multi-format export (JSON/CSV/HTML)"
echo "  • Continuous monitoring"
echo "  • Database tracking"
echo ""

echo -e "${CYAN}Documentation:${NC}"
echo "  • README.md - Project overview"
echo "  • docs/GUIDE.md - Comprehensive guide"
echo "  • docs/API.md - API reference"
echo "  • http://localhost:8000/docs - API docs (when running)"
echo ""

echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Restart your shell: ${YELLOW}source ~/.bashrc${NC}"
echo -e "  2. Launch scanner: ${YELLOW}ipv9scan${NC}"
echo -e "  3. Or start API: ${YELLOW}ipv9api${NC}"
echo ""

echo -e "${GREEN}Happy scanning! 🔍${NC}\n"
