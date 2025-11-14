#!/usr/bin/env python3
"""
Basic IPv9 API Usage Examples

Demonstrates basic operations using the IPv9 Scanner API.
"""

from ipv9tool.api.client import IPv9APIClient


def main():
    # Initialize API client
    client = IPv9APIClient("http://localhost:8000")

    # Check API health
    print("=== Checking API Health ===")
    health = client.health()
    print(f"API Status: {health.status}")
    print(f"DNS Servers Reachable: {health.dns_servers_reachable}")
    print(f"Database Connected: {health.database_connected}")
    print()

    # DNS Resolution
    print("=== DNS Resolution ===")
    domains = ["www.v9.chn", "em777.chn", "www.hqq.chn"]

    for domain in domains:
        result = client.resolve(domain)
        print(f"{domain}:")
        if result.addresses:
            for addr in result.addresses:
                print(f"  -> {addr}")
            print(f"  (from cache: {result.from_cache})")
        else:
            print("  -> Not found")
    print()

    # Ping Test
    print("=== Ping Test ===")
    target = "www.v9.chn"
    ping_result = client.ping(target, count=4)

    if ping_result.reachable:
        print(f"{target} is reachable")
        print(f"  Packets: {ping_result.packets_received}/{ping_result.packets_sent}")
        if ping_result.rtt_avg:
            print(f"  RTT: min={ping_result.rtt_min}ms, avg={ping_result.rtt_avg}ms, max={ping_result.rtt_max}ms")
    else:
        print(f"{target} is not reachable")
    print()

    # Port Scan
    print("=== Port Scan ===")
    scan_result = client.scan(target, ports="80,443,8080,22")

    for host in scan_result.hosts:
        print(f"Host: {host.address}")
        if host.hostname:
            print(f"  Hostname: {host.hostname}")

        print("  Open Ports:")
        for port in host.ports:
            if port.state == "open":
                service_info = f"{port.service}" if port.service else "unknown"
                if port.version:
                    service_info += f" {port.version}"
                print(f"    {port.port}/{port.protocol}: {service_info}")

        if host.os:
            print(f"  OS: {host.os} (accuracy: {host.os_accuracy}%)")
    print()

    # Get Statistics
    print("=== Network Statistics ===")
    stats = client.get_stats()
    print(f"Total Domains: {stats.total_domains}")
    print(f"Total IPs: {stats.total_ips}")
    print(f"Active Hosts: {stats.active_hosts}")
    print(f"Responsive Web: {stats.responsive_web}")
    if stats.last_scan:
        print(f"Last Scan: {stats.last_scan}")


if __name__ == "__main__":
    main()
