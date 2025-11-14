# IPv9 Scanner - Installation & Quick Start Guide

## One-Command Installation

The IPv9 Scanner provides a unified installation script that handles everything:

```bash
./setup.sh
```

This will:
- ✅ Install system dependencies (nmap, masscan, dnsmasq, etc.)
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Configure DNS forwarding (optional)
- ✅ Create launcher scripts
- ✅ Set up directories and permissions

## Post-Installation

After installation completes, restart your shell to update PATH:

```bash
source ~/.bashrc
```

## Three Ways to Use IPv9 Scanner

### 1. Interactive TUI (Recommended) 🎯

Launch the comprehensive Text User Interface with real-time streaming logs:

```bash
ipv9scan
```

**Features:**
- 📊 Real-time log streaming
- 🔍 DNS resolution, ping, port scanning
- 🌐 Domain enumeration (pattern-based, phone numbers)
- 🔬 Full network audit (6-phase methodology)
- ⚡ Masscan integration (high-speed enumeration)
- 📈 Live statistics dashboard
- 📋 Discovered hosts, ports, and domains tables
- ⌨️ Keyboard shortcuts (q=quit, d=dark mode, s=stats, l=clear logs, h=help)

**Quick Start:**
1. Launch: `ipv9scan`
2. Enter target (e.g., `www.v9.chn` or `em777.chn`)
3. Click buttons or use keyboard shortcuts
4. Watch real-time logs stream in

### 2. REST API Server 🚀

Start the production-ready API server:

```bash
ipv9api
```

Server will start on `http://localhost:8000`

**Features:**
- 🔌 15+ REST endpoints
- 📚 Automatic OpenAPI docs at `/docs` and `/redoc`
- ⚙️ Background job processing
- 💾 SQLite database backend
- 🔄 Async I/O (1000+ req/s)
- 🌐 CORS support for web integration

**Quick API Test:**

```bash
# Check health
curl http://localhost:8000/health

# Resolve domain
curl -X POST http://localhost:8000/dns/resolve \
  -H "Content-Type: application/json" \
  -d '{"hostname": "www.v9.chn"}'

# Scan ports
curl -X POST http://localhost:8000/network/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "em777.chn", "ports": "80,443"}'
```

**Python Client:**

```python
from ipv9tool.api.client import IPv9APIClient

client = IPv9APIClient("http://localhost:8000")

# DNS resolution
result = client.resolve("www.v9.chn")
print(result.addresses)

# Port scan
scan = client.scan("em777.chn", ports="80,443,8080")
for host in scan.hosts:
    for port in host.ports:
        print(f"Port {port.port}: {port.state}")

# Get statistics
stats = client.get_stats()
print(f"Active hosts: {stats.active_hosts}")
```

### 3. CLI Tool 🖥️

Use the command-line interface for scripting:

```bash
# Resolve DNS
ipv9tool resolve www.v9.chn

# Ping host
ipv9tool ping em777.chn

# Scan ports
ipv9tool scan em777.chn --ports 80,443,8080

# Enumerate domains
ipv9tool enumerate --pattern "861381234NNNN" --max-results 100

# Cache statistics
ipv9tool cache-stats
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              IPv9 Scanner Platform                       │
├─────────────────────────────────────────────────────────┤
│  User Interfaces                                         │
│  ├── ipv9scan   - Interactive TUI (Textual)            │
│  ├── ipv9api    - REST API Server (FastAPI)            │
│  └── ipv9tool   - CLI Tool (Click)                     │
├─────────────────────────────────────────────────────────┤
│  Core Capabilities                                       │
│  ├── DNS Resolution (IPv9 .chn domains)                │
│  ├── Port Scanning (nmap/masscan)                      │
│  ├── Host Discovery (ICMP, TCP probes)                 │
│  ├── Domain Enumeration (pattern-based)                │
│  ├── Network Auditing (6-phase methodology)            │
│  ├── Masscan Integration (10M pps)                     │
│  ├── Continuous Monitoring (change detection)          │
│  └── Multi-format Export (JSON/CSV/HTML/MD)            │
├─────────────────────────────────────────────────────────┤
│  Backend Services                                        │
│  ├── SQLite Database (async)                           │
│  ├── Background Job System                             │
│  ├── DNS Cache (LRU)                                   │
│  └── Rate Limiting (token bucket)                      │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 🎯 TUI Scanner (ipv9scan)
- **Real-time Streaming Logs**: Watch operations as they happen
- **Tab-based Interface**: Scanner, Hosts, Ports, Domains
- **Live Statistics**: Network stats update automatically
- **Comprehensive Operations**: All features in one interface
- **Keyboard Shortcuts**: Quick access to common actions

### 🚀 REST API (ipv9api)
- **OpenAPI Documentation**: Interactive docs at `/docs`
- **Background Jobs**: Long operations run asynchronously
- **Database Tracking**: Persistent storage of all discoveries
- **Python Client**: Type-safe programmatic access
- **High Performance**: Async I/O for 1000+ req/s

### 🖥️ CLI Tool (ipv9tool)
- **Scriptable**: Perfect for automation
- **Simple Interface**: Clear command structure
- **Flexible Output**: Human-readable or JSON
- **Quick Operations**: Fast one-off queries

## Common Use Cases

### 1. Quick Domain Check

**TUI:**
```bash
ipv9scan
# Enter domain, click "Resolve DNS"
```

**API:**
```bash
curl -X POST http://localhost:8000/dns/resolve \
  -H "Content-Type: application/json" \
  -d '{"hostname": "www.v9.chn"}'
