# Proxy Rotation - Mullvad-Style Operational Security

## Overview

The IPv9 Scanner includes a sophisticated proxy rotation system inspired by Mullvad VPN, providing operational security and avoiding detection/rate limiting during network intelligence operations.

---

## Features

### Core Capabilities

- ✅ **Multiple Proxy Types**: HTTP, HTTPS, SOCKS5, SOCKS4, Tor
- ✅ **Automatic Rotation**: Random, round-robin, least-used, fastest, country-based strategies
- ✅ **Mullvad Integration**: Built-in support for Mullvad VPN SOCKS5 proxies
- ✅ **Tor Integration**: Automatic Tor SOCKS5 proxy detection and circuit rotation
- ✅ **Health Checking**: Automatic latency testing and failure detection
- ✅ **IP Verification**: Confirm IP changes after rotation
- ✅ **Failure Handling**: Automatic rotation on rate limits or connection failures
- ✅ **Commercial Proxy Support**: Compatible with Bright Data, Oxylabs, etc.

---

## Quick Start

### 1. Basic Configuration

Edit `/etc/ipv9tool/ipv9tool.yml`:

```yaml
proxy:
  enable_rotation: true
  rotation_strategy: "random"
  rotation_interval: 60  # Rotate every 60 seconds
  max_failures: 3
```

### 2. Add Proxies

**Option A: Proxy List File**

Create `config/proxies.txt`:

```
socks5://127.0.0.1:9050 ANON Tor Tor
http://proxy1.example.com:8080 US NewYork Provider1
socks5://user:pass@proxy2.example.com:1080 GB London Provider2
```

**Option B: Configuration File**

Add to `ipv9tool.yml`:

```yaml
proxy:
  proxy_list:
    - host: "1.2.3.4"
      port: 1080
      proxy_type: "socks5"
      country: "US"
      provider: "custom"
```

### 3. Enable and Test

```bash
# Test all proxies
ipv9tool test-proxies

# Verify rotation
ipv9tool verify-rotation

# Check current IP
ipv9tool current-ip

# Launch with proxies
ipv9scan  # Proxies are automatically used if enabled
```

---

## Mullvad VPN Integration

### Setup

1. **Get Mullvad Account**: https://mullvad.net/
2. **Find Account Number**: Login to Mullvad website
3. **Configure IPv9 Scanner**:

```yaml
proxy:
  enable_mullvad: true
  mullvad_account: "1234567890123456"  # Your account number
```

### Available Servers

Mullvad SOCKS5 proxies are automatically configured for:

| Location | Server | Country | City |
|----------|--------|---------|------|
| US East | us-nyc.mullvad.net | US | New York |
| US West | us-lax.mullvad.net | US | Los Angeles |
| UK | gb-lon.mullvad.net | GB | London |
| Germany | de-fra.mullvad.net | DE | Frankfurt |
| Sweden | se-sto.mullvad.net | SE | Stockholm |
| Netherlands | nl-ams.mullvad.net | NL | Amsterdam |
| Singapore | sg.mullvad.net | SG | Singapore |
| Japan | jp.mullvad.net | JP | Tokyo |

### Usage

```bash
# Enable Mullvad in config
vim /etc/ipv9tool/ipv9tool.yml
# Set enable_mullvad: true
# Set mullvad_account: YOUR_ACCOUNT_NUMBER

# Restart scanner
ipv9scan
```

---

## Tor Integration

### Setup

1. **Install Tor**:

```bash
sudo apt-get install tor
```

2. **Start Tor Service**:

```bash
sudo systemctl start tor
sudo systemctl enable tor
```

3. **Enable in IPv9 Scanner**:

```yaml
proxy:
  enable_tor: true
  tor_host: "127.0.0.1"
  tor_port: 9050
  tor_control_port: 9051
```

### Tor Circuit Rotation

**Manual Rotation**:

```python
from ipv9tool.proxy import get_proxy_manager

proxy_mgr = get_proxy_manager()
proxy_mgr.rotate_tor_circuit()
```

**Automatic Rotation**:

```yaml
proxy:
  rotation_interval: 300  # Rotate every 5 minutes
```

### Tor Control Port (Advanced)

For manual circuit rotation:

1. **Configure Tor Control Port**:

Edit `/etc/tor/torrc`:

```
ControlPort 9051
HashedControlPassword 16:HASHED_PASSWORD
```

Generate password:

```bash
tor --hash-password "your_password"
```

2. **Configure IPv9 Scanner**:

```yaml
proxy:
  tor_control_port: 9051
  tor_control_password: "your_password"
```

---

## Rotation Strategies

### Random (Recommended)

Random selection from available proxies.

```yaml
proxy:
  rotation_strategy: "random"
```

**Pros**: Unpredictable, good for evasion
**Cons**: May reuse same proxy multiple times

### Round Robin

Sequential rotation through proxy list.

```yaml
proxy:
  rotation_strategy: "round_robin"
```

**Pros**: Even distribution, predictable
**Cons**: Predictable pattern

