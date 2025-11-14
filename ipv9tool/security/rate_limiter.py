"""
Rate Limiter for IPv9 Tool

Implements token bucket rate limiting for scanning operations.
"""

import time
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, rate: int, per: float = 1.0, burst: Optional[int] = None):
        """
        Initialize rate limiter

        Args:
            rate: Number of operations allowed per time period
            per: Time period in seconds (default: 1 second)
            burst: Maximum burst size (default: same as rate)
        """
        self.rate = rate
        self.per = per
        self.burst = burst or rate
        self.allowance = float(self.burst)
        self.last_check = time.time()
        self.lock = threading.Lock()

        logger.info(f"Rate limiter initialized: {rate} ops/{per}s (burst={self.burst})")

    def acquire(self, tokens: int = 1, blocking: bool = True) -> bool:
        """
        Acquire tokens from the bucket

        Args:
            tokens: Number of tokens to acquire
            blocking: If True, wait until tokens are available

        Returns:
            True if tokens acquired, False otherwise
        """
        with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            # Add tokens based on time passed
            self.allowance += time_passed * (self.rate / self.per)

            # Cap at burst size
            if self.allowance > self.burst:
                self.allowance = float(self.burst)

            # Check if we have enough tokens
            if self.allowance >= tokens:
                self.allowance -= tokens
                return True

            if not blocking:
                return False

        # Blocking mode: wait for tokens
        wait_time = (tokens - self.allowance) * (self.per / self.rate)
        logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
        time.sleep(wait_time)

        with self.lock:
            self.allowance = 0  # Consumed waiting time
            return True

    def __enter__(self):
        """Context manager entry"""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

    def reset(self):
        """Reset the rate limiter"""
        with self.lock:
            self.allowance = float(self.burst)
            self.last_check = time.time()
        logger.debug("Rate limiter reset")

    def get_status(self) -> dict:
        """Get current rate limiter status"""
        with self.lock:
            return {
                'rate': self.rate,
                'per': self.per,
                'burst': self.burst,
                'current_allowance': self.allowance,
                'available_tokens': int(self.allowance)
            }
