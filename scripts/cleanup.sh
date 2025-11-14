#!/bin/bash
# IPv9 Scanner Cleanup Script
# Removes IPv9 tool and restores system configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}IPv9 Scanner Uninstallation${NC}"
echo "=========================================="
echo -e "${YELLOW}This will remove IPv9 tool and restore DNS settings${NC}"
echo "Continue? (y/N)"
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Stop services
echo -e "\n${GREEN}Stopping services...${NC}"
systemctl stop ipv9-resolver || true
systemctl stop ipv9-monitor || true
systemctl stop dnsmasq || true

# Disable services
echo "Disabling services..."
systemctl disable ipv9-resolver || true
systemctl disable ipv9-monitor || true

# Remove systemd service files
echo -e "\n${GREEN}Removing systemd services...${NC}"
rm -f /etc/systemd/system/ipv9-resolver.service
rm -f /etc/systemd/system/ipv9-monitor.service
systemctl daemon-reload

# Restore DNS configuration
echo -e "\n${GREEN}Restoring DNS configuration...${NC}"

# Find most recent backup
BACKUP=$(ls -t /etc/resolv.conf.backup.* 2>/dev/null | head -1)

if [ -n "$BACKUP" ]; then
    echo "Restoring from: $BACKUP"
    cp "$BACKUP" /etc/resolv.conf
else
    echo -e "${YELLOW}No backup found, creating default resolv.conf${NC}"
    cat > /etc/resolv.conf << EOF
# Default DNS configuration
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
EOF
fi

# Re-enable systemd-resolved if it was disabled
if ! systemctl is-enabled --quiet systemd-resolved 2>/dev/null; then
    echo -e "\n${YELLOW}Re-enable systemd-resolved? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        systemctl enable systemd-resolved
        systemctl start systemd-resolved
        echo -e "${GREEN}systemd-resolved enabled${NC}"
    fi
fi

# Remove dnsmasq IPv9 configuration
echo -e "\n${GREEN}Removing dnsmasq configuration...${NC}"
rm -f /etc/dnsmasq.d/ipv9.conf
rm -f /etc/systemd/resolved.conf.d/ipv9.conf

# Restart dnsmasq if it's running
if systemctl is-active --quiet dnsmasq; then
    systemctl restart dnsmasq
fi

# Uninstall Python package
echo -e "\n${GREEN}Uninstalling Python package...${NC}"
pip3 uninstall -y ipv9tool || true

# Remove command-line tools
echo -e "\n${GREEN}Removing command-line tools...${NC}"
rm -f /usr/local/bin/ipv9tool
rm -f /usr/local/bin/ipv9-resolve
rm -f /usr/local/bin/ipv9-ping
rm -f /usr/local/bin/ipv9-scan
rm -f /usr/local/bin/ipv9-http
rm -f /usr/local/bin/ipv9-monitor

# Remove configuration files
echo -e "\n${YELLOW}Remove configuration files? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    rm -rf /etc/ipv9tool
    echo "Configuration files removed"
fi

# Remove log files
echo -e "\n${YELLOW}Remove log files? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    rm -rf /var/log/ipv9tool
    rm -f /var/log/ipv9-dnsmasq.log
    rm -f /var/log/ipv9-unbound.log
    echo "Log files removed"
fi

# Remove data files
echo -e "\n${YELLOW}Remove data files? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    rm -rf /var/lib/ipv9tool
    echo "Data files removed"
fi

# Remove user
echo -e "\n${YELLOW}Remove ipv9tool user? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    userdel ipv9tool || true
    echo "User removed"
fi

# Test DNS
echo -e "\n${GREEN}Testing DNS resolution...${NC}"
if host google.com > /dev/null 2>&1; then
    echo -e "${GREEN}✓ DNS working${NC}"
else
    echo -e "${RED}✗ DNS not working${NC}"
    echo "You may need to manually configure /etc/resolv.conf"
fi

echo -e "\n${GREEN}=========================================="
echo "Uninstallation Complete!"
echo "==========================================${NC}"
echo ""
echo "IPv9 tool has been removed from your system."
echo "DNS configuration has been restored."
echo ""
