# IPv9 DNS Overlay - Comprehensive Technical Guide

## Table of Contents

1. [Introduction](#introduction)
2. [IPv9 Architecture](#ipv9-architecture)
3. [DNS Overlay Mechanism](#dns-overlay-mechanism)
4. [IPv9 Scanner Integration](#ipv9-scanner-integration)
5. [Exploring the IPv9 Network](#exploring-the-ipv9-network)
6. [Advanced Techniques](#advanced-techniques)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is IPv9?

IPv9 (also known as the "Decimal Network") is China's experimental network addressing scheme that uses:
- **Numeric domain names** based on decimal digits
- **Phone number integration** as domain identifiers
- **DNS overlay architecture** rather than a new protocol stack
- **Standard IPv4/IPv6 routing** underneath

**Key Insight**: IPv9 is not a replacement for IPv4/IPv6 but rather a DNS-based overlay that maps decimal identifiers to traditional IP addresses.

### Why IPv9 Matters

- **Massive Address Space**: Theoretically unlimited decimal domain names
- **Cultural Integration**: Chinese phone numbers as network identifiers
- **Research Interest**: Alternative approach to network addressing
- **Real Deployments**: Active infrastructure with DNS servers and domains

---

## IPv9 Architecture

### Three-Layer Model

```
┌────────────────────────────────────────────────────┐
│  Layer 3: Application Layer                        │
│  ┌──────────────────────────────────────────────┐  │
│  │ User enters: www.v9.chn or 8613812345678.chn│  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────┐
│  Layer 2: DNS Overlay Layer                        │
│  ┌──────────────────────────────────────────────┐  │
│  │ IPv9 DNS Servers (202.170.218.93, etc.)     │  │
│  │ - Intercept .chn queries                     │  │
│  │ - Resolve decimal names to IP addresses      │  │
│  │ - Return standard A/AAAA records             │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────┐
│  Layer 1: Standard IP Layer (IPv4/IPv6)            │
│  ┌──────────────────────────────────────────────┐  │
│  │ Normal IP routing to: 1.2.3.4 or 2001:db8::1│  │
│  │ - Uses existing Internet infrastructure      │  │
│  │ - No special routing required                │  │
│  │ - Works with standard protocols              │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### DNS Servers

**Primary IPv9 DNS Servers:**
- `202.170.218.93` - Primary server
- `61.244.5.162` - Secondary server

These servers:
1. Intercept queries for `.chn` TLD
2. Maintain mappings of decimal domains to IP addresses
3. Return standard DNS A/AAAA records
4. Work with standard DNS protocol (no modifications)

---

## DNS Overlay Mechanism

### How Resolution Works

#### Traditional DNS
```
User → DNS Resolver → Root Servers → TLD Servers → Authoritative → IP
       (8.8.8.8)      (.)            (.com)         (example.com)
```

#### IPv9 DNS Overlay
```
User → IPv9 DNS → Direct Resolution → IP
       (202.170.218.93)  (.chn mapping)
```

**Key Difference**: IPv9 DNS servers bypass the traditional DNS hierarchy and directly resolve `.chn` domains.

### Example Resolution Flow

```bash
# Query sent to IPv9 DNS
dig @202.170.218.93 www.v9.chn

# Server checks internal database:
# www.v9.chn → 1.2.3.4

# Returns standard A record:
;; ANSWER SECTION:
www.v9.chn.    300    IN    A    1.2.3.4

# Client connects to 1.2.3.4 using normal TCP/IP
```

### Domain Naming Patterns

#### 1. Branded Domains
```
www.v9.chn        # IPv9 main site
em777.chn         # Business domain
www.hqq.chn       # Application domain
```

#### 2. Phone Number Domains
```
8613812345678.chn      # Chinese mobile number
02155512345.chn        # Chinese landline
13800138000.chn        # Service number
```

#### 3. Numeric Patterns
```
123456.chn            # Pure numeric
12345678901234.chn    # Long numeric
```

---

## IPv9 Scanner Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           IPv9 Scanner Platform                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────┐        │
│  │  DNS Resolution Layer                        │        │
│  │  ┌────────────────────────────────────────┐│        │
│  │  │ IPv9Resolver                            ││        │
│  │  │ - Queries 202.170.218.93 & 61.244.5.162││        │
│  │  │ - Multi-server verification            ││        │
│  │  │ - LRU caching (3600s TTL)              ││        │
│  │  │ - Handles .chn and numeric domains     ││        │
│  │  └────────────────────────────────────────┘│        │
│  └─────────────────────────────────────────────┘        │
│                       │                                   │
│                       ▼                                   │
│  ┌─────────────────────────────────────────────┐        │
│  │  Enumeration Layer                           │        │
│  │  ┌────────────────────────────────────────┐│        │
│  │  │ DNSEnumerator                          ││        │
│  │  │ - Pattern-based: 861381234NNNN.chn    ││        │
│  │  │ - Phone ranges: 130-199 prefixes      ││        │
│  │  │ - Parallel resolution (10 threads)    ││        │
│  │  │ - Validity checking                   ││        │
│  │  └────────────────────────────────────────┘│        │
│  └─────────────────────────────────────────────┘        │
│                       │                                   │
│                       ▼                                   │
│  ┌─────────────────────────────────────────────┐        │
│  │  Discovery Layer                             │        │
│  │  ┌────────────────────────────────────────┐│        │
│  │  │ HostDiscovery                          ││        │
│  │  │ - ICMP ping (is host alive?)          ││        │
│  │  │ - TCP probing (common ports)          ││        │
│  │  │ - HTTP detection (web services)       ││        │
│  │  └────────────────────────────────────────┘│        │
│  └─────────────────────────────────────────────┘        │
│                       │                                   │
│                       ▼                                   │
│  ┌─────────────────────────────────────────────┐        │
│  │  Scanning Layer                              │        │
│  │  ┌────────────────────────────────────────┐│        │
│  │  │ PortScanner & MasscanEnumerator       ││        │
│  │  │ - Nmap: Service detection             ││        │
│  │  │ - Masscan: High-speed enumeration     ││        │
│  │  │ - Port range: 1-65535                 ││        │
│  │  │ - Rate limiting: 100-10000 pps        ││        │
│  │  └────────────────────────────────────────┘│        │
│  └─────────────────────────────────────────────┘        │
│                       │                                   │
│                       ▼                                   │
│  ┌─────────────────────────────────────────────┐        │
│  │  Storage Layer                               │        │
│  │  ┌────────────────────────────────────────┐│        │
│  │  │ DatabaseManager (SQLite/PostgreSQL)   ││        │
│  │  │ - hosts: IP, hostname, status         ││        │
│  │  │ - ports: Port, service, version       ││        │
│  │  │ - domains: .chn domains, responsiveness││        │
│  │  │ - scans: Audit history, results       ││        │
│  │  └────────────────────────────────────────┘│        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### How to Configure IPv9 DNS

#### Method 1: System-wide (via setup.sh)

```bash
./setup.sh
# Choose "Yes" when prompted for DNS configuration
```

This configures dnsmasq to forward `.chn` queries to IPv9 DNS servers.

#### Method 2: Application-level (default)

IPv9 Scanner automatically queries IPv9 DNS servers for `.chn` domains without system configuration.

```python
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()
# Automatically uses 202.170.218.93 and 61.244.5.162
addresses = resolver.resolve("www.v9.chn")
```

#### Method 3: Manual dnsmasq configuration

Edit `/etc/dnsmasq.conf`:

```conf
# Forward .chn queries to IPv9 DNS
server=/chn/202.170.218.93
server=/chn/61.244.5.162

# Normal queries go to regular DNS
server=8.8.8.8
server=8.8.4.4
```

Restart dnsmasq:
```bash
sudo systemctl restart dnsmasq
```

---

## Exploring the IPv9 Network

### Step 1: Verify IPv9 DNS Connectivity

```bash
# Using IPv9 Scanner CLI
ipv9tool resolve www.v9.chn

# Using dig directly
dig @202.170.218.93 www.v9.chn

# Expected output:
# www.v9.chn. 300 IN A <IP_ADDRESS>
```

### Step 2: Discover Known Domains

**TUI Method:**
```bash
ipv9scan
# Enter "www.v9.chn" and click "Resolve DNS"
```

**API Method:**
```python
from ipv9tool.api.client import IPv9APIClient

client = IPv9APIClient("http://localhost:8000")

# Test known domains
known_domains = ["www.v9.chn", "em777.chn", "www.hqq.chn"]

for domain in known_domains:
    result = client.resolve(domain)
    if result.addresses:
        print(f"{domain} → {result.addresses}")
```

**CLI Method:**
```bash
for domain in www.v9.chn em777.chn www.hqq.chn; do
    echo -n "$domain → "
    ipv9tool resolve $domain
done
```

### Step 3: Enumerate Phone Number Domains

**Pattern-based Enumeration:**

```bash
# Using TUI
ipv9scan
# Enter pattern: "861381234NNNN"
# Click "Enumerate"

# Using API
python examples/full_enumeration.py

# Using CLI
ipv9tool enumerate --pattern "861381234NNNN" --max-results 10000
```

**Common Patterns:**
- `8613NNNNNNNNN.chn` - Mobile numbers (13x prefix)
- `8615NNNNNNNNN.chn` - Mobile numbers (15x prefix)
- `8618NNNNNNNNN.chn` - Mobile numbers (18x prefix)
- `02155NNNNNN.chn` - Shanghai landlines
- `01058NNNNNN.chn` - Beijing landlines

### Step 4: Full Network Audit

```bash
# Using TUI
ipv9scan
# Click "Full Audit" button

# Using API
python examples/network_audit.py

# The audit runs 6 phases:
# 1. DNS Infrastructure Scan (20%)
# 2. Domain Enumeration (40%)
# 3. Host Discovery (60%)
# 4. Port Scanning (80%)
# 5. Deep Inspection (90%)
# 6. Analysis & Reporting (100%)
```

### Step 5: Masscan High-Speed Enumeration

```bash
# Using TUI
ipv9scan
# Click "Masscan" button

# Using example script
python examples/masscan_full_scan.py

# Direct API usage
from ipv9tool.audit import MasscanEnumerator

enumerator = MasscanEnumerator(rate=10000)

# Create 24-hour enumeration plan
plan = enumerator.create_enumeration_plan(
    total_budget_hours=24,
    ports="80,443,8080"
)

print(f"Rate: {plan['rate_pps']:,} pps")
print(f"Coverage: {plan['coverage_percent']:.4f}%")

# Enumerate IPv9 space (10% sample)
results = enumerator.enumerate_ipv9_space(
    sample_rate=0.10,
    ports="80,443"
)
```

---

## Advanced Techniques

### 1. Multi-Server Verification

Detect DNS spoofing by comparing responses from multiple servers:

```python
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()

# Enable multi-server verification
result = resolver.resolve("www.v9.chn", verify=True)

if result.verified:
    print(f"Verified: {result.addresses}")
else:
    print(f"Warning: Inconsistent responses!")
    print(f"  Server 1: {result.server1_addresses}")
    print(f"  Server 2: {result.server2_addresses}")
```

### 2. DNS Cache Optimization

```python
from ipv9tool.dns import IPv9Resolver

# Configure cache parameters
resolver = IPv9Resolver(
    cache_size=10000,  # Max entries
    cache_ttl=3600     # 1 hour
)

# Check cache statistics
stats = resolver.get_cache_stats()
print(f"Cache hits: {stats.hits}")
print(f"Cache misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.2%}")
```

### 3. Parallel Enumeration

```python
from ipv9tool.scanner import DNSEnumerator
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()
enumerator = DNSEnumerator(resolver)

# Enumerate with 20 parallel threads
results = enumerator.enumerate_pattern(
    pattern="861381234NNNN",
    max_results=100000,
    threads=20  # Parallel workers
)

for domain, addresses in results:
    print(f"{domain} → {addresses}")
```

### 4. Continuous Monitoring

```python
from ipv9tool.audit import ContinuousMonitor
from ipv9tool.audit import AuditEngine

# Initialize components
engine = AuditEngine(resolver, scanner, discovery, enumerator, db)
monitor = ContinuousMonitor(engine)

# Set up change callbacks
def on_new_host(host):
    print(f"New host discovered: {host.ip_address}")

def on_port_change(host, port):
    print(f"Port change on {host.ip_address}:{port.port}")

monitor.on_new_host = on_new_host
monitor.on_port_change = on_port_change

# Start monitoring (check every 5 minutes)
monitor.start(interval=300)
```

### 5. IPv9 Address Space Coverage

The scanner covers these IPv9-relevant IP blocks:

```python
IPV9_IP_BLOCKS = [
    # China Telecom
    "58.0.0.0/8", "59.0.0.0/8", "60.0.0.0/8", "61.0.0.0/8",
    "110.0.0.0/8", "111.0.0.0/8", "112.0.0.0/8",
    "113.0.0.0/8", "114.0.0.0/8", "115.0.0.0/8",

    # China Unicom
    "123.0.0.0/8", "124.0.0.0/8", "125.0.0.0/8",
    "210.0.0.0/8", "211.0.0.0/8",

    # China Mobile
    "117.0.0.0/8", "118.0.0.0/8", "120.0.0.0/8",
    "121.0.0.0/8", "183.0.0.0/8",

    # CERNET (Education)
    "202.0.0.0/8", "203.0.0.0/8",

    # Additional blocks
    "1.0.0.0/8", "14.0.0.0/8", "27.0.0.0/8",
    "36.0.0.0/8", "42.0.0.0/8", "49.0.0.0/8",
]
```

Masscan scans these blocks for IPv9 services.

---

## Security Considerations

### 1. DNS Spoofing Risks

**Problem**: IPv9 DNS servers could return malicious IP addresses.

**Mitigation**:
- Multi-server verification (compare responses)
- DNSSEC validation (if available)
- Monitor for IP address changes
- Cross-reference with WHOIS/geolocation data

```python
# Enable verification
result = resolver.resolve("www.v9.chn", verify=True)
if not result.verified:
    # Handle inconsistent responses
    log.warning("DNS verification failed!")
```

### 2. Rate Limiting

**Problem**: Aggressive scanning can overload targets or trigger IDS.

**Mitigation**:
- Token bucket rate limiting (default 100 pps)
- Configurable scan speeds
- Respect robots.txt and rate limits

```python
# Set conservative rate limit
scanner = PortScanner(rate_limit=50)  # 50 packets/second
```

### 3. Privacy Concerns

**Problem**: Enumerating phone numbers could reveal PII.

**Mitigation**:
- Only enumerate patterns, not individual numbers
- Respect privacy laws and regulations
- Anonymize results in reports
- Don't store sensitive phone numbers

### 4. Legal Compliance

**Important**: Always obtain authorization before scanning:
- Written permission for penetration testing
- Authorized security research only
- Educational use in controlled environments
- No unauthorized network reconnaissance

---

## Troubleshooting

### DNS Resolution Fails

**Symptom**: Cannot resolve `.chn` domains

**Diagnosis**:
```bash
# Test connectivity to IPv9 DNS servers
ping 202.170.218.93
ping 61.244.5.162

# Test direct DNS query
dig @202.170.218.93 www.v9.chn

# Check firewall rules
sudo iptables -L -n | grep 53
```

**Solutions**:
1. Check network connectivity
2. Verify firewall allows UDP/53 outbound
3. Try alternate IPv9 DNS server
4. Check if DNS servers are responsive

### Enumeration Returns No Results

**Symptom**: Pattern enumeration finds no domains

**Diagnosis**:
```python
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()

# Test a known domain first
test = resolver.resolve("www.v9.chn")
if not test:
    print("DNS resolution not working!")

# Try a specific pattern
result = resolver.resolve("8613812345678.chn")
if not result:
    print("Pattern may be invalid")
```

**Solutions**:
1. Verify DNS resolution works for known domains
2. Try simpler patterns first
3. Check if IPv9 DNS servers are filtering
4. Reduce enumeration scope (fewer digits)

### Slow Scanning Performance

**Symptom**: Scans take too long

**Diagnosis**:
```bash
# Check system resources
top
free -h
iotop

# Monitor network usage
iftop
nethogs
```

**Solutions**:
1. Increase parallel threads (if CPU allows)
2. Use masscan for large-scale scans
3. Reduce port range to common ports
4. Enable DNS caching
5. Use faster storage (SSD) for database

### Database Errors

**Symptom**: SQLite errors or slow queries

**Diagnosis**:
```bash
# Check database size
du -h ~/.ipv9tool/ipv9.db

# Analyze database
sqlite3 ~/.ipv9tool/ipv9.db "ANALYZE;"
sqlite3 ~/.ipv9tool/ipv9.db "PRAGMA integrity_check;"
```

**Solutions**:
1. Vacuum database: `sqlite3 ipv9.db "VACUUM;"`
2. Add indexes on frequently queried columns
3. Upgrade to PostgreSQL for large datasets
4. Implement database sharding

---

## Best Practices

### 1. Start Small
```bash
# Test with known domains first
ipv9tool resolve www.v9.chn
ipv9tool resolve em777.chn

# Then try limited enumeration
ipv9tool enumerate --pattern "86138NNNNN" --max-results 100
```

### 2. Use Caching
```python
# Enable aggressive caching for repeated queries
resolver = IPv9Resolver(
    cache_size=50000,
    cache_ttl=7200  # 2 hours
)
```

### 3. Monitor Resources
```bash
# Run in screen/tmux for long operations
screen -S ipv9scan
ipv9scan
# Ctrl+A, D to detach
```

### 4. Export Results Regularly
```python
from ipv9tool.export import DataExporter

exporter = DataExporter()
exporter.export_audit_results(
    results,
    output_dir='./backups',
    formats=['json', 'csv']
)
```

### 5. Continuous Monitoring
```python
# Set up automated monitoring
monitor = ContinuousMonitor(audit_engine)
monitor.start(interval=3600)  # Check every hour
```

---

## Conclusion

The IPv9 DNS overlay represents an interesting alternative approach to network addressing. This guide has shown you how to:

✅ Understand IPv9's DNS overlay architecture
✅ Configure and use IPv9 Scanner's three interfaces (TUI/API/CLI)
✅ Enumerate and discover IPv9 domains
✅ Perform comprehensive network audits
✅ Use advanced techniques for large-scale scanning
✅ Address security and privacy concerns
✅ Troubleshoot common issues

For more information, see:
- [INSTALL.md](../INSTALL.md) - Installation guide
- [README.md](../README.md) - Project overview
- [docs/GUIDE.md](GUIDE.md) - User guide
- [docs/API.md](API.md) - API reference

---

**Happy exploring! 🔍**
