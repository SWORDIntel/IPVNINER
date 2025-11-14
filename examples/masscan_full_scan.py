#!/usr/bin/env python3
"""
Masscan Full Network Scan Example

Demonstrates high-speed full network enumeration using masscan.
"""

from ipv9tool.audit import MasscanEnumerator


def main():
    print("=== Masscan Full IPv9 Network Scan ===\n")

    # Initialize masscan enumerator
    enumerator = MasscanEnumerator(rate=10000)  # 10,000 packets per second

    # Create enumeration plan
    print("Creating enumeration plan...")
    plan = enumerator.create_enumeration_plan(
        total_budget_hours=24,  # 24 hour scan budget
        ports="80,443,8080,22,21,25,53"
    )

    print(f"\nEnumeration Plan:")
    print(f"  Budget: {plan['budget_hours']} hours")
    print(f"  Rate: {plan['rate_pps']:,} packets/second")
    print(f"  Ports: {plan['ports']}")
    print(f"  Total IPs Scannable: {plan['total_ips_scannable']:,}")
    print(f"  Coverage: {plan['coverage_percent']:.4f}% of IPv4 space")
    print(f"  Recommended Approach: {plan['recommended_approach']}")
    print()

    # Example: Enumerate IPv9 address space (sample)
    print("Starting IPv9 address space enumeration (10% sample)...")

    results = enumerator.enumerate_ipv9_space(
        sample_rate=0.10,  # Sample 10% of address space
        ports="80,443,8080"
    )

    print(f"\nScan Results:")
    print(f"  Total Hosts Found: {results.get('total_hosts', 0)}")
    print(f"  Total Open Ports: {results.get('total_ports', 0)}")

    if results.get('hosts'):
        print(f"\nFirst 10 discovered hosts:")
        for host in results['hosts'][:10]:
            print(f"  {host['ip']}:")
            for port in host['ports']:
                print(f"    - Port {port['port']}/{port['proto']}: {port['status']}")

    # Export results
    if results.get('hosts'):
        import json
        with open('masscan_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults exported to: masscan_results.json")


if __name__ == "__main__":
    main()
