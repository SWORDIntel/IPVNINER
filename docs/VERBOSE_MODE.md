# Verbose Mode - Detailed Operational Feedback

## Overview

The IPv9 Scanner includes comprehensive verbose mode that provides detailed real-time feedback during all scanning operations. This ensures complete visibility into what the scanner is doing, helping you track progress, diagnose issues, and understand results.

---

## Enabling Verbose Mode

### Configuration File

Edit `/etc/ipv9tool/ipv9tool.yml`:

```yaml
scanner:
  verbose: true
```

### Programmatic

```python
from ipv9tool.config import ConfigManager

config = ConfigManager()
config.update({'scanner': {'verbose': True}})
```

---

## Verbose Output Examples

### 1. DNS Resolution

**Standard Output:**
```
Resolved www.v9.chn to ['1.2.3.4']
```

**Verbose Output:**
```
124530Z ► INF   ► Initiating DNS query: www.v9.chn (type: A)
124530Z ► INF   ► Primary DNS server: 202.170.218.93
124531Z ► INF   ► Primary DNS response: 1 record(s) in 45.2ms
124531Z ► INF     1. 1.2.3.4
124531Z ► INF   ► Verifying with secondary DNS: 61.244.5.162
124531Z ► INF   ► Secondary DNS response: 1 record(s) in 52.8ms
124531Z ► INF   ✓ DNS verification PASSED - Results match
124531Z ► INF   ✓ Resolution COMPLETE: www.v9.chn → ['1.2.3.4']
```

**Detailed Breakdown:**
- **Query initiation**: Shows what domain is being resolved
- **DNS servers**: Displays which servers are being queried
- **Response times**: Measures latency for each query (in milliseconds)
- **Record details**: Lists all returned IP addresses
- **Verification**: Shows secondary DNS check results
- **Completion**: Final summary of resolution

### 2. DNS Verification Mismatch

When primary and secondary DNS servers return different results:

```
124600Z ► INF   ► Initiating DNS query: suspicious.chn (type: A)
124600Z ► INF   ► Primary DNS server: 202.170.218.93
124601Z ► INF   ► Primary DNS response: 1 record(s) in 120.5ms
124601Z ► INF     1. 1.2.3.4
124601Z ► INF   ► Verifying with secondary DNS: 61.244.5.162
124602Z ► INF   ► Secondary DNS response: 1 record(s) in 98.3ms
124602Z ▲ WRN   ▲ DNS VERIFICATION MISMATCH for suspicious.chn:
124602Z ▲ WRN     Primary:   ['1.2.3.4']
124602Z ▲ WRN     Secondary: ['5.6.7.8']
124602Z ▲ WRN   ▲ Using primary DNS results
```

**Security Alert:**
- Shows potential DNS spoofing
- Displays conflicting results
- Indicates which result is being used

### 3. DNS Failures

**Domain Not Found:**
```
124700Z ► INF   ► Initiating DNS query: nonexistent.chn (type: A)
124700Z ► INF   ► Primary DNS server: 202.170.218.93
124701Z ✗ WRN   ✗ Domain NOT FOUND: nonexistent.chn
124701Z ✗ WRN     The domain does not exist in IPv9 DNS
```

**DNS Timeout:**
```
124800Z ► INF   ► Initiating DNS query: timeout.chn (type: A)
124800Z ► INF   ► Primary DNS server: 202.170.218.93
124805Z ✗ ERR   ✗ DNS TIMEOUT for timeout.chn
124805Z ✗ ERR     No response from DNS servers within timeout period
```

**Resolution Error:**
```
124900Z ► INF   ► Initiating DNS query: error.chn (type: A)
124900Z ► INF   ► Primary DNS server: 202.170.218.93
124901Z ✗ ERR   ✗ DNS RESOLUTION ERROR for error.chn
124901Z ✗ ERR     Error type: ConnectionRefusedError
124901Z ✗ ERR     Error message: [Errno 111] Connection refused
```

### 4. Port Scanning (Future Enhancement)

