"""
FastAPI Server for IPv9 Tool

Provides RESTful API for all IPv9 operations.
"""

import time
import logging
import asyncio
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import *
from ..dns import IPv9Resolver, DNSCache
from ..scanner import PortScanner, HostDiscovery, DNSEnumerator
from ..config import ConfigManager
from ..security import setup_logging
from ..database import DatabaseManager
from .jobs import JobManager

logger = logging.getLogger(__name__)

# Global state
app_state = {
    'start_time': time.time(),
    'resolver': None,
    'cache': None,
    'scanner': None,
    'discovery': None,
    'enumerator': None,
    'db': None,
    'jobs': None,
    'config': None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting IPv9 API server...")

    # Initialize components
    config_manager = ConfigManager()
    config = config_manager.get_config()
    app_state['config'] = config

    setup_logging(config.get('logging', {}))

    app_state['resolver'] = IPv9Resolver(config)
    app_state['cache'] = DNSCache(
        max_size=config['dns']['cache_size'],
        default_ttl=config['dns']['ttl']
    )
    app_state['scanner'] = PortScanner(config)
    app_state['discovery'] = HostDiscovery(config)
    app_state['enumerator'] = DNSEnumerator(app_state['resolver'], config)
    app_state['db'] = DatabaseManager(config.get('database', {}))
    app_state['jobs'] = JobManager()

    # Initialize database
    await app_state['db'].initialize()

    logger.info("IPv9 API server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down IPv9 API server...")
    await app_state['db'].close()
    logger.info("IPv9 API server stopped")


def create_api_app(config_path: Optional[str] = None) -> FastAPI:
    """
    Create FastAPI application

    Args:
        config_path: Path to configuration file

    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="IPv9 Scanner API",
        description="Robust API for IPv9 network exploration, scanning, and auditing",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Check API health status"""
        from ..dns.forwarder import DNSForwarder

        # Check DNS servers
        forwarder = DNSForwarder(
            app_state['config']['dns']['primary'],
            app_state['config']['dns']['secondary']
        )
        dns_status = forwarder.check_dns_reachability()
        dns_reachable = all(s['reachable'] for s in dns_status.values())

        # Check database
        db_connected = await app_state['db'].is_connected()

        return HealthResponse(
            status="healthy" if (dns_reachable and db_connected) else "degraded",
            version="1.0.0",
            uptime=time.time() - app_state['start_time'],
            dns_servers_reachable=dns_reachable,
            database_connected=db_connected
        )

    # API info endpoint
    @app.get("/", response_model=APIInfo, tags=["System"])
    async def api_info():
        """Get API information"""
        return APIInfo(
            endpoints=[
                "/health", "/", "/dns/resolve", "/network/ping", "/network/scan",
                "/enumerate/pattern", "/enumerate/full", "/audit/start", "/audit/status",
                "/jobs/{job_id}", "/hosts", "/ports", "/stats"
            ],
            features=[
                "DNS Resolution with Caching",
                "Host Discovery (Ping, TCP, HTTP)",
                "Port Scanning (nmap, masscan)",
                "Domain Enumeration",
                "Full Network Auditing",
                "Background Job Processing",
                "Persistent Storage",
                "Real-time Statistics"
            ]
        )

    # DNS Resolution endpoint
    @app.post("/dns/resolve", response_model=ResolveResponse, tags=["DNS"])
    async def resolve_dns(request: ResolveRequest):
        """Resolve IPv9 hostname"""
        try:
            resolver = app_state['resolver']
            cache = app_state['cache']

            # Check cache
            if request.use_cache:
                cached = cache.get(request.hostname, request.record_type)
                if cached:
                    return ResolveResponse(
                        hostname=request.hostname,
                        record_type=request.record_type,
                        addresses=cached,
                        from_cache=True
                    )

            # Resolve
            addresses = resolver.resolve(request.hostname, request.record_type)

            if addresses and request.use_cache:
                cache.set(request.hostname, addresses, request.record_type)

            return ResolveResponse(
                hostname=request.hostname,
                record_type=request.record_type,
                addresses=addresses,
                from_cache=False
            )

        except Exception as e:
            logger.error(f"DNS resolution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Ping endpoint
    @app.post("/network/ping", response_model=PingResponse, tags=["Network"])
    async def ping_host(request: PingRequest):
        """Ping IPv9 host"""
        try:
            discovery = app_state['discovery']
            resolver = app_state['resolver']

            target = request.target

            # Resolve if IPv9 domain
            if resolver.is_ipv9_domain(target):
                addresses = resolver.resolve(target)
                if not addresses:
                    raise HTTPException(status_code=404, detail="Failed to resolve hostname")
                target = addresses[0]

            # Ping
            result = discovery.ping(target, request.count)

            stats = result.get('statistics', {})

            return PingResponse(
                target=target,
                reachable=result.get('reachable', False),
                packets_sent=request.count,
                packets_received=stats.get('received'),
                packet_loss=stats.get('packet_loss'),
                rtt_min=stats.get('rtt', {}).get('min'),
                rtt_avg=stats.get('rtt', {}).get('avg'),
                rtt_max=stats.get('rtt', {}).get('max')
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Scan endpoint
    @app.post("/network/scan", response_model=ScanResponse, tags=["Network"])
    async def scan_ports(request: ScanRequest, background_tasks: BackgroundTasks):
        """Scan IPv9 host ports"""
        try:
            scanner = app_state['scanner']
            resolver = app_state['resolver']

            target = request.target

            # Resolve if IPv9 domain
            if resolver.is_ipv9_domain(target):
                addresses = resolver.resolve(target)
                if not addresses:
                    raise HTTPException(status_code=404, detail="Failed to resolve hostname")
                target = addresses[0]

            # Scan
            start_time = time.time()
            result = scanner.scan_nmap(
                target,
                ports=request.ports,
                scan_type=request.scan_type,
                service_detection=request.service_detection,
                os_detection=request.os_detection
            )
            duration = time.time() - start_time

            if 'error' in result:
                raise HTTPException(status_code=500, detail=result['error'])

            # Convert to response model
            hosts = []
            for host_data in result.get('hosts', []):
                ports = []
                for port_data in host_data.get('ports', []):
                    service = port_data.get('service', {})
                    ports.append(PortInfo(
                        port=port_data['port'],
                        protocol=port_data['protocol'],
                        state=port_data['state'],
                        service=service.get('name'),
                        version=service.get('version'),
                        product=service.get('product')
                    ))

                os_info = host_data.get('os')
                hosts.append(HostInfo(
                    address=host_data.get('addresses', [{}])[0].get('addr', target),
                    hostname=host_data.get('hostnames', [{}])[0].get('name') if host_data.get('hostnames') else None,
                    ports=ports,
                    os=os_info.get('name') if os_info else None,
                    os_accuracy=int(os_info.get('accuracy', 0)) if os_info else None
                ))

            # Store in database (background task)
            background_tasks.add_task(store_scan_results, target, hosts)

            return ScanResponse(
                target=target,
                scan_type=request.scan_type,
                ports_scanned=request.ports,
                hosts=hosts,
                scan_duration=duration
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Enumerate endpoint
    @app.post("/enumerate/pattern", response_model=EnumerateResponse, tags=["Enumeration"])
    async def enumerate_pattern(request: EnumerateRequest, background_tasks: BackgroundTasks):
        """Enumerate IPv9 domains by pattern"""
        try:
            enumerator = app_state['enumerator']

            start_time = time.time()
            results = enumerator.brute_force_pattern(
                request.pattern,
                request.tld,
                request.max_combinations
            )
            duration = time.time() - start_time

            domains = [
                EnumeratedDomain(
                    hostname=r['hostname'],
                    addresses=r['addresses'],
                    responsive=len(r['addresses']) > 0
                )
                for r in results
            ]

            # Store in database (background task)
            background_tasks.add_task(store_enumeration_results, domains)

            return EnumerateResponse(
                pattern=request.pattern,
                total_checked=request.max_combinations,
                total_found=len(results),
                domains=domains,
                duration=duration
            )

        except Exception as e:
            logger.error(f"Enumeration failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Full enumeration endpoint (background job)
    @app.post("/enumerate/full", response_model=JobStatus, tags=["Enumeration"])
    async def enumerate_full(background_tasks: BackgroundTasks):
        """Start full IPv9 network enumeration (background job)"""
        try:
            job_id = app_state['jobs'].create_job("full_enumeration")

            background_tasks.add_task(
                run_full_enumeration,
                job_id
            )

            return app_state['jobs'].get_job(job_id)

        except Exception as e:
            logger.error(f"Failed to start enumeration: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Audit start endpoint
    @app.post("/audit/start", response_model=JobStatus, tags=["Audit"])
    async def start_audit(request: AuditRequest, background_tasks: BackgroundTasks):
        """Start full network audit (background job)"""
        try:
            job_id = app_state['jobs'].create_job("network_audit", metadata=request.dict())

            background_tasks.add_task(
                run_network_audit,
                job_id,
                request
            )

            return app_state['jobs'].get_job(job_id)

        except Exception as e:
            logger.error(f"Failed to start audit: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # Job status endpoint
    @app.get("/jobs/{job_id}", response_model=JobStatus, tags=["Jobs"])
    async def get_job_status(job_id: str):
        """Get background job status"""
        job = app_state['jobs'].get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    # List jobs endpoint
    @app.get("/jobs", response_model=List[JobStatus], tags=["Jobs"])
    async def list_jobs(
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: int = Query(100, ge=1, le=1000)
    ):
        """List background jobs"""
        return app_state['jobs'].list_jobs(status=status, limit=limit)

    # Get discovered hosts
    @app.get("/hosts", response_model=List[DiscoveredHost], tags=["Data"])
    async def get_hosts(
        alive_only: bool = Query(True),
        limit: int = Query(100, ge=1, le=10000)
    ):
        """Get discovered hosts from database"""
        return await app_state['db'].get_hosts(alive_only=alive_only, limit=limit)

    # Get discovered ports
    @app.get("/ports", response_model=List[DiscoveredPort], tags=["Data"])
    async def get_ports(
        host_id: Optional[int] = Query(None),
        state: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=10000)
    ):
        """Get discovered ports from database"""
        return await app_state['db'].get_ports(host_id=host_id, state=state, limit=limit)

    # Get network statistics
    @app.get("/stats", response_model=NetworkStats, tags=["Statistics"])
    async def get_stats():
        """Get network statistics"""
        return await app_state['db'].get_stats()

    return app


# Background task functions
async def store_scan_results(target: str, hosts: List[HostInfo]):
    """Store scan results in database"""
    try:
        db = app_state['db']
        for host in hosts:
            await db.store_host(host)
    except Exception as e:
        logger.error(f"Failed to store scan results: {e}")


async def store_enumeration_results(domains: List[EnumeratedDomain]):
    """Store enumeration results in database"""
    try:
        db = app_state['db']
        for domain in domains:
            if domain.addresses:
                await db.store_domain(domain)
    except Exception as e:
        logger.error(f"Failed to store enumeration results: {e}")


async def run_full_enumeration(job_id: str):
    """Run full IPv9 network enumeration"""
    jobs = app_state['jobs']
    enumerator = app_state['enumerator']

    try:
        jobs.update_job(job_id, status="running", started_at=datetime.utcnow())

        # Enumerate common patterns
        patterns = [
            "86138NNNNNNNN",  # Mobile pattern
            "86139NNNNNNNN",
            "86186NNNNNNNN",
            "86187NNNNNNNN",
            "86188NNNNNNNN",
        ]

        all_results = []
        total = len(patterns)

        for i, pattern in enumerate(patterns):
            results = enumerator.brute_force_pattern(pattern, "chn", 10000)
            all_results.extend(results)

            progress = (i + 1) / total * 100
            jobs.update_job(job_id, progress=progress)

        jobs.update_job(
            job_id,
            status="completed",
            completed_at=datetime.utcnow(),
            progress=100.0,
            result={'total_found': len(all_results), 'domains': all_results}
        )

    except Exception as e:
        logger.error(f"Full enumeration failed: {e}")
        jobs.update_job(job_id, status="failed", error=str(e))


async def run_network_audit(job_id: str, request: AuditRequest):
    """Run full network audit"""
    jobs = app_state['jobs']

    try:
        jobs.update_job(job_id, status="running", started_at=datetime.utcnow())

        # TODO: Implement full audit logic
        # This would include:
        # 1. DNS infrastructure scan
        # 2. Web services scan
        # 3. Full port scan if requested
        # 4. Vulnerability assessment
        # 5. Continuous monitoring if requested

        await asyncio.sleep(5)  # Placeholder

        jobs.update_job(
            job_id,
            status="completed",
            completed_at=datetime.utcnow(),
            progress=100.0,
            result={'status': 'completed'}
        )

    except Exception as e:
        logger.error(f"Network audit failed: {e}")
        jobs.update_job(job_id, status="failed", error=str(e))


def main():
    """Run API server"""
    import uvicorn

    app = create_api_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
