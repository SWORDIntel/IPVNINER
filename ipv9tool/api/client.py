"""
IPv9 API Client

Python client library for the IPv9 Scanner API.
"""

import requests
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from .models import *

logger = logging.getLogger(__name__)


class IPv9APIClient:
    """Client for IPv9 Scanner API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL of the API server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers['Authorization'] = f"Bearer {api_key}"

        logger.info(f"IPv9 API client initialized for {base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Response JSON
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def health(self) -> HealthResponse:
        """Get API health status"""
        data = self._request('GET', '/health')
        return HealthResponse(**data)

    def info(self) -> APIInfo:
        """Get API information"""
        data = self._request('GET', '/')
        return APIInfo(**data)

    # DNS Operations

    def resolve(self, hostname: str, record_type: str = 'A', use_cache: bool = True) -> ResolveResponse:
        """
        Resolve hostname

        Args:
            hostname: Hostname to resolve
            record_type: DNS record type
            use_cache: Use DNS cache

        Returns:
            Resolution result
        """
        request = ResolveRequest(
            hostname=hostname,
            record_type=record_type,
            use_cache=use_cache
        )

        data = self._request('POST', '/dns/resolve', json=request.dict())
        return ResolveResponse(**data)

    # Network Operations

    def ping(self, target: str, count: int = 4, timeout: int = 5) -> PingResponse:
        """
        Ping host

        Args:
            target: Target to ping
            count: Number of packets
            timeout: Timeout in seconds

        Returns:
            Ping result
        """
        request = PingRequest(
            target=target,
            count=count,
            timeout=timeout
        )

        data = self._request('POST', '/network/ping', json=request.dict())
        return PingResponse(**data)

    def scan(
        self,
        target: str,
        ports: str = "1-1000",
        scan_type: str = "syn",
        service_detection: bool = True,
        os_detection: bool = False
    ) -> ScanResponse:
        """
        Scan host ports

        Args:
            target: Target to scan
            ports: Port range or list
            scan_type: Scan type
            service_detection: Enable service detection
            os_detection: Enable OS detection

        Returns:
            Scan result
        """
        request = ScanRequest(
            target=target,
            ports=ports,
            scan_type=scan_type,
            service_detection=service_detection,
            os_detection=os_detection
        )

        data = self._request('POST', '/network/scan', json=request.dict())
        return ScanResponse(**data)

    # Enumeration Operations

    def enumerate_pattern(
        self,
        pattern: str,
        tld: str = "chn",
        max_combinations: int = 1000,
        parallel: bool = True
    ) -> EnumerateResponse:
        """
        Enumerate domains by pattern

        Args:
            pattern: Pattern to enumerate
            tld: Top-level domain
            max_combinations: Maximum combinations
            parallel: Use parallel enumeration

        Returns:
            Enumeration result
        """
        request = EnumerateRequest(
            pattern=pattern,
            tld=tld,
            max_combinations=max_combinations,
            parallel=parallel
        )

        data = self._request('POST', '/enumerate/pattern', json=request.dict())
        return EnumerateResponse(**data)

    def enumerate_full(self) -> JobStatus:
        """
        Start full network enumeration (background job)

        Returns:
            Job status
        """
        data = self._request('POST', '/enumerate/full')
        return JobStatus(**data)

    # Audit Operations

    def start_audit(
        self,
        scan_dns: bool = True,
        scan_web: bool = True,
        scan_all_ports: bool = False,
        deep_scan: bool = False,
        continuous: bool = False
    ) -> JobStatus:
        """
        Start full network audit (background job)

        Args:
            scan_dns: Scan DNS infrastructure
            scan_web: Scan web services
            scan_all_ports: Scan all 65535 ports
            deep_scan: Enable deep inspection
            continuous: Continuous monitoring mode

        Returns:
            Job status
        """
        request = AuditRequest(
            scan_dns=scan_dns,
            scan_web=scan_web,
            scan_all_ports=scan_all_ports,
            deep_scan=deep_scan,
            continuous=continuous
        )

        data = self._request('POST', '/audit/start', json=request.dict())
        return JobStatus(**data)

    # Job Operations

    def get_job(self, job_id: str) -> JobStatus:
        """
        Get job status

        Args:
            job_id: Job ID

        Returns:
            Job status
        """
        data = self._request('GET', f'/jobs/{job_id}')
        return JobStatus(**data)

    def list_jobs(self, status: Optional[str] = None, limit: int = 100) -> List[JobStatus]:
        """
        List jobs

        Args:
            status: Filter by status
            limit: Maximum number of jobs

        Returns:
            List of job statuses
        """
        params = {'limit': limit}
        if status:
            params['status'] = status

        data = self._request('GET', '/jobs', params=params)
        return [JobStatus(**job) for job in data]

    def wait_for_job(self, job_id: str, poll_interval: int = 2, timeout: int = 3600) -> JobStatus:
        """
        Wait for job to complete

        Args:
            job_id: Job ID
            poll_interval: Poll interval in seconds
            timeout: Timeout in seconds

        Returns:
            Final job status
        """
        import time

        start_time = time.time()

        while True:
            job = self.get_job(job_id)

            if job.status in ['completed', 'failed']:
                return job

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

            time.sleep(poll_interval)

    # Data Operations

    def get_hosts(self, alive_only: bool = True, limit: int = 100) -> List[DiscoveredHost]:
        """
        Get discovered hosts

        Args:
            alive_only: Only return alive hosts
            limit: Maximum number of hosts

        Returns:
            List of discovered hosts
        """
        params = {'alive_only': alive_only, 'limit': limit}
        data = self._request('GET', '/hosts', params=params)
        return [DiscoveredHost(**host) for host in data]

    def get_ports(
        self,
        host_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[DiscoveredPort]:
        """
        Get discovered ports

        Args:
            host_id: Filter by host ID
            state: Filter by state
            limit: Maximum number of ports

        Returns:
            List of discovered ports
        """
        params = {'limit': limit}
        if host_id:
            params['host_id'] = host_id
        if state:
            params['state'] = state

        data = self._request('GET', '/ports', params=params)
        return [DiscoveredPort(**port) for port in data]

    def get_stats(self) -> NetworkStats:
        """
        Get network statistics

        Returns:
            Network statistics
        """
        data = self._request('GET', '/stats')
        return NetworkStats(**data)


# Convenience functions for quick operations

def quick_resolve(hostname: str, api_url: str = "http://localhost:8000") -> List[str]:
    """Quick DNS resolution"""
    client = IPv9APIClient(api_url)
    result = client.resolve(hostname)
    return result.addresses


def quick_scan(target: str, ports: str = "80,443", api_url: str = "http://localhost:8000") -> ScanResponse:
    """Quick port scan"""
    client = IPv9APIClient(api_url)
    return client.scan(target, ports=ports)


def quick_enumerate(pattern: str, max_results: int = 100, api_url: str = "http://localhost:8000") -> EnumerateResponse:
    """Quick domain enumeration"""
    client = IPv9APIClient(api_url)
    return client.enumerate_pattern(pattern, max_combinations=max_results)
