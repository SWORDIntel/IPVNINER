"""
Port Scanner Module

Scans IPv9 hosts for open ports and services using nmap/masscan.
"""

import subprocess
import json
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PortScanner:
    """Port scanning functionality for IPv9 hosts"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize port scanner

        Args:
            config: Configuration dictionary
        """
        from ..config import ConfigManager

        self.config = config or ConfigManager().get_config()
        self.scanner_config = self.config.get('scanner', {})
        self.rate_limit = self.scanner_config.get('rate_limit', 100)
        self.timeout = self.scanner_config.get('timeout', 5)

    def check_nmap_installed(self) -> bool:
        """Check if nmap is installed"""
        try:
            result = subprocess.run(['nmap', '--version'],
                                    capture_output=True,
                                    timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def check_masscan_installed(self) -> bool:
        """Check if masscan is installed"""
        try:
            result = subprocess.run(['masscan', '--version'],
                                    capture_output=True,
                                    timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def scan_nmap(self,
                  target: str,
                  ports: str = "1-1000",
                  scan_type: str = "syn",
                  service_detection: bool = True,
                  os_detection: bool = False) -> Dict[str, Any]:
        """
        Scan target using nmap

        Args:
            target: IP address or hostname
            ports: Port range (e.g., "1-1000", "80,443,8080")
            scan_type: Scan type (syn, tcp, udp, ack)
            service_detection: Enable service version detection
            os_detection: Enable OS detection

        Returns:
            Dictionary with scan results
        """
        if not self.check_nmap_installed():
            logger.error("nmap is not installed")
            return {'error': 'nmap not installed'}

        # Build nmap command
        cmd = ['nmap']

        # Scan type
        if scan_type == 'syn':
            cmd.append('-sS')
        elif scan_type == 'tcp':
            cmd.append('-sT')
        elif scan_type == 'udp':
            cmd.append('-sU')
        elif scan_type == 'ack':
            cmd.append('-sA')

        # Port specification
        cmd.extend(['-p', ports])

        # Service detection
        if service_detection:
            cmd.append('-sV')

        # OS detection
        if os_detection:
            cmd.append('-O')

        # Rate limiting
        cmd.extend(['--max-rate', str(self.rate_limit)])

        # Timeout
        cmd.extend(['--host-timeout', f'{self.timeout}s'])

        # Output format (XML for parsing)
        cmd.extend(['-oX', '-'])

        # Skip host discovery (assume host is up)
        cmd.append('-Pn')

        # Target
        cmd.append(target)

        logger.info(f"Running nmap: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd,
                                    capture_output=True,
                                    timeout=self.timeout * 10,
                                    text=True)

            if result.returncode != 0:
                logger.error(f"nmap failed: {result.stderr}")
                return {'error': result.stderr}

            # Parse XML output
            scan_results = self._parse_nmap_xml(result.stdout)
            scan_results['target'] = target
            scan_results['ports_scanned'] = ports

            return scan_results

        except subprocess.TimeoutExpired:
            logger.error(f"nmap scan timed out for {target}")
            return {'error': 'scan timeout'}
        except Exception as e:
            logger.error(f"nmap scan failed: {e}")
            return {'error': str(e)}

    def _parse_nmap_xml(self, xml_data: str) -> Dict[str, Any]:
        """Parse nmap XML output"""
        try:
            root = ET.fromstring(xml_data)

            results = {
                'hosts': [],
                'scan_info': {}
            }

            # Parse scan info
            scaninfo = root.find('scaninfo')
            if scaninfo is not None:
                results['scan_info'] = {
                    'type': scaninfo.get('type'),
                    'protocol': scaninfo.get('protocol'),
                    'services': scaninfo.get('services')
                }

            # Parse hosts
            for host in root.findall('host'):
                host_data = {
                    'addresses': [],
                    'hostnames': [],
                    'ports': [],
                    'os': None
                }

                # Addresses
                for addr in host.findall('address'):
                    host_data['addresses'].append({
                        'addr': addr.get('addr'),
                        'type': addr.get('addrtype')
                    })

                # Hostnames
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    for hostname in hostnames.findall('hostname'):
                        host_data['hostnames'].append({
                            'name': hostname.get('name'),
                            'type': hostname.get('type')
                        })

                # Ports
                ports = host.find('ports')
                if ports is not None:
                    for port in ports.findall('port'):
                        state = port.find('state')
                        service = port.find('service')

                        port_data = {
                            'port': int(port.get('portid')),
                            'protocol': port.get('protocol'),
                            'state': state.get('state') if state is not None else 'unknown'
                        }

                        if service is not None:
                            port_data['service'] = {
                                'name': service.get('name'),
                                'product': service.get('product'),
                                'version': service.get('version'),
                                'extrainfo': service.get('extrainfo')
                            }

                        host_data['ports'].append(port_data)

                # OS detection
                os_elem = host.find('os')
                if os_elem is not None:
                    osmatch = os_elem.find('osmatch')
                    if osmatch is not None:
                        host_data['os'] = {
                            'name': osmatch.get('name'),
                            'accuracy': osmatch.get('accuracy')
                        }

                results['hosts'].append(host_data)

            return results

        except ET.ParseError as e:
            logger.error(f"Failed to parse nmap XML: {e}")
            return {'error': 'XML parse error'}

    def scan_masscan(self,
                     targets: List[str],
                     ports: str = "1-1000") -> Dict[str, Any]:
        """
        Scan targets using masscan (fast, but requires IP addresses)

        Args:
            targets: List of IP addresses (masscan doesn't do DNS)
            ports: Port range

        Returns:
            Dictionary with scan results
        """
        if not self.check_masscan_installed():
            logger.error("masscan is not installed")
            return {'error': 'masscan not installed'}

        # Write targets to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            for target in targets:
                f.write(f"{target}\n")
            target_file = f.name

        try:
            # Build masscan command
            cmd = [
                'masscan',
                '-iL', target_file,
                '-p', ports,
                '--rate', str(self.rate_limit),
                '-oJ', '-'  # JSON output to stdout
            ]

            logger.info(f"Running masscan on {len(targets)} targets")

            result = subprocess.run(cmd,
                                    capture_output=True,
                                    timeout=self.timeout * 10,
                                    text=True)

            if result.returncode != 0:
                logger.error(f"masscan failed: {result.stderr}")
                return {'error': result.stderr}

            # Parse JSON output
            scan_results = self._parse_masscan_json(result.stdout)
            scan_results['targets_count'] = len(targets)
            scan_results['ports_scanned'] = ports

            return scan_results

        except subprocess.TimeoutExpired:
            logger.error("masscan timed out")
            return {'error': 'scan timeout'}
        except Exception as e:
            logger.error(f"masscan failed: {e}")
            return {'error': str(e)}
        finally:
            # Clean up temp file
            Path(target_file).unlink(missing_ok=True)

    def _parse_masscan_json(self, json_data: str) -> Dict[str, Any]:
        """Parse masscan JSON output"""
        results = {
            'hosts': []
        }

        try:
            # masscan outputs one JSON object per line
            for line in json_data.strip().split('\n'):
                if not line.strip():
                    continue

                try:
                    entry = json.loads(line)

                    if 'ip' in entry and 'ports' in entry:
                        host_data = {
                            'ip': entry['ip'],
                            'ports': entry['ports']
                        }
                        results['hosts'].append(host_data)

                except json.JSONDecodeError:
                    continue

            logger.info(f"masscan found {len(results['hosts'])} hosts with open ports")
            return results

        except Exception as e:
            logger.error(f"Failed to parse masscan JSON: {e}")
            return {'error': 'JSON parse error'}

    def quick_scan(self, target: str, common_ports: bool = True) -> Dict[str, Any]:
        """
        Quick scan of common ports

        Args:
            target: IP or hostname
            common_ports: Use common port list vs top 100

        Returns:
            Scan results
        """
        if common_ports:
            ports = "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080"
        else:
            ports = "1-100"

        return self.scan_nmap(target, ports=ports, service_detection=True)
