"""
Masscan-based Full Network Enumerator

Uses masscan for high-speed enumeration of the entire IPv9 address space.
"""

import subprocess
import json
import logging
import tempfile
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class MasscanEnumerator:
    """High-speed masscan-based network enumerator"""

    def __init__(self, rate: int = 10000, max_rate: int = 100000):
        """
        Initialize masscan enumerator

        Args:
            rate: Default scan rate (packets per second)
            max_rate: Maximum allowed scan rate
        """
        self.rate = min(rate, max_rate)
        self.max_rate = max_rate

        # Check if masscan is installed
        try:
            subprocess.run(['masscan', '--version'], capture_output=True, check=True)
            logger.info(f"Masscan enumerator initialized (rate={self.rate} pps)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("masscan not found - enumeration will be limited")

    def enumerate_full_network(
        self,
        ip_ranges: List[str],
        ports: str = "80,443,8080,22,21",
        exclude: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Enumerate full network using masscan

        Args:
            ip_ranges: List of IP ranges to scan (CIDR notation)
            ports: Ports to scan
            exclude: IP ranges to exclude
            progress_callback: Optional progress callback

        Returns:
            Scan results
        """
        logger.info(f"Starting masscan enumeration of {len(ip_ranges)} ranges")

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as targets_file:
            for ip_range in ip_ranges:
                targets_file.write(f"{ip_range}\n")
            targets_path = targets_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as exclude_file:
            if exclude:
                for exc in exclude:
                    exclude_file.write(f"{exc}\n")
            exclude_path = exclude_file.name

        output_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        output_path = output_file.name
        output_file.close()

        try:
            # Build masscan command
            cmd = [
                'masscan',
                '-iL', targets_path,
                '-p', ports,
                '--rate', str(self.rate),
                '-oJ', output_path
            ]

            if exclude:
                cmd.extend(['--excludefile', exclude_path])

            logger.info(f"Running masscan: {' '.join(cmd)}")

            # Run masscan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode != 0:
                logger.error(f"masscan failed: {result.stderr}")
                return {'error': result.stderr, 'hosts': []}

            # Parse results
            results = self._parse_masscan_output(output_path)

            logger.info(f"Masscan enumeration complete: {len(results['hosts'])} hosts found")

            return results

        except subprocess.TimeoutExpired:
            logger.error("Masscan timed out")
            return {'error': 'timeout', 'hosts': []}
        except Exception as e:
            logger.error(f"Masscan enumeration failed: {e}")
            return {'error': str(e), 'hosts': []}
        finally:
            # Cleanup temp files
            Path(targets_path).unlink(missing_ok=True)
            Path(exclude_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def _parse_masscan_output(self, output_file: str) -> Dict[str, Any]:
        """Parse masscan JSON output"""
        hosts = {}

        try:
            with open(output_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    try:
                        entry = json.loads(line.rstrip(','))

                        if 'ip' in entry and 'ports' in entry:
                            ip = entry['ip']

                            if ip not in hosts:
                                hosts[ip] = {
                                    'ip': ip,
                                    'ports': [],
                                    'timestamp': entry.get('timestamp')
                                }

                            for port_data in entry['ports']:
                                hosts[ip]['ports'].append({
                                    'port': port_data.get('port'),
                                    'proto': port_data.get('proto'),
                                    'status': port_data.get('status'),
                                    'reason': port_data.get('reason'),
                                    'ttl': port_data.get('ttl')
                                })

                    except json.JSONDecodeError:
                        continue

            return {
                'hosts': list(hosts.values()),
                'total_hosts': len(hosts),
                'total_ports': sum(len(h['ports']) for h in hosts.values())
            }

        except Exception as e:
            logger.error(f"Failed to parse masscan output: {e}")
            return {'hosts': [], 'total_hosts': 0, 'total_ports': 0}

    def enumerate_ipv9_space(
        self,
        sample_rate: float = 0.01,
        ports: str = "80,443",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Enumerate IPv9 address space

        Since IPv9 resolves to regular IPv4/IPv6, we enumerate likely ranges
        based on known Chinese network allocations.

        Args:
            sample_rate: Percentage of address space to sample (0.0-1.0)
            ports: Ports to scan
            progress_callback: Optional progress callback

        Returns:
            Enumeration results
        """
        logger.info(f"Enumerating IPv9 address space (sample rate: {sample_rate})")

        # Known Chinese IP blocks (sample - would need comprehensive list)
        chinese_ip_ranges = [
            '1.0.0.0/8',      # APNIC/China
            '14.0.0.0/8',     # China Telecom
            '27.0.0.0/8',     # APNIC/China
            '36.0.0.0/8',     # China Telecom
            '42.0.0.0/8',     # APNIC/China
            '58.0.0.0/8',     # China Unicom
            '59.0.0.0/8',     # China Telecom
            '60.0.0.0/8',     # China Telecom
            '61.0.0.0/8',     # APNIC/China
            '101.0.0.0/8',    # China Mobile
            '106.0.0.0/8',    # China Unicom
            '110.0.0.0/8',    # China Telecom
            '111.0.0.0/8',    # China Mobile
            '112.0.0.0/8',    # China Telecom
            '113.0.0.0/8',    # China Mobile
            '114.0.0.0/8',    # China Telecom
            '115.0.0.0/8',    # China Telecom
            '116.0.0.0/8',    # China Unicom
            '117.0.0.0/8',    # China Mobile
            '118.0.0.0/8',    # China Telecom
            '119.0.0.0/8',    # China Telecom
            '120.0.0.0/8',    # China Mobile
            '121.0.0.0/8',    # China Telecom
            '122.0.0.0/8',    # China Telecom
            '123.0.0.0/8',    # China Telecom
            '124.0.0.0/8',    # China Telecom
            '125.0.0.0/8',    # China Telecom
            '180.0.0.0/8',    # China Telecom
            '182.0.0.0/8',    # China Unicom
            '183.0.0.0/8',    # China Telecom
            '202.0.0.0/8',    # APNIC/China
            '203.0.0.0/8',    # APNIC/China
            '210.0.0.0/8',    # APNIC/China
            '211.0.0.0/8',    # APNIC/China
            '218.0.0.0/8',    # China Unicom
            '219.0.0.0/8',    # China Telecom
            '220.0.0.0/8',    # China Telecom
            '221.0.0.0/8',    # China Unicom
            '222.0.0.0/8',    # China Telecom
            '223.0.0.0/8',    # China Mobile
        ]

        # Sample ranges based on sample_rate
        import random
        sampled_ranges = random.sample(
            chinese_ip_ranges,
            int(len(chinese_ip_ranges) * sample_rate)
        )

        # Run enumeration
        return self.enumerate_full_network(
            sampled_ranges,
            ports=ports,
            progress_callback=progress_callback
        )

    def create_enumeration_plan(
        self,
        total_budget_hours: int = 24,
        ports: str = "80,443,8080,22"
    ) -> Dict[str, Any]:
        """
        Create an enumeration plan that fits within a time budget

        Args:
            total_budget_hours: Total time budget in hours
            ports: Ports to scan

        Returns:
            Enumeration plan
        """
        # Calculate how much of address space can be scanned
        # Masscan can do ~10M packets/sec theoretically
        # In practice, use conservative estimate

        packets_per_second = self.rate
        total_seconds = total_budget_hours * 3600
        total_packets = packets_per_second * total_seconds

        # Each IP+port combination = 1 packet (SYN scan)
        num_ports = len(ports.split(','))
        total_ips_scannable = total_packets // num_ports

        # Calculate coverage
        total_ipv4_space = 2**32  # ~4.3 billion
        coverage = (total_ips_scannable / total_ipv4_space) * 100

        plan = {
            'budget_hours': total_budget_hours,
            'rate_pps': packets_per_second,
            'ports': ports,
            'num_ports': num_ports,
            'total_packets': total_packets,
            'total_ips_scannable': total_ips_scannable,
            'coverage_percent': coverage,
            'estimated_duration_hours': total_budget_hours,
            'recommended_approach': 'targeted' if coverage < 1 else 'comprehensive'
        }

        logger.info(f"Enumeration plan created: {coverage:.2f}% coverage in {total_budget_hours}h")

        return plan
