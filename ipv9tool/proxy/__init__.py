"""
Proxy Module for IPv9 Scanner

Mullvad-style proxy rotation for operational security:
- SOCKS5/HTTP proxy support
- Tor integration
- Mullvad VPN API
- Automatic rotation
- IP verification
"""

from .manager import (
    ProxyManager,
    ProxyEndpoint,
    ProxyType,
    ProxyRotationStrategy,
    get_proxy_manager,
    configure_proxies
)

__all__ = [
    'ProxyManager',
    'ProxyEndpoint',
    'ProxyType',
    'ProxyRotationStrategy',
    'get_proxy_manager',
    'configure_proxies'
]