### Least Used

Select proxy with fewest successful uses.

```yaml
proxy:
  rotation_strategy: "least_used"
```

**Pros**: Balanced usage across proxies
**Cons**: May favor slow/unreliable proxies

### Fastest

Select proxy with lowest latency.

```yaml
proxy:
  rotation_strategy: "fastest"
```

**Pros**: Best performance
**Cons**: Requires latency testing first

### Country Based

Rotate within specific countries.

```yaml
proxy:
  rotation_strategy: "country_based"
```

**Pros**: Geographic targeting
**Cons**: Requires country metadata

---

## Commercial Proxy Services

### Bright Data (formerly Luminati)

```
http://user-CUSTOMER:pass@zproxy.lum-superproxy.io:22225 US Rotating BrightData
```

### Oxylabs

```
http://user:pass@pr.oxylabs.io:7777 EU Rotating Oxylabs
```

### SmartProxy

```
http://user:pass@gate.smartproxy.com:7000 US Rotating SmartProxy
```

### Configuration

Add to `config/proxies.txt`:

```
# Bright Data
http://user-CUSTOMER:pass@zproxy.lum-superproxy.io:22225 US Rotating BrightData

# Oxylabs
http://user:pass@pr.oxylabs.io:7777 EU Rotating Oxylabs

# SmartProxy
http://user:pass@gate.smartproxy.com:7000 US Rotating SmartProxy
```

---

## Advanced Features

### Failure Detection

Proxies are automatically disabled after max failures:

```yaml
proxy:
  max_failures: 3  # Disable proxy after 3 failures
```

Failed proxies are temporarily removed from rotation and periodically retested.

### Latency Testing

Test all proxies and measure latency:

```bash
ipv9tool test-proxies
```

Output:

```
Testing 8 proxies...
Proxy test passed: 127.0.0.1:9050 (latency: 145ms)
Proxy test passed: us-nyc.mullvad.net:1080 (latency: 78ms)
Proxy test failed: 1.2.3.4:8080
Proxy testing complete: 7/8 working
```

### IP Verification

Verify your external IP:

```bash
# Direct IP (no proxy)
ipv9tool current-ip --no-proxy

# IP through proxy
ipv9tool current-ip
```

### Rotation Verification

Verify rotation is working:

```bash
ipv9tool verify-rotation
```

Output:

```
Testing proxy rotation...
Direct IP: 203.0.113.1
Proxy 1 IP: 198.51.100.42
Proxy 2 IP: 192.0.2.123
Proxy rotation verified successfully
```

---

## TUI Integration

### Proxy Status Widget

The military TUI displays proxy status:

```
╔════════════════════════╗
║   PROXY STATUS        ║
╠════════════════════════╣
│ STATUS:     █ ACTIVE   │
│ PROVIDER:   Mullvad    │
│ LOCATION:   US-NYC     │
│ CURRENT IP: 198.51.100.42
│ PROXIES:    8/10       │
│ ROTATION:   Random     │
╚════════════════════════╝
```

### Proxy Controls

**Buttons**:
- `[ROTATE]` - Force proxy rotation
- `[VERIFY IP]` - Check current external IP
- `[TEST PROXIES]` - Test all proxies

**Keyboard**:
- `P` - Rotate proxy
- `V` - Verify IP
- `T` - Test proxies

---

## Use Cases

### 1. Rate Limit Evasion

Avoid rate limiting during large-scale enumeration:

```yaml
proxy:
  enable_rotation: true
  rotation_strategy: "random"
  rotation_interval: 30  # Rotate every 30 seconds
```

### 2. Geographic Distribution

Scan from multiple countries:

```yaml
proxy:
  rotation_strategy: "country_based"
  mullvad_servers:
    - country: "US"
    - country: "GB"
    - country: "DE"
    - country: "JP"
```

### 3. Anonymity

Maximum anonymity with Tor:

```yaml
proxy:
  enable_tor: true
  rotation_interval: 600  # New Tor circuit every 10 minutes
```

### 4. High Performance

Fast scanning with low-latency proxies:

```yaml
proxy:
  rotation_strategy: "fastest"
```

---

## Programmatic Usage

### Python API

```python
from ipv9tool.proxy import get_proxy_manager

# Get proxy manager
proxy_mgr = get_proxy_manager()

# Add proxy
proxy_mgr.add_proxy(
    host="1.2.3.4",
    port=1080,
    proxy_type="socks5",
    country="US",
    provider="custom"
)

# Rotate proxy
proxy = proxy_mgr.rotate()
print(f"Using proxy: {proxy.host}:{proxy.port}")

# Get proxy dict for requests
proxies = proxy_mgr.get_proxy_dict(rotate=True)

# Make request
import requests
response = requests.get("https://api.ipify.org", proxies=proxies)
print(f"Current IP: {response.text}")

# Mark success/failure
proxy_mgr.mark_success()
# or
proxy_mgr.mark_failure()

# Get statistics
stats = proxy_mgr.get_stats()
print(f"Available proxies: {stats['available_proxies']}")
```

