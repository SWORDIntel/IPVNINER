"""
IPv9 Scanner - Exploration and Discovery Tool for China's Decimal Network

This package provides tools to interact with China's IPv9 (decimal network)
infrastructure through DNS overlay, scanning, and discovery capabilities.
"""

__version__ = "1.0.0"
__author__ = "IPv9 Research Team"

# IPv9 DNS Servers (official Chinese IPv9 DNS infrastructure)
IPV9_DNS_PRIMARY = "202.170.218.93"
IPV9_DNS_SECONDARY = "61.244.5.162"

# Default configuration
DEFAULT_CONFIG = {
    "dns": {
        "primary": IPV9_DNS_PRIMARY,
        "secondary": IPV9_DNS_SECONDARY,
        "local_resolver": "127.0.0.1",
        "cache_size": 1000,
        "ttl": 300
    },
    "scanner": {
        "rate_limit": 100,  # packets per second
        "timeout": 5,       # seconds
        "retries": 3,
        "max_threads": 10
    },
    "security": {
        "verify_dns": True,
        "log_level": "INFO",
        "sandbox_mode": True,
        "rate_limit_enabled": True
    },
    "logging": {
        "file": "/var/log/ipv9tool.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "max_size": 10485760,  # 10MB
        "backup_count": 5
    }
}