```
125000Z ● OPR   MISSION 1001: PORT SCAN OPERATION
125000Z ► INF   TARGET: 1.2.3.4 | PORTS: 80,443,8080
125000Z ► INF   ► Initializing nmap scan
125000Z ► INF   ► Scan type: SYN scan (requires root)
125000Z ► INF   ► Target: 1.2.3.4
125000Z ► INF   ► Port range: 80,443,8080
125000Z ► INF   ► Starting scan...
125001Z ► INF   ► Scanning port 80/tcp
125002Z ✓ OPS   ► Port 80/tcp: OPEN (http)
125002Z ► INF     Service: Apache httpd 2.4.41
125002Z ► INF   ► Scanning port 443/tcp
125003Z ✓ OPS   ► Port 443/tcp: OPEN (https)
125003Z ► INF     Service: Apache httpd 2.4.41
125003Z ► INF     SSL/TLS: TLSv1.2, TLSv1.3
125003Z ► INF   ► Scanning port 8080/tcp
125004Z ► INF   ► Port 8080/tcp: CLOSED
125004Z ✓ OPS   PORT SCAN: 2 PORTS IDENTIFIED
```

### 5. Domain Enumeration

```
125100Z ● OPR   MISSION 1002: DOMAIN ENUMERATION
125100Z ► INF   PATTERN: 86138NNNNN
125100Z ► INF   ► Generating candidates from pattern
125100Z ► INF   ► Pattern will generate 100,000 domains
125100Z ► INF   ► Maximum results: 100
125100Z ► INF   ► Parallel threads: 10
125100Z ► INF   ► Starting enumeration...
125101Z ► INF   ► Testing: 8613800000.chn
125101Z ► INF   ► Testing: 8613800001.chn
125101Z ► INF   ► Testing: 8613800002.chn
125102Z ✓ OPS   ► FOUND: 8613800001.chn → 1.2.3.4
125103Z ► INF   ► Progress: 50/100,000 (0.05%)
125104Z ✓ OPS   ► FOUND: 8613800042.chn → 5.6.7.8
125105Z ► INF   ► Progress: 100/100,000 (0.10%)
...
125200Z ✓ OPS   ENUMERATION: 15 DOMAINS DISCOVERED
```

### 6. Full Network Audit

```
125300Z ● OPR   MISSION 1003: FULL TACTICAL AUDIT
125300Z ► INF   CLASSIFICATION: OPERATION NETWORK SWEEP
125300Z ► INF   ► Commencing 6-phase tactical audit
125300Z ► INF
125300Z ► INF   ═══ PHASE 1: DNS INFRASTRUCTURE SCAN (0-20%) ═══
125300Z ► INF   ► Testing IPv9 DNS servers
125301Z ► INF   ► Primary DNS: 202.170.218.93 - RESPONSIVE (45ms)
125301Z ► INF   ► Secondary DNS: 61.244.5.162 - RESPONSIVE (52ms)
125302Z ► INF   ► DNS resolution test: PASSED
125302Z ► INF   ► Phase 1 COMPLETE (20%)
125302Z ► INF
125302Z ► INF   ═══ PHASE 2: DOMAIN ENUMERATION (20-40%) ═══
125302Z ► INF   ► Pattern-based enumeration: 86138NNNNN
125303Z ► INF   ► Found 15 valid domains
125310Z ► INF   ► Phase 2 COMPLETE (40%)
125310Z ► INF
125310Z ► INF   ═══ PHASE 3: HOST DISCOVERY (40-60%) ═══
125310Z ► INF   ► ICMP ping sweep
125311Z ► INF   ► Testing 15 hosts
125315Z ► INF   ► 12/15 hosts RESPONSIVE
125315Z ► INF   ► Phase 3 COMPLETE (60%)
125315Z ► INF
125315Z ► INF   ═══ PHASE 4: PORT SCANNING (60-80%) ═══
125315Z ► INF   ► Scanning 12 active hosts
125315Z ► INF   ► Port range: 21,22,23,25,80,443,3389,8080
125320Z ► INF   ► Found 48 open ports
125320Z ► INF   ► Phase 4 COMPLETE (80%)
125320Z ► INF
125320Z ► INF   ═══ PHASE 5: DEEP INSPECTION (80-90%) ═══
125320Z ► INF   ► HTTP/HTTPS probing
125325Z ► INF   ► Service fingerprinting
125330Z ► INF   ► Phase 5 COMPLETE (90%)
125330Z ► INF
125330Z ► INF   ═══ PHASE 6: ANALYSIS & REPORTING (90-100%) ═══
125330Z ► INF   ► Generating statistics
125330Z ► INF   ► Creating security assessment
125335Z ► INF   ► Phase 6 COMPLETE (100%)
125335Z ► INF
125335Z ✓ OPS   TACTICAL AUDIT: COMPLETE
125335Z ► INF   DOMAINS: 15
125335Z ► INF   HOSTS: 12
125335Z ► INF   PORTS: 48
```

