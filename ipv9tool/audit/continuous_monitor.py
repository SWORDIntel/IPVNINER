"""
Continuous Network Monitor

Continuously monitors IPv9 network for changes.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ContinuousMonitor:
    """Continuous network monitoring system"""

    def __init__(self, audit_engine, db_manager, interval_minutes: int = 60):
        """
        Initialize continuous monitor

        Args:
            audit_engine: AuditEngine instance
            db_manager: DatabaseManager instance
            interval_minutes: Monitoring interval in minutes
        """
        self.audit_engine = audit_engine
        self.db = db_manager
        self.interval = interval_minutes * 60  # Convert to seconds

        self.running = False
        self.last_scan = None
        self.scan_count = 0

        logger.info(f"Continuous monitor initialized (interval={interval_minutes}min)")

    async def start(self, change_callback: Optional[Callable] = None):
        """
        Start continuous monitoring

        Args:
            change_callback: Optional callback for detected changes
        """
        self.running = True
        logger.info("Starting continuous monitoring...")

        while self.running:
            try:
                logger.info(f"Running scheduled scan #{self.scan_count + 1}")

                # Run audit
                results = await self.audit_engine.run_full_audit(
                    scan_dns=True,
                    scan_web=True,
                    scan_all_ports=False,
                    deep_scan=False
                )

                # Detect changes
                changes = await self._detect_changes(results)

                if changes and change_callback:
                    change_callback(changes)

                self.last_scan = datetime.utcnow()
                self.scan_count += 1

                logger.info(f"Scan complete. {len(changes)} changes detected.")

                # Wait for next interval
                await asyncio.sleep(self.interval)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    def stop(self):
        """Stop continuous monitoring"""
        self.running = False
        logger.info("Stopping continuous monitoring...")

    async def _detect_changes(self, current_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect changes from previous scan

        Args:
            current_results: Current scan results

        Returns:
            List of detected changes
        """
        changes = []

        # Get previous state from database
        stats = await self.db.get_stats()

        # Compare findings
        current_findings = current_results.get('findings', [])

        # New hosts
        new_hosts = [f for f in current_findings if f['type'] == 'host_alive']
        if new_hosts:
            changes.append({
                'type': 'new_hosts',
                'count': len(new_hosts),
                'hosts': new_hosts
            })

        # New open ports
        new_ports = [f for f in current_findings if f['type'] == 'open_port']
        if new_ports:
            changes.append({
                'type': 'new_ports',
                'count': len(new_ports),
                'ports': new_ports
            })

        # New domains
        new_domains = [f for f in current_findings if f['type'] == 'domain_discovered']
        if new_domains:
            changes.append({
                'type': 'new_domains',
                'count': len(new_domains),
                'domains': new_domains
            })

        return changes

    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            'running': self.running,
            'interval_minutes': self.interval // 60,
            'last_scan': self.last_scan,
            'scan_count': self.scan_count,
            'next_scan': self.last_scan + timedelta(seconds=self.interval) if self.last_scan else None
        }
