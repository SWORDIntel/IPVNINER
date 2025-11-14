# IPv9 Scanner

**Comprehensive Network Intelligence Platform for China's Decimal Network**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

---

## 🚀 Quick Start

**One-command installation:**

```bash
./setup.sh
```

**Three ways to use:**

```bash
ipv9scan   # 🎯 Interactive TUI with real-time logs
ipv9api    # 🚀 REST API server
ipv9tool   # 🖥️ CLI tool for scripting
```

That's it! See [INSTALL.md](INSTALL.md) for detailed installation and usage guide.

---

## What is IPv9?

IPv9 is China's experimental "decimal network" that uses:
- **Numeric domain names** based on phone numbers (e.g., `8613812345678.chn`)
- **Special DNS servers** (202.170.218.93 and 61.244.5.162) that intercept `.chn` queries
- **Standard IP routing** - domains resolve to normal IPv4/IPv6 addresses
- **DNS overlay architecture** - no new protocol stack required

**Example IPv9 sites:**
- `www.v9.chn`
- `em777.chn`
- `www.hqq.chn`

IPv9 Scanner provides comprehensive tools to explore, enumerate, and audit this network infrastructure.

---

## 🎯 Features

### Interactive TUI (ipv9scan)

Real-time Text User Interface with streaming logs:

```
┌─────────────────────────────────────────────────────────────┐
│  IPv9 Scanner                                      [q]Quit  │
├─────────────────────────────────────────────────────────────┤
│  Scanner │ Hosts │ Ports │ Domains                          │
├─────────────────────────────────────────────────────────────┤
│  Target: www.v9.chn                                         │
│  [Resolve DNS] [Ping] [Port Scan] [Enumerate]              │
│  [Full Audit] [Masscan] [Monitor] [Stop]                   │
├─────────────────────────────────────────────────────────────┤
│  Logs (streaming):                                          │
│  [13:45:12] [INFO] Resolving www.v9.chn...                 │
│  [13:45:12] [SUCCESS] Resolved to: 1.2.3.4                 │
│  [13:45:13] [INFO] Starting port scan...                   │
│  [13:45:15] [SUCCESS] Found 3 open ports                   │
├─────────────────────────────────────────────────────────────┤
│  Statistics: 15 domains | 42 hosts | 128 ports             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- ✅ Real-time log streaming
- ✅ DNS resolution, ping, port scanning
- ✅ Domain enumeration (pattern-based, phone numbers)
- ✅ Full network audit (6-phase methodology)
- ✅ Masscan integration (high-speed enumeration)
- ✅ Live statistics dashboard
- ✅ Discovered hosts, ports, domains tables
- ✅ Keyboard shortcuts (q=quit, d=dark mode, s=stats, l=clear logs, h=help)

### REST API Server (ipv9api)

Production-ready FastAPI server with OpenAPI documentation:

```bash
# Start server
ipv9api

# Access documentation
open http://localhost:8000/docs
```

**Features:**
- 🔌 15+ REST endpoints
- 📚 Automatic OpenAPI/Swagger docs
- ⚙️ Background job processing
- 💾 SQLite database backend
- 🔄 Async I/O (1000+ req/s)
- 🌐 CORS support

**Quick API Examples:**

```python
from ipv9tool.api.client import IPv9APIClient

client = IPv9APIClient("http://localhost:8000")

# DNS resolution
result = client.resolve("www.v9.chn")
print(result.addresses)  # ['1.2.3.4']

# Port scan
scan = client.scan("em777.chn", ports="80,443")
for host in scan.hosts:
    for port in host.ports:
        print(f"{port.port}: {port.state}")

# Full network audit (background job)
job = client.start_audit(scan_dns=True, scan_web=True)
result = client.wait_for_job(job.job_id, timeout=3600)

# Export results
from ipv9tool.export import DataExporter
exporter = DataExporter()
exporter.export_audit_results(
    result.result,
    output_dir='./reports',
    formats=['json', 'html', 'csv']
)
```

### CLI Tool (ipv9tool)

Command-line interface for scripting and automation:

```bash
# DNS resolution
ipv9tool resolve www.v9.chn

# Ping test
ipv9tool ping em777.chn

# Port scanning
ipv9tool scan em777.chn --ports 80,443,8080

# Domain enumeration
ipv9tool enumerate --pattern "861381234NNNN" --max-results 100

