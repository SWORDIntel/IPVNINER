# IPv9 Scanner API Documentation

## Overview

The IPv9 Scanner API provides a robust REST interface for programmatic access to all IPv9 exploration and auditing capabilities. Built with FastAPI, it offers high performance, automatic API documentation, and comprehensive data persistence.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Python Client](#python-client)
6. [Background Jobs](#background-jobs)
7. [Database Integration](#database-integration)
8. [Examples](#examples)

## Quick Start

### Starting the API Server

```bash
# Start with uvicorn
uvicorn ipv9tool.api.server:create_api_app --host 0.0.0.0 --port 8000

# Or using the module
python -m ipv9tool.api.server
```

### Access API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

## Authentication

Currently, the API uses optional API key authentication via Bearer tokens.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/dns/resolve
```

## API Endpoints

### System Endpoints

#### GET /
Get API information and available endpoints.

**Response:**
```json
{
  "name": "IPv9 Scanner API",
  "version": "1.0.0",
  "description": "Robust API for IPv9 network exploration and auditing",
  "endpoints": ["/health", "/dns/resolve", ...],
  "features": ["DNS Resolution with Caching", ...]
}
```

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600.5,
  "dns_servers_reachable": true,
  "database_connected": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### DNS Endpoints

#### POST /dns/resolve
Resolve IPv9 hostname to IP addresses.

**Request:**
```json
{
  "hostname": "www.v9.chn",
  "record_type": "A",
  "use_cache": true
}
```

**Response:**
```json
{
  "hostname": "www.v9.chn",
  "record_type": "A",
  "addresses": ["203.0.113.10"],
  "from_cache": false,
  "ttl": 300,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Network Endpoints

#### POST /network/ping
Ping an IPv9 host.

**Request:**
```json
{
  "target": "em777.chn",
  "count": 4,
  "timeout": 5
}
```

**Response:**
```json
{
  "target": "203.0.113.10",
  "reachable": true,
  "packets_sent": 4,
  "packets_received": 4,
  "packet_loss": 0.0,
  "rtt_min": 10.5,
  "rtt_avg": 12.3,
  "rtt_max": 15.2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /network/scan
Scan host ports.

**Request:**
```json
{
  "target": "www.v9.chn",
  "ports": "80,443,8080",
  "scan_type": "syn",
  "service_detection": true,
  "os_detection": false
}
```

**Response:**
```json
{
  "target": "203.0.113.10",
  "scan_type": "syn",
  "ports_scanned": "80,443,8080",
  "hosts": [
    {
      "address": "203.0.113.10",
      "hostname": "www.v9.chn",
      "ports": [
        {
          "port": 80,
          "protocol": "tcp",
          "state": "open",
          "service": "http",
          "version": "Apache/2.4.41"
        }
      ],
      "os": "Linux 5.4",
      "os_accuracy": 95
    }
  ],
  "scan_duration": 2.5,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Enumeration Endpoints

#### POST /enumerate/pattern
Enumerate domains by pattern.

**Request:**
```json
{
  "pattern": "861381234NNNN",
  "tld": "chn",
  "max_combinations": 1000,
  "parallel": true
}
```

**Response:**
```json
{
  "pattern": "861381234NNNN",
  "total_checked": 1000,
  "total_found": 45,
  "domains": [
    {
      "hostname": "8613812340001.chn",
      "addresses": ["203.0.113.20"],
      "responsive": true,
      "http_status": 200,
      "discovered_at": "2024-01-01T12:00:00Z"
    }
  ],
  "duration": 15.3,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /enumerate/full
Start full network enumeration (background job).

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Audit Endpoints

#### POST /audit/start
Start comprehensive network audit (background job).

**Request:**
```json
{
  "scan_dns": true,
  "scan_web": true,
  "scan_all_ports": false,
  "deep_scan": false,
  "continuous": false
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Job Management Endpoints

#### GET /jobs/{job_id}
Get background job status.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100.0,
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:00:05Z",
  "completed_at": "2024-01-01T12:15:30Z",
  "result": {
    "total_found": 1234,
    "domains": [...]
  }
}
```

#### GET /jobs
List all background jobs.

**Query Parameters:**
- `status` (optional): Filter by status (pending, running, completed, failed)
- `limit` (default: 100): Maximum number of jobs to return

**Response:**
```json
[
  {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100.0,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Data Endpoints

#### GET /hosts
Get discovered hosts from database.

**Query Parameters:**
- `alive_only` (default: true): Only return alive hosts
- `limit` (default: 100): Maximum number of hosts

**Response:**
```json
[
  {
    "id": 1,
    "ip_address": "203.0.113.10",
    "hostname": "www.v9.chn",
    "first_seen": "2024-01-01T10:00:00Z",
    "last_seen": "2024-01-01T12:00:00Z",
    "alive": true,
    "os": "Linux 5.4",
    "tags": ["web", "ipv9"]
  }
]
```

#### GET /ports
Get discovered ports from database.

**Query Parameters:**
- `host_id` (optional): Filter by host ID
- `state` (optional): Filter by state (open, closed, filtered)
- `limit` (default: 100): Maximum number of ports

**Response:**
```json
[
  {
    "id": 1,
    "host_id": 1,
    "port": 80,
    "protocol": "tcp",
    "state": "open",
    "service": "http",
    "version": "Apache/2.4.41",
    "first_seen": "2024-01-01T10:00:00Z",
    "last_seen": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /stats
Get network statistics.

**Response:**
```json
{
  "total_domains": 5432,
  "total_ips": 3210,
  "total_ports": 12345,
  "active_hosts": 2987,
  "responsive_web": 1456,
  "last_scan": "2024-01-01T12:00:00Z"
}
```

## Data Models

### Request Models

See complete Pydantic models in `ipv9tool/api/models.py`:

- `ResolveRequest`
- `PingRequest`
- `ScanRequest`
- `EnumerateRequest`
- `MasscanRequest`
- `AuditRequest`

### Response Models

- `ResolveResponse`
- `PingResponse`
- `ScanResponse`
- `EnumerateResponse`
- `JobStatus`
- `HealthResponse`
- `NetworkStats`

## Python Client

### Installation

The Python client is included in the main package:

```python
from ipv9tool.api.client import IPv9APIClient
```

### Basic Usage

```python
from ipv9tool.api.client import IPv9APIClient

# Initialize client
client = IPv9APIClient("http://localhost:8000")

# DNS resolution
result = client.resolve("www.v9.chn")
print(result.addresses)  # ['203.0.113.10']

# Ping
ping_result = client.ping("em777.chn", count=4)
print(f"Reachable: {ping_result.reachable}")

# Port scan
scan_result = client.scan("www.v9.chn", ports="80,443")
for host in scan_result.hosts:
    for port in host.ports:
        print(f"Port {port.port}: {port.state}")

# Domain enumeration
enum_result = client.enumerate_pattern("861381234NNNN", max_combinations=100)
print(f"Found {enum_result.total_found} domains")

# Full audit (background job)
job = client.start_audit(scan_dns=True, scan_web=True)
print(f"Audit started: {job.job_id}")

# Wait for job completion
final_job = client.wait_for_job(job.job_id, timeout=3600)
print(f"Audit completed: {final_job.status}")

# Get network statistics
stats = client.get_stats()
print(f"Total domains: {stats.total_domains}")
```

### Convenience Functions

```python
from ipv9tool.api.client import quick_resolve, quick_scan, quick_enumerate

# Quick operations
addresses = quick_resolve("www.v9.chn")
scan_result = quick_scan("em777.chn", ports="80,443")
domains = quick_enumerate("861381234NNNN", max_results=100)
```

## Background Jobs

Long-running operations (full enumeration, network audits) run as background jobs.

### Job Lifecycle

1. **Create**: POST to `/enumerate/full` or `/audit/start`
2. **Monitor**: GET `/jobs/{job_id}` to check progress
3. **Complete**: Job status becomes "completed" or "failed"
4. **Retrieve**: Get results from `job.result`

### Job States

- `pending`: Job created, not yet started
- `running`: Job is currently executing
- `completed`: Job finished successfully
- `failed`: Job encountered an error

### Example: Polling for Completion

```python
import time

# Start job
job = client.enumerate_full()
job_id = job.job_id

# Poll until complete
while True:
    status = client.get_job(job_id)

    print(f"Status: {status.status}, Progress: {status.progress}%")

    if status.status in ['completed', 'failed']:
        break

    time.sleep(5)  # Poll every 5 seconds

# Get results
if status.status == 'completed':
    print(f"Results: {status.result}")
```

## Database Integration

All discoveries are automatically stored in a SQLite database (`~/.ipv9tool/ipv9.db`).

### Database Schema

**hosts table:**
- id, ip_address, hostname, first_seen, last_seen, alive, os, tags

**ports table:**
- id, host_id, port, protocol, state, service, version, first_seen, last_seen

**domains table:**
- id, hostname, ip_addresses, first_seen, last_seen, responsive, http_status

**scans table:**
- id, scan_type, target, started_at, completed_at, status, result_data

### Querying the Database

```python
# Get all discovered hosts
hosts = client.get_hosts(alive_only=True, limit=100)

# Get ports for specific host
ports = client.get_ports(host_id=1, state="open")

# Get overall statistics
stats = client.get_stats()
```

## Examples

### Example 1: Complete IPv9 Site Audit

```python
from ipv9tool.api.client import IPv9APIClient

client = IPv9APIClient("http://localhost:8000")

# Resolve domain
site = "www.v9.chn"
resolution = client.resolve(site)
print(f"Resolved {site} to {resolution.addresses}")

# Ping
ping = client.ping(site, count=4)
print(f"Host alive: {ping.reachable}, RTT avg: {ping.rtt_avg}ms")

# Scan common ports
scan = client.scan(site, ports="21,22,23,25,80,443,8080")
for host in scan.hosts:
    print(f"\nHost: {host.address}")
    for port in host.ports:
        if port.state == "open":
            print(f"  Port {port.port}: {port.service} {port.version or ''}")
```

### Example 2: Full Network Enumeration

```python
client = IPv9APIClient("http://localhost:8000")

# Start full enumeration
job = client.enumerate_full()
print(f"Enumeration started: {job.job_id}")

# Wait for completion
result = client.wait_for_job(job.job_id, poll_interval=10, timeout=7200)

if result.status == 'completed':
    domains = result.result['domains']
    print(f"Found {len(domains)} domains")

    # Analyze discoveries
    responsive = [d for d in domains if d.get('responsive')]
    print(f"{len(responsive)} domains are responsive")
```

### Example 3: Continuous Monitoring

```python
import time

client = IPv9APIClient("http://localhost:8000")

# Start continuous audit
job = client.start_audit(
    scan_dns=True,
    scan_web=True,
    scan_all_ports=False,
    continuous=True
)

print(f"Continuous monitoring started: {job.job_id}")

# Monitor changes
while True:
    status = client.get_job(job.job_id)

    if status.status == 'running':
        stats = client.get_stats()
        print(f"Active hosts: {stats.active_hosts}, Total domains: {stats.total_domains}")

    time.sleep(300)  # Check every 5 minutes
```

### Example 4: Batch Scanning

```python
client = IPv9APIClient("http://localhost:8000")

targets = [
    "www.v9.chn",
    "em777.chn",
    "www.hqq.chn"
]

results = []

for target in targets:
    print(f"Scanning {target}...")

    # Resolve
    resolution = client.resolve(target)

    # Scan if resolved
    if resolution.addresses:
        scan = client.scan(target, ports="80,443,8080")
        results.append({
            'target': target,
            'addresses': resolution.addresses,
            'scan': scan
        })

# Export results
import json
with open('scan_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

### Example 5: Integration with External Tools

```python
import requests
from ipv9tool.api.client import IPv9APIClient

client = IPv9APIClient("http://localhost:8000")

# Get all discovered web services
stats = client.get_stats()
hosts = client.get_hosts(alive_only=True, limit=1000)

web_services = []

for host in hosts:
    # Get HTTP ports for this host
    ports = client.get_ports(host_id=host['id'])

    for port in ports:
        if port['service'] in ['http', 'https']:
            web_services.append({
                'host': host['ip_address'],
                'port': port['port'],
                'service': port['service']
            })

# Export to CSV for external analysis
import csv
with open('web_services.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['host', 'port', 'service'])
    writer.writeheader()
    writer.writerows(web_services)
```

## Rate Limiting and Best Practices

1. **Respect Rate Limits**: Use configured rate limits (default 100 pps)
2. **Use Background Jobs**: For long operations, use background jobs
3. **Cache DNS Results**: Enable DNS caching to reduce queries
4. **Monitor Progress**: Poll job status for long-running tasks
5. **Handle Errors**: Implement retry logic with exponential backoff
6. **Clean Up**: Periodically clean old job records

## Error Handling

```python
from ipv9tool.api.client import IPv9APIClient
import requests

client = IPv9APIClient("http://localhost:8000")

try:
    result = client.resolve("invalid.chn")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API server")
except requests.exceptions.Timeout:
    print("Request timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

- **Database**: SQLite is suitable for moderate scale (< 1M records). For larger deployments, use PostgreSQL
- **Caching**: DNS cache significantly reduces query load
- **Parallel Scanning**: Use masscan for large-scale scans
- **Background Jobs**: Offload long operations to background workers
- **Rate Limiting**: Adjust rate limits based on network capacity

## Security Considerations

1. **Authentication**: Use API keys for production deployments
2. **HTTPS**: Deploy behind reverse proxy with TLS
3. **Rate Limiting**: Prevent abuse with rate limits
4. **Input Validation**: All inputs are validated via Pydantic
5. **Sandboxing**: Scanning operations run in sandboxed environment
6. **Audit Logging**: All operations are logged

## Support and Resources

- **API Documentation**: http://localhost:8000/docs
- **Source Code**: https://github.com/SWORDIntel/IPVNINER
- **Issues**: https://github.com/SWORDIntel/IPVNINER/issues
