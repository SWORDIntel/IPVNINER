"""
IPv9 DNS Resolver

Resolves .chn and numeric domain names using IPv9 DNS servers.
"""

import socket
import logging
import dns.resolver
import dns.query
import dns.message
from typing import List, Optional, Dict, Any
from ..config import ConfigManager

logger = logging.getLogger(__name__)


class IPv9Resolver:
    """DNS resolver for IPv9 decimal network domains"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize IPv9 DNS resolver

        Args:
            config: Configuration dictionary. If None, uses default config.
        """
        self.config = config or ConfigManager().get_config()
        self.primary_dns = self.config['dns']['primary']
        self.secondary_dns = self.config['dns']['secondary']

        # Create custom resolver instances
        self.primary_resolver = self._create_resolver(self.primary_dns)
        self.secondary_resolver = self._create_resolver(self.secondary_dns)

        # Verification mode
        self.verify_dns = self.config.get('security', {}).get('verify_dns', True)

        logger.info(f"IPv9 Resolver initialized with DNS servers: {self.primary_dns}, {self.secondary_dns}")

    def _create_resolver(self, nameserver: str) -> dns.resolver.Resolver:
        """Create a DNS resolver instance for the specified nameserver"""
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        resolver.timeout = self.config.get('scanner', {}).get('timeout', 5)
        resolver.lifetime = self.config.get('scanner', {}).get('timeout', 5) * 2
        return resolver

    def resolve(self, hostname: str, record_type: str = 'A') -> List[str]:
        """
        Resolve an IPv9 hostname to IP addresses

        Args:
            hostname: The .chn or numeric domain to resolve
            record_type: DNS record type (A, AAAA, CNAME, etc.)

        Returns:
            List of IP addresses or record values
        """
        logger.debug(f"Resolving {hostname} (type: {record_type})")

        try:
            # Query primary DNS
            primary_results = self._query_dns(self.primary_resolver, hostname, record_type)

            if self.verify_dns:
                # Verify with secondary DNS
                secondary_results = self._query_dns(self.secondary_resolver, hostname, record_type)

                # Check if results match
                if set(primary_results) != set(secondary_results):
                    logger.warning(
                        f"DNS mismatch for {hostname}: "
                        f"Primary={primary_results}, Secondary={secondary_results}"
                    )
                    # Return primary but log the discrepancy
                    return primary_results

            logger.info(f"Resolved {hostname} to {primary_results}")
            return primary_results

        except dns.resolver.NXDOMAIN:
            logger.warning(f"Domain not found: {hostname}")
            return []
        except dns.resolver.Timeout:
            logger.error(f"DNS timeout for {hostname}")
            return []
        except Exception as e:
            logger.error(f"DNS resolution error for {hostname}: {e}")
            return []

    def _query_dns(self, resolver: dns.resolver.Resolver, hostname: str, record_type: str) -> List[str]:
        """Query DNS and return results as list of strings"""
        try:
            answers = resolver.resolve(hostname, record_type)
            return [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"Query failed: {e}")
            raise

    def resolve_with_metadata(self, hostname: str, record_type: str = 'A') -> Dict[str, Any]:
        """
        Resolve hostname and return detailed metadata

        Returns:
            Dictionary with IP addresses, TTL, and other metadata
        """
        try:
            answers = self.primary_resolver.resolve(hostname, record_type)

            return {
                'hostname': hostname,
                'record_type': record_type,
                'addresses': [str(rdata) for rdata in answers],
                'ttl': answers.rrset.ttl if answers.rrset else None,
                'canonical_name': answers.canonical_name.to_text(),
                'response_time': answers.response.time if hasattr(answers.response, 'time') else None
            }
        except Exception as e:
            logger.error(f"Failed to resolve {hostname} with metadata: {e}")
            return {
                'hostname': hostname,
                'record_type': record_type,
                'addresses': [],
                'error': str(e)
            }

    def is_ipv9_domain(self, hostname: str) -> bool:
        """
        Check if a hostname is an IPv9 domain (.chn or all-numeric)

        Args:
            hostname: Domain name to check

        Returns:
            True if it's an IPv9 domain
        """
        hostname = hostname.lower().strip()

        # Check for .chn TLD
        if hostname.endswith('.chn'):
            return True

        # Check if domain (before first dot) is all numeric
        domain_part = hostname.split('.')[0]
        if domain_part.isdigit():
            return True

        return False

    def reverse_lookup(self, ip_address: str) -> Optional[str]:
        """
        Perform reverse DNS lookup

        Args:
            ip_address: IP address to look up

        Returns:
            Hostname if found, None otherwise
        """
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            logger.info(f"Reverse lookup: {ip_address} -> {hostname}")
            return hostname
        except (socket.herror, socket.gaierror) as e:
            logger.debug(f"Reverse lookup failed for {ip_address}: {e}")
            return None
