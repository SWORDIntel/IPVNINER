"""
Audit Engine

Comprehensive network auditing engine for IPv9 networks.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class AuditEngine:
    """Comprehensive IPv9 network audit engine"""

    def __init__(self, resolver, scanner, discovery, enumerator, db_manager):
        """
        Initialize audit engine

        Args:
            resolver: IPv9Resolver instance
            scanner: PortScanner instance
            discovery: HostDiscovery instance
            enumerator: DNSEnumerator instance
            db_manager: DatabaseManager instance
        """
        self.resolver = resolver
        self.scanner = scanner
        self.discovery = discovery
        self.enumerator = enumerator
        self.db = db_manager

        self.audit_id = None
        self.status = "idle"
        self.progress = 0.0
        self.findings = []

        logger.info("Audit engine initialized")

    async def run_full_audit(
        self,
        scan_dns: bool = True,
        scan_web: bool = True,
        scan_all_ports: bool = False,
        deep_scan: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive network audit

        Args:
            scan_dns: Scan DNS infrastructure
            scan_web: Scan web services
            scan_all_ports: Scan all 65535 ports
            deep_scan: Enable deep inspection
            progress_callback: Optional progress callback function

        Returns:
            Audit results
        """
        import uuid

        self.audit_id = str(uuid.uuid4())
        self.status = "running"
        self.progress = 0.0
        self.findings = []

        started_at = datetime.utcnow()

        logger.info(f"Starting full audit {self.audit_id}")

        try:
            # Phase 1: DNS Infrastructure Scan (20%)
            if scan_dns:
                logger.info("Phase 1: DNS Infrastructure Scan")
                await self._scan_dns_infrastructure()
                self.progress = 20.0
                if progress_callback:
                    progress_callback(self.progress)

            # Phase 2: Domain Enumeration (40%)
            logger.info("Phase 2: Domain Enumeration")
            await self._enumerate_domains()
            self.progress = 40.0
            if progress_callback:
                progress_callback(self.progress)

            # Phase 3: Host Discovery (60%)
            logger.info("Phase 3: Host Discovery")
            discovered_hosts = await self._discover_hosts()
            self.progress = 60.0
            if progress_callback:
                progress_callback(self.progress)

            # Phase 4: Port Scanning (80%)
            logger.info("Phase 4: Port Scanning")
            if scan_all_ports:
                await self._scan_all_ports(discovered_hosts)
            else:
                await self._scan_common_ports(discovered_hosts)
            self.progress = 80.0
            if progress_callback:
                progress_callback(self.progress)

            # Phase 5: Deep Inspection (90%)
            if deep_scan:
                logger.info("Phase 5: Deep Inspection")
                await self._deep_inspection(discovered_hosts)
            self.progress = 90.0
            if progress_callback:
                progress_callback(self.progress)

            # Phase 6: Analysis and Reporting (100%)
            logger.info("Phase 6: Analysis and Reporting")
            results = await self._analyze_results()
            self.progress = 100.0
            if progress_callback:
                progress_callback(self.progress)

            self.status = "completed"
            completed_at = datetime.utcnow()

            logger.info(f"Audit {self.audit_id} completed successfully")

            return {
                'audit_id': self.audit_id,
                'status': self.status,
                'started_at': started_at,
                'completed_at': completed_at,
                'duration': (completed_at - started_at).total_seconds(),
                'findings': self.findings,
                'results': results
            }

        except Exception as e:
            self.status = "failed"
            logger.error(f"Audit {self.audit_id} failed: {e}")
            raise

    async def _scan_dns_infrastructure(self):
        """Scan IPv9 DNS infrastructure"""
        logger.info("Scanning DNS infrastructure...")

        from ..dns.forwarder import DNSForwarder

        forwarder = DNSForwarder(
            self.resolver.primary_dns,
            self.resolver.secondary_dns
        )

        # Check DNS server reachability
        dns_status = forwarder.check_dns_reachability()

        for server, status in dns_status.items():
            if status['reachable']:
                self.findings.append({
                    'type': 'dns_server',
                    'severity': 'info',
                    'server': server,
                    'ip': status['ip'],
                    'status': 'reachable'
                })
            else:
                self.findings.append({
                    'type': 'dns_server',
                    'severity': 'warning',
                    'server': server,
                    'ip': status['ip'],
                    'status': 'unreachable'
                })

        # Test DNS resolution for known domains
        test_domains = ['www.v9.chn', 'em777.chn', 'www.hqq.chn']

        for domain in test_domains:
            addresses = self.resolver.resolve(domain)
            if addresses:
                self.findings.append({
                    'type': 'dns_resolution',
                    'severity': 'info',
                    'domain': domain,
                    'addresses': addresses
                })

    async def _enumerate_domains(self):
        """Enumerate IPv9 domains"""
        logger.info("Enumerating domains...")

        # Chinese mobile number prefixes (comprehensive list)
        mobile_prefixes = [
            # China Mobile
            '134', '135', '136', '137', '138', '139',
            '147', '148', '150', '151', '152', '157', '158', '159',
            '172', '178', '182', '183', '184', '187', '188', '198',

            # China Unicom
            '130', '131', '132', '145', '146', '155', '156',
            '166', '171', '175', '176', '185', '186',

            # China Telecom
            '133', '149', '153', '173', '174', '177', '180', '181', '189', '191', '199'
        ]

        # Sample each prefix
        for prefix in mobile_prefixes[:10]:  # Limit for performance
            pattern = f"86{prefix}NNNNNNNN"
            results = self.enumerator.brute_force_pattern(pattern, "chn", 100)

            for result in results:
                await self.db.store_domain({
                    'hostname': result['hostname'],
                    'addresses': result['addresses'],
                    'responsive': True
                })

                self.findings.append({
                    'type': 'domain_discovered',
                    'severity': 'info',
                    'hostname': result['hostname'],
                    'addresses': result['addresses']
                })

    async def _discover_hosts(self) -> List[str]:
        """Discover active hosts"""
        logger.info("Discovering hosts...")

        # Get all discovered IPs from database
        hosts = await self.db.get_hosts(alive_only=False, limit=10000)

        discovered = []

        for host in hosts:
            ip = host['ip_address']

            # Ping test
            ping_result = self.discovery.ping(ip, count=2)

            if ping_result.get('reachable'):
                discovered.append(ip)

                self.findings.append({
                    'type': 'host_alive',
                    'severity': 'info',
                    'ip': ip,
                    'ping_stats': ping_result.get('statistics')
                })

        logger.info(f"Discovered {len(discovered)} alive hosts")
        return discovered

    async def _scan_common_ports(self, hosts: List[str]):
        """Scan common ports on hosts"""
        logger.info(f"Scanning common ports on {len(hosts)} hosts...")

        common_ports = "21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,1521,3306,3389,5432,5900,8000,8080,8443,8888"

        for host in hosts[:100]:  # Limit for performance
            try:
                result = self.scanner.scan_nmap(
                    host,
                    ports=common_ports,
                    scan_type="syn",
                    service_detection=True
                )

                if 'hosts' in result:
                    for host_data in result['hosts']:
                        for port in host_data.get('ports', []):
                            if port['state'] == 'open':
                                self.findings.append({
                                    'type': 'open_port',
                                    'severity': 'info',
                                    'host': host,
                                    'port': port['port'],
                                    'service': port.get('service', {}).get('name'),
                                    'version': port.get('service', {}).get('version')
                                })
            except Exception as e:
                logger.error(f"Scan failed for {host}: {e}")

    async def _scan_all_ports(self, hosts: List[str]):
        """Scan all ports on hosts using masscan"""
        logger.info(f"Scanning all ports on {len(hosts)} hosts (masscan)...")

        # Use masscan for high-speed full port scan
        result = self.scanner.scan_masscan(
            hosts[:100],  # Limit for performance
            ports="1-65535"
        )

        for host_data in result.get('hosts', []):
            for port_data in host_data.get('ports', []):
                self.findings.append({
                    'type': 'open_port',
                    'severity': 'info',
                    'host': host_data['ip'],
                    'port': port_data['port'],
                    'state': 'open'
                })

    async def _deep_inspection(self, hosts: List[str]):
        """Perform deep inspection on discovered services"""
        logger.info("Performing deep inspection...")

        # HTTP service inspection
        for host in hosts[:50]:  # Limit for performance
            # Try HTTP
            http_result = self.discovery.http_probe(host, port=80, use_https=False)
            if http_result.get('reachable'):
                self.findings.append({
                    'type': 'http_service',
                    'severity': 'info',
                    'host': host,
                    'port': 80,
                    'status_code': http_result.get('status_code'),
                    'server': http_result.get('server')
                })

            # Try HTTPS
            https_result = self.discovery.http_probe(host, port=443, use_https=True)
            if https_result.get('reachable'):
                self.findings.append({
                    'type': 'https_service',
                    'severity': 'info',
                    'host': host,
                    'port': 443,
                    'status_code': https_result.get('status_code'),
                    'server': https_result.get('server')
                })

    async def _analyze_results(self) -> Dict[str, Any]:
        """Analyze audit results"""
        logger.info("Analyzing results...")

        # Get statistics from database
        stats = await self.db.get_stats()

        # Categorize findings
        findings_by_type = {}
        for finding in self.findings:
            finding_type = finding['type']
            if finding_type not in findings_by_type:
                findings_by_type[finding_type] = []
            findings_by_type[finding_type].append(finding)

        # Calculate security score (placeholder)
        security_score = 100

        return {
            'statistics': stats,
            'findings_summary': {
                'total': len(self.findings),
                'by_type': {k: len(v) for k, v in findings_by_type.items()}
            },
            'security_score': security_score,
            'recommendations': self._generate_recommendations(findings_by_type)
        }

    def _generate_recommendations(self, findings_by_type: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        # DNS recommendations
        if 'dns_server' in findings_by_type:
            unreachable = [f for f in findings_by_type['dns_server'] if f['status'] == 'unreachable']
            if unreachable:
                recommendations.append("Some DNS servers are unreachable. Consider redundancy.")

        # Open port recommendations
        if 'open_port' in findings_by_type:
            dangerous_ports = [f for f in findings_by_type['open_port'] if f['port'] in [23, 3389, 1433, 3306]]
            if dangerous_ports:
                recommendations.append("Dangerous ports (Telnet, RDP, SQL) are exposed. Restrict access.")

        # HTTP recommendations
        if 'http_service' in findings_by_type:
            http_only = [f for f in findings_by_type['http_service']]
            if http_only:
                recommendations.append("HTTP-only services found. Consider migrating to HTTPS.")

        return recommendations
