"""
Logging Setup for IPv9 Tool

Configures logging with rotation and audit trails.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]):
    """
    Setup logging configuration

    Args:
        config: Logging configuration dictionary
    """
    log_file = config.get('file', '/var/log/ipv9tool.log')
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_level = config.get('log_level', 'INFO')
    max_size = config.get('max_size', 10485760)  # 10MB
    backup_count = config.get('backup_count', 5)

    # Create log directory if it doesn't exist
    log_dir = Path(log_file).parent
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fall back to user's home directory
        log_file = os.path.expanduser(f'~/.ipv9tool/ipv9tool.log')
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        root_logger.info(f"Logging initialized: {log_file}")

    except PermissionError:
        root_logger.warning(f"Cannot write to {log_file}, logging to console only")


def get_audit_logger(name: str = 'ipv9.audit') -> logging.Logger:
    """
    Get audit logger for security events

    Args:
        name: Logger name

    Returns:
        Logger instance for audit events
    """
    audit_logger = logging.getLogger(name)

    # Create separate audit log file
    audit_file = os.path.expanduser('~/.ipv9tool/audit.log')
    audit_dir = Path(audit_file).parent
    audit_dir.mkdir(parents=True, exist_ok=True)

    # Add rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        audit_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )

    formatter = logging.Formatter(
        '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

    return audit_logger
