"""
Database Manager

Manages SQLite database for storing discoveries and scan results.
"""

import os
import sqlite3
import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages IPv9 database"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize database manager

        Args:
            config: Database configuration
        """
        config = config or {}
        self.db_path = config.get('path', os.path.expanduser('~/.ipv9tool/ipv9.db'))
        self.connection = None

        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Database manager initialized: {self.db_path}")

    async def initialize(self):
        """Initialize database connection and create tables"""
        self.connection = await aiosqlite.connect(self.db_path)

        # Enable foreign keys
        await self.connection.execute("PRAGMA foreign_keys = ON")

        # Create tables
        await self._create_tables()

        logger.info("Database initialized")

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")

    async def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self.connection:
            return False

        try:
            await self.connection.execute("SELECT 1")
            return True
        except:
            return False

    async def _create_tables(self):
        """Create database tables"""

        # Hosts table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                hostname TEXT,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                alive BOOLEAN DEFAULT 1,
                os TEXT,
                os_accuracy INTEGER,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Ports table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER NOT NULL,
                port INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                state TEXT NOT NULL,
                service TEXT,
                version TEXT,
                product TEXT,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE,
                UNIQUE(host_id, port, protocol)
            )
        """)

        # Domains table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT UNIQUE NOT NULL,
                ip_addresses TEXT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                responsive BOOLEAN DEFAULT 0,
                http_status INTEGER,
                metadata TEXT
            )
        """)

        # Scans table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT NOT NULL,
                target TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                status TEXT NOT NULL,
                hosts_found INTEGER DEFAULT 0,
                ports_found INTEGER DEFAULT 0,
                result_data TEXT
            )
        """)

        # Create indexes
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_hosts_ip ON hosts(ip_address)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_hosts_alive ON hosts(alive)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_ports_host ON ports(host_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_ports_state ON ports(state)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_domains_hostname ON domains(hostname)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_scans_type ON scans(scan_type)")

        await self.connection.commit()

    # Host operations

    async def store_host(self, host_info) -> int:
        """
        Store or update host information

        Args:
            host_info: HostInfo object

        Returns:
            Host ID
        """
        import json

        now = datetime.utcnow()

        # Check if host exists
        cursor = await self.connection.execute(
            "SELECT id FROM hosts WHERE ip_address = ?",
            (host_info.address,)
        )
        row = await cursor.fetchone()

        if row:
            # Update existing host
            host_id = row[0]
            await self.connection.execute("""
                UPDATE hosts SET
                    hostname = COALESCE(?, hostname),
                    last_seen = ?,
                    alive = 1,
                    os = COALESCE(?, os),
                    os_accuracy = COALESCE(?, os_accuracy)
                WHERE id = ?
            """, (host_info.hostname, now, host_info.os, host_info.os_accuracy, host_id))
        else:
            # Insert new host
            cursor = await self.connection.execute("""
                INSERT INTO hosts (ip_address, hostname, first_seen, last_seen, os, os_accuracy)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (host_info.address, host_info.hostname, now, now, host_info.os, host_info.os_accuracy))
            host_id = cursor.lastrowid

        # Store ports
        for port_info in host_info.ports:
            await self.store_port(host_id, port_info)

        await self.connection.commit()
        return host_id

    async def store_port(self, host_id: int, port_info) -> int:
        """
        Store or update port information

        Args:
            host_id: Host ID
            port_info: PortInfo object

        Returns:
            Port ID
        """
        now = datetime.utcnow()

        # Check if port exists
        cursor = await self.connection.execute(
            "SELECT id FROM ports WHERE host_id = ? AND port = ? AND protocol = ?",
            (host_id, port_info.port, port_info.protocol)
        )
        row = await cursor.fetchone()

        if row:
            # Update existing port
            port_id = row[0]
            await self.connection.execute("""
                UPDATE ports SET
                    state = ?,
                    service = COALESCE(?, service),
                    version = COALESCE(?, version),
                    product = COALESCE(?, product),
                    last_seen = ?
                WHERE id = ?
            """, (port_info.state, port_info.service, port_info.version, port_info.product, now, port_id))
        else:
            # Insert new port
            cursor = await self.connection.execute("""
                INSERT INTO ports (host_id, port, protocol, state, service, version, product, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (host_id, port_info.port, port_info.protocol, port_info.state,
                  port_info.service, port_info.version, port_info.product, now, now))
            port_id = cursor.lastrowid

        await self.connection.commit()
        return port_id

    async def store_domain(self, domain_info) -> int:
        """
        Store or update domain information

        Args:
            domain_info: EnumeratedDomain object

        Returns:
            Domain ID
        """
        import json

        now = datetime.utcnow()
        ip_addresses_json = json.dumps(domain_info.addresses)

        # Check if domain exists
        cursor = await self.connection.execute(
            "SELECT id FROM domains WHERE hostname = ?",
            (domain_info.hostname,)
        )
        row = await cursor.fetchone()

        if row:
            # Update existing domain
            domain_id = row[0]
            await self.connection.execute("""
                UPDATE domains SET
                    ip_addresses = ?,
                    last_seen = ?,
                    responsive = ?,
                    http_status = COALESCE(?, http_status)
                WHERE id = ?
            """, (ip_addresses_json, now, domain_info.responsive, domain_info.http_status, domain_id))
        else:
            # Insert new domain
            cursor = await self.connection.execute("""
                INSERT INTO domains (hostname, ip_addresses, first_seen, last_seen, responsive, http_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (domain_info.hostname, ip_addresses_json, now, now, domain_info.responsive, domain_info.http_status))
            domain_id = cursor.lastrowid

        await self.connection.commit()
        return domain_id

    # Query operations

    async def get_hosts(self, alive_only: bool = True, limit: int = 100) -> List[Dict]:
        """Get discovered hosts"""
        query = "SELECT * FROM hosts"
        params = []

        if alive_only:
            query += " WHERE alive = 1"

        query += " ORDER BY last_seen DESC LIMIT ?"
        params.append(limit)

        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()

        hosts = []
        for row in rows:
            import json
            hosts.append({
                'id': row[0],
                'ip_address': row[1],
                'hostname': row[2],
                'first_seen': row[3],
                'last_seen': row[4],
                'alive': bool(row[5]),
                'os': row[6],
                'os_accuracy': row[7],
                'tags': json.loads(row[8]) if row[8] else []
            })

        return hosts

    async def get_ports(
        self,
        host_id: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get discovered ports"""
        query = "SELECT * FROM ports WHERE 1=1"
        params = []

        if host_id:
            query += " AND host_id = ?"
            params.append(host_id)

        if state:
            query += " AND state = ?"
            params.append(state)

        query += " ORDER BY last_seen DESC LIMIT ?"
        params.append(limit)

        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()

        ports = []
        for row in rows:
            ports.append({
                'id': row[0],
                'host_id': row[1],
                'port': row[2],
                'protocol': row[3],
                'state': row[4],
                'service': row[5],
                'version': row[6],
                'product': row[7],
                'first_seen': row[8],
                'last_seen': row[9]
            })

        return ports

    async def get_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        stats = {}

        # Total domains
        cursor = await self.connection.execute("SELECT COUNT(*) FROM domains")
        stats['total_domains'] = (await cursor.fetchone())[0]

        # Total IPs
        cursor = await self.connection.execute("SELECT COUNT(*) FROM hosts")
        stats['total_ips'] = (await cursor.fetchone())[0]

        # Total ports
        cursor = await self.connection.execute("SELECT COUNT(*) FROM ports")
        stats['total_ports'] = (await cursor.fetchone())[0]

        # Active hosts
        cursor = await self.connection.execute("SELECT COUNT(*) FROM hosts WHERE alive = 1")
        stats['active_hosts'] = (await cursor.fetchone())[0]

        # Responsive web
        cursor = await self.connection.execute("SELECT COUNT(*) FROM domains WHERE responsive = 1")
        stats['responsive_web'] = (await cursor.fetchone())[0]

        # Last scan
        cursor = await self.connection.execute("SELECT MAX(completed_at) FROM scans WHERE status = 'completed'")
        last_scan = (await cursor.fetchone())[0]
        stats['last_scan'] = last_scan

        return stats
