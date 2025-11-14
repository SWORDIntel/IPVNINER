"""
Host Discovery Module

Discovers active IPv9 hosts using ping and other techniques.
"""

import subprocess
import logging
import platform
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class HostDiscovery:
    """IPv9 host discovery functionality"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize host discovery

        Args:
            config: Configuration dictionary
        """
        from ..config import ConfigManager

        self.config = config or ConfigManager().get_config()
        self.scanner_config = self.config.get('scanner', {})
        self.timeout = self.scanner_config.get('timeout', 5)

    def ping(self, target: str, count: int = 4) -> Dict[str, Any]:
        """
        Ping an IPv9 host

        Args:
            target: IP address or hostname
            count: Number of ping packets

        Returns:
            Dictionary with ping results
        """
        logger.info(f"Pinging {target} ({count} packets)")

        # Platform-specific ping command
        system = platform.system().lower()

        if system == 'windows':
            cmd = ['ping', '-n', str(count), target]
        else:  # Linux, macOS, etc.
            cmd = ['ping', '-c', str(count), '-W', str(self.timeout), target]

        try:
            result = subprocess.run(cmd,
                                    capture_output=True,
                                    timeout=self.timeout * count + 5,
                                    text=True)

            # Parse output
            output = result.stdout

            ping_result = {
                'target': target,
                'reachable': result.returncode == 0,
                'packets_sent': count,
                'raw_output': output
            }

            # Try to extract statistics
            if 'packets transmitted' in output:
                ping_result['statistics'] = self._parse_ping_stats(output)

            logger.info(f"Ping {target}: {'success' if ping_result['reachable'] else 'failed'}")
            return ping_result

        except subprocess.TimeoutExpired:
            logger.warning(f"Ping timeout for {target}")
            return {
                'target': target,
                'reachable': False,
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"Ping failed for {target}: {e}")
            return {
                'target': target,
                'reachable': False,
                'error': str(e)
            }

    def _parse_ping_stats(self, output: str) -> Dict[str, Any]:
        """Extract ping statistics from output"""
        stats = {}

        # Look for packet statistics line
        # Format: "X packets transmitted, Y received, Z% packet loss, time Wms"
        import re

        packets_match = re.search(r'(\d+) packets transmitted, (\d+) received', output)
        if packets_match:
            stats['transmitted'] = int(packets_match.group(1))
            stats['received'] = int(packets_match.group(2))

        loss_match = re.search(r'(\d+(?:\.\d+)?)% packet loss', output)
        if loss_match:
            stats['packet_loss'] = float(loss_match.group(1))

        # Look for RTT statistics
        # Format: "rtt min/avg/max/mdev = X/Y/Z/W ms"
        rtt_match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output)
        if rtt_match:
            stats['rtt'] = {
                'min': float(rtt_match.group(1)),
                'avg': float(rtt_match.group(2)),
                'max': float(rtt_match.group(3)),
                'mdev': float(rtt_match.group(4))
            }

        return stats

    def ping_sweep(self, targets: List[str], timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Ping sweep multiple targets

        Args:
            targets: List of IP addresses or hostnames
            timeout: Timeout per host

        Returns:
            List of ping results for each target
        """
        results = []
        timeout = timeout or self.timeout

        logger.info(f"Starting ping sweep of {len(targets)} targets")

        for target in targets:
            result = self.ping(target, count=1)
            results.append(result)

        # Count successful pings
        alive_count = sum(1 for r in results if r.get('reachable', False))
        logger.info(f"Ping sweep complete: {alive_count}/{len(targets)} hosts alive")

        return results

    def tcp_ping(self, target: str, port: int = 80) -> Dict[str, Any]:
        """
        TCP ping (SYN ping) to check if host is alive

        Args:
            target: IP address or hostname
            port: TCP port to probe

        Returns:
            Dictionary with TCP ping result
        """
        import socket

        logger.debug(f"TCP ping {target}:{port}")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            start_time = __import__('time').time()
            result = sock.connect_ex((target, port))
            end_time = __import__('time').time()

            sock.close()

            reachable = (result == 0)
            response_time = (end_time - start_time) * 1000  # ms

            return {
                'target': target,
                'port': port,
                'reachable': reachable,
                'response_time_ms': response_time
            }

        except socket.timeout:
            return {
                'target': target,
                'port': port,
                'reachable': False,
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"TCP ping failed for {target}:{port}: {e}")
            return {
                'target': target,
                'port': port,
                'reachable': False,
                'error': str(e)
            }

    def http_probe(self, target: str, port: int = 80, use_https: bool = False) -> Dict[str, Any]:
        """
        HTTP/HTTPS probe to check web service

        Args:
            target: IP address or hostname
            port: HTTP(S) port
            use_https: Use HTTPS instead of HTTP

        Returns:
            Dictionary with HTTP probe result
        """
        import urllib.request
        import urllib.error
        import ssl

        protocol = 'https' if use_https else 'http'
        url = f"{protocol}://{target}:{port}/"

        logger.debug(f"HTTP probe: {url}")

        try:
            # Create SSL context that doesn't verify certificates (for testing)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(url, headers={'User-Agent': 'IPv9Scanner/1.0'})

            start_time = __import__('time').time()
            response = urllib.request.urlopen(req, timeout=self.timeout, context=ctx)
            end_time = __import__('time').time()

            return {
                'target': target,
                'url': url,
                'reachable': True,
                'status_code': response.getcode(),
                'response_time_ms': (end_time - start_time) * 1000,
                'server': response.headers.get('Server')
            }

        except urllib.error.HTTPError as e:
            return {
                'target': target,
                'url': url,
                'reachable': True,
                'status_code': e.code,
                'error': str(e)
            }
        except urllib.error.URLError as e:
            return {
                'target': target,
                'url': url,
                'reachable': False,
                'error': str(e.reason)
            }
        except Exception as e:
            logger.error(f"HTTP probe failed for {url}: {e}")
            return {
                'target': target,
                'url': url,
                'reachable': False,
                'error': str(e)
            }
