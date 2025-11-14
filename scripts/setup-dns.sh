#!/bin/bash
# IPv9 DNS Setup Script
# Configures system DNS to use IPv9 resolver

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}IPv9 DNS Setup${NC}"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

# Backup current resolv.conf
echo -e "\n${GREEN}Backing up /etc/resolv.conf...${NC}"
if [ -f /etc/resolv.conf ]; then
    cp /etc/resolv.conf /etc/resolv.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo "Backup created"
fi

# Check which DNS system is in use
if systemctl is-active --quiet systemd-resolved; then
    echo -e "\n${YELLOW}systemd-resolved is active${NC}"
    echo "Choose configuration method:"
    echo "1) Disable systemd-resolved and use dnsmasq (recommended)"
    echo "2) Configure systemd-resolved to forward .chn domains"
    echo "3) Cancel"
    read -p "Enter choice [1-3]: " choice

    case $choice in
        1)
            echo "Stopping systemd-resolved..."
            systemctl stop systemd-resolved
            systemctl disable systemd-resolved

            # Remove symlink if exists
            if [ -L /etc/resolv.conf ]; then
                rm /etc/resolv.conf
            fi

            # Create new resolv.conf
            cat > /etc/resolv.conf << EOF
# IPv9 DNS Configuration
nameserver 127.0.0.1

# Fallback to IPv9 DNS servers directly
nameserver 202.170.218.93
nameserver 61.244.5.162
EOF

            echo -e "${GREEN}DNS configured to use local resolver${NC}"
            ;;

        2)
            echo "Configuring systemd-resolved..."

            # Create resolved.conf.d directory
            mkdir -p /etc/systemd/resolved.conf.d

            # Create IPv9 configuration
            cat > /etc/systemd/resolved.conf.d/ipv9.conf << EOF
[Resolve]
DNS=202.170.218.93 61.244.5.162
Domains=~chn
FallbackDNS=8.8.8.8 1.1.1.1
Cache=yes
DNSSEC=allow-downgrade
EOF

            # Restart systemd-resolved
            systemctl restart systemd-resolved

            echo -e "${GREEN}systemd-resolved configured for IPv9${NC}"
            ;;

        3)
            echo "Cancelled"
            exit 0
            ;;

        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac

elif systemctl is-active --quiet dnsmasq; then
    echo -e "\n${YELLOW}dnsmasq is active${NC}"

    # Check if IPv9 config exists
    if [ -f /etc/dnsmasq.d/ipv9.conf ] || [ -f /etc/ipv9tool/dnsmasq-ipv9.conf ]; then
        echo "IPv9 dnsmasq configuration found"

        # Restart dnsmasq
        echo "Restarting dnsmasq..."
        systemctl restart dnsmasq

        echo -e "${GREEN}dnsmasq configured for IPv9${NC}"
    else
        echo -e "${RED}IPv9 dnsmasq configuration not found${NC}"
        echo "Please run install.sh first"
        exit 1
    fi

else
    echo -e "\n${YELLOW}No DNS resolver detected${NC}"
    echo "Configuring manual DNS..."

    # Create resolv.conf
    cat > /etc/resolv.conf << EOF
# IPv9 DNS Configuration
# Local resolver (if dnsmasq is running)
nameserver 127.0.0.1

# IPv9 DNS servers (Chinese decimal network)
nameserver 202.170.218.93
nameserver 61.244.5.162

# Fallback DNS servers
nameserver 8.8.8.8
nameserver 1.1.1.1
EOF

    echo -e "${GREEN}DNS configuration updated${NC}"
fi

# Test DNS resolution
echo -e "\n${GREEN}Testing DNS resolution...${NC}"

# Test regular DNS
echo -n "Testing google.com... "
if host google.com > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
fi

# Test IPv9 DNS
echo -n "Testing IPv9 DNS servers... "
if host -W 5 www.example.com 202.170.218.93 > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING: IPv9 DNS not responding${NC}"
fi

# Show current DNS configuration
echo -e "\n${GREEN}Current DNS configuration:${NC}"
if command -v resolvectl &> /dev/null; then
    resolvectl status | grep -A 5 "DNS Servers"
else
    cat /etc/resolv.conf
fi

echo -e "\n${GREEN}DNS setup complete!${NC}"
echo ""
echo "You can now use IPv9 tool to resolve .chn domains:"
echo "  ipv9tool resolve www.v9.chn"
echo "  ipv9tool ping em777.chn"
echo ""
