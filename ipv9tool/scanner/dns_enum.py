"""
DNS Enumeration Module

Enumerates IPv9 .chn domains and numeric hostnames.
"""

import logging
import itertools
from typing import List, Dict, Any, Optional, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class DNSEnumerator:
    """DNS enumeration for IPv9 decimal network"""

    # Chinese mobile phone prefixes (common ones)
    MOBILE_PREFIXES = [
        '130', '131', '132', '133', '134', '135', '136', '137', '138', '139',  # China Telecom
        '145', '147', '148', '149',
        '150', '151', '152', '153', '155', '156', '157', '158', '159',  # China Mobile
        '162', '165', '166', '167',
        '170', '171', '172', '173', '174', '175', '176', '177', '178',
        '180', '181', '182', '183', '184', '185', '186', '187', '188', '189',  # China Unicom
        '190', '191', '192', '193', '195', '196', '197', '198', '199'
    ]

    def __init__(self, resolver, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DNS enumerator

        Args:
            resolver: IPv9Resolver instance
            config: Configuration dictionary
        """
        from ..config import ConfigManager

        self.resolver = resolver
        self.config = config or ConfigManager().get_config()
        self.scanner_config = self.config.get('scanner', {})
        self.max_threads = self.scanner_config.get('max_threads', 10)

    def enumerate_numeric_range(self,
                                 prefix: str,
                                 start: int = 0,
                                 end: int = 9999,
                                 tld: str = 'chn') -> List[Dict[str, Any]]:
        """
        Enumerate numeric domain range

        Args:
            prefix: Numeric prefix (e.g., '861381234' for phone number)
            start: Starting number
            end: Ending number
            tld: Top-level domain (default: 'chn')

        Returns:
            List of found domains with their IP addresses
        """
        logger.info(f"Enumerating {prefix}[{start}-{end}].{tld}")

        results = []

        for num in range(start, end + 1):
            hostname = f"{prefix}{num}.{tld}"

            # Resolve the hostname
            addresses = self.resolver.resolve(hostname)

            if addresses:
                results.append({
                    'hostname': hostname,
                    'addresses': addresses,
                    'prefix': prefix,
                    'number': num
                })
                logger.info(f"Found: {hostname} -> {addresses}")

        logger.info(f"Enumeration complete: found {len(results)} hosts")
        return results

    def enumerate_phone_numbers(self,
                                 area_code: str,
                                 exchange: str,
                                 start: int = 0,
                                 end: int = 9999,
                                 tld: str = 'chn') -> List[Dict[str, Any]]:
        """
        Enumerate phone number-based domains

        Chinese phone numbers: +86 (country) + area/prefix (3 digits) + number (8 digits)

        Args:
            area_code: Area code or mobile prefix (e.g., '138', '021')
            exchange: Exchange or next digits (e.g., '1234')
            start: Starting number (last 4 digits)
            end: Ending number
            tld: Top-level domain

        Returns:
            List of found domains
        """
        # Build phone number prefix: 86 + area_code + exchange
        prefix = f"86{area_code}{exchange}"

        logger.info(f"Enumerating phone numbers: +86-{area_code}-{exchange}-[{start:04d}-{end:04d}]")

        return self.enumerate_numeric_range(prefix, start, end, tld)

    def enumerate_common_mobile_prefixes(self,
                                         exchange: str,
                                         count: int = 100,
                                         tld: str = 'chn') -> List[Dict[str, Any]]:
        """
        Enumerate common Chinese mobile phone prefixes

        Args:
            exchange: Middle digits of phone number
            count: How many numbers to try per prefix
            tld: Top-level domain

        Returns:
            List of found domains
        """
        logger.info(f"Enumerating {len(self.MOBILE_PREFIXES)} mobile prefixes")

        all_results = []

        for prefix in self.MOBILE_PREFIXES:
            logger.debug(f"Trying prefix {prefix}")

            results = self.enumerate_phone_numbers(
                area_code=prefix,
                exchange=exchange,
                start=0,
                end=min(count - 1, 9999),
                tld=tld
            )

            all_results.extend(results)

        logger.info(f"Mobile enumeration complete: found {len(all_results)} hosts")
        return all_results

    def enumerate_wordlist(self,
                           wordlist: List[str],
                           tld: str = 'chn',
                           parallel: bool = True) -> List[Dict[str, Any]]:
        """
        Enumerate domains from wordlist

        Args:
            wordlist: List of numeric strings to try
            tld: Top-level domain
            parallel: Use parallel resolution

        Returns:
            List of found domains
        """
        logger.info(f"Enumerating {len(wordlist)} domains from wordlist")

        if parallel and len(wordlist) > 10:
            return self._enumerate_parallel(wordlist, tld)
        else:
            return self._enumerate_sequential(wordlist, tld)

    def _enumerate_sequential(self, wordlist: List[str], tld: str) -> List[Dict[str, Any]]:
        """Sequential enumeration"""
        results = []

        for word in wordlist:
            hostname = f"{word}.{tld}"
            addresses = self.resolver.resolve(hostname)

            if addresses:
                results.append({
                    'hostname': hostname,
                    'addresses': addresses
                })
                logger.info(f"Found: {hostname} -> {addresses}")

        return results

    def _enumerate_parallel(self, wordlist: List[str], tld: str) -> List[Dict[str, Any]]:
        """Parallel enumeration using thread pool"""
        results = []

        def resolve_word(word):
            hostname = f"{word}.{tld}"
            addresses = self.resolver.resolve(hostname)
            if addresses:
                return {
                    'hostname': hostname,
                    'addresses': addresses
                }
            return None

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_word = {executor.submit(resolve_word, word): word for word in wordlist}

            for future in as_completed(future_to_word):
                result = future.result()
                if result:
                    results.append(result)
                    logger.info(f"Found: {result['hostname']} -> {result['addresses']}")

        return results

    def generate_numeric_wordlist(self,
                                   length: int = 11,
                                   prefix: str = '86',
                                   count: int = 1000) -> List[str]:
        """
        Generate numeric wordlist for enumeration

        Args:
            length: Total length of numeric string
            prefix: Prefix to use (e.g., '86' for China)
            count: Maximum number of entries to generate

        Returns:
            List of numeric strings
        """
        import random

        wordlist = []
        remaining_length = length - len(prefix)

        for _ in range(count):
            # Generate random number of appropriate length
            number = ''.join(str(random.randint(0, 9)) for _ in range(remaining_length))
            wordlist.append(f"{prefix}{number}")

        return wordlist

    def brute_force_pattern(self,
                            pattern: str,
                            tld: str = 'chn',
                            max_combinations: int = 1000) -> List[Dict[str, Any]]:
        """
        Brute force with pattern

        Pattern uses:
        - N for numeric digit (0-9)
        - X for any digit
        - Fixed digits remain

        Example: "861381234NNNN" will try 861381234[0000-9999]

        Args:
            pattern: Pattern string
            tld: Top-level domain
            max_combinations: Maximum combinations to try

        Returns:
            List of found domains
        """
        logger.info(f"Brute forcing pattern: {pattern}")

        # Parse pattern and generate combinations
        combinations = self._generate_pattern_combinations(pattern, max_combinations)

        logger.info(f"Generated {len(combinations)} combinations")

        return self.enumerate_wordlist(combinations, tld, parallel=True)

    def _generate_pattern_combinations(self, pattern: str, max_count: int) -> List[str]:
        """Generate combinations from pattern"""
        # Find positions of N/X in pattern
        variable_positions = [i for i, c in enumerate(pattern) if c in 'NX']

        if not variable_positions:
            return [pattern]

        # Generate combinations
        combinations = []
        pattern_list = list(pattern)

        # Calculate total possible combinations
        total_combinations = 10 ** len(variable_positions)
        actual_count = min(total_combinations, max_count)

        if total_combinations <= max_count:
            # Generate all combinations
            for combo in itertools.product('0123456789', repeat=len(variable_positions)):
                pattern_copy = pattern_list.copy()
                for pos, digit in zip(variable_positions, combo):
                    pattern_copy[pos] = digit
                combinations.append(''.join(pattern_copy))
        else:
            # Random sampling
            import random
            for _ in range(actual_count):
                pattern_copy = pattern_list.copy()
                for pos in variable_positions:
                    pattern_copy[pos] = str(random.randint(0, 9))
                combination = ''.join(pattern_copy)
                if combination not in combinations:
                    combinations.append(combination)

        return combinations

    def zone_transfer_attempt(self, domain: str = 'chn') -> Optional[List[str]]:
        """
        Attempt DNS zone transfer (AXFR)

        Args:
            domain: Domain to attempt transfer on

        Returns:
            List of records if successful, None otherwise
        """
        import dns.zone
        import dns.query

        logger.info(f"Attempting zone transfer for {domain}")

        try:
            # Try both IPv9 DNS servers
            for server in [self.resolver.primary_dns, self.resolver.secondary_dns]:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(server, domain, timeout=10))

                    records = []
                    for name, node in zone.nodes.items():
                        records.append(str(name))

                    logger.info(f"Zone transfer successful from {server}: {len(records)} records")
                    return records

                except Exception as e:
                    logger.debug(f"Zone transfer failed from {server}: {e}")
                    continue

            logger.warning("Zone transfer not allowed")
            return None

        except Exception as e:
            logger.error(f"Zone transfer attempt failed: {e}")
            return None
