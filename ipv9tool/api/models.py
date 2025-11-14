"""
API Data Models

Pydantic models for API request/response validation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress


# Request Models
class ResolveRequest(BaseModel):
    """DNS resolution request"""
    hostname: str = Field(..., description="Hostname to resolve")
    record_type: str = Field("A", description="DNS record type")
    use_cache: bool = Field(True, description="Use DNS cache")


class PingRequest(BaseModel):
    """Ping request"""
    target: str = Field(..., description="Target to ping")
    count: int = Field(4, ge=1, le=100, description="Number of packets")
    timeout: int = Field(5, ge=1, le=60, description="Timeout in seconds")


class ScanRequest(BaseModel):
    """Port scan request"""
    target: str = Field(..., description="Target to scan")
    ports: str = Field("1-1000", description="Port range or list")
    scan_type: str = Field("syn", description="Scan type (syn, tcp, udp)")
    service_detection: bool = Field(True, description="Enable service detection")
    os_detection: bool = Field(False, description="Enable OS detection")


class EnumerateRequest(BaseModel):
    """Domain enumeration request"""
    pattern: str = Field(..., description="Pattern to enumerate (N = any digit)")
    tld: str = Field("chn", description="Top-level domain")
    max_combinations: int = Field(1000, ge=1, le=100000, description="Max combinations")
    parallel: bool = Field(True, description="Use parallel enumeration")


class MasscanRequest(BaseModel):
    """Masscan full network scan request"""
    targets: Optional[List[str]] = Field(None, description="Target IP ranges")
    ports: str = Field("80,443,8080,22,21,25,53", description="Ports to scan")
    rate: int = Field(1000, ge=1, le=100000, description="Packets per second")
    exclude: Optional[List[str]] = Field(None, description="IPs to exclude")


class AuditRequest(BaseModel):
    """Full network audit request"""
    scan_dns: bool = Field(True, description="Scan DNS infrastructure")
    scan_web: bool = Field(True, description="Scan web services")
    scan_all_ports: bool = Field(False, description="Scan all 65535 ports")
    deep_scan: bool = Field(False, description="Enable deep inspection")
    continuous: bool = Field(False, description="Continuous monitoring mode")


# Response Models
class ResolveResponse(BaseModel):
    """DNS resolution response"""
    hostname: str
    record_type: str
    addresses: List[str]
    from_cache: bool
    ttl: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PingResponse(BaseModel):
    """Ping response"""
    target: str
    reachable: bool
    packets_sent: int
    packets_received: Optional[int] = None
    packet_loss: Optional[float] = None
    rtt_min: Optional[float] = None
    rtt_avg: Optional[float] = None
    rtt_max: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PortInfo(BaseModel):
    """Port information"""
    port: int
    protocol: str
    state: str
    service: Optional[str] = None
    version: Optional[str] = None
    product: Optional[str] = None


class HostInfo(BaseModel):
    """Host information"""
    address: str
    hostname: Optional[str] = None
    ports: List[PortInfo] = []
    os: Optional[str] = None
    os_accuracy: Optional[int] = None


class ScanResponse(BaseModel):
    """Port scan response"""
    target: str
    scan_type: str
    ports_scanned: str
    hosts: List[HostInfo]
    scan_duration: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EnumeratedDomain(BaseModel):
    """Enumerated domain information"""
    hostname: str
    addresses: List[str]
    responsive: bool = False
    http_status: Optional[int] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)


class EnumerateResponse(BaseModel):
    """Domain enumeration response"""
    pattern: str
    total_checked: int
    total_found: int
    domains: List[EnumeratedDomain]
    duration: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NetworkStats(BaseModel):
    """Network statistics"""
    total_domains: int
    total_ips: int
    total_ports: int
    active_hosts: int
    responsive_web: int
    last_scan: Optional[datetime] = None


class AuditResult(BaseModel):
    """Network audit result"""
    audit_id: str
    status: str
    progress: float
    stats: NetworkStats
    started_at: datetime
    completed_at: Optional[datetime] = None
    findings: List[Dict[str, Any]] = []


class JobStatus(BaseModel):
    """Background job status"""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


# Database Models
class DiscoveredHost(BaseModel):
    """Discovered host record"""
    id: Optional[int] = None
    ip_address: str
    hostname: Optional[str] = None
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    alive: bool = True
    os: Optional[str] = None
    tags: List[str] = []


class DiscoveredPort(BaseModel):
    """Discovered port record"""
    id: Optional[int] = None
    host_id: int
    port: int
    protocol: str
    state: str
    service: Optional[str] = None
    version: Optional[str] = None
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)


class ScanHistory(BaseModel):
    """Scan history record"""
    id: Optional[int] = None
    scan_type: str
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    hosts_found: int = 0
    ports_found: int = 0
    result_data: Optional[Dict[str, Any]] = None


# API Health and Info
class HealthResponse(BaseModel):
    """API health check response"""
    status: str
    version: str
    uptime: float
    dns_servers_reachable: bool
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIInfo(BaseModel):
    """API information"""
    name: str = "IPv9 Scanner API"
    version: str = "1.0.0"
    description: str = "Robust API for IPv9 network exploration and auditing"
    endpoints: List[str] = []
    features: List[str] = []
