#!/bin/bash
# IPv9 Scanner Installation Script
# Installs IPv9 tool and dependencies on Debian-based systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run: sudo $0"
    exit 1
fi

echo -e "${GREEN}IPv9 Scanner Installation${NC}"
echo "=========================================="

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}Error: Cannot detect OS${NC}"
    exit 1
fi

echo "Detected OS: $OS $VER"

# Check if Debian-based
if [[ "$OS" != "debian" && "$OS" != "ubuntu" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Debian/Ubuntu${NC}"
    echo "Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package lists
echo -e "\n${GREEN}Updating package lists...${NC}"
apt-get update

# Install system dependencies
echo -e "\n${GREEN}Installing system dependencies...${NC}"
apt-get install -y \
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
    wget

# Optional: Install unbound as alternative to dnsmasq
echo -e "\n${YELLOW}Install unbound DNS resolver? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    apt-get install -y unbound
fi

# Create ipv9tool user and group
echo -e "\n${GREEN}Creating ipv9tool user...${NC}"
if ! id -u ipv9tool > /dev/null 2>&1; then
    useradd -r -s /bin/false -d /var/lib/ipv9tool ipv9tool
    echo "User 'ipv9tool' created"
else
    echo "User 'ipv9tool' already exists"
fi

# Create directories
echo -e "\n${GREEN}Creating directories...${NC}"
mkdir -p /etc/ipv9tool
mkdir -p /var/log/ipv9tool
mkdir -p /var/lib/ipv9tool
mkdir -p /opt/ipv9tool

# Set permissions
chown -R ipv9tool:ipv9tool /var/log/ipv9tool
chown -R ipv9tool:ipv9tool /var/lib/ipv9tool
chmod 755 /etc/ipv9tool

# Install Python package
echo -e "\n${GREEN}Installing IPv9 tool Python package...${NC}"
cd "$(dirname "$0")/.."

# Install in development mode or production mode
echo -e "${YELLOW}Install in development mode? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    pip3 install -e .
else
    pip3 install .
fi

# Copy configuration files
echo -e "\n${GREEN}Installing configuration files...${NC}"
cp config/ipv9tool.yml /etc/ipv9tool/
cp config/dnsmasq-ipv9.conf /etc/ipv9tool/
cp config/unbound-ipv9.conf /etc/ipv9tool/

# Install systemd services
echo -e "\n${GREEN}Installing systemd services...${NC}"
cp systemd/ipv9-resolver.service /etc/systemd/system/
cp systemd/ipv9-monitor.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Configure dnsmasq
echo -e "\n${YELLOW}Configure dnsmasq for IPv9? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    # Stop systemd-resolved if running (conflicts with dnsmasq)
    if systemctl is-active --quiet systemd-resolved; then
        echo "Stopping systemd-resolved..."
        systemctl stop systemd-resolved
        systemctl disable systemd-resolved
    fi

    # Link dnsmasq config
    ln -sf /etc/ipv9tool/dnsmasq-ipv9.conf /etc/dnsmasq.d/ipv9.conf

    # Restart dnsmasq
    systemctl restart dnsmasq
    systemctl enable dnsmasq

    # Update /etc/resolv.conf
    echo "nameserver 127.0.0.1" > /etc/resolv.conf

    echo -e "${GREEN}dnsmasq configured for IPv9${NC}"
fi

# Enable services
echo -e "\n${YELLOW}Enable IPv9 services? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    systemctl enable ipv9-resolver
    # Don't enable monitor by default
    echo -e "${GREEN}IPv9 resolver service enabled${NC}"
fi

# Create command-line tools symlinks
echo -e "\n${GREEN}Creating command-line tools...${NC}"
ln -sf /usr/local/bin/ipv9tool /usr/local/bin/ipv9-resolve
ln -sf /usr/local/bin/ipv9tool /usr/local/bin/ipv9-ping
ln -sf /usr/local/bin/ipv9tool /usr/local/bin/ipv9-scan
ln -sf /usr/local/bin/ipv9tool /usr/local/bin/ipv9-http

# Verify installation
echo -e "\n${GREEN}Verifying installation...${NC}"

if command -v ipv9tool &> /dev/null; then
    echo -e "${GREEN}✓ ipv9tool command installed${NC}"
else
    echo -e "${RED}✗ ipv9tool command not found${NC}"
fi

if systemctl list-unit-files | grep -q ipv9-resolver; then
    echo -e "${GREEN}✓ systemd services installed${NC}"
else
    echo -e "${RED}✗ systemd services not found${NC}"
fi

# Print summary
echo -e "\n${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "Configuration files:"
echo "  /etc/ipv9tool/ipv9tool.yml"
echo "  /etc/ipv9tool/dnsmasq-ipv9.conf"
echo ""
echo "Log files:"
echo "  /var/log/ipv9tool/ipv9tool.log"
echo "  /var/log/ipv9-dnsmasq.log"
echo ""
echo "Commands:"
echo "  ipv9tool resolve <hostname>"
echo "  ipv9tool ping <host>"
echo "  ipv9tool scan <host>"
echo "  ipv9tool http <host>"
echo ""
echo "Services:"
echo "  systemctl start ipv9-resolver"
echo "  systemctl status ipv9-resolver"
echo ""
echo "Documentation:"
echo "  See docs/GUIDE.md for usage guide"
echo ""
echo -e "${YELLOW}Note: You may need to reboot or restart networking${NC}"
echo -e "${YELLOW}for DNS changes to take effect.${NC}"
echo ""
