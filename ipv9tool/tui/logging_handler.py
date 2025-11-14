#!/usr/bin/env python3
"""
TUI Logging Handler

Custom logging handler that captures log messages and forwards them
to the TUI military log widget for real-time display.
"""

import logging
from typing import Optional, Callable


class TUILogHandler(logging.Handler):
    """
    Logging handler that forwards log messages to TUI

    Captures log messages from all modules and displays them in the
    tactical log widget with appropriate severity levels.
    """

    def __init__(self, log_callback: Callable[[str, str], None]):
        """
        Initialize TUI log handler

        Args:
            log_callback: Function to call with (message, level) for each log entry
        """
        super().__init__()
        self.log_callback = log_callback

        # Set format
        formatter = logging.Formatter('%(message)s')
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to the TUI

        Args:
            record: Log record to emit
        """
        try:
            # Map Python logging levels to TUI levels
            level_map = {
                logging.DEBUG: "DEBUG",
                logging.INFO: "INFO",
                logging.WARNING: "WARNING",
                logging.ERROR: "ERROR",
                logging.CRITICAL: "CRITICAL"
            }

            # Get TUI level
            tui_level = level_map.get(record.levelno, "INFO")

            # Format message
            message = self.format(record)

            # Send to TUI callback
            if self.log_callback:
                self.log_callback(message, tui_level)

        except Exception:
            self.handleError(record)


def setup_tui_logging(log_callback: Callable[[str, str], None],
                      level: int = logging.INFO) -> TUILogHandler:
    """
    Setup TUI logging handler

    Args:
        log_callback: Function to call with (message, level) for each log entry
        level: Minimum logging level

    Returns:
        TUILogHandler instance
    """
    # Create handler
    handler = TUILogHandler(log_callback)
    handler.setLevel(level)

    # Get root logger
    root_logger = logging.getLogger()

    # Remove existing handlers for ipv9tool modules
    ipv9_logger = logging.getLogger('ipv9tool')
    ipv9_logger.handlers.clear()

    # Add TUI handler to ipv9tool logger
    ipv9_logger.addHandler(handler)
    ipv9_logger.setLevel(level)

    # Ensure propagation is enabled
    ipv9_logger.propagate = False

    return handler
