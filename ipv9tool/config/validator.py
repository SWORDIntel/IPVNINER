"""
Configuration Validator

Validates IPv9 tool configuration for correctness and security.
"""

import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration settings"""

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IPv4 address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False

        # Check each octet is 0-255
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)

    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return isinstance(port, int) and 1 <= port <= 65535

    @staticmethod
    def validate_rate_limit(rate: int) -> bool:
        """Validate rate limit value"""
        return isinstance(rate, int) and rate > 0 and rate <= 10000

    @staticmethod
    def validate_timeout(timeout: int) -> bool:
        """Validate timeout value"""
        return isinstance(timeout, int) and timeout > 0 and timeout <= 300

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate DNS settings
        if 'dns' in config:
            dns_config = config['dns']

            # Validate DNS server IPs
            for key in ['primary', 'secondary']:
                if key in dns_config:
                    if not self.validate_ip_address(dns_config[key]):
                        errors.append(f"Invalid DNS {key} IP address: {dns_config[key]}")

            # Validate cache size
            if 'cache_size' in dns_config:
                if not isinstance(dns_config['cache_size'], int) or dns_config['cache_size'] < 0:
                    errors.append(f"Invalid cache_size: {dns_config['cache_size']}")

            # Validate TTL
            if 'ttl' in dns_config:
                if not isinstance(dns_config['ttl'], int) or dns_config['ttl'] < 0:
                    errors.append(f"Invalid TTL: {dns_config['ttl']}")

        # Validate scanner settings
        if 'scanner' in config:
            scanner_config = config['scanner']

            # Validate rate limit
            if 'rate_limit' in scanner_config:
                if not self.validate_rate_limit(scanner_config['rate_limit']):
                    errors.append(f"Invalid rate_limit: {scanner_config['rate_limit']}")

            # Validate timeout
            if 'timeout' in scanner_config:
                if not self.validate_timeout(scanner_config['timeout']):
                    errors.append(f"Invalid timeout: {scanner_config['timeout']}")

            # Validate retries
            if 'retries' in scanner_config:
                if not isinstance(scanner_config['retries'], int) or scanner_config['retries'] < 0:
                    errors.append(f"Invalid retries: {scanner_config['retries']}")

            # Validate max_threads
            if 'max_threads' in scanner_config:
                threads = scanner_config['max_threads']
                if not isinstance(threads, int) or threads < 1 or threads > 100:
                    errors.append(f"Invalid max_threads (must be 1-100): {threads}")

        # Validate logging settings
        if 'logging' in config:
            log_config = config['logging']

            # Validate log level
            if 'log_level' in log_config:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if log_config['log_level'] not in valid_levels:
                    errors.append(f"Invalid log_level: {log_config['log_level']}")

        # Log validation results
        if errors:
            for error in errors:
                logger.error(f"Config validation error: {error}")
            return False, errors
        else:
            logger.info("Configuration validation passed")
            return True, []
