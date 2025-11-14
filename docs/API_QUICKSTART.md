## IPv9 Scanner - API Quick Start

## Overview

The IPv9 Scanner now includes a production-ready REST API with comprehensive auditing and enumeration capabilities.

### Key Features

- **FastAPI-based REST API** with automatic OpenAPI documentation
- **SQLite/PostgreSQL database** for persistent storage
- **Background job processing** for long-running scans
- **Masscan integration** for high-speed full network enumeration
- **Comprehensive auditing** with 6-phase methodology
- **Continuous monitoring** for real-time change detection
- **Multi-format export** (JSON, CSV, XML, HTML, Markdown)
- **Python client library** for easy integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start API Server

```bash
# Using the start script
./scripts/start-api-server.sh

# Or directly with uvicorn
uvicorn ipv9tool.api.server:create_api_app --host 0.0.0.0 --port 8000
```

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Basic Usage

```python
from ipv9tool.api.client import IPv9APIClient

# Initialize client
client = IPv9APIClient("http://localhost:8000")

# DNS resolution
result = client.resolve("www.v9.chn")
print(result.addresses)

# Port scan
scan = client.scan("www.v9.chn", ports="80,443")

# Start full network audit
job = client.start_audit(scan_dns=True, scan_web=True)
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              IPv9 Scanner API                        │
├─────────────────────────────────────────────────────┤
│  FastAPI Server (Port 8000)                         │
│  ├── REST Endpoints                                 │
│  ├── Background Jobs                                │
│  ├── WebSocket Support                              │
│  └── Auto-generated Docs                            │
├─────────────────────────────────────────────────────┤
│  Core Engines                                       │
│  ├── AuditEngine (6-phase auditing)                │
│  ├── MasscanEnumerator (high-speed scanning)       │
│  ├── ContinuousMonitor (change detection)          │
│  └── DataExporter (multi-format export)            │
├─────────────────────────────────────────────────────┤
│  Database Layer                                     │
│  ├── SQLite (default)                               │
│  ├── PostgreSQL (optional)                          │
│  └── Async I/O (aiosqlite)                         │
├─────────────────────────────────────────────────────┤
│  Scanner Integrations                               │
│  ├── nmap (service detection)                       │
│  ├── masscan (high-speed)                           │
│  └── Custom IPv9 resolver                           │
└─────────────────────────────────────────────────────┘
```

## API Endpoints

### System
- `GET /` - API information
- `GET /health` - Health check

### DNS
- `POST /dns/resolve` - Resolve hostname

### Network
- `POST /network/ping` - Ping host
- `POST /network/scan` - Scan ports

### Enumeration
- `POST /enumerate/pattern` - Pattern-based enumeration
- `POST /enumerate/full` - Full network enumeration (background)

### Audit
- `POST /audit/start` - Start comprehensive audit (background)

### Jobs
- `GET /jobs` - List jobs
- `GET /jobs/{job_id}` - Get job status

### Data
- `GET /hosts` - Get discovered hosts
- `GET /ports` - Get discovered ports
- `GET /stats` - Get network statistics

## Examples

See `examples/` directory for complete examples:

- `basic_api_usage.py` - Basic operations
- `full_enumeration.py` - Domain enumeration
- `network_audit.py` - Comprehensive audit
- `continuous_monitoring.py` - Continuous monitoring
- `masscan_full_scan.py` - High-speed masscan

## Audit Engine (6-Phase Methodology)

1. **DNS Infrastructure Scan** (20%)
   - Test IPv9 DNS servers
   - Verify DNS resolution
   - Detect DNS issues

2. **Domain Enumeration** (40%)
   - Pattern-based discovery
   - Phone number enumeration
   - Mobile prefix scanning

3. **Host Discovery** (60%)
   - ICMP ping sweeps
   - TCP probing
   - HTTP service detection

4. **Port Scanning** (80%)
   - Common ports (fast)
   - All ports (comprehensive)
   - Service version detection

5. **Deep Inspection** (90%)
   - HTTP/HTTPS probing
   - Banner grabbing
   - Service fingerprinting

6. **Analysis & Reporting** (100%)
   - Statistical analysis
   - Security scoring
   - Recommendations

