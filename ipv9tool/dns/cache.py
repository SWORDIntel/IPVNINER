"""
DNS Cache Module

Caches DNS query results to reduce load on IPv9 DNS servers.
"""

import time
import logging
from typing import Dict, Optional, List, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)


class DNSCache:
    """LRU cache for DNS query results"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize DNS cache

        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default TTL in seconds if none specified
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, Tuple[List[str], float, int]] = OrderedDict()
        logger.info(f"DNS Cache initialized (max_size={max_size}, default_ttl={default_ttl}s)")

    def _make_key(self, hostname: str, record_type: str) -> str:
        """Generate cache key from hostname and record type"""
        return f"{hostname.lower()}:{record_type.upper()}"

    def get(self, hostname: str, record_type: str = 'A') -> Optional[List[str]]:
        """
        Get cached DNS result

        Args:
            hostname: Domain name
            record_type: DNS record type

        Returns:
            List of IP addresses if cached and valid, None otherwise
        """
        key = self._make_key(hostname, record_type)

        if key not in self.cache:
            logger.debug(f"Cache miss: {key}")
            return None

        addresses, timestamp, ttl = self.cache[key]

        # Check if entry has expired
        if time.time() - timestamp > ttl:
            logger.debug(f"Cache expired: {key}")
            del self.cache[key]
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        logger.debug(f"Cache hit: {key} -> {addresses}")
        return addresses

    def set(self, hostname: str, addresses: List[str], record_type: str = 'A', ttl: Optional[int] = None):
        """
        Store DNS result in cache

        Args:
            hostname: Domain name
            addresses: List of IP addresses
            record_type: DNS record type
            ttl: Time-to-live in seconds (None = use default)
        """
        key = self._make_key(hostname, record_type)

        # Use provided TTL or default
        cache_ttl = ttl if ttl is not None else self.default_ttl

        # Add to cache
        self.cache[key] = (addresses, time.time(), cache_ttl)
        self.cache.move_to_end(key)

        # Evict oldest entry if cache is full
        if len(self.cache) > self.max_size:
            evicted_key = next(iter(self.cache))
            del self.cache[evicted_key]
            logger.debug(f"Cache full, evicted: {evicted_key}")

        logger.debug(f"Cached: {key} -> {addresses} (TTL={cache_ttl}s)")

    def clear(self):
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared ({count} entries removed)")

    def remove(self, hostname: str, record_type: str = 'A'):
        """Remove specific entry from cache"""
        key = self._make_key(hostname, record_type)
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Removed from cache: {key}")

    def stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        valid_entries = 0
        expired_entries = 0

        current_time = time.time()
        for addresses, timestamp, ttl in self.cache.values():
            if current_time - timestamp > ttl:
                expired_entries += 1
            else:
                valid_entries += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'max_size': self.max_size
        }