### Integration with Scanner

Proxies are automatically used by all scanning operations:

```python
from ipv9tool.scanner import PortScanner
from ipv9tool.proxy import configure_proxies

# Configure proxies
configure_proxies({
    'enable_rotation': True,
    'rotation_strategy': 'random',
    'proxy_list': [
        {'host': '1.2.3.4', 'port': 1080, 'proxy_type': 'socks5'}
    ]
})

# Scanner automatically uses proxies
scanner = PortScanner()
results = scanner.scan_nmap(['target.com'], ports='80,443')
```

---

## Troubleshooting

### Proxies Not Working

**Check proxy connectivity**:

```bash
# Test all proxies
ipv9tool test-proxies

# Test specific proxy
curl --proxy socks5://127.0.0.1:9050 https://api.ipify.org
```

**Verify SOCKS5 support**:

```bash
pip install PySocks
python -c "import socks; print('PySocks installed')"
```

### Tor Not Connecting

**Check Tor service**:

```bash
sudo systemctl status tor
sudo systemctl restart tor
```

**Test Tor SOCKS**:

```bash
curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

### Mullvad Not Working

**Verify account**:

```bash
# Test Mullvad SOCKS5
curl --socks5 ACCOUNT_NUMBER@us-nyc.mullvad.net:1080 https://am.i.mullvad.net/json
```

**Check subscription**:
- Login to https://mullvad.net/
- Verify account is active

### IP Not Changing

**Verify rotation**:

```bash
ipv9tool verify-rotation
```

**Check proxy configuration**:

```bash
ipv9tool proxy-stats
```

**Force rotation**:

```python
from ipv9tool.proxy import get_proxy_manager
proxy_mgr = get_proxy_manager()
proxy_mgr.rotate(force=True)
```

---

## Best Practices

### 1. Mix Proxy Types

Combine multiple proxy types:

```
socks5://127.0.0.1:9050 ANON Tor Tor
socks5://ACCOUNT@us-nyc.mullvad.net:1080 US NewYork Mullvad
http://user:pass@commercial.example.com:8080 EU Rotating Commercial
```

### 2. Test Before Operations

Always test proxies before critical operations:

```bash
ipv9tool test-proxies
ipv9tool verify-rotation
```

### 3. Monitor Failures

Watch for proxy failures:

```bash
ipv9tool proxy-stats
```

### 4. Rotate Frequently

For anonymity, rotate frequently:

```yaml
proxy:
  rotation_interval: 30  # Every 30 seconds
```

### 5. Geographic Diversity

Use proxies from multiple countries:

```yaml
proxy:
  mullvad_servers:
    - country: "US"
    - country: "GB"
    - country: "DE"
    - country: "JP"
    - country: "SG"
```

---

## Security Considerations

### 1. Proxy Trust

- **Trusted**: Mullvad, Tor (encrypted, no logging)
- **Commercial**: Bright Data, Oxylabs (commercial services, may log)
- **Free**: Public proxies (NEVER for sensitive operations)

### 2. DNS Leaks

Ensure DNS queries go through proxy:

```yaml
dns:
  use_proxy: true  # Route DNS through proxy
```

### 3. Authentication

Protect proxy credentials:

```bash
chmod 600 /etc/ipv9tool/ipv9tool.yml
chmod 600 config/proxies.txt
```

### 4. Legal Compliance

- Obtain written authorization before scanning
- Respect Terms of Service for proxy providers
- Comply with local laws regarding proxy usage

---

## Performance Impact

| Proxy Type | Latency | Throughput | Anonymity |
|------------|---------|------------|-----------|
| Direct | ~1ms | 100% | None |
| HTTP Proxy | +10-50ms | 80-90% | Low |
| SOCKS5 | +10-50ms | 85-95% | Medium |
| Mullvad | +20-100ms | 70-90% | High |
| Tor | +200-2000ms | 20-50% | Very High |

**Recommendations**:
- **High Speed**: HTTP/SOCKS5 proxies
- **Balance**: Mullvad VPN
- **Maximum Anonymity**: Tor (with patience)

---

## Conclusion

The proxy rotation system provides:

✅ **Operational Security**: Avoid detection and tracking
✅ **Rate Limit Evasion**: Distribute requests across IPs
✅ **Geographic Diversity**: Scan from multiple locations
✅ **Anonymity**: Tor and Mullvad integration
✅ **Reliability**: Automatic failure handling
✅ **Performance**: Latency-based selection
✅ **Flexibility**: Multiple providers and strategies

For more information:
- **Configuration**: `config/ipv9tool.yml`
- **Proxy List**: `config/proxies.txt.example`
- **API Reference**: `docs/API.md`

---

**CLASSIFICATION: UNCLASSIFIED**
**FACILITY: TACTICAL NETWORK OPERATIONS CENTER (TNOC)**
**SYSTEM: IPVNINER NETWORK INTELLIGENCE PLATFORM**

---

**End of Document**
