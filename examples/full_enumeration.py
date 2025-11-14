#!/usr/bin/env python3
"""
Full IPv9 Network Enumeration Example

Demonstrates comprehensive domain enumeration.
"""

import time
from ipv9tool.api.client import IPv9APIClient


def main():
    client = IPv9APIClient("http://localhost:8000")

    print("=== IPv9 Network Enumeration ===\n")

    # Example 1: Pattern-based enumeration
    print("1. Pattern-Based Enumeration")
    print("   Enumerating: 861381234NNNN (10,000 combinations)")

    result = client.enumerate_pattern(
        pattern="861381234NNNN",
        max_combinations=10000
    )

    print(f"   Checked: {result.total_checked} domains")
    print(f"   Found: {result.total_found} domains")
    print(f"   Duration: {result.duration:.2f}s\n")

    if result.domains:
        print("   First 10 discovered domains:")
        for domain in result.domains[:10]:
            print(f"     {domain.hostname} -> {', '.join(domain.addresses)}")
    print()

    # Example 2: Full network enumeration (background job)
    print("2. Full Network Enumeration (Background Job)")
    job = client.enumerate_full()
    print(f"   Job ID: {job.job_id}")
    print(f"   Status: {job.status}\n")

    print("   Waiting for completion...")

    # Poll job status
    while True:
        status = client.get_job(job.job_id)

        print(f"   Progress: {status.progress:.1f}% ({status.status})", end='\r')

        if status.status in ['completed', 'failed']:
            print()
            break

        time.sleep(5)

    if status.status == 'completed':
        print(f"\n   Enumeration completed!")
        print(f"   Total found: {status.result.get('total_found', 0)} domains")

        # Export results
        import json
        with open('enumeration_results.json', 'w') as f:
            json.dump(status.result, f, indent=2, default=str)
        print(f"   Results exported to: enumeration_results.json")
    else:
        print(f"\n   Enumeration failed: {status.error}")


if __name__ == "__main__":
    main()