```

**CLI:**
```bash
ipv9tool resolve www.v9.chn
```

### 2. Port Scanning

**TUI:**
```bash
ipv9scan
# Enter target, click "Port Scan"
```

**API:**
```python
from ipv9tool.api.client import IPv9APIClient
client = IPv9APIClient("http://localhost:8000")
scan = client.scan("em777.chn", ports="1-1000")
```

**CLI:**
```bash
ipv9tool scan em777.chn --ports 1-1000
```

### 3. Full Network Enumeration

**TUI:**
```bash
ipv9scan
# Click "Full Audit" or "Masscan"
```

**API:**
```python
from ipv9tool.api.client import IPv9APIClient
client = IPv9APIClient("http://localhost:8000")

# Start comprehensive audit
job = client.start_audit(
    scan_dns=True,
    scan_web=True,
    deep_scan=True
)

# Wait for completion
result = client.wait_for_job(job.job_id, timeout=3600)
```

**CLI:**
```bash
ipv9tool enumerate --pattern "861381234NNNN" --max-results 10000
```

### 4. Continuous Monitoring

**TUI:**
```bash
ipv9scan
# Click "Monitor" button
```

**API:**
```python
from ipv9tool.api.client import IPv9APIClient
import time

client = IPv9APIClient("http://localhost:8000")

# Start continuous monitoring
job = client.start_audit(
    scan_dns=True,
    scan_web=True,
    continuous=True
)

# Monitor changes
while True:
    stats = client.get_stats()
    print(f"Active hosts: {stats.active_hosts}")
    print(f"Open ports: {stats.total_open_ports}")
    time.sleep(300)  # Check every 5 minutes
```

## Directory Structure

After installation:

```
~/.ipv9tool/
├── scans/          # Scan results
├── reports/        # Generated reports
└── logs/           # Application logs

/etc/ipv9tool/
└── ipv9tool.yml    # Configuration file

/var/log/ipv9tool/  # System logs
/var/lib/ipv9tool/  # Database and cache
```

## Configuration

Edit `/etc/ipv9tool/ipv9tool.yml`:

```yaml
dns:
  servers:
    - 202.170.218.93  # IPv9 DNS Primary
    - 61.244.5.162    # IPv9 DNS Secondary
  cache_ttl: 3600
  timeout: 5

scanning:
  default_ports: "21,22,23,25,80,443,3389,8080,8443"
  rate_limit: 100
  max_threads: 10

audit:
  enable_masscan: true
  deep_scan: false
  export_format: ["json", "html"]
```

## System Requirements

- **OS**: Ubuntu 20.04+, Debian 10+, or similar
- **Python**: 3.7+
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 1GB for installation, more for scan results
- **Network**: Outbound access to IPv9 DNS servers

## Dependencies

**System:**
- nmap (port scanning)
- masscan (high-speed enumeration)
- dnsmasq (DNS forwarding)
- dnsutils (DNS tools)
- sqlite3 (database)

**Python:**
- fastapi (API server)
- textual (TUI framework)
- rich (terminal formatting)
- dnspython (DNS resolution)
- pyyaml (configuration)
- aiosqlite (async database)

## Troubleshooting

### TUI doesn't start

```bash
# Check if installed
which ipv9scan

# Reinstall
cd /home/user/IPVNINER
./setup.sh
```

### API server won't start

```bash
# Check port availability
sudo lsof -i :8000

# Start manually
cd /home/user/IPVNINER
source venv/bin/activate
uvicorn ipv9tool.api.server:create_api_app --host 0.0.0.0 --port 8000
```

### DNS resolution fails

```bash
# Test IPv9 DNS servers
dig @202.170.218.93 www.v9.chn
dig @61.244.5.162 www.v9.chn

# Check DNS configuration
cat /etc/ipv9tool/ipv9tool.yml
```

### Permission errors

```bash
# Fix directory permissions
sudo chown -R $USER:$USER ~/.ipv9tool
sudo chmod 755 /var/log/ipv9tool
sudo chmod 755 /var/lib/ipv9tool
```

## Examples

See the `examples/` directory for complete usage examples:

- **basic_api_usage.py** - DNS, ping, scan basics
- **full_enumeration.py** - Pattern enumeration
- **network_audit.py** - Comprehensive audit
- **continuous_monitoring.py** - Real-time monitoring
- **masscan_full_scan.py** - High-speed scanning

## Documentation

- **README.md** - Project overview
- **INSTALL.md** - This guide
- **docs/GUIDE.md** - Comprehensive user guide
- **docs/API.md** - API reference (1000+ lines)
- **docs/API_QUICKSTART.md** - API quick start

## Next Steps

1. ✅ Run unified installer: `./setup.sh`
2. ✅ Restart shell: `source ~/.bashrc`
3. 🎯 Launch TUI: `ipv9scan`
4. 🚀 Or start API: `ipv9api`
5. 📚 Read documentation: `docs/GUIDE.md`
6. 🧪 Try examples: `python examples/basic_api_usage.py`

## Support

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **API Docs**: http://localhost:8000/docs (when API running)
- **Issues**: https://github.com/SWORDIntel/IPVNINER/issues

---

**Happy scanning! 🔍**
