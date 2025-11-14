# IPv9 Scanner

**Exploration and Discovery Tool for China's Decimal Network**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## Overview

IPv9 Scanner is a comprehensive toolkit for exploring China's "IPv9" (decimal network) infrastructure. IPv9 is a non-standard network addressing scheme that uses numeric "digital domain" names under the `.chn` pseudo-top-level domain. This tool provides DNS resolution, host discovery, port scanning, and domain enumeration capabilities specifically designed for IPv9 networks.

### What is IPv9?

IPv9 is China's experimental "decimal network" that uses:
- **Numeric domain names** based on phone numbers (e.g., `8613812345678.chn`)
- **Special DNS servers** (202.170.218.93 and 61.244.5.162) that intercept `.chn` queries
- **Standard IP routing** - domains resolve to normal IPv4/IPv6 addresses
- **DNS overlay architecture** - no new protocol stack required

Example IPv9 sites:
- `www.v9.chn`
- `em777.chn`
- `www.hqq.chn`

## Features

### Core Capabilities

- **DNS Resolution**: Query IPv9 DNS servers for `.chn` and numeric domains
- **DNS Caching**: Efficient local caching with configurable TTL
- **Multi-Server Verification**: Validate DNS responses across multiple servers to detect spoofing
- **Host Discovery**:
  - ICMP ping
  - TCP ping
  - HTTP/HTTPS probing
- **Port Scanning**:
  - Nmap integration with service detection
  - Masscan support for high-speed scanning
  - Customizable port ranges and scan types
- **Domain Enumeration**:
  - Pattern-based brute forcing
  - Phone number range enumeration
  - Chinese mobile prefix scanning
  - Wordlist-based discovery

### Security Features

- **Rate Limiting**: Token bucket algorithm to control scan speed
- **Sandbox Mode**: Isolated execution environment
- **Audit Logging**: Comprehensive logging of all operations
- **DNS Verification**: Multi-server DNS response validation
- **Privilege Dropping**: Run with minimal required permissions

### Architecture

```
┌─────────────────────────────────────────────────┐
│              IPv9 Scanner Tool                   │
├─────────────────────────────────────────────────┤
│  CLI Interface  │  Python API  │  Web Dashboard  │
├─────────────────┴──────────────┴─────────────────┤
│              Core Modules                        │
│  ┌──────────┐  ┌─────────┐  ┌──────────────┐   │
│  │   DNS    │  │ Scanner │  │   Security   │   │
│  │ Resolver │  │ Module  │  │   Controls   │   │
│  └──────────┘  └─────────┘  └──────────────┘   │
└─────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ IPv9 DNS │   │  Targets │   │ System   │
    │ Servers  │   │  (IPv4/6)│   │ Resources│
    └──────────┘   └──────────┘   └──────────┘
```

## Installation

### Quick Start (Debian/Ubuntu)

```bash
# Clone repository
git clone https://github.com/SWORDIntel/IPVNINER
cd IPVNINER

# Run installation script
sudo ./scripts/install.sh
```

### Manual Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip dnsmasq nmap masscan dnsutils

# Install Python package
sudo pip3 install .

# Setup DNS forwarding
sudo ./scripts/setup-dns.sh
```

### Requirements

**System:**
- Debian 10+ or Ubuntu 18.04+
- Python 3.7+
- Root access (for DNS configuration and raw socket scanning)

**Dependencies:**
- `dnsmasq` or `unbound` (DNS forwarding)
- `nmap` (port scanning)
- `masscan` (optional, for high-speed scanning)
- `dnspython` (Python DNS library)
- `pyyaml` (configuration files)

## Quick Start

### Resolve an IPv9 Domain

```bash
ipv9tool resolve www.v9.chn
```

Output:
```
www.v9.chn resolves to:
  203.0.113.10
```

### Ping an IPv9 Host

```bash
ipv9tool ping em777.chn
```

### Scan IPv9 Host Ports

```bash
ipv9tool scan www.v9.chn --ports 80,443,8080
```

### HTTP Probe

```bash
ipv9tool http www.v9.chn
```

### Enumerate Domains

```bash
# Enumerate phone number pattern
# N = any digit (0-9)
ipv9tool enumerate "861381234NNNN" --max 1000
```

## Configuration

Main configuration file: `/etc/ipv9tool/ipv9tool.yml`

```yaml
dns:
  primary: "202.170.218.93"
  secondary: "61.244.5.162"
  cache_size: 1000
  ttl: 300

scanner:
  rate_limit: 100      # packets per second
  timeout: 5          # seconds
  max_threads: 10

security:
  verify_dns: true
  sandbox_mode: true
  log_level: "INFO"
```

## Usage Examples

### Command-Line Interface

```bash
# Resolve domain with JSON output
ipv9tool resolve em777.chn --json

# Ping with custom count
ipv9tool ping www.v9.chn --count 10

# Comprehensive port scan
ipv9tool scan em777.chn --ports 1-65535 --type syn

# HTTPS probe
ipv9tool http www.v9.chn --https --port 443

# Enumerate with pattern
ipv9tool enumerate "86138NNNNNNNN" --max 5000

# View cache statistics
ipv9tool cache-stats
```

### Python API

```python
from ipv9tool.dns import IPv9Resolver
from ipv9tool.scanner import PortScanner, DNSEnumerator

