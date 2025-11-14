#!/usr/bin/env python3
"""
Continuous Network Monitoring Example

Demonstrates continuous monitoring of IPv9 network for changes.
"""

import time
from datetime import datetime
from ipv9tool.api.client import IPv9APIClient


def print_change_notification(changes):
    """Print change notifications"""
    print(f"\n{'='*60}")
    print(f"CHANGE DETECTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)

    for change in changes:
        change_type = change['type']
        count = change['count']

        if change_type == 'new_hosts':
            print(f"\n🆕 {count} New Host(s) Discovered:")
            for host in change['hosts'][:5]:  # Show first 5
                print(f"   - {host.get('host', 'Unknown')}")

        elif change_type == 'new_ports':
            print(f"\n🔓 {count} New Open Port(s) Found:")
            for port in change['ports'][:5]:
                print(f"   - {port.get('host', 'Unknown')}:{port.get('port', '?')}")

        elif change_type == 'new_domains':
            print(f"\n🌐 {count} New Domain(s) Discovered:")
            for domain in change['domains'][:5]:
                print(f"   - {domain.get('hostname', 'Unknown')}")

    print('='*60 + '\n')


def main():
    client = IPv9APIClient("http://localhost:8000")

    print("=== IPv9 Continuous Monitoring ===\n")

    # Get initial statistics
    print("Initial Network State:")
    stats = client.get_stats()
    print(f"  Domains: {stats.total_domains}")
    print(f"  IPs: {stats.total_ips}")
    print(f"  Active Hosts: {stats.active_hosts}")
    print()

    # Start continuous audit
    print("Starting continuous monitoring...")
    job = client.start_audit(
        scan_dns=True,
        scan_web=True,
        scan_all_ports=False,
        deep_scan=False,
        continuous=True  # Enable continuous mode
    )

    print(f"Monitor Job ID: {job.job_id}")
    print("Monitoring for changes... (Press Ctrl+C to stop)\n")

    try:
        iteration = 0

        while True:
            # Get current job status
            status = client.get_job(job.job_id)

            if status.status == 'failed':
                print(f"Monitoring failed: {status.error}")
                break

            # Get updated statistics
            new_stats = client.get_stats()

            # Check for significant changes
            if (new_stats.total_domains != stats.total_domains or
                new_stats.total_ips != stats.total_ips or
                new_stats.active_hosts != stats.active_hosts):

                changes = []

                if new_stats.total_domains > stats.total_domains:
                    diff = new_stats.total_domains - stats.total_domains
                    changes.append({
                        'type': 'new_domains',
                        'count': diff,
                        'domains': []
                    })

                if new_stats.active_hosts > stats.active_hosts:
                    diff = new_stats.active_hosts - stats.active_hosts
                    changes.append({
                        'type': 'new_hosts',
                        'count': diff,
                        'hosts': []
                    })

                if changes:
                    print_change_notification(changes)

                stats = new_stats

            # Print periodic status
            iteration += 1
            if iteration % 12 == 0:  # Every 12 iterations (~ 1 hour at 5 min intervals)
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status Update:")
                print(f"  Domains: {stats.total_domains}")
                print(f"  Active Hosts: {stats.active_hosts}")
                print(f"  Responsive Web: {stats.responsive_web}")
                print()

            # Wait before next check (5 minutes)
            time.sleep(300)

    except KeyboardInterrupt:
        print("\n\nStopping continuous monitoring...")
        print("Final statistics:")
        final_stats = client.get_stats()
        print(f"  Total Domains: {final_stats.total_domains}")
        print(f"  Total IPs: {final_stats.total_ips}")
        print(f"  Active Hosts: {final_stats.active_hosts}")


if __name__ == "__main__":
    main()
