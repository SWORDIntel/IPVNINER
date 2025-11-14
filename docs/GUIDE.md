# IPv9 Scanner - Comprehensive Usage Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Command-Line Usage](#command-line-usage)
5. [DNS Resolution](#dns-resolution)
6. [Host Discovery](#host-discovery)
7. [Port Scanning](#port-scanning)
8. [Domain Enumeration](#domain-enumeration)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

## Overview

IPv9 Scanner is a comprehensive tool for exploring China's "IPv9" (decimal network) infrastructure. IPv9 is not a standard IETF protocol but rather a DNS overlay system that uses numeric domain names under the `.chn` pseudo-top-level domain.

### How IPv9 Works

IPv9 uses special DNS servers (202.170.218.93 and 61.244.5.162) that intercept queries for:
- `.chn` domains (e.g., `www.v9.chn`)
- All-numeric domains (e.g., `8613812345678.chn`)

These domains are resolved to standard IPv4/IPv6 addresses, allowing access through normal internet routing.

### Key Features

- **DNS Resolution**: Query IPv9 DNS servers for .chn domains
- **DNS Caching**: Efficient caching to reduce DNS load
- **Host Discovery**: Ping and probe IPv9 hosts
- **Port Scanning**: Scan IPv9 hosts using nmap/masscan
- **Domain Enumeration**: Brute-force discovery of numeric domains
- **Security Controls**: Rate limiting, sandboxing, audit logging
- **Modular Design**: Easy to extend and customize

## Installation

### Prerequisites

- Debian/Ubuntu-based Linux distribution
- Python 3.7 or higher
- Root access (for DNS configuration)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/ipv9-scanner
cd ipv9-scanner

# Run installation script
sudo ./scripts/install.sh
```

The installation script will:
1. Install system dependencies (dnsmasq, nmap, masscan)
2. Install Python dependencies
3. Create system user and directories
4. Install systemd services
5. Configure DNS forwarding

### Manual Installation

```bash
# Install system packages
sudo apt-get update
sudo apt-get install python3 python3-pip dnsmasq nmap masscan dnsutils

# Install Python package
sudo pip3 install .

# Or install in development mode
sudo pip3 install -e .

# Copy configuration files
sudo mkdir -p /etc/ipv9tool
sudo cp config/ipv9tool.yml /etc/ipv9tool/
sudo cp config/dnsmasq-ipv9.conf /etc/ipv9tool/

# Setup DNS
sudo ./scripts/setup-dns.sh
```

## Configuration

### Main Configuration File

Edit `/etc/ipv9tool/ipv9tool.yml`:

```yaml
dns:
  primary: "202.170.218.93"
  secondary: "61.244.5.162"
  cache_size: 1000
  ttl: 300

scanner:
  rate_limit: 100        # packets per second
  timeout: 5            # seconds
  max_threads: 10

security:
  verify_dns: true      # verify responses across servers
  sandbox_mode: true    # run in sandbox
  log_level: "INFO"

logging:
  file: "/var/log/ipv9tool.log"
  max_size: 10485760   # 10MB
  backup_count: 5
```

### DNS Configuration

#### Using dnsmasq (Recommended)

Edit `/etc/ipv9tool/dnsmasq-ipv9.conf`:

```
# Forward .chn domains to IPv9 DNS
server=/.chn/202.170.218.93
server=/.chn/61.244.5.162

# Cache settings
cache-size=1000

# Logging
log-queries
log-facility=/var/log/ipv9-dnsmasq.log
```

Start dnsmasq:
```bash
sudo systemctl start dnsmasq
sudo systemctl enable dnsmasq
```

#### Using unbound

Edit `/etc/ipv9tool/unbound-ipv9.conf`:

```
forward-zone:
    name: "chn."
    forward-addr: 202.170.218.93
    forward-addr: 61.244.5.162
```

Start unbound:
```bash
sudo systemctl start unbound
sudo systemctl enable unbound
```

## Command-Line Usage

### Basic Commands

#### Resolve a Hostname

```bash
# Resolve .chn domain
ipv9tool resolve www.v9.chn

# Resolve with specific record type
ipv9tool resolve em777.chn --type A

# JSON output
ipv9tool resolve www.hqq.chn --json
```

#### Ping a Host

```bash
# Ping IPv9 host
ipv9tool ping em777.chn

# Specify packet count
ipv9tool ping www.v9.chn --count 10

# JSON output
ipv9tool ping em777.chn --json
```

#### Scan Ports

```bash
# Quick scan (common ports)
ipv9tool scan www.v9.chn

# Scan specific ports
ipv9tool scan em777.chn --ports 80,443,8080

# Scan port range
ipv9tool scan www.hqq.chn --ports 1-10000

# TCP scan
ipv9tool scan em777.chn --type tcp
```

#### HTTP Probe

```bash
# HTTP probe
ipv9tool http www.v9.chn

# HTTPS probe
ipv9tool http em777.chn --https --port 443

# Custom port
ipv9tool http www.hqq.chn --port 8080
```

### Domain Enumeration

#### Pattern-Based Enumeration

```bash
# Enumerate with pattern (N = any digit)
ipv9tool enumerate "861381234NNNN" --max 1000

# Different TLD
ipv9tool enumerate "8613NNNNNNNN" --tld chn --max 5000

# JSON output for automation
ipv9tool enumerate "86138NNNNNNN" --json > results.json
```

Pattern syntax:
- `N` = any digit (0-9)
- Fixed digits remain unchanged
- Example: `861381234NNNN` generates 861381234[0000-9999]

### Cache Management

```bash
# View cache statistics
ipv9tool cache-stats

# JSON output
ipv9tool cache-stats --json
```

## DNS Resolution

### How DNS Resolution Works

1. Client queries `.chn` domain
2. Local resolver (dnsmasq/unbound) forwards to IPv9 DNS
3. IPv9 DNS server resolves to IPv4/IPv6 address
4. Result is cached locally
5. Client connects using normal IP routing

### Testing DNS Resolution

```bash
# Test using dig
dig @202.170.218.93 www.v9.chn

# Test using host
host www.v9.chn 202.170.218.93

# Test using ipv9tool
ipv9tool resolve www.v9.chn --verbose
```

### DNS Caching

The tool caches DNS results to reduce load:

```python
from ipv9tool.dns import IPv9Resolver, DNSCache

# Create resolver with cache
resolver = IPv9Resolver()
cache = DNSCache(max_size=1000, default_ttl=300)

# Resolve and cache
hostname = "www.v9.chn"
cached = cache.get(hostname)

if not cached:
    addresses = resolver.resolve(hostname)
    cache.set(hostname, addresses)
```

## Host Discovery

### ICMP Ping

```bash
# Simple ping
ipv9tool ping em777.chn

# Multiple packets
ipv9tool ping www.v9.chn --count 10
```

### TCP Ping

```python
from ipv9tool.scanner import HostDiscovery

discovery = HostDiscovery()

# TCP ping on port 80
result = discovery.tcp_ping("www.v9.chn", port=80)

if result['reachable']:
    print(f"Host is up (response time: {result['response_time_ms']}ms)")
```

### HTTP Probe

```bash
# HTTP probe
ipv9tool http www.v9.chn

# HTTPS probe
ipv9tool http em777.chn --https
```

## Port Scanning

### Quick Scans

```bash
# Common ports (fast)
ipv9tool scan www.v9.chn

# Top 100 ports
ipv9tool scan em777.chn --ports 1-100

# Specific services
ipv9tool scan www.hqq.chn --ports 80,443,8080,8443
```

### Advanced Scanning

```python
from ipv9tool.scanner import PortScanner
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()
scanner = PortScanner()

# Resolve hostname
hostname = "www.v9.chn"
addresses = resolver.resolve(hostname)

if addresses:
    target = addresses[0]

    # Scan with service detection
    result = scanner.scan_nmap(
        target,
        ports="1-1000",
        scan_type="syn",
        service_detection=True,
        os_detection=False
    )

    # Process results
    for host in result.get('hosts', []):
        for port in host.get('ports', []):
            if port['state'] == 'open':
                print(f"Port {port['port']}: {port.get('service', {}).get('name', 'unknown')}")
```

### Masscan (High-Speed)

```python
from ipv9tool.scanner import PortScanner

scanner = PortScanner()

# Masscan requires IP addresses (not hostnames)
targets = ["1.2.3.4", "5.6.7.8"]

result = scanner.scan_masscan(
    targets,
    ports="1-65535"
)
```

## Domain Enumeration

### Phone Number-Based Enumeration

Chinese mobile numbers: `+86` + 3-digit prefix + 8 digits

```python
from ipv9tool.scanner import DNSEnumerator
from ipv9tool.dns import IPv9Resolver

resolver = IPv9Resolver()
enumerator = DNSEnumerator(resolver)

# Enumerate phone numbers
# Format: 86 + area_code + exchange + [0000-9999]
results = enumerator.enumerate_phone_numbers(
    area_code="138",      # Mobile prefix
    exchange="1234",      # Next 4 digits
    start=0,
    end=9999,
    tld="chn"
)

for result in results:
    print(f"{result['hostname']} -> {result['addresses']}")
```

### Pattern-Based Enumeration

```python
# Brute force with pattern
results = enumerator.brute_force_pattern(
    pattern="861381234NNNN",
    tld="chn",
    max_combinations=1000
)

# Save results
import json
with open('enumeration_results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Common Mobile Prefixes

The tool includes common Chinese mobile prefixes:

```python
# Enumerate all common mobile prefixes
results = enumerator.enumerate_common_mobile_prefixes(
    exchange="1234",
    count=100,
    tld="chn"
)
```

## Security Considerations

### Rate Limiting

Always use rate limiting to avoid overwhelming targets:

```yaml
# config/ipv9tool.yml
scanner:
  rate_limit: 100  # Max 100 packets per second
```

```python
from ipv9tool.security import RateLimiter

# Create rate limiter
limiter = RateLimiter(rate=100, per=1.0)

# Use in scanning loop
for target in targets:
    limiter.acquire()  # Wait if rate limit exceeded
    scan(target)
```

### Sandbox Mode

Run scans in isolated environment:

```python
from ipv9tool.security import Sandbox

sandbox = Sandbox(enable=True)

# Check capabilities
caps = sandbox.check_capabilities()

# Run isolated command
result = sandbox.run_isolated(
    ['nmap', '-p80', '1.2.3.4'],
    timeout=60
)
```

### Logging and Auditing

All operations are logged:

```bash
# View logs
tail -f /var/log/ipv9tool/ipv9tool.log

# Audit log
tail -f /var/log/ipv9tool/audit.log
```

### DNS Verification

Verify DNS responses across multiple servers:

```yaml
security:
  verify_dns: true  # Enable multi-server verification
```

This protects against DNS spoofing by comparing responses from both IPv9 DNS servers.

## Troubleshooting

### DNS Not Working

```bash
# Check dnsmasq status
sudo systemctl status dnsmasq

# Check logs
sudo tail -f /var/log/ipv9-dnsmasq.log

# Test DNS manually
dig @202.170.218.93 www.v9.chn

# Verify /etc/resolv.conf
cat /etc/resolv.conf
```

### Can't Resolve .chn Domains

1. Verify DNS servers are reachable:
```bash
ping -c 4 202.170.218.93
ping -c 4 61.244.5.162
```

2. Check DNS forwarding:
```bash
# Should show 127.0.0.1
cat /etc/resolv.conf
```

3. Test direct query:
```bash
dig @202.170.218.93 www.v9.chn
```

### Scanning Fails

1. Check if nmap is installed:
```bash
which nmap
nmap --version
```

2. Check permissions:
```bash
# nmap SYN scan requires root
sudo ipv9tool scan www.v9.chn
```

3. Try TCP scan instead:
```bash
ipv9tool scan www.v9.chn --type tcp
```

### Permission Denied Errors

```bash
# Check log directory permissions
ls -la /var/log/ipv9tool

# Fix permissions
sudo chown -R ipv9tool:ipv9tool /var/log/ipv9tool
sudo chmod 755 /var/log/ipv9tool
```

## Advanced Usage

### Python API

```python
from ipv9tool.dns import IPv9Resolver
from ipv9tool.scanner import PortScanner, HostDiscovery, DNSEnumerator
from ipv9tool.config import ConfigManager

# Load configuration
config = ConfigManager('/etc/ipv9tool/ipv9tool.yml')

# Initialize components
resolver = IPv9Resolver(config.get_config())
scanner = PortScanner(config.get_config())
discovery = HostDiscovery(config.get_config())

# Resolve domain
addresses = resolver.resolve('www.v9.chn')

# Ping host
result = discovery.ping(addresses[0])

# Scan ports
scan_result = scanner.scan_nmap(addresses[0], ports="1-1000")
```

### Custom DNS Forwarder

```python
from ipv9tool.dns import DNSForwarder

forwarder = DNSForwarder(
    primary_dns="202.170.218.93",
    secondary_dns="61.244.5.162"
)

# Generate dnsmasq config
config = forwarder.generate_dnsmasq_config()
print(config)

# Check DNS reachability
status = forwarder.check_dns_reachability()
```

### Batch Scanning

```python
from concurrent.futures import ThreadPoolExecutor

targets = ["www.v9.chn", "em777.chn", "www.hqq.chn"]

def scan_target(hostname):
    addresses = resolver.resolve(hostname)
    if addresses:
        return scanner.quick_scan(addresses[0])
    return None

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(scan_target, targets))
```

### Custom Enumeration

```python
# Generate custom wordlist
wordlist = []
for prefix in ['138', '139', '186']:
    for i in range(1000, 2000):
        wordlist.append(f"86{prefix}{i:07d}")

# Enumerate in parallel
results = enumerator.enumerate_wordlist(
    wordlist,
    tld="chn",
    parallel=True
)
```

## Examples

### Example 1: Discover and Scan IPv9 Host

```bash
# Resolve hostname
ipv9tool resolve www.v9.chn

# Ping to verify
ipv9tool ping www.v9.chn

# Quick scan
ipv9tool scan www.v9.chn

# HTTP probe
ipv9tool http www.v9.chn
```

### Example 2: Enumerate Phone Number Range

```bash
# Enumerate pattern
ipv9tool enumerate "861381234NNNN" --max 10000 --json > results.json

# Process results
cat results.json | jq '.[] | select(.addresses | length > 0)'
```

### Example 3: Automated Scanning Pipeline

```python
#!/usr/bin/env python3
import json
from ipv9tool.dns import IPv9Resolver
from ipv9tool.scanner import PortScanner, DNSEnumerator

resolver = IPv9Resolver()
scanner = PortScanner()
enumerator = DNSEnumerator(resolver)

# Enumerate domains
print("Enumerating domains...")
domains = enumerator.brute_force_pattern("861381234NNNN", max_combinations=100)

# Scan each discovered host
results = []
for domain in domains:
    hostname = domain['hostname']
    addresses = domain['addresses']

    print(f"Scanning {hostname}...")

    for address in addresses:
        scan_result = scanner.quick_scan(address)
        results.append({
            'hostname': hostname,
            'address': address,
            'scan': scan_result
        })

# Save results
with open('scan_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Scanned {len(results)} hosts")
```

## Best Practices

1. **Always use rate limiting** to avoid overwhelming targets
2. **Enable DNS verification** to detect spoofing
3. **Run in sandbox mode** for security
4. **Log all operations** for audit trail
5. **Respect target resources** - don't scan aggressively
6. **Use caching** to reduce DNS load
7. **Monitor logs** for errors and anomalies
8. **Test on known hosts** before production use

## Legal and Ethical Considerations

- Only scan systems you have permission to test
- Respect rate limits and target resources
- Follow responsible disclosure for vulnerabilities
- Comply with local laws and regulations
- IPv9 infrastructure is experimental - use responsibly

## References

- [IPv9 Wikipedia](https://en.wikipedia.org/wiki/IPv9_(China))
- [Explaining China's IPv9](https://circleid.com/posts/explaining_chinas_ipv9)
- [IPv9 Research Papers](https://reference-global.com/article/10.21307/ijanmc-2020-026)

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/ipv9-scanner/issues
- Documentation: https://github.com/yourusername/ipv9-scanner/docs
