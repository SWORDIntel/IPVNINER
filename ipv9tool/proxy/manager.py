#!/usr/bin/env python3
"""
Proxy Manager - Mullvad-style Rotation System

Provides operational security through proxy rotation, supporting:
- SOCKS5/HTTP proxies
- Tor integration
- Mullvad VPN API
- Commercial proxy services
- Automatic rotation on rate limits/failures
- IP verification
"""

import logging
import random
import time
import requests
import subprocess
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import socket

logger = logging.getLogger(__name__)


class ProxyType(Enum):
    """Proxy type enumeration"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"
    SOCKS4 = "socks4"
    TOR = "tor"
    MULLVAD = "mullvad"


@dataclass
class ProxyEndpoint:
    """Proxy endpoint configuration"""
    host: str
    port: int
    proxy_type: ProxyType
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    provider: str = "custom"
    latency_ms: Optional[float] = None
    last_used: Optional[float] = None
    failure_count: int = 0
    success_count: int = 0

    def to_url(self) -> str:
        """Convert to proxy URL"""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"

        return f"{self.proxy_type.value}://{auth}{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, str]:
        """Convert to requests-compatible proxy dict"""
        url = self.to_url()
        return {
            'http': url,
            'https': url
        }


class ProxyRotationStrategy(Enum):
    """Proxy rotation strategies"""
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    FASTEST = "fastest"
    COUNTRY_BASED = "country_based"


class ProxyManager:
    """
    Proxy rotation manager with Mullvad-style capabilities

    Features:
    - Multiple proxy types (HTTP, SOCKS5, Tor, Mullvad)
    - Automatic rotation strategies
    - Health checking and latency testing
    - IP verification
    - Rate limit detection and rotation
    - Failure tracking
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize proxy manager"""
        self.config = config or {}
        self.proxies: List[ProxyEndpoint] = []
        self.current_index = 0
        self.rotation_strategy = ProxyRotationStrategy(
            self.config.get('rotation_strategy', 'random')
        )
        self.enable_rotation = self.config.get('enable_rotation', True)
        self.max_failures = self.config.get('max_failures', 3)
        self.rotation_interval = self.config.get('rotation_interval', 0)  # seconds, 0 = disabled
        self.last_rotation = time.time()

        # IP verification endpoints
        self.ip_check_urls = [
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://ifconfig.me/ip',
            'https://checkip.amazonaws.com'
        ]

        # Load proxies from config
        self._load_proxies_from_config()

    def _load_proxies_from_config(self):
        """Load proxies from configuration"""
        # Load from proxy list file
        proxy_file = self.config.get('proxy_file')
        if proxy_file:
            self.load_proxies_from_file(proxy_file)

        # Load from proxy list in config
        proxy_list = self.config.get('proxy_list', [])
        for proxy_config in proxy_list:
            self.add_proxy(**proxy_config)

        # Auto-configure Mullvad if enabled
        if self.config.get('enable_mullvad', False):
            self._configure_mullvad()

        # Auto-configure Tor if enabled
        if self.config.get('enable_tor', False):
            self._configure_tor()

    def add_proxy(self, host: str, port: int, proxy_type: str = "http",
                  username: Optional[str] = None, password: Optional[str] = None,
                  country: Optional[str] = None, city: Optional[str] = None,
                  provider: str = "custom"):
        """Add a proxy endpoint"""
        proxy = ProxyEndpoint(
            host=host,
            port=port,
            proxy_type=ProxyType(proxy_type),
            username=username,
            password=password,
            country=country,
            city=city,
            provider=provider
        )
        self.proxies.append(proxy)
        logger.info(f"Added proxy: {proxy.host}:{proxy.port} ({provider})")

    def load_proxies_from_file(self, filepath: str):
        """
        Load proxies from file

        Format:
        type://[user:pass@]host:port [country] [city] [provider]

        Example:
        socks5://user:pass@1.2.3.4:1080 US NewYork Mullvad
        http://5.6.7.8:8080 NL Amsterdam Private
        """
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if not parts:
                        continue

                    # Parse proxy URL
                    proxy_url = parts[0]
                    country = parts[1] if len(parts) > 1 else None
                    city = parts[2] if len(parts) > 2 else None
                    provider = parts[3] if len(parts) > 3 else "custom"

                    # Parse type://[user:pass@]host:port
                    if '://' not in proxy_url:
                        continue

                    proxy_type, rest = proxy_url.split('://', 1)

                    username = None
                    password = None
                    if '@' in rest:
                        auth, hostport = rest.split('@', 1)
                        if ':' in auth:
                            username, password = auth.split(':', 1)
                    else:
                        hostport = rest

                    if ':' not in hostport:
                        continue

                    host, port_str = hostport.rsplit(':', 1)
                    port = int(port_str)

                    self.add_proxy(
                        host=host,
                        port=port,
                        proxy_type=proxy_type,
                        username=username,
                        password=password,
                        country=country,
                        city=city,
                        provider=provider
                    )

            logger.info(f"Loaded {len(self.proxies)} proxies from {filepath}")

        except Exception as e:
            logger.error(f"Failed to load proxies from {filepath}: {e}")

    def _configure_tor(self):
        """Auto-configure Tor SOCKS5 proxy"""
        # Check if Tor is running
        tor_host = self.config.get('tor_host', '127.0.0.1')
        tor_port = self.config.get('tor_port', 9050)

        try:
            # Test Tor connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((tor_host, tor_port))
            sock.close()

            if result == 0:
                self.add_proxy(
                    host=tor_host,
                    port=tor_port,
                    proxy_type='socks5',
                    provider='tor'
                )
                logger.info("Configured Tor SOCKS5 proxy")
            else:
                logger.warning(f"Tor not running on {tor_host}:{tor_port}")

        except Exception as e:
            logger.error(f"Failed to configure Tor: {e}")

    def _configure_mullvad(self):
        """Auto-configure Mullvad VPN SOCKS5 proxies"""
        # Mullvad provides SOCKS5 proxies on various servers
        # Format: <country-city>.mullvad.net:1080

        mullvad_servers = self.config.get('mullvad_servers', [
            {'country': 'US', 'city': 'NewYork', 'host': 'us-nyc.mullvad.net'},
            {'country': 'US', 'city': 'LosAngeles', 'host': 'us-lax.mullvad.net'},
            {'country': 'GB', 'city': 'London', 'host': 'gb-lon.mullvad.net'},
            {'country': 'DE', 'city': 'Frankfurt', 'host': 'de-fra.mullvad.net'},
            {'country': 'SE', 'city': 'Stockholm', 'host': 'se-sto.mullvad.net'},
            {'country': 'NL', 'city': 'Amsterdam', 'host': 'nl-ams.mullvad.net'},
            {'country': 'SG', 'city': 'Singapore', 'host': 'sg.mullvad.net'},
            {'country': 'JP', 'city': 'Tokyo', 'host': 'jp.mullvad.net'},
        ])

        mullvad_account = self.config.get('mullvad_account')

        for server in mullvad_servers:
            self.add_proxy(
                host=server['host'],
                port=1080,
                proxy_type='socks5',
                username=mullvad_account if mullvad_account else None,
                country=server['country'],
                city=server['city'],
                provider='mullvad'
            )

        logger.info(f"Configured {len(mullvad_servers)} Mullvad proxies")

    def rotate(self, force: bool = False) -> Optional[ProxyEndpoint]:
        """
        Rotate to next proxy based on strategy

        Args:
            force: Force rotation even if interval not reached

        Returns:
            New proxy endpoint or None
        """
        if not self.enable_rotation or not self.proxies:
            return None

        # Check rotation interval
        if not force and self.rotation_interval > 0:
            if time.time() - self.last_rotation < self.rotation_interval:
                return self.get_current_proxy()

        # Filter out failed proxies
        available_proxies = [
            p for p in self.proxies
            if p.failure_count < self.max_failures
        ]

        if not available_proxies:
            logger.warning("No available proxies (all failed)")
            # Reset failure counts
            for proxy in self.proxies:
                proxy.failure_count = 0
            available_proxies = self.proxies

        # Select proxy based on strategy
        if self.rotation_strategy == ProxyRotationStrategy.RANDOM:
            proxy = random.choice(available_proxies)

        elif self.rotation_strategy == ProxyRotationStrategy.ROUND_ROBIN:
            self.current_index = (self.current_index + 1) % len(available_proxies)
            proxy = available_proxies[self.current_index]

        elif self.rotation_strategy == ProxyRotationStrategy.LEAST_USED:
            proxy = min(available_proxies, key=lambda p: p.success_count)

        elif self.rotation_strategy == ProxyRotationStrategy.FASTEST:
            # Filter proxies with latency data
            tested_proxies = [p for p in available_proxies if p.latency_ms is not None]
            if tested_proxies:
                proxy = min(tested_proxies, key=lambda p: p.latency_ms)
            else:
                proxy = random.choice(available_proxies)

        else:  # COUNTRY_BASED or fallback
            proxy = random.choice(available_proxies)

        proxy.last_used = time.time()
        self.last_rotation = time.time()

        logger.info(f"Rotated to proxy: {proxy.host}:{proxy.port} ({proxy.provider})")
        return proxy

    def get_current_proxy(self) -> Optional[ProxyEndpoint]:
        """Get current proxy without rotation"""
        if not self.proxies:
            return None

        # Find most recently used
        recent = max(self.proxies, key=lambda p: p.last_used or 0)
        if recent.last_used:
            return recent

        # Or first proxy
        return self.proxies[0]

    def get_proxy_dict(self, rotate: bool = False) -> Optional[Dict[str, str]]:
        """
        Get proxy configuration for requests library

        Args:
            rotate: Whether to rotate to new proxy

        Returns:
            Proxy dict or None if no proxies
        """
        if rotate:
            proxy = self.rotate()
        else:
            proxy = self.get_current_proxy()

        if not proxy:
            return None

        return proxy.to_dict()

    def mark_success(self, proxy: Optional[ProxyEndpoint] = None):
        """Mark proxy as successful"""
        if proxy is None:
            proxy = self.get_current_proxy()

        if proxy:
            proxy.success_count += 1
            proxy.failure_count = max(0, proxy.failure_count - 1)  # Decay failures
            logger.debug(f"Proxy success: {proxy.host}:{proxy.port}")

    def mark_failure(self, proxy: Optional[ProxyEndpoint] = None, auto_rotate: bool = True):
        """Mark proxy as failed and optionally rotate"""
        if proxy is None:
            proxy = self.get_current_proxy()

        if proxy:
            proxy.failure_count += 1
            logger.warning(
                f"Proxy failure: {proxy.host}:{proxy.port} "
                f"(failures: {proxy.failure_count}/{self.max_failures})"
            )

            if auto_rotate and proxy.failure_count >= self.max_failures:
                logger.info(f"Proxy {proxy.host}:{proxy.port} exceeded max failures, rotating...")
                self.rotate(force=True)

    def test_proxy(self, proxy: ProxyEndpoint, timeout: int = 10) -> bool:
        """
        Test proxy connectivity and measure latency

        Args:
            proxy: Proxy to test
            timeout: Request timeout in seconds

        Returns:
            True if proxy works
        """
        start_time = time.time()

        try:
            response = requests.get(
                self.ip_check_urls[0],
                proxies=proxy.to_dict(),
                timeout=timeout
            )

            if response.status_code == 200:
                latency = (time.time() - start_time) * 1000  # Convert to ms
                proxy.latency_ms = latency
                logger.info(
                    f"Proxy test passed: {proxy.host}:{proxy.port} "
                    f"(latency: {latency:.0f}ms)"
                )
                return True
            else:
                logger.warning(f"Proxy test failed: {proxy.host}:{proxy.port}")
                return False

        except Exception as e:
            logger.error(f"Proxy test error: {proxy.host}:{proxy.port} - {e}")
            return False

    def test_all_proxies(self, timeout: int = 10):
        """Test all proxies and update latency"""
        logger.info(f"Testing {len(self.proxies)} proxies...")

        working_count = 0
        for proxy in self.proxies:
            if self.test_proxy(proxy, timeout=timeout):
                working_count += 1
            time.sleep(0.5)  # Rate limit testing

        logger.info(f"Proxy testing complete: {working_count}/{len(self.proxies)} working")

    def get_current_ip(self, use_proxy: bool = True, timeout: int = 10) -> Optional[str]:
        """
        Get current external IP address

        Args:
            use_proxy: Whether to use proxy
            timeout: Request timeout

        Returns:
            IP address or None
        """
        proxies = None
        if use_proxy:
            proxies = self.get_proxy_dict()

        for url in self.ip_check_urls:
            try:
                response = requests.get(url, proxies=proxies, timeout=timeout)
                if response.status_code == 200:
                    ip = response.text.strip()
                    logger.info(f"Current IP: {ip} (proxy: {use_proxy})")
                    return ip
            except Exception as e:
                logger.debug(f"IP check failed for {url}: {e}")
                continue

        logger.error("Failed to get current IP from all endpoints")
        return None

    def verify_rotation(self) -> bool:
        """
        Verify proxy rotation is working

        Returns:
            True if rotation works
        """
        if not self.proxies:
            logger.warning("No proxies configured for rotation test")
            return False

        logger.info("Testing proxy rotation...")

        # Get IP without proxy
        direct_ip = self.get_current_ip(use_proxy=False)
        logger.info(f"Direct IP: {direct_ip}")

        # Get IP with first proxy
        self.rotate(force=True)
        proxy1_ip = self.get_current_ip(use_proxy=True)
        logger.info(f"Proxy 1 IP: {proxy1_ip}")

        # Rotate and get IP with second proxy
        self.rotate(force=True)
        proxy2_ip = self.get_current_ip(use_proxy=True)
        logger.info(f"Proxy 2 IP: {proxy2_ip}")

        # Verify IPs are different
        if proxy1_ip and proxy2_ip:
            if proxy1_ip != direct_ip and proxy2_ip != direct_ip:
                logger.info("Proxy rotation verified successfully")
                return True
            else:
                logger.warning("Proxy IPs match direct IP - proxies may not be working")
                return False
        else:
            logger.error("Failed to get IPs through proxies")
            return False

    def rotate_tor_circuit(self) -> bool:
        """
        Rotate Tor circuit (requires control port access)

        Returns:
            True if successful
        """
        try:
            control_port = self.config.get('tor_control_port', 9051)
            control_password = self.config.get('tor_control_password')

            # Connect to Tor control port
            import telnetlib
            tn = telnetlib.Telnet('127.0.0.1', control_port, timeout=5)

            # Authenticate
            if control_password:
                tn.write(f'AUTHENTICATE "{control_password}"\r\n'.encode())
            else:
                tn.write(b'AUTHENTICATE\r\n')

            # Send NEWNYM signal (new identity)
            tn.write(b'SIGNAL NEWNYM\r\n')
            response = tn.read_until(b'250 OK', timeout=5)

            tn.write(b'QUIT\r\n')
            tn.close()

            if b'250 OK' in response:
                logger.info("Tor circuit rotated successfully")
                time.sleep(2)  # Wait for circuit to establish
                return True
            else:
                logger.error("Failed to rotate Tor circuit")
                return False

        except Exception as e:
            logger.error(f"Tor circuit rotation failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        if not self.proxies:
            return {
                'total_proxies': 0,
                'available_proxies': 0,
                'failed_proxies': 0
            }

        available = [p for p in self.proxies if p.failure_count < self.max_failures]
        failed = [p for p in self.proxies if p.failure_count >= self.max_failures]

        return {
            'total_proxies': len(self.proxies),
            'available_proxies': len(available),
            'failed_proxies': len(failed),
            'rotation_strategy': self.rotation_strategy.value,
            'current_proxy': f"{self.get_current_proxy().host}:{self.get_current_proxy().port}" if self.get_current_proxy() else None,
            'providers': list(set(p.provider for p in self.proxies)),
            'countries': list(set(p.country for p in self.proxies if p.country)),
        }


# Global proxy manager instance
_proxy_manager: Optional[ProxyManager] = None


def get_proxy_manager(config: Optional[Dict[str, Any]] = None) -> ProxyManager:
    """Get global proxy manager instance"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager(config)
    return _proxy_manager


def configure_proxies(config: Dict[str, Any]):
    """Configure global proxy manager"""
    global _proxy_manager
    _proxy_manager = ProxyManager(config)
