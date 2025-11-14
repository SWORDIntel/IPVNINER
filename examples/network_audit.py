#!/usr/bin/env python3
"""
Comprehensive Network Audit Example

Demonstrates full IPv9 network auditing capabilities.
"""

import time
from ipv9tool.api.client import IPv9APIClient
from ipv9tool.export import DataExporter


def main():
    client = IPv9APIClient("http://localhost:8000")

    print("=== IPv9 Comprehensive Network Audit ===\n")

    # Start comprehensive audit
    print("Starting network audit...")
    job = client.start_audit(
        scan_dns=True,
        scan_web=True,
        scan_all_ports=False,  # Set to True for full port scan
        deep_scan=True,
        continuous=False
    )

    print(f"Audit ID: {job.job_id}")
    print(f"Status: {job.status}\n")

    # Monitor progress
    print("Monitoring audit progress...\n")

    last_progress = 0

    while True:
        status = client.get_job(job.job_id)

        if status.progress != last_progress:
            print(f"Progress: {status.progress:.1f}% - {status.status}")
            last_progress = status.progress

        if status.status in ['completed', 'failed']:
            break

        time.sleep(5)

    print()

    if status.status == 'completed':
        print("Audit completed successfully!\n")

        results = status.result

        # Display statistics
        print("=== Audit Results ===\n")

        if 'statistics' in results:
            stats = results['statistics']
            print("Network Statistics:")
            print(f"  Total Domains: {stats.get('total_domains', 0)}")
            print(f"  Total IPs: {stats.get('total_ips', 0)}")
            print(f"  Active Hosts: {stats.get('active_hosts', 0)}")
            print(f"  Total Ports: {stats.get('total_ports', 0)}")
            print(f"  Responsive Web: {stats.get('responsive_web', 0)}")
            print()

        if 'findings_summary' in results:
            summary = results['findings_summary']
            print(f"Total Findings: {summary.get('total', 0)}")

            if 'by_type' in summary:
                print("\nFindings by Type:")
                for finding_type, count in summary['by_type'].items():
                    print(f"  {finding_type}: {count}")
            print()

        if 'security_score' in results:
            print(f"Security Score: {results['security_score']}/100\n")

        if 'recommendations' in results and results['recommendations']:
            print("Recommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
            print()

        # Export results
        print("Exporting results...")
        exporter = DataExporter()

        # Export to multiple formats
        timestamp = time.strftime('%Y%m%d_%H%M%S')

        # JSON
        exporter.to_json(results, f'audit_results_{timestamp}.json')
        print(f"  ✓ JSON: audit_results_{timestamp}.json")

        # HTML Report
        exporter.to_html(results, f'audit_report_{timestamp}.html', title="IPv9 Network Audit Report")
        print(f"  ✓ HTML: audit_report_{timestamp}.html")

        # Markdown
        exporter.to_markdown(results, f'audit_report_{timestamp}.md', title="IPv9 Network Audit Report")
        print(f"  ✓ Markdown: audit_report_{timestamp}.md")

        # CSV (if hosts data available)
        if 'hosts' in results and results['hosts']:
            exporter.to_csv(results['hosts'], f'audit_hosts_{timestamp}.csv')
            print(f"  ✓ CSV: audit_hosts_{timestamp}.csv")

        print("\nAudit complete! Reports saved.")

    else:
        print(f"Audit failed: {status.error}")


if __name__ == "__main__":
    main()