### 7. Proxy Rotation

```
125400Z ● OPR   MISSION 1004: DNS RESOLUTION OPERATION (WITH PROXY)
125400Z ► INF   TARGET: www.v9.chn
125400Z ► INF   ► Proxy rotation: ENABLED
125400Z ► INF   ► Rotation strategy: random
125400Z ► INF   ► Current proxy: us-nyc.mullvad.net:1080 (Mullvad)
125400Z ► INF   ► Proxy location: US-NewYork
125400Z ► INF   ► Initiating DNS query: www.v9.chn (type: A)
125400Z ► INF   ► Primary DNS server: 202.170.218.93
125401Z ► INF   ► Primary DNS response: 1 record(s) in 145.2ms
125401Z ► INF     1. 1.2.3.4
125401Z ► INF   ► Proxy overhead: +100ms
125401Z ✓ OPS   ✓ Resolution COMPLETE: www.v9.chn → ['1.2.3.4']
125401Z ► INF   ► External IP verification: 198.51.100.42 (US)
```

---

## Log Symbols

Verbose mode uses tactical symbols for quick visual identification:

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `►` | Action/Step | Indicates a step in the process |
| `✓` | Success | Operation completed successfully |
| `✗` | Failure | Operation failed |
| `▲` | Warning | Caution or potential issue |
| `●` | Operational | Mission/operation start |
| `■` | Secure | Security verification passed |

---

## Log Levels

### OPERATIONAL (OPR)
Mission starts and major operations:
```
125500Z ● OPR   MISSION 1005: DNS RESOLUTION OPERATION
```

### SUCCESS (OPS)
Successful completions:
```
125501Z ✓ OPS   DNS RESOLUTION: SUCCESS
```

### INFO (INF)
Detailed step-by-step information:
```
125502Z ► INF   ► Primary DNS response: 1 record(s) in 45.2ms
```

### WARNING (WRN)
Issues that don't stop operation:
```
125503Z ▲ WRN   ▲ DNS VERIFICATION MISMATCH
```

### ERROR (ERR)
Operation failures:
```
125504Z ✗ ERR   ✗ DNS TIMEOUT
```

### SECURE (SEC)
Security verifications:
```
125505Z ■ SEC   TEMPEST COMPLIANCE: VERIFIED
```

---

## Benefits of Verbose Mode

### 1. Real-Time Progress Tracking
- See exactly what's happening
- Monitor scan progress
- Track enumeration status
- Watch audit phases

### 2. Performance Metrics
- DNS query latency
- Proxy overhead measurement
- Scan speed tracking
- Operation timing

### 3. Troubleshooting
- Identify where failures occur
- See which DNS server failed
- Track proxy issues
- Debug network problems

### 4. Security Monitoring
- DNS verification results
- Proxy location tracking
- IP verification
- Anomaly detection

### 5. Operational Awareness
- Know which servers are being queried
- See which proxies are in use
- Track external IP changes
- Monitor rate limiting

---

## Configuration Tips

### High Verbosity (Recommended for Debugging)

```yaml
scanner:
  verbose: true

logging:
  log_level: "DEBUG"  # Capture everything
```

### Balanced (Recommended for Normal Use)

```yaml
scanner:
  verbose: true

logging:
  log_level: "INFO"  # Skip DEBUG messages
```

### Minimal (Fast Operations)

```yaml
scanner:
  verbose: false

logging:
  log_level: "WARNING"  # Only warnings and errors
```

---

## TUI Integration

In the military TUI, verbose output appears in the **TACTICAL LOG**:

