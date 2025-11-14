"""
Configuration Manager

Loads and manages IPv9 tool configuration from YAML files.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .. import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for IPv9 tool"""

    DEFAULT_CONFIG_PATHS = [
        '/etc/ipv9tool/config.yml',
        '/etc/ipv9tool/ipv9tool.yml',
        '~/.config/ipv9tool/config.yml',
        './config/ipv9tool.yml',
        './ipv9tool.yml'
    ]

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config file. If None, searches default paths.
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""

        # If specific path provided, use it
        if self.config_path:
            if os.path.exists(self.config_path):
                return self._read_yaml(self.config_path)
            else:
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return DEFAULT_CONFIG.copy()

        # Search default paths
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                logger.info(f"Loading config from {expanded_path}")
                return self._read_yaml(expanded_path)

        # No config file found, use defaults
        logger.info("No config file found, using defaults")
        return DEFAULT_CONFIG.copy()

    def _read_yaml(self, path: str) -> Dict[str, Any]:
        """Read and parse YAML config file"""
        try:
            with open(path, 'r') as f:
                user_config = yaml.safe_load(f) or {}

            # Merge with defaults (user config overrides defaults)
            config = self._deep_merge(DEFAULT_CONFIG.copy(), user_config)

            logger.info(f"Configuration loaded from {path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config {path}: {e}")
            return DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Failed to read config {path}: {e}")
            return DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge override dict into base dict"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary"""
        return self.config.copy()

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path

        Args:
            key_path: Dot-separated path (e.g., 'dns.primary')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        Set configuration value by dot-separated path

        Args:
            key_path: Dot-separated path (e.g., 'dns.primary')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value
        logger.debug(f"Set config {key_path} = {value}")

    def save(self, output_path: Optional[str] = None):
        """
        Save current configuration to file

        Args:
            output_path: Path to save to. If None, uses original config_path.
        """
        save_path = output_path or self.config_path

        if not save_path:
            logger.error("No save path specified and no original config path")
            return

        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)

            logger.info(f"Configuration saved to {save_path}")

        except Exception as e:
            logger.error(f"Failed to save config to {save_path}: {e}")

    def create_default_config(self, output_path: str):
        """
        Create a default configuration file

        Args:
            output_path: Where to write the default config
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write("# IPv9 Tool Configuration\n")
                f.write("# See documentation for full options\n\n")
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, indent=2)

            logger.info(f"Default configuration created at {output_path}")

        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
