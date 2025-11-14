"""
DNS Resolver Module for IPv9

Handles DNS resolution for .chn and numeric domains via IPv9 DNS servers.
"""

from .resolver import IPv9Resolver
from .forwarder import DNSForwarder
from .cache import DNSCache

__all__ = ['IPv9Resolver', 'DNSForwarder', 'DNSCache']
