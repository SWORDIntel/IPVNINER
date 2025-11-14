"""
DNS Forwarder Configuration

Generates configuration files for dnsmasq and unbound to forward .chn queries.
"""

import os
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DNSForwarder:
    """Manages DNS forwarder configuration for IPv9"""

    def __init__(self, primary_dns: str, secondary_dns: str):
        """
        Initialize DNS forwarder

        Args:
            primary_dns: Primary IPv9 DNS server
            secondary_dns: Secondary IPv9 DNS server
        """
        self.primary_dns = primary_dns
        self.secondary_dns = secondary_dns

    def generate_dnsmasq_config(self, output_path: Optional[str] = None) -> str:
        """
        Generate dnsmasq configuration for IPv9

        Args:
            output_path: Path to write config file (None = return as string)

        Returns:
            Configuration content as string
        """
        config = f"""# IPv9 DNS Forwarder Configuration for dnsmasq
# Forward .chn domains to IPv9 DNS servers

# Listen on localhost only
listen-address=127.0.0.1

# Don't read /etc/resolv.conf
no-resolv

# Cache size
cache-size=1000

# Forward .chn domains to IPv9 DNS servers
server=/.chn/{self.primary_dns}
server=/.chn/{self.secondary_dns}

# Forward all numeric domains to IPv9 DNS (experimental)
# This catches phone-number-like domains
# Uncomment if needed:
# address=/[0-9]*.chn/{self.primary_dns}

# Log queries (for debugging)
log-queries

# Log to specific file
log-facility=/var/log/ipv9-dnsmasq.log

# Enable DNSSEC if available
# dnssec

# Additional options
no-hosts
no-poll
"""

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(config)
            logger.info(f"dnsmasq config written to {output_path}")

        return config

    def generate_unbound_config(self, output_path: Optional[str] = None) -> str:
        """
        Generate unbound configuration for IPv9

        Args:
            output_path: Path to write config file (None = return as string)

        Returns:
            Configuration content as string
        """
        config = f"""# IPv9 DNS Forwarder Configuration for unbound
# Forward .chn domains to IPv9 DNS servers

server:
    # Listen on localhost
    interface: 127.0.0.1

    # Access control
    access-control: 127.0.0.0/8 allow
    access-control: 0.0.0.0/0 refuse

    # Cache settings
    cache-max-ttl: 300
    cache-min-ttl: 60

    # Logging
    verbosity: 1
    log-queries: yes
    logfile: "/var/log/ipv9-unbound.log"

    # Don't query localhost
    do-not-query-localhost: no

    # Privacy settings
    hide-identity: yes
    hide-version: yes

# Forward .chn to IPv9 DNS servers
forward-zone:
    name: "chn."
    forward-addr: {self.primary_dns}
    forward-addr: {self.secondary_dns}
    forward-first: no

# Optional: Forward numeric domains
# forward-zone:
#     name: "[0-9]*."
#     forward-addr: {self.primary_dns}
#     forward-addr: {self.secondary_dns}
"""

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(config)
            logger.info(f"unbound config written to {output_path}")

        return config

    def generate_systemd_resolved_config(self, output_path: Optional[str] = None) -> str:
        """
        Generate systemd-resolved configuration snippet

        Args:
            output_path: Path to write config file

        Returns:
            Configuration content
        """
        config = f"""# IPv9 DNS Configuration for systemd-resolved
# Place in /etc/systemd/resolved.conf.d/ipv9.conf

[Resolve]
# Use IPv9 DNS servers for .chn domains
DNS={self.primary_dns} {self.secondary_dns}
Domains=~chn

# Fallback to system DNS for other domains
FallbackDNS=8.8.8.8 1.1.1.1

# Cache settings
Cache=yes
CacheFromLocalhost=yes

# DNSSEC if supported
DNSSEC=allow-downgrade
"""

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(config)
            logger.info(f"systemd-resolved config written to {output_path}")

        return config

    def check_dns_reachability(self) -> dict:
        """
        Check if IPv9 DNS servers are reachable

        Returns:
            Dictionary with reachability status for each server
        """
        import socket

        results = {}

        for server_name, server_ip in [('primary', self.primary_dns), ('secondary', self.secondary_dns)]:
            try:
                # Try to connect to DNS port (53)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((server_ip, 53))
                sock.close()

                reachable = (result == 0)
                results[server_name] = {
                    'ip': server_ip,
                    'reachable': reachable,
                    'status': 'OK' if reachable else 'UNREACHABLE'
                }

                logger.info(f"DNS server {server_name} ({server_ip}): {'reachable' if reachable else 'unreachable'}")

            except Exception as e:
                results[server_name] = {
                    'ip': server_ip,
                    'reachable': False,
                    'status': f'ERROR: {str(e)}'
                }
                logger.error(f"Failed to check {server_name} DNS server: {e}")

        return results