# Resolve domain
resolver = IPv9Resolver()
addresses = resolver.resolve('www.v9.chn')
print(addresses)  # ['203.0.113.10']

# Scan ports
scanner = PortScanner()
result = scanner.scan_nmap('203.0.113.10', ports='1-1000')

# Enumerate domains
enumerator = DNSEnumerator(resolver)
results = enumerator.brute_force_pattern('861381234NNNN')
```

### Advanced: Batch Scanning

```python
#!/usr/bin/env python3
from ipv9tool.dns import IPv9Resolver
from ipv9tool.scanner import PortScanner, DNSEnumerator
import json

resolver = IPv9Resolver()
scanner = PortScanner()
enumerator = DNSEnumerator(resolver)

# Discover domains
domains = enumerator.brute_force_pattern("861381234NNNN", max_combinations=100)

# Scan each discovered host
results = []
for domain in domains:
    for address in domain['addresses']:
        scan = scanner.quick_scan(address)
        results.append({
            'hostname': domain['hostname'],
            'address': address,
            'scan': scan
        })

# Save results
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

## Documentation

- **[Comprehensive Usage Guide](docs/GUIDE.md)** - Detailed documentation
- **Configuration Reference** - See `config/ipv9tool.yml`
- **API Documentation** - See source code docstrings

## Architecture Details

### DNS Resolver Module

- **IPv9Resolver**: Queries IPv9 DNS servers
- **DNSCache**: LRU cache for DNS results
- **DNSForwarder**: Generates dnsmasq/unbound configs

### Scanner Module

- **PortScanner**: Nmap/masscan integration
- **HostDiscovery**: Ping and TCP probing
- **DNSEnumerator**: Domain enumeration

### Security Module

- **RateLimiter**: Token bucket rate limiting
- **Sandbox**: Process isolation
- **Logging**: Audit trail and monitoring

## Security Considerations

### Best Practices

1. **Always use rate limiting** - Default 100 packets/sec
2. **Enable DNS verification** - Detect spoofing
3. **Run in sandbox mode** - Minimize risk
4. **Monitor logs** - `/var/log/ipv9tool.log`
5. **Respect targets** - Don't overwhelm systems

### Rate Limiting

```yaml
scanner:
  rate_limit: 100  # Max packets per second
```

### Sandboxing

```yaml
security:
  sandbox_mode: true  # Enable isolation
```

### DNS Verification

```yaml
security:
  verify_dns: true  # Compare responses from both DNS servers
```

## Troubleshooting

### DNS Not Working

```bash
# Check dnsmasq
sudo systemctl status dnsmasq
sudo tail -f /var/log/ipv9-dnsmasq.log

# Test DNS manually
dig @202.170.218.93 www.v9.chn

# Verify resolv.conf
cat /etc/resolv.conf
```

### Scanning Permission Denied

```bash
# SYN scans require root
sudo ipv9tool scan www.v9.chn

# Or use TCP scan
ipv9tool scan www.v9.chn --type tcp
```

### IPv9 DNS Unreachable

```bash
# Check connectivity
ping -c 4 202.170.218.93
ping -c 4 61.244.5.162

# Try direct query
dig @202.170.218.93 www.v9.chn
```

## Development

### Project Structure

```
ipv9-scanner/
├── ipv9tool/              # Main Python package
│   ├── dns/               # DNS resolver
│   ├── scanner/           # Scanning modules
│   ├── cli/               # CLI interface
│   ├── config/            # Configuration
│   └── security/          # Security controls
├── config/                # Configuration files
├── scripts/               # Installation scripts
├── systemd/               # Service files
├── docs/                  # Documentation
├── tests/                 # Unit tests
└── setup.py               # Installation script
```

### Running Tests

```bash
# Install development dependencies
pip3 install -e .[dev]

# Run tests
pytest tests/

# Run with coverage
pytest --cov=ipv9tool tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Legal and Ethical Notice

⚠️ **Important**: This tool is for **authorized security testing, research, and educational purposes only**.

- Only scan systems you have **explicit permission** to test
- Respect rate limits and target resources
- Follow **responsible disclosure** for vulnerabilities
- Comply with **local laws and regulations**
- IPv9 is **experimental** - use responsibly

**The authors assume no liability for misuse of this tool.**

## References

- [IPv9 Wikipedia](https://en.wikipedia.org/wiki/IPv9_(China))
- [Explaining China's IPv9 - CircleID](https://circleid.com/posts/explaining_chinas_ipv9)
- [IPv9 Research Paper](https://reference-global.com/article/10.21307/ijanmc-2020-026)
- [The Register: China disowns IPv9 hype](https://www.theregister.com/2004/07/06/ipv9_hype_dismissed/)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Authors

IPv9 Research Team

## Acknowledgments

- Dnsmasq and Unbound projects
- Nmap and Masscan developers
- Python dnspython library
- Chinese IPv9 research community

## Support

- **Issues**: [GitHub Issues](https://github.com/SWORDIntel/IPVNINER/issues)
- **Documentation**: [Comprehensive Guide](docs/GUIDE.md)
- **Email**: research@example.com

---

**Note**: IPv9 is an experimental network system developed in China and is not recognized by international standards bodies. This tool is provided for research and educational purposes to understand alternative network addressing schemes.
