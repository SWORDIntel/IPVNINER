#!/usr/bin/env python3
"""
IPv9 Scanner - Unified TUI Application

Comprehensive text user interface with real-time streaming logs,
network discovery, scanning, and monitoring capabilities.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Static, Log, Input,
    Label, ProgressBar, DataTable, TabbedContent, TabPane
)
from textual.binding import Binding
from textual import on
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable

from ..dns import IPv9Resolver, DNSCache
from ..scanner import PortScanner, HostDiscovery, DNSEnumerator
from ..audit import AuditEngine, MasscanEnumerator
from ..database import DatabaseManager
from ..config import ConfigManager
from ..security import setup_logging


class StatisticsWidget(Static):
    """Real-time statistics display"""

    def __init__(self):
        super().__init__()
        self.stats = {
            'total_domains': 0,
            'total_ips': 0,
            'active_hosts': 0,
            'total_ports': 0,
            'responsive_web': 0
        }

    def update_stats(self, stats: dict):
        """Update statistics"""
        self.stats.update(stats)
        self.refresh()

    def render(self) -> Panel:
        """Render statistics panel"""
        table = RichTable.grid(padding=(0, 2))
        table.add_column(style="cyan")
        table.add_column(style="green bold")

        table.add_row("Total Domains:", f"{self.stats['total_domains']:,}")
        table.add_row("Total IPs:", f"{self.stats['total_ips']:,}")
        table.add_row("Active Hosts:", f"{self.stats['active_hosts']:,}")
        table.add_row("Total Ports:", f"{self.stats['total_ports']:,}")
        table.add_row("Responsive Web:", f"{self.stats['responsive_web']:,}")

        return Panel(
            table,
            title="[bold cyan]Network Statistics[/bold cyan]",
            border_style="cyan"
        )


class LogStreamWidget(Log):
    """Real-time log streaming widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, highlight=True, markup=True)
        self.max_lines = 1000

    def write_log(self, message: str, level: str = "INFO"):
        """Write log message with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color based on level
        if level == "ERROR":
            style = "red bold"
        elif level == "WARNING":
            style = "yellow"
        elif level == "SUCCESS":
            style = "green bold"
        elif level == "DEBUG":
            style = "dim"
        else:
            style = "white"

        self.write(f"[dim]{timestamp}[/dim] [{style}]{level:8}[/{style}] {message}")


class IPv9ScannerTUI(App):
    """IPv9 Scanner TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
        height: 3;
    }

    Footer {
        background: $panel;
        color: $text;
    }

    #stats-container {
        height: 10;
        border: solid $primary;
    }

    #log-container {
        height: 1fr;
        border: solid $accent;
        margin-top: 1;
    }

    #control-panel {
        height: auto;
        border: solid $secondary;
        margin-top: 1;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }

    .success {
        background: $success;
        color: $text;
    }

    .warning {
        background: $warning;
        color: $text;
    }

    .error {
        background: $error;
        color: $text;
    }

    ProgressBar {
        margin: 1 0;
    }

    DataTable {
        height: 100%;
    }

    Input {
        margin: 0 1;
    }

    Label {
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("s", "show_stats", "Statistics"),
        Binding("l", "clear_logs", "Clear Logs"),
        Binding("h", "show_help", "Help"),
    ]

    TITLE = "IPv9 Network Scanner"
    SUB_TITLE = "Comprehensive IPv9 Discovery & Auditing Platform"

    def __init__(self):
        super().__init__()

        # Initialize components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()

        setup_logging(self.config.get('logging', {}))

        self.resolver = IPv9Resolver(self.config)
        self.cache = DNSCache(
            max_size=self.config['dns']['cache_size'],
            default_ttl=self.config['dns']['ttl']
        )
        self.scanner = PortScanner(self.config)
        self.discovery = HostDiscovery(self.config)
        self.enumerator = DNSEnumerator(self.resolver, self.config)
        self.masscan_enum = MasscanEnumerator(rate=10000)

        # Initialize database (will be done async)
        self.db = None
        self.audit_engine = None

        # UI components
        self.stats_widget = None
        self.log_widget = None
        self.progress_bar = None

        # State
        self.scanning = False
        self.current_job = None

    def compose(self) -> ComposeResult:
        """Create UI layout"""
        yield Header()

        with TabbedContent():
            with TabPane("Scanner", id="tab-scanner"):
                # Statistics
                yield Container(
                    StatisticsWidget(),
                    id="stats-container"
                )

                # Control Panel
                with Container(id="control-panel"):
                    with Horizontal():
                        yield Button("DNS Resolve", id="btn-resolve", variant="primary")
                        yield Button("Ping Host", id="btn-ping", variant="primary")
                        yield Button("Port Scan", id="btn-scan", variant="primary")
                        yield Button("Enumerate", id="btn-enum", variant="success")

                    with Horizontal():
                        yield Button("Full Audit", id="btn-audit", variant="warning")
                        yield Button("Masscan", id="btn-masscan", variant="warning")
                        yield Button("Monitor", id="btn-monitor", variant="success")
                        yield Button("Stop", id="btn-stop", variant="error")

                    with Horizontal():
                        yield Label("Target:")
                        yield Input(placeholder="www.v9.chn or IP", id="target-input")
                        yield Label("Ports:")
                        yield Input(placeholder="80,443", value="80,443,8080", id="ports-input")

                    yield ProgressBar(total=100, show_eta=False, id="progress")

                # Log Stream
                yield Container(
                    LogStreamWidget(id="log-stream"),
                    id="log-container"
                )

            with TabPane("Discovered Hosts", id="tab-hosts"):
                yield DataTable(id="hosts-table")

            with TabPane("Open Ports", id="tab-ports"):
                yield DataTable(id="ports-table")

            with TabPane("Domains", id="tab-domains"):
                yield DataTable(id="domains-table")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize application after mount"""
        # Get widget references
        self.stats_widget = self.query_one(StatisticsWidget)
        self.log_widget = self.query_one("#log-stream", LogStreamWidget)
        self.progress_bar = self.query_one("#progress", ProgressBar)

        # Setup data tables
        hosts_table = self.query_one("#hosts-table", DataTable)
        hosts_table.add_columns("IP Address", "Hostname", "Status", "OS", "Last Seen")

        ports_table = self.query_one("#ports-table", DataTable)
        ports_table.add_columns("Host", "Port", "Protocol", "State", "Service")

        domains_table = self.query_one("#domains-table", DataTable)
        domains_table.add_columns("Hostname", "IP Addresses", "Responsive", "HTTP Status")

        # Initialize database
        self.log_widget.write_log("Initializing database...", "INFO")
        self.db = DatabaseManager(self.config.get('database', {}))
        await self.db.initialize()

        # Create audit engine
        self.audit_engine = AuditEngine(
            self.resolver,
            self.scanner,
            self.discovery,
            self.enumerator,
            self.db
        )

        self.log_widget.write_log("IPv9 Scanner ready!", "SUCCESS")
        self.log_widget.write_log("Use buttons to start scanning or press 'h' for help", "INFO")

        # Load initial stats
        await self.refresh_stats()

    async def refresh_stats(self):
        """Refresh statistics from database"""
        if self.db:
            stats = await self.db.get_stats()
            self.stats_widget.update_stats(stats)

    async def refresh_hosts_table(self):
        """Refresh hosts table"""
        if self.db:
            hosts = await self.db.get_hosts(alive_only=False, limit=100)
            table = self.query_one("#hosts-table", DataTable)
            table.clear()

            for host in hosts:
                status = "✓ Alive" if host['alive'] else "✗ Down"
                last_seen = host['last_seen'][:19] if host['last_seen'] else "N/A"
                table.add_row(
                    host['ip_address'],
                    host.get('hostname', 'N/A'),
                    status,
                    host.get('os', 'Unknown'),
                    last_seen
                )

    async def refresh_ports_table(self):
        """Refresh ports table"""
        if self.db:
            ports = await self.db.get_ports(state="open", limit=100)
            table = self.query_one("#ports-table", DataTable)
            table.clear()

            # Get host IPs
            for port in ports:
                hosts = await self.db.get_hosts(alive_only=False, limit=1000)
                host_map = {h['id']: h['ip_address'] for h in hosts}

                host_ip = host_map.get(port['host_id'], 'Unknown')

                table.add_row(
                    host_ip,
                    str(port['port']),
                    port['protocol'],
                    port['state'],
                    port.get('service', 'unknown')
                )

    @on(Button.Pressed, "#btn-resolve")
    async def action_dns_resolve(self):
        """DNS resolution action"""
        target_input = self.query_one("#target-input", Input)
        target = target_input.value.strip()

        if not target:
            self.log_widget.write_log("Please enter a hostname", "WARNING")
            return

        self.log_widget.write_log(f"Resolving {target}...", "INFO")

        try:
            addresses = self.resolver.resolve(target)

            if addresses:
                self.log_widget.write_log(f"Resolved {target} to:", "SUCCESS")
                for addr in addresses:
                    self.log_widget.write_log(f"  → {addr}", "INFO")
            else:
                self.log_widget.write_log(f"No addresses found for {target}", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"Resolution failed: {e}", "ERROR")

    @on(Button.Pressed, "#btn-ping")
    async def action_ping(self):
        """Ping action"""
        target_input = self.query_one("#target-input", Input)
        target = target_input.value.strip()

        if not target:
            self.log_widget.write_log("Please enter a target", "WARNING")
            return

        self.log_widget.write_log(f"Pinging {target}...", "INFO")

        try:
            # Resolve if needed
            if self.resolver.is_ipv9_domain(target):
                addresses = self.resolver.resolve(target)
                if addresses:
                    target = addresses[0]
                    self.log_widget.write_log(f"Resolved to {target}", "INFO")

            result = self.discovery.ping(target, count=4)

            if result.get('reachable'):
                self.log_widget.write_log(f"Host {target} is reachable", "SUCCESS")

                if 'statistics' in result:
                    stats = result['statistics']
                    self.log_widget.write_log(
                        f"  Packets: {stats.get('received', 0)}/{stats.get('transmitted', 0)} "
                        f"(loss: {stats.get('packet_loss', 0)}%)",
                        "INFO"
                    )

                    if 'rtt' in stats:
                        rtt = stats['rtt']
                        self.log_widget.write_log(
                            f"  RTT: min={rtt['min']}ms, avg={rtt['avg']}ms, max={rtt['max']}ms",
                            "INFO"
                        )
            else:
                self.log_widget.write_log(f"Host {target} is not reachable", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"Ping failed: {e}", "ERROR")

    @on(Button.Pressed, "#btn-scan")
    async def action_port_scan(self):
        """Port scan action"""
        target_input = self.query_one("#target-input", Input)
        ports_input = self.query_one("#ports-input", Input)

        target = target_input.value.strip()
        ports = ports_input.value.strip() or "80,443,8080"

        if not target:
            self.log_widget.write_log("Please enter a target", "WARNING")
            return

        self.log_widget.write_log(f"Scanning {target} ports {ports}...", "INFO")
        self.scanning = True

        try:
            # Resolve if needed
            if self.resolver.is_ipv9_domain(target):
                addresses = self.resolver.resolve(target)
                if addresses:
                    target = addresses[0]
                    self.log_widget.write_log(f"Resolved to {target}", "INFO")

            result = self.scanner.scan_nmap(
                target,
                ports=ports,
                scan_type="syn",
                service_detection=True
            )

            if 'error' in result:
                self.log_widget.write_log(f"Scan failed: {result['error']}", "ERROR")
            else:
                self.log_widget.write_log(f"Scan completed for {target}", "SUCCESS")

                for host_data in result.get('hosts', []):
                    for port in host_data.get('ports', []):
                        if port['state'] == 'open':
                            service = port.get('service', {})
                            service_name = service.get('name', 'unknown')
                            version = service.get('version', '')

                            self.log_widget.write_log(
                                f"  Port {port['port']}/{port['protocol']}: "
                                f"{port['state']} ({service_name} {version})".strip(),
                                "SUCCESS"
                            )

                # Refresh tables
                await self.refresh_hosts_table()
                await self.refresh_ports_table()
                await self.refresh_stats()

        except Exception as e:
            self.log_widget.write_log(f"Scan failed: {e}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-enum")
    async def action_enumerate(self):
        """Enumeration action"""
        self.log_widget.write_log("Starting domain enumeration...", "INFO")
        self.scanning = True
        self.progress_bar.update(total=100, progress=0)

        try:
            # Enumerate a sample pattern
            pattern = "861381234NNNN"
            max_combinations = 1000

            self.log_widget.write_log(f"Enumerating pattern: {pattern}", "INFO")
            self.log_widget.write_log(f"Max combinations: {max_combinations}", "INFO")

            results = self.enumerator.brute_force_pattern(pattern, "chn", max_combinations)

            self.log_widget.write_log(f"Found {len(results)} domains", "SUCCESS")

            for i, result in enumerate(results[:10]):  # Show first 10
                self.log_widget.write_log(
                    f"  {result['hostname']} → {', '.join(result['addresses'])}",
                    "INFO"
                )

            if len(results) > 10:
                self.log_widget.write_log(f"  ... and {len(results) - 10} more", "INFO")

            self.progress_bar.update(progress=100)

            # Refresh tables
            await self.refresh_stats()

        except Exception as e:
            self.log_widget.write_log(f"Enumeration failed: {e}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-audit")
    async def action_full_audit(self):
        """Full audit action"""
        self.log_widget.write_log("Starting comprehensive network audit...", "INFO")
        self.scanning = True
        self.progress_bar.update(total=100, progress=0)

        try:
            def progress_callback(progress):
                self.progress_bar.update(progress=progress)
                self.log_widget.write_log(f"Audit progress: {progress:.1f}%", "INFO")

            results = await self.audit_engine.run_full_audit(
                scan_dns=True,
                scan_web=True,
                scan_all_ports=False,
                deep_scan=False,
                progress_callback=progress_callback
            )

            self.log_widget.write_log("Audit completed!", "SUCCESS")

            if 'findings_summary' in results:
                summary = results['findings_summary']
                self.log_widget.write_log(f"Total findings: {summary.get('total', 0)}", "INFO")

            # Refresh all tables
            await self.refresh_hosts_table()
            await self.refresh_ports_table()
            await self.refresh_stats()

        except Exception as e:
            self.log_widget.write_log(f"Audit failed: {e}", "ERROR")
        finally:
            self.scanning = False
            self.progress_bar.update(progress=100)

    @on(Button.Pressed, "#btn-masscan")
    async def action_masscan(self):
        """Masscan action"""
        self.log_widget.write_log("Masscan enumeration (this may take a while)...", "WARNING")
        self.scanning = True

        try:
            # Create a plan first
            plan = self.masscan_enum.create_enumeration_plan(
                total_budget_hours=1,  # 1 hour
                ports="80,443,8080"
            )

            self.log_widget.write_log(f"Masscan plan:", "INFO")
            self.log_widget.write_log(f"  Rate: {plan['rate_pps']:,} pps", "INFO")
            self.log_widget.write_log(f"  IPs scannable: {plan['total_ips_scannable']:,}", "INFO")
            self.log_widget.write_log(f"  Coverage: {plan['coverage_percent']:.4f}%", "INFO")

            # Run enumeration (sample)
            self.log_widget.write_log("Starting masscan (10% sample)...", "INFO")

            results = self.masscan_enum.enumerate_ipv9_space(
                sample_rate=0.10,
                ports="80,443"
            )

            self.log_widget.write_log(
                f"Masscan complete: {results.get('total_hosts', 0)} hosts found",
                "SUCCESS"
            )

        except Exception as e:
            self.log_widget.write_log(f"Masscan failed: {e}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-monitor")
    async def action_monitor(self):
        """Continuous monitoring action"""
        self.log_widget.write_log("Starting continuous monitoring...", "INFO")
        # TODO: Implement continuous monitoring

    @on(Button.Pressed, "#btn-stop")
    async def action_stop(self):
        """Stop current operation"""
        if self.scanning:
            self.log_widget.write_log("Stopping current operation...", "WARNING")
            self.scanning = False
        else:
            self.log_widget.write_log("No operation running", "INFO")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark

    def action_show_stats(self) -> None:
        """Show statistics"""
        self.log_widget.write_log("Statistics refreshed", "INFO")
        asyncio.create_task(self.refresh_stats())

    def action_clear_logs(self) -> None:
        """Clear log display"""
        self.log_widget.clear()
        self.log_widget.write_log("Logs cleared", "INFO")

    def action_show_help(self) -> None:
        """Show help"""
        self.log_widget.write_log("=== IPv9 Scanner Help ===", "INFO")
        self.log_widget.write_log("Keybindings:", "INFO")
        self.log_widget.write_log("  q - Quit", "INFO")
        self.log_widget.write_log("  d - Toggle dark mode", "INFO")
        self.log_widget.write_log("  s - Refresh statistics", "INFO")
        self.log_widget.write_log("  l - Clear logs", "INFO")
        self.log_widget.write_log("  h - Show this help", "INFO")


def main():
    """Main entry point"""
    app = IPv9ScannerTUI()
    app.run()


if __name__ == "__main__":
    main()