```
╔═══════════════════════════ TACTICAL LOG ══════════════════════════════╗
│ 125600Z ● OPR   MISSION 1006: DNS RESOLUTION OPERATION                │
│ 125600Z ► INF   TARGET: www.v9.chn                                    │
│ 125600Z ► INF   ► Initiating DNS query: www.v9.chn (type: A)         │
│ 125600Z ► INF   ► Primary DNS server: 202.170.218.93                 │
│ 125601Z ► INF   ► Primary DNS response: 1 record(s) in 45.2ms        │
│ 125601Z ► INF     1. 1.2.3.4                                          │
│ 125601Z ► INF   ► Verifying with secondary DNS: 61.244.5.162         │
│ 125601Z ► INF   ► Secondary DNS response: 1 record(s) in 52.8ms      │
│ 125601Z ► INF   ✓ DNS verification PASSED - Results match             │
│ 125601Z ✓ OPS   ✓ Resolution COMPLETE: www.v9.chn → ['1.2.3.4']     │
╚════════════════════════════════════════════════════════════════════════╝
```

**Features:**
- Real-time streaming
- Color-coded by severity
- Tactical formatting with symbols
- Zulu timestamps
- Auto-scrolling

---

## Performance Impact

### With Verbose Mode

- **CPU**: +5-10% (logging overhead)
- **Memory**: +10-20MB (log buffer)
- **Network**: No impact
- **Disk**: More log file growth

### Without Verbose Mode

- **CPU**: Baseline
- **Memory**: Baseline
- **Network**: Baseline
- **Disk**: Minimal log growth

**Recommendation**: Enable verbose mode during:
- Initial testing and debugging
- Troubleshooting issues
- Security audits
- Learning the system

Disable for:
- High-speed bulk scanning
- Resource-constrained environments
- Automated/background operations

---

## Example Session

Full verbose session showing DNS resolution with proxy:

```
125700Z ► INF   IPv9 Resolver initialized with DNS servers: 202.170.218.93, 61.244.5.162
125700Z ► INF   ► Verbose mode: ENABLED
125700Z ► INF   ► DNS verification: ENABLED
125700Z ► INF   ► Timeout: 5s
125700Z ► INF
125700Z ● OPR   MISSION 1007: DNS RESOLUTION OPERATION
125700Z ► INF   TARGET: www.v9.chn
125700Z ► INF
125700Z ► INF   ► Proxy rotation: ENABLED
125700Z ► INF   ► Current proxy: de-fra.mullvad.net:1080 (Mullvad)
125700Z ► INF   ► Proxy location: DE-Frankfurt
125700Z ► INF
125700Z ► INF   ► Initiating DNS query: www.v9.chn (type: A)
125700Z ► INF   ► Primary DNS server: 202.170.218.93
125701Z ► INF   ► Primary DNS response: 1 record(s) in 78.5ms
125701Z ► INF     1. 1.2.3.4
125701Z ► INF
125701Z ► INF   ► Verifying with secondary DNS: 61.244.5.162
125702Z ► INF   ► Secondary DNS response: 1 record(s) in 82.3ms
125702Z ► INF   ✓ DNS verification PASSED - Results match
125702Z ► INF
125702Z ✓ OPS   ✓ Resolution COMPLETE: www.v9.chn → ['1.2.3.4']
125702Z ► INF
125702Z ► INF   ► Verifying external IP
125703Z ► INF   ► External IP: 185.65.134.42 (DE)
125703Z ► INF   ✓ Proxy working - IP matches location
125703Z ► INF
125703Z ✓ OPS   MISSION 1007: COMPLETE
```

---

## Conclusion

Verbose mode provides:

✅ **Complete Visibility**: See every step of the scanning process
✅ **Performance Metrics**: Track latency and timing
✅ **Troubleshooting**: Identify exactly where failures occur
✅ **Security Monitoring**: Track DNS verification and proxy usage
✅ **Operational Awareness**: Know what's happening in real-time
✅ **Professional Output**: Military-grade tactical formatting

Enable verbose mode in `/etc/ipv9tool/ipv9tool.yml` and watch your operations in real-time through the TEMPEST-compliant military TUI!

---

**CLASSIFICATION: UNCLASSIFIED**
**FACILITY: TACTICAL NETWORK OPERATIONS CENTER (TNOC)**
**SYSTEM: IPVNINER NETWORK INTELLIGENCE PLATFORM**

---

**End of Document**
