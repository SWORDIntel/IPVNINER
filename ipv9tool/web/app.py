"""
Flask Web Dashboard for IPv9 Tool

Optional web interface for monitoring and managing IPv9 scans.
"""

import os
import json
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from ..dns import IPv9Resolver, DNSCache
from ..scanner import PortScanner, HostDiscovery, DNSEnumerator
from ..config import ConfigManager

logger = logging.getLogger(__name__)


def create_app(config_path=None):
    """
    Create and configure Flask application

    Args:
        config_path: Path to configuration file

    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    CORS(app)

    # Load configuration
    config_manager = ConfigManager(config_path)
    config = config_manager.get_config()

    # Initialize components
    resolver = IPv9Resolver(config)
    cache = DNSCache(
        max_size=config['dns']['cache_size'],
        default_ttl=config['dns']['ttl']
    )
    scanner = PortScanner(config)
    discovery = HostDiscovery(config)
    enumerator = DNSEnumerator(resolver, config)

    # Store in app context
    app.config['IPV9_RESOLVER'] = resolver
    app.config['IPV9_CACHE'] = cache
    app.config['IPV9_SCANNER'] = scanner
    app.config['IPV9_DISCOVERY'] = discovery
    app.config['IPV9_ENUMERATOR'] = enumerator
    app.config['IPV9_CONFIG'] = config

    # Routes
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('index.html', config=config)

    @app.route('/api/resolve', methods=['POST'])
    def api_resolve():
        """Resolve DNS hostname"""
        data = request.json
        hostname = data.get('hostname')

        if not hostname:
            return jsonify({'error': 'hostname required'}), 400

        try:
            # Check cache
            cached = cache.get(hostname)
            if cached:
                return jsonify({
                    'hostname': hostname,
                    'addresses': cached,
                    'from_cache': True
                })

            # Resolve
            addresses = resolver.resolve(hostname)

            if addresses:
                cache.set(hostname, addresses)

            return jsonify({
                'hostname': hostname,
                'addresses': addresses,
                'from_cache': False
            })

        except Exception as e:
            logger.error(f"Resolve error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ping', methods=['POST'])
    def api_ping():
        """Ping host"""
        data = request.json
        target = data.get('target')
        count = data.get('count', 4)

        if not target:
            return jsonify({'error': 'target required'}), 400

        try:
            # Resolve if IPv9 domain
            if resolver.is_ipv9_domain(target):
                addresses = resolver.resolve(target)
                if not addresses:
                    return jsonify({'error': 'failed to resolve'}), 400
                target = addresses[0]

            # Ping
            result = discovery.ping(target, count)
            return jsonify(result)

        except Exception as e:
            logger.error(f"Ping error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scan', methods=['POST'])
    def api_scan():
        """Scan ports"""
        data = request.json
        target = data.get('target')
        ports = data.get('ports', '1-1000')
        scan_type = data.get('type', 'syn')

        if not target:
            return jsonify({'error': 'target required'}), 400

        try:
            # Resolve if IPv9 domain
            if resolver.is_ipv9_domain(target):
                addresses = resolver.resolve(target)
                if not addresses:
                    return jsonify({'error': 'failed to resolve'}), 400
                target = addresses[0]

            # Scan
            result = scanner.scan_nmap(target, ports, scan_type, service_detection=True)
            return jsonify(result)

        except Exception as e:
            logger.error(f"Scan error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/http-probe', methods=['POST'])
    def api_http_probe():
        """HTTP probe"""
        data = request.json
        target = data.get('target')
        port = data.get('port', 80)
        use_https = data.get('https', False)

        if not target:
            return jsonify({'error': 'target required'}), 400

        try:
            # Resolve if IPv9 domain
            if resolver.is_ipv9_domain(target):
                addresses = resolver.resolve(target)
                if not addresses:
                    return jsonify({'error': 'failed to resolve'}), 400
                target = addresses[0]

            # Probe
            result = discovery.http_probe(target, port, use_https)
            return jsonify(result)

        except Exception as e:
            logger.error(f"HTTP probe error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/enumerate', methods=['POST'])
    def api_enumerate():
        """Enumerate domains"""
        data = request.json
        pattern = data.get('pattern')
        tld = data.get('tld', 'chn')
        max_combinations = data.get('max', 1000)

        if not pattern:
            return jsonify({'error': 'pattern required'}), 400

        try:
            results = enumerator.brute_force_pattern(pattern, tld, max_combinations)
            return jsonify({'results': results})

        except Exception as e:
            logger.error(f"Enumerate error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cache/stats', methods=['GET'])
    def api_cache_stats():
        """Get cache statistics"""
        try:
            stats = cache.stats()
            return jsonify(stats)

        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cache/clear', methods=['POST'])
    def api_cache_clear():
        """Clear cache"""
        try:
            cache.clear()
            return jsonify({'status': 'cache cleared'})

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/config', methods=['GET'])
    def api_config():
        """Get configuration (sanitized)"""
        try:
            # Return sanitized config (no sensitive data)
            sanitized = {
                'dns': {
                    'primary': config['dns']['primary'],
                    'secondary': config['dns']['secondary'],
                    'cache_size': config['dns']['cache_size']
                },
                'scanner': config['scanner'],
                'security': {
                    'verify_dns': config['security']['verify_dns'],
                    'log_level': config['security']['log_level']
                }
            }
            return jsonify(sanitized)

        except Exception as e:
            logger.error(f"Config error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0'
        })

    return app


def main():
    """Run development server"""
    import argparse

    parser = argparse.ArgumentParser(description='IPv9 Web Dashboard')
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    # Create app
    app = create_app(args.config)

    # Run server
    print(f"Starting IPv9 Web Dashboard on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