# Cache statistics
ipv9tool cache-stats
```

---

## 🏗️ Architecture

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

---

## 🎓 Core Capabilities

### 1. DNS Resolution
- Query IPv9 DNS servers for `.chn` domains
- Multi-server verification (detect spoofing)
- LRU caching with configurable TTL
- Support for numeric hostnames (phone numbers)

### 2. Host Discovery
- **ICMP Ping**: Traditional ping probes
- **TCP Ping**: Connection-based detection
- **HTTP/HTTPS Probing**: Web service detection
- **Parallel Discovery**: Multi-threaded scanning

### 3. Port Scanning
- **Nmap Integration**: Service detection, OS fingerprinting
- **Masscan Support**: High-speed scanning (up to 10M packets/second)
- **Customizable Ranges**: Specific ports or full range (1-65535)
- **Service Identification**: Banner grabbing, version detection

### 4. Domain Enumeration
- **Pattern-based**: Brute force with wildcards (e.g., `861381234NNNN`)
- **Phone Number Ranges**: Chinese mobile prefixes (130-199)
- **Wordlist Discovery**: Custom domain lists
- **Parallel Enumeration**: 10 concurrent threads (configurable)

### 5. Network Auditing
Comprehensive 6-phase methodology:
1. **DNS Infrastructure** (20%) - Test IPv9 DNS servers, verify resolution
2. **Domain Enumeration** (40%) - Pattern-based, phone number scanning
3. **Host Discovery** (60%) - ICMP ping, TCP probing, HTTP detection
4. **Port Scanning** (80%) - Common ports (fast) or all ports (comprehensive)
5. **Deep Inspection** (90%) - HTTP/HTTPS probing, service fingerprinting
6. **Analysis & Reporting** (100%) - Statistics, security scoring, recommendations

### 6. Masscan Integration
- **High-speed Enumeration**: Full IPv9 space scanning
- **Scan Planning**: Time/coverage calculations
- **Sample-based Scanning**: Configurable sample rates
- **IPv9 Address Blocks**: Covers 40+ Chinese /8 IP blocks

### 7. Continuous Monitoring
- **Real-time Change Detection**: Automatic notification of network changes
- **Configurable Intervals**: Custom monitoring frequency
- **Callback System**: Hook into change events
- **Status Tracking**: Timestamps and change history

### 8. Multi-format Export
- **JSON**: Machine-readable full data
- **CSV**: Spreadsheet-compatible lists
- **XML**: Structured data export
- **HTML**: Interactive visual reports with styling
- **Markdown**: Documentation-friendly reports

---

## 🔒 Security Features

- **Rate Limiting**: Token bucket algorithm to control scan speed
- **Input Validation**: Pydantic models for all API inputs
- **SQL Injection Prevention**: Parameterized queries throughout
- **Privilege Dropping**: Run with minimal required permissions
- **Sandbox Mode**: Isolated execution environment
- **Audit Logging**: Comprehensive logging of all operations
- **DNS Verification**: Multi-server response validation

---

## 📖 Documentation

- **[INSTALL.md](INSTALL.md)** - Installation and quick start guide
- **[docs/GUIDE.md](docs/GUIDE.md)** - Comprehensive user guide
- **[docs/API.md](docs/API.md)** - API reference (1000+ lines)
- **[docs/API_QUICKSTART.md](docs/API_QUICKSTART.md)** - API quick start
- **[API_ENHANCEMENT_SUMMARY.md](API_ENHANCEMENT_SUMMARY.md)** - Enhancement details

---

## 🧪 Examples

Complete usage examples in `examples/` directory:

```bash
# Basic API operations
python examples/basic_api_usage.py

# Full enumeration
python examples/full_enumeration.py

# Network audit
python examples/network_audit.py

# Continuous monitoring
python examples/continuous_monitoring.py

# Masscan full scan
python examples/masscan_full_scan.py
```

---

## 🔧 Configuration

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

---

## 📊 Project Statistics

- **Total Modules**: 33 Python files
- **Code Lines**: ~8,000 (including documentation)
- **API Endpoints**: 15+ REST endpoints
- **Database Tables**: 4 (hosts, ports, domains, scans)
- **Export Formats**: 5 (JSON, CSV, XML, HTML, Markdown)
- **Documentation**: 3,000+ lines

---

## 🛠️ System Requirements

- **OS**: Ubuntu 20.04+, Debian 10+, or similar
- **Python**: 3.7+
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 1GB for installation, more for scan results
- **Network**: Outbound access to IPv9 DNS servers

**Dependencies:**
- System: nmap, masscan, dnsmasq, dnsutils, sqlite3
- Python: fastapi, textual, rich, dnspython, pyyaml, aiosqlite

---

## 🚀 Common Use Cases

### Quick Domain Check

```bash
# Using TUI
ipv9scan
# Enter domain, click "Resolve DNS"

# Using API
curl -X POST http://localhost:8000/dns/resolve \
  -H "Content-Type: application/json" \
  -d '{"hostname": "www.v9.chn"}'

# Using CLI
ipv9tool resolve www.v9.chn
```

### Port Scanning

```bash
# Using TUI
ipv9scan
# Enter target, click "Port Scan"

# Using API
python -c "
from ipv9tool.api.client import IPv9APIClient
client = IPv9APIClient('http://localhost:8000')
scan = client.scan('em777.chn', ports='1-1000')
print(scan)
"

# Using CLI
ipv9tool scan em777.chn --ports 1-1000
```

### Full Network Audit

```bash
# Using TUI
ipv9scan
# Click "Full Audit" button

# Using API
python examples/network_audit.py

# Using CLI (enumeration only)
ipv9tool enumerate --pattern "861381234NNNN" --max-results 10000
```

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for authorized security testing, research, and educational purposes only. Always obtain proper authorization before scanning networks you do not own or have permission to test.

---

## 🙏 Acknowledgments

- Inspired by HDAIS workflow and masscan architecture
- Built with FastAPI, Textual, Rich, and other excellent open-source projects
- IPv9 DNS servers provided by China's decimal network infrastructure

---

## 📞 Support

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **API Docs**: http://localhost:8000/docs (when API running)
- **Issues**: https://github.com/SWORDIntel/IPVNINER/issues

---

**Happy scanning! 🔍**