## Masscan Integration

High-speed full network enumeration:

```python
from ipv9tool.audit import MasscanEnumerator

enumerator = MasscanEnumerator(rate=10000)  # 10K pps

# Create enumeration plan
plan = enumerator.create_enumeration_plan(
    total_budget_hours=24,
    ports="80,443,8080"
)

# Enumerate IPv9 space
results = enumerator.enumerate_ipv9_space(
    sample_rate=0.10,  # 10% sample
    ports="80,443"
)
```

## Database Schema

```sql
-- Hosts table
CREATE TABLE hosts (
    id INTEGER PRIMARY KEY,
    ip_address TEXT UNIQUE,
    hostname TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    alive BOOLEAN,
    os TEXT,
    tags TEXT
);

-- Ports table
CREATE TABLE ports (
    id INTEGER PRIMARY KEY,
    host_id INTEGER,
    port INTEGER,
    protocol TEXT,
    state TEXT,
    service TEXT,
    version TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id)
);

-- Domains table
CREATE TABLE domains (
    id INTEGER PRIMARY KEY,
    hostname TEXT UNIQUE,
    ip_addresses TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    responsive BOOLEAN,
    http_status INTEGER
);

-- Scans table
CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    scan_type TEXT,
    target TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT,
    result_data TEXT
);
```

## Data Export

Export to multiple formats:

```python
from ipv9tool.export import DataExporter

exporter = DataExporter()

# Export to JSON
exporter.to_json(data, 'results.json')

# Export to CSV
exporter.to_csv(hosts, 'hosts.csv')

# Export to HTML
exporter.to_html(audit_results, 'report.html')

# Export to Markdown
exporter.to_markdown(audit_results, 'report.md')

# Batch export
exporter.export_audit_results(
    audit_results,
    output_dir='./reports',
    formats=['json', 'csv', 'html', 'markdown']
)
```

## Continuous Monitoring

Monitor network for changes:

```python
client = IPv9APIClient("http://localhost:8000")

# Start continuous monitoring
job = client.start_audit(
    scan_dns=True,
    scan_web=True,
    continuous=True  # Enable continuous mode
)

# Monitor changes
while True:
    stats = client.get_stats()
    print(f"Active hosts: {stats.active_hosts}")
    time.sleep(300)  # Check every 5 minutes
```

## Performance

- **Masscan**: Up to 10M packets/second (theoretical)
- **API Throughput**: 1000+ req/s (FastAPI + async)
- **Database**: Handles millions of records (PostgreSQL recommended for scale)
- **Background Jobs**: Async processing for long operations

## Security

- Optional API key authentication
- Rate limiting (configurable)
- Input validation (Pydantic)
- SQL injection prevention (parameterized queries)
- Sandboxed scanning operations
- Comprehensive audit logging

## Production Deployment

```bash
# With Gunicorn + Uvicorn workers
gunicorn ipv9tool.api.server:create_api_app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

# With systemd service
sudo systemctl enable ipv9-api
sudo systemctl start ipv9-api

# Behind nginx reverse proxy
# See docs/DEPLOYMENT.md for configuration
```

## Documentation

- **API Reference**: [docs/API.md](API.md)
- **Usage Guide**: [docs/GUIDE.md](GUIDE.md)
- **Examples**: `examples/` directory
- **Interactive Docs**: http://localhost:8000/docs

## Troubleshooting

### API won't start

```bash
# Check dependencies
pip install -r requirements.txt

# Check port availability
lsof -i :8000

# Check logs
tail -f /var/log/ipv9tool.log
```

### Database errors

```bash
# Reset database
rm ~/.ipv9tool/ipv9.db

# Check permissions
chmod 644 ~/.ipv9tool/ipv9.db
```

### Masscan not found

```bash
# Install masscan
sudo apt-get install masscan

# Or build from source
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
sudo make install
```

## Next Steps

1. Start the API server: `./scripts/start-api-server.sh`
2. Run basic example: `python examples/basic_api_usage.py`
3. Try full enumeration: `python examples/full_enumeration.py`
4. Run comprehensive audit: `python examples/network_audit.py`
5. Read full API docs: [docs/API.md](API.md)
