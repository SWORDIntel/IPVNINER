"""
Sandbox Module for IPv9 Tool

Provides isolation and security controls for scanning operations.
"""

import os
import logging
import subprocess
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class Sandbox:
    """Sandbox for isolating scanning operations"""

    def __init__(self, enable: bool = True):
        """
        Initialize sandbox

        Args:
            enable: Enable sandboxing
        """
        self.enabled = enable
        self.original_uid = os.getuid() if hasattr(os, 'getuid') else None

        if self.enabled:
            logger.info("Sandbox enabled")
        else:
            logger.warning("Sandbox disabled - operations will run with full privileges")

    def drop_privileges(self, user: str = 'nobody', group: str = 'nogroup'):
        """
        Drop privileges to specified user/group

        Args:
            user: Username to drop to
            group: Group name to drop to

        Warning: This is a one-way operation and cannot be reversed
        """
        if not self.enabled:
            logger.warning("Sandbox disabled, not dropping privileges")
            return

        if not hasattr(os, 'setuid'):
            logger.warning("OS doesn't support setuid, cannot drop privileges")
            return

        if os.getuid() != 0:
            logger.info("Not running as root, cannot drop privileges")
            return

        try:
            import pwd
            import grp

            # Get user/group IDs
            pw_record = pwd.getpwnam(user)
            gr_record = grp.getgrnam(group)

            uid = pw_record.pw_uid
            gid = gr_record.gr_gid

            # Drop privileges
            os.setgroups([])
            os.setgid(gid)
            os.setuid(uid)

            logger.info(f"Dropped privileges to {user}:{group} (uid={uid}, gid={gid})")

        except Exception as e:
            logger.error(f"Failed to drop privileges: {e}")
            raise

    def run_isolated(self,
                     command: List[str],
                     timeout: Optional[int] = None,
                     env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        """
        Run command in isolated environment

        Args:
            command: Command to run
            timeout: Timeout in seconds
            env: Environment variables

        Returns:
            CompletedProcess instance
        """
        if not self.enabled:
            # Run without isolation
            return subprocess.run(command, capture_output=True, timeout=timeout, env=env)

        # Create restricted environment
        restricted_env = {
            'PATH': '/usr/bin:/bin',
            'HOME': '/tmp',
            'SHELL': '/bin/sh'
        }

        if env:
            restricted_env.update(env)

        logger.debug(f"Running isolated: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=timeout,
                env=restricted_env,
                cwd='/tmp'
            )

            return result

        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out: {' '.join(command)}")
            raise
        except Exception as e:
            logger.error(f"Isolated execution failed: {e}")
            raise

    def check_capabilities(self) -> Dict[str, bool]:
        """
        Check available security capabilities

        Returns:
            Dictionary of available capabilities
        """
        capabilities = {
            'drop_privileges': hasattr(os, 'setuid') and os.getuid() == 0,
            'network_namespace': self._check_network_namespace(),
            'seccomp': self._check_seccomp(),
            'apparmor': self._check_apparmor(),
            'selinux': self._check_selinux()
        }

        logger.info(f"Security capabilities: {capabilities}")
        return capabilities

    def _check_network_namespace(self) -> bool:
        """Check if network namespaces are available"""
        try:
            result = subprocess.run(
                ['ip', 'netns', 'list'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_seccomp(self) -> bool:
        """Check if seccomp is available"""
        return os.path.exists('/proc/sys/kernel/seccomp')

    def _check_apparmor(self) -> bool:
        """Check if AppArmor is available"""
        return os.path.exists('/sys/kernel/security/apparmor')

    def _check_selinux(self) -> bool:
        """Check if SELinux is available"""
        return os.path.exists('/sys/fs/selinux')

    def create_network_namespace(self, name: str) -> bool:
        """
        Create a network namespace for isolation

        Args:
            name: Namespace name

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            subprocess.run(
                ['ip', 'netns', 'add', name],
                check=True,
                timeout=5
            )
            logger.info(f"Created network namespace: {name}")
            return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to create network namespace: {e}")
            return False

    def delete_network_namespace(self, name: str) -> bool:
        """
        Delete a network namespace

        Args:
            name: Namespace name

        Returns:
            True if successful
        """
        try:
            subprocess.run(
                ['ip', 'netns', 'delete', name],
                check=True,
                timeout=5
            )
            logger.info(f"Deleted network namespace: {name}")
            return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"Failed to delete network namespace: {e}")
            return False
