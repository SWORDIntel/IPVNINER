"""
CLI Commands for IPv9 Tool

Implements command-line interface for all IPv9 operations.
"""

import sys
import json
import logging
import argparse
from typing import Optional

from ..dns import IPv9Resolver, DNSCache
from ..scanner import PortScanner, HostDiscovery, DNSEnumerator
from ..config import ConfigManager
from ..security import setup_logging, RateLimiter

logger = logging.getLogger(__name__)


class IPv9CLI:
    """Command-line interface for IPv9 tool"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CLI

        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()

        # Setup logging
        setup_logging(self.config.get('logging', {}))

        # Initialize components
        self.resolver = IPv9Resolver(self.config)
        self.cache = DNSCache(
            max_size=self.config['dns']['cache_size'],
            default_ttl=self.config['dns']['ttl']
        )
        self.scanner = PortScanner(self.config)
        self.discovery = HostDiscovery(self.config)
        self.enumerator = DNSEnumerator(self.resolver, self.config)

    def resolve(self, hostname: str, record_type: str = 'A', json_output: bool = False):
        """
        Resolve IPv9 hostname

        Args:
            hostname: Domain name to resolve
            record_type: DNS record type
            json_output: Output as JSON
        """
        # Check cache first
        cached = self.cache.get(hostname, record_type)
        if cached:
            logger.info(f"Using cached result for {hostname}")
            addresses = cached
            from_cache = True
        else:
            addresses = self.resolver.resolve(hostname, record_type)
            if addresses:
                self.cache.set(hostname, addresses, record_type)
            from_cache = False

        result = {
            'hostname': hostname,
            'record_type': record_type,
            'addresses': addresses,
            'from_cache': from_cache
        }

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            if addresses:
                print(f"{hostname} resolves to:")
                for addr in addresses:
                    print(f"  {addr}")
                if from_cache:
                    print("  (from cache)")
            else:
                print(f"{hostname}: No addresses found")

        return result

    def ping(self, target: str, count: int = 4, json_output: bool = False):
        """
        Ping IPv9 host

        Args:
            target: Hostname or IP address
            count: Number of ping packets
            json_output: Output as JSON
        """
        # Resolve if it's a .chn domain
        if self.resolver.is_ipv9_domain(target):
            print(f"Resolving {target}...")
            addresses = self.resolver.resolve(target)
            if not addresses:
                print(f"Failed to resolve {target}")
                return None
            target = addresses[0]
            print(f"Pinging {target}...")

        result = self.discovery.ping(target, count)

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            if result.get('reachable'):
                print(f"{target} is reachable")
                if 'statistics' in result:
                    stats = result['statistics']
                    print(f"  Packets: {stats.get('transmitted', 'N/A')} sent, "
                          f"{stats.get('received', 'N/A')} received")
                    if 'rtt' in stats:
                        rtt = stats['rtt']
                        print(f"  RTT: min={rtt['min']}ms, avg={rtt['avg']}ms, max={rtt['max']}ms")
            else:
                print(f"{target} is not reachable")
                if 'error' in result:
                    print(f"  Error: {result['error']}")

        return result

    def scan(self,
             target: str,
             ports: str = "1-1000",
             scan_type: str = "syn",
             json_output: bool = False):
        """
        Scan IPv9 host

        Args:
            target: Hostname or IP address
            ports: Port range
            scan_type: Scan type (syn, tcp, udp)
            json_output: Output as JSON
        """
        # Resolve if it's a .chn domain
        if self.resolver.is_ipv9_domain(target):
            print(f"Resolving {target}...")
            addresses = self.resolver.resolve(target)
            if not addresses:
                print(f"Failed to resolve {target}")
                return None
            target = addresses[0]
            print(f"Scanning {target}...")

        result = self.scanner.scan_nmap(target, ports, scan_type, service_detection=True)

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            if 'error' in result:
                print(f"Scan failed: {result['error']}")
            else:
                print(f"\nScan results for {target}:")
                print(f"Ports scanned: {result.get('ports_scanned', 'N/A')}")

                if result.get('hosts'):
                    for host in result['hosts']:
                        print(f"\nHost: {host.get('addresses', [{}])[0].get('addr', 'N/A')}")

                        if host.get('ports'):
                            print("Open ports:")
                            for port in host['ports']:
                                port_info = f"  {port['port']}/{port['protocol']} - {port['state']}"
                                if 'service' in port and port['service'].get('name'):
                                    service = port['service']
                                    port_info += f" - {service['name']}"
                                    if service.get('version'):
                                        port_info += f" {service['version']}"
                                print(port_info)
                        else:
                            print("  No open ports found")

                        if host.get('os'):
                            print(f"OS: {host['os']['name']} (accuracy: {host['os']['accuracy']}%)")

        return result

    def http_probe(self, target: str, port: int = 80, https: bool = False, json_output: bool = False):
        """
        HTTP probe of IPv9 host

        Args:
            target: Hostname or IP address
            port: HTTP port
            https: Use HTTPS
            json_output: Output as JSON
        """
        # Resolve if it's a .chn domain
        if self.resolver.is_ipv9_domain(target):
            print(f"Resolving {target}...")
            addresses = self.resolver.resolve(target)
            if not addresses:
                print(f"Failed to resolve {target}")
                return None
            target = addresses[0]

        result = self.discovery.http_probe(target, port, https)

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            if result.get('reachable'):
                print(f"{result['url']} is reachable")
                print(f"  Status: {result.get('status_code', 'N/A')}")
                print(f"  Response time: {result.get('response_time_ms', 'N/A'):.2f}ms")
                if result.get('server'):
                    print(f"  Server: {result['server']}")
            else:
                print(f"{result['url']} is not reachable")
                if 'error' in result:
                    print(f"  Error: {result['error']}")

        return result

    def enumerate(self,
                  pattern: str,
                  tld: str = 'chn',
                  max_combinations: int = 1000,
                  json_output: bool = False):
        """
        Enumerate IPv9 domains

        Args:
            pattern: Pattern to enumerate (e.g., "861381234NNNN")
            tld: Top-level domain
            max_combinations: Maximum combinations
            json_output: Output as JSON
        """
        print(f"Enumerating pattern: {pattern}.{tld}")
        print(f"Max combinations: {max_combinations}")

        results = self.enumerator.brute_force_pattern(pattern, tld, max_combinations)

        if json_output:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nFound {len(results)} hosts:")
            for result in results:
                print(f"  {result['hostname']} -> {', '.join(result['addresses'])}")

        return results

    def cache_stats(self, json_output: bool = False):
        """
        Show DNS cache statistics

        Args:
            json_output: Output as JSON
        """
        stats = self.cache.stats()

        if json_output:
            print(json.dumps(stats, indent=2))
        else:
            print("DNS Cache Statistics:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Valid entries: {stats['valid_entries']}")
            print(f"  Expired entries: {stats['expired_entries']}")
            print(f"  Max size: {stats['max_size']}")
            print(f"  Usage: {stats['total_entries']}/{stats['max_size']} "
                  f"({stats['total_entries']/stats['max_size']*100:.1f}%)")

        return stats


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='IPv9 Scanner - Exploration and Discovery Tool for China\'s Decimal Network',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ipv9tool resolve www.v9.chn
  ipv9tool ping em777.chn
  ipv9tool scan www.hqq.chn --ports 80,443,8080
  ipv9tool http www.v9.chn --port 80
  ipv9tool enumerate "861381234NNNN" --max 100
  ipv9tool cache-stats
        """
    )

    parser.add_argument('--config', '-c',
                        help='Path to configuration file')
    parser.add_argument('--json', '-j',
                        action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Resolve IPv9 hostname')
    resolve_parser.add_argument('hostname', help='Hostname to resolve')
    resolve_parser.add_argument('--type', '-t', default='A',
                                help='DNS record type (default: A)')

    # Ping command
    ping_parser = subparsers.add_parser('ping', help='Ping IPv9 host')
    ping_parser.add_argument('target', help='Hostname or IP to ping')
    ping_parser.add_argument('--count', '-c', type=int, default=4,
                             help='Number of ping packets (default: 4)')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan IPv9 host')
    scan_parser.add_argument('target', help='Hostname or IP to scan')
    scan_parser.add_argument('--ports', '-p', default='1-1000',
                             help='Port range (default: 1-1000)')
    scan_parser.add_argument('--type', '-t', default='syn',
                             choices=['syn', 'tcp', 'udp', 'ack'],
                             help='Scan type (default: syn)')

    # HTTP probe command
    http_parser = subparsers.add_parser('http', help='HTTP probe IPv9 host')
    http_parser.add_argument('target', help='Hostname or IP')
    http_parser.add_argument('--port', '-p', type=int, default=80,
                             help='HTTP port (default: 80)')
    http_parser.add_argument('--https', '-s', action='store_true',
                             help='Use HTTPS')

    # Enumerate command
    enum_parser = subparsers.add_parser('enumerate', help='Enumerate IPv9 domains')
    enum_parser.add_argument('pattern', help='Pattern (e.g., 861381234NNNN)')
    enum_parser.add_argument('--tld', default='chn',
                             help='Top-level domain (default: chn)')
    enum_parser.add_argument('--max', type=int, default=1000,
                             help='Max combinations (default: 1000)')

    # Cache stats command
    subparsers.add_parser('cache-stats', help='Show DNS cache statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = IPv9CLI(args.config)

    # Execute command
    try:
        if args.command == 'resolve':
            cli.resolve(args.hostname, args.type, args.json)
        elif args.command == 'ping':
            cli.ping(args.target, args.count, args.json)
        elif args.command == 'scan':
            cli.scan(args.target, args.ports, args.type, args.json)
        elif args.command == 'http':
            cli.http_probe(args.target, args.port, args.https, args.json)
        elif args.command == 'enumerate':
            cli.enumerate(args.pattern, args.tld, args.max, args.json)
        elif args.command == 'cache-stats':
            cli.cache_stats(args.json)
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=args.verbose)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
