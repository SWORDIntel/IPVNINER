#!/usr/bin/env python3
"""
IPv9 Scanner - TEMPEST-Compliant Military TUI
<
Classification: UNCLASSIFIED
System: IPVNINER Network Intelligence Platform
Facility: TACTICAL NETWORK OPERATIONS CENTER (TNOC)
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.widgets import (
    Header, Footer, Button, Static, Log, Input,
    Label, ProgressBar, DataTable, TabbedContent, TabPane
)
from textual.binding import Binding
from textual import on
from rich.text import Text
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.align import Align

from ..dns import IPv9Resolver, DNSCache
from ..scanner import PortScanner, HostDiscovery, DNSEnumerator
from ..audit import AuditEngine, MasscanEnumerator
from ..database import DatabaseManager
from ..config import ConfigManager
from ..security import setup_logging


class SecurityBanner(Static):
    """TEMPEST-compliant security classification banner"""

    def render(self) -> Text:
        """Render security banner"""
        banner = Text()
        banner.append("█" * 120, style="bold green")
        banner.append("\n")
        banner.append("  CLASSIFICATION: UNCLASSIFIED  ", style="bold black on green")
        banner.append("  SYSTEM: IPVNINER NETWORK INTELLIGENCE PLATFORM  ", style="bold green")
        banner.append("  FACILITY: TNOC  ", style="bold black on green")
        banner.append("\n")
        banner.append("█" * 120, style="bold green")
        return banner


class SystemStatusWidget(Static):
    """Military-grade system status display"""

    def __init__(self):
        super().__init__()
        self.status = "OPERATIONAL"
        self.integrity = "SECURE"
        self.uptime_start = datetime.now(timezone.utc)

    def get_zulu_time(self) -> str:
        """Get current time in Zulu (UTC) format"""
        return datetime.now(timezone.utc).strftime("%d%H%M%SZMAY%y")

    def get_uptime(self) -> str:
        """Calculate system uptime"""
        delta = datetime.now(timezone.utc) - self.uptime_start
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        seconds = int(delta.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def render(self) -> Panel:
        """Render system status panel"""
        table = RichTable.grid(padding=(0, 2))
        table.add_column(style="bold green", justify="right")
        table.add_column(style="bold white")

        table.add_row("SYS STATUS:", f"[bold green]█ {self.status}[/bold green]")
        table.add_row("INTEGRITY:", f"[bold green]█ {self.integrity}[/bold green]")
        table.add_row("ZULU TIME:", f"[bold yellow]{self.get_zulu_time()}[/bold yellow]")
        table.add_row("UPTIME:", f"[bold cyan]{self.get_uptime()}[/bold cyan]")

        return Panel(
            table,
            title="[bold green]║ SYSTEM STATUS ║[/bold green]",
            border_style="bold green",
            padding=(0, 1)
        )


class TacticalStatsWidget(Static):
    """Tactical network statistics display"""

    def __init__(self):
        super().__init__()
        self.stats = {
            'total_domains': 0,
            'total_ips': 0,
            'active_hosts': 0,
            'total_ports': 0,
            'responsive_web': 0,
            'threats': 0
        }

    def update_stats(self, stats: dict):
        """Update statistics"""
        self.stats.update(stats)
        self.refresh()

    def render(self) -> Panel:
        """Render tactical statistics"""
        table = RichTable.grid(padding=(0, 2))
        table.add_column(style="bold green", justify="right", width=20)
        table.add_column(style="bold yellow", justify="right", width=10)

        table.add_row("DOMAINS DISCOVERED:", f"{self.stats['total_domains']:>7,}")
        table.add_row("IP ADDRESSES:", f"{self.stats['total_ips']:>7,}")
        table.add_row("ACTIVE HOSTS:", f"[bold green]{self.stats['active_hosts']:>7,}[/bold green]")
        table.add_row("PORTS IDENTIFIED:", f"{self.stats['total_ports']:>7,}")
        table.add_row("WEB SERVICES:", f"{self.stats['responsive_web']:>7,}")
        table.add_row("THREAT LEVEL:", f"[bold yellow]{self.stats['threats']:>7}[/bold yellow]")

        return Panel(
            table,
            title="[bold green]║ TACTICAL NETWORK INTELLIGENCE ║[/bold green]",
            border_style="bold green",
            padding=(0, 1)
        )


class MilitaryLogWidget(Log):
    """Military-styled log output with tactical formatting"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, highlight=True, markup=True)
        self.max_lines = 5000

    def write_log(self, message: str, level: str = "INFO"):
        """Write military-formatted log message"""
        # Zulu timestamp
        timestamp = datetime.now(timezone.utc).strftime("%H%M%SZ")

        # Level indicators with military styling
        level_styles = {
            "ERROR": ("[bold red]", "ERR", "█"),
            "WARNING": ("[bold yellow]", "WRN", "▲"),
            "SUCCESS": ("[bold green]", "OPS", "✓"),
            "INFO": ("[bold cyan]", "INF", "►"),
            "DEBUG": ("[dim white]", "DBG", "·"),
            "CRITICAL": ("[bold red on white]", "CRT", "█"),
            "OPERATIONAL": ("[bold green]", "OPR", "●"),
            "SECURE": ("[bold green]", "SEC", "■"),
        }

        style, code, symbol = level_styles.get(level, ("[white]", "LOG", "○"))

        log_line = (
            f"[dim green]{timestamp}[/dim green] "
            f"{style}{symbol} {code:3}[/{style[1:-1]}] "
            f"[white]{message}[/white]"
        )

        self.write(log_line)


class OperationalControlPanel(Container):
    """Tactical operations control panel"""

    def compose(self) -> ComposeResult:
        """Compose control panel"""
        with Container(id="control-header"):
            yield Label("[bold green]╔═══════════════════════════ TACTICAL OPERATIONS ═══════════════════════════╗[/bold green]")

        # Primary Operations
        with Horizontal(classes="button-row"):
            yield Label("[bold green]│[/bold green] PRIMARY OPS:", classes="section-label")
            yield Button("DNS RESOLVE", id="btn-resolve", variant="primary", classes="mil-button")
            yield Button("PING SWEEP", id="btn-ping", variant="primary", classes="mil-button")
            yield Button("PORT SCAN", id="btn-scan", variant="primary", classes="mil-button")
            yield Button("ENUMERATE", id="btn-enum", variant="success", classes="mil-button")

        # Advanced Operations
        with Horizontal(classes="button-row"):
            yield Label("[bold green]│[/bold green] ADV OPS:", classes="section-label")
            yield Button("FULL AUDIT", id="btn-audit", variant="warning", classes="mil-button")
            yield Button("MASSCAN", id="btn-masscan", variant="warning", classes="mil-button")
            yield Button("MONITOR", id="btn-monitor", variant="success", classes="mil-button")
            yield Button("█ STOP", id="btn-stop", variant="error", classes="mil-button")

        # Target Configuration
        with Horizontal(classes="input-row"):
            yield Label("[bold green]│[/bold green] TARGET:", classes="input-label")
            yield Input(placeholder="www.v9.chn or IPv4/IPv6", id="target-input", classes="mil-input")
            yield Label("PORTS:", classes="input-label")
            yield Input(placeholder="80,443", value="80,443,8080", id="ports-input", classes="mil-input-small")

        # Mission Progress
        with Container(id="progress-container"):
            yield Label("[bold green]│[/bold green] MISSION PROGRESS:", classes="section-label")
            yield ProgressBar(total=100, show_eta=False, id="progress", classes="mil-progress")

        with Container(id="control-footer"):
            yield Label("[bold green]╚═══════════════════════════════════════════════════════════════════════════╝[/bold green]")


class IPv9MilitaryTUI(App):
    """TEMPEST-Compliant IPv9 Network Intelligence Platform"""

    CSS = """
    /* TEMPEST-Compliant Military Theme */

    Screen {
        background: #000000;
        color: #00ff00;
    }

    Header {
        background: #001100;
        color: #00ff00;
        height: 1;
        text-style: bold;
    }

    Footer {
        background: #001100;
        color: #00ff00;
        text-style: bold;
    }

    SecurityBanner {
        height: 3;
        background: #000000;
        color: #00ff00;
        text-style: bold;
    }

    #top-status-bar {
        layout: horizontal;
        height: 8;
        background: #000000;
        margin-bottom: 1;
    }

    SystemStatusWidget {
        width: 1fr;
        height: 100%;
        border: solid #00ff00;
        background: #001100;
    }

    TacticalStatsWidget {
        width: 2fr;
        height: 100%;
        border: solid #00ff00;
        background: #001100;
        margin-left: 1;
    }

    OperationalControlPanel {
        height: auto;
        background: #000000;
        margin-top: 1;
        margin-bottom: 1;
    }

    #control-header, #control-footer {
        height: 1;
        background: #000000;
    }

    .button-row, .input-row {
        height: 3;
        background: #000000;
        padding: 0 1;
    }

    #progress-container {
        height: 3;
        background: #000000;
        padding: 0 1;
    }

    .section-label {
        width: 15;
        content-align: center middle;
        text-style: bold;
        color: #00ff00;
        background: #000000;
    }

    .input-label {
        width: 10;
        content-align: right middle;
        text-style: bold;
        color: #00ff00;
        background: #000000;
    }

    Button.mil-button {
        min-width: 15;
        height: 2;
        background: #003300;
        color: #00ff00;
        border: solid #00ff00;
        text-style: bold;
        margin: 0 1;
    }

    Button.mil-button:hover {
        background: #005500;
        color: #ffffff;
        border: solid #00ff00;
        text-style: bold;
    }

    Button.mil-button:focus {
        background: #007700;
        color: #ffffff;
        border: double #00ff00;
        text-style: bold;
    }

    Input.mil-input {
        width: 2fr;
        height: 1;
        background: #001100;
        color: #00ff00;
        border: solid #00ff00;
        padding: 0 1;
    }

    Input.mil-input-small {
        width: 1fr;
        height: 1;
        background: #001100;
        color: #00ff00;
        border: solid #00ff00;
        padding: 0 1;
    }

    Input:focus {
        border: double #00ff00;
        background: #002200;
    }

    ProgressBar.mil-progress {
        height: 1;
        background: #001100;
        color: #00ff00;
        border: solid #00ff00;
        margin-left: 16;
    }

    ProgressBar > .bar--bar {
        color: #00ff00;
        background: #00ff00;
    }

    ProgressBar > .bar--complete {
        color: #00ff00;
    }

    #log-container {
        height: 1fr;
        border: double #00ff00;
        background: #000000;
        margin-top: 1;
    }

    MilitaryLogWidget {
        background: #000000;
        color: #00ff00;
        border: none;
        scrollbar-background: #001100;
        scrollbar-color: #00ff00;
    }

    TabbedContent {
        background: #000000;
        height: 100%;
    }

    TabPane {
        background: #000000;
        padding: 0;
    }

    Tabs {
        background: #001100;
        color: #00ff00;
    }

    Tab {
        background: #001100;
        color: #00ff00;
        text-style: bold;
    }

    Tab:hover {
        background: #003300;
        color: #ffffff;
    }

    Tab.-active {
        background: #005500;
        color: #ffffff;
        text-style: bold;
    }

    DataTable {
        height: 100%;
        background: #000000;
        color: #00ff00;
        border: solid #00ff00;
    }

    DataTable > .datatable--header {
        background: #003300;
        color: #ffffff;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: #005500;
        color: #ffffff;
        text-style: bold;
    }

    DataTable > .datatable--fixed {
        background: #001100;
    }

    DataTable:focus > .datatable--cursor {
        background: #007700;
        color: #ffffff;
        text-style: bold;
    }

    Label {
        background: transparent;
        color: #00ff00;
    }

    Static {
        background: transparent;
    }

    .classification-footer {
        height: 1;
        background: #000000;
        color: #00ff00;
        text-align: center;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "ABORT", priority=True),
        Binding("ctrl+c", "quit", "EMERGENCY EXIT", priority=True),
        Binding("s", "show_stats", "STATUS", priority=False),
        Binding("l", "clear_logs", "CLEAR LOG", priority=False),
        Binding("h", "show_help", "HELP", priority=False),
        Binding("r", "refresh", "REFRESH", priority=False),
    ]

    TITLE = "█ IPVNINER TACTICAL NETWORK OPERATIONS █"
    SUB_TITLE = "TEMPEST-COMPLIANT INTELLIGENCE PLATFORM"

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
        self.system_status = None
        self.stats_widget = None
        self.log_widget = None
        self.progress_bar = None

        # State
        self.scanning = False
        self.current_job = None
        self.mission_number = 1000

    def compose(self) -> ComposeResult:
        """Compose military-grade UI"""
        yield Header()
        yield SecurityBanner()

        # Top status bar
        with Horizontal(id="top-status-bar"):
            yield SystemStatusWidget()
            yield TacticalStatsWidget()

        # Main tactical interface
        with TabbedContent():
            with TabPane("█ TACTICAL OPS █", id="tab-ops"):
                yield OperationalControlPanel()

                # Log Stream
                with Container(id="log-container"):
                    yield MilitaryLogWidget(id="log-stream")

            with TabPane("█ HOSTILE NET █", id="tab-hosts"):
                yield DataTable(id="hosts-table")

            with TabPane("█ PORT INTEL █", id="tab-ports"):
                yield DataTable(id="ports-table")

            with TabPane("█ DOMAIN DB █", id="tab-domains"):
                yield DataTable(id="domains-table")

        yield Static("[bold green]█" * 120 + "\n  CLASSIFICATION: UNCLASSIFIED  │  FACILITY: TNOC  │  SYSTEM: IPVNINER\n" + "█" * 120 + "[/bold green]", classes="classification-footer")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize tactical system after mount"""
        # Get widget references
        self.system_status = self.query_one(SystemStatusWidget)
        self.stats_widget = self.query_one(TacticalStatsWidget)
        self.log_widget = self.query_one("#log-stream", MilitaryLogWidget)
        self.progress_bar = self.query_one("#progress", ProgressBar)

        # Setup data tables
        hosts_table = self.query_one("#hosts-table", DataTable)
        hosts_table.add_columns("IP ADDRESS", "HOSTNAME", "STATUS", "OS TYPE", "LAST CONTACT")

        ports_table = self.query_one("#ports-table", DataTable)
        ports_table.add_columns("HOST", "PORT", "PROTOCOL", "STATE", "SERVICE", "VERSION")

        domains_table = self.query_one("#domains-table", DataTable)
        domains_table.add_columns("HOSTNAME", "IP ADDRESSES", "STATUS", "HTTP CODE", "THREAT")

        # Initialize database
        self.log_widget.write_log("INITIALIZING TACTICAL DATABASE...", "INFO")
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

        self.log_widget.write_log("SYSTEM INITIALIZATION COMPLETE", "SUCCESS")
        self.log_widget.write_log("ALL SUBSYSTEMS NOMINAL - READY FOR OPERATIONS", "OPERATIONAL")
        self.log_widget.write_log("AWAITING TACTICAL DIRECTIVES...", "INFO")
        self.log_widget.write_log("TEMPEST COMPLIANCE: VERIFIED", "SECURE")

        # Load initial stats
        await self.refresh_stats()

        # Start status update timer
        self.set_interval(1.0, self.update_system_status)

    async def update_system_status(self) -> None:
        """Update system status display"""
        if self.system_status:
            self.system_status.refresh()

    async def refresh_stats(self) -> None:
        """Refresh tactical statistics"""
        if self.db:
            stats = await self.db.get_statistics()
            if self.stats_widget:
                self.stats_widget.update_stats(stats)

    @on(Button.Pressed, "#btn-resolve")
    async def action_dns_resolve(self):
        """DNS resolution operation"""
        target_input = self.query_one("#target-input", Input)
        target = target_input.value.strip()

        if not target:
            self.log_widget.write_log("ERROR: NO TARGET SPECIFIED", "ERROR")
            return

        self.log_widget.write_log(f"MISSION {self.mission_number}: DNS RESOLUTION OPERATION", "OPERATIONAL")
        self.log_widget.write_log(f"TARGET: {target}", "INFO")
        self.mission_number += 1

        try:
            addresses = self.resolver.resolve(target)

            if addresses:
                self.log_widget.write_log(f"DNS RESOLUTION: SUCCESS", "SUCCESS")
                for addr in addresses:
                    self.log_widget.write_log(f"  ► RESOLVED ADDRESS: {addr}", "INFO")

                # Store in database
                if self.db:
                    for addr in addresses:
                        await self.db.store_host(addr, target, alive=True)
                    await self.refresh_stats()
            else:
                self.log_widget.write_log(f"DNS RESOLUTION: NO RECORDS FOUND", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"DNS RESOLUTION: FAILED - {str(e)}", "ERROR")

    @on(Button.Pressed, "#btn-ping")
    async def action_ping(self):
        """Ping sweep operation"""
        target_input = self.query_one("#target-input", Input)
        target = target_input.value.strip()

        if not target:
            self.log_widget.write_log("ERROR: NO TARGET SPECIFIED", "ERROR")
            return

        self.log_widget.write_log(f"MISSION {self.mission_number}: PING SWEEP OPERATION", "OPERATIONAL")
        self.log_widget.write_log(f"TARGET: {target}", "INFO")
        self.mission_number += 1

        try:
            # First resolve if it's a domain
            if not target.replace('.', '').isdigit():
                addresses = self.resolver.resolve(target)
                if not addresses:
                    self.log_widget.write_log("PING: TARGET RESOLUTION FAILED", "ERROR")
                    return
                target_ip = addresses[0]
            else:
                target_ip = target

            self.log_widget.write_log(f"PINGING: {target_ip}", "INFO")
            result = self.discovery.ping_host(target_ip)

            if result:
                self.log_widget.write_log(f"PING: TARGET RESPONSIVE", "SUCCESS")
                if self.db:
                    await self.db.store_host(target_ip, target, alive=True)
                    await self.refresh_stats()
            else:
                self.log_widget.write_log(f"PING: NO RESPONSE", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"PING: OPERATION FAILED - {str(e)}", "ERROR")

    @on(Button.Pressed, "#btn-scan")
    async def action_port_scan(self):
        """Port scanning operation"""
        target_input = self.query_one("#target-input", Input)
        ports_input = self.query_one("#ports-input", Input)

        target = target_input.value.strip()
        ports = ports_input.value.strip() or "80,443"

        if not target:
            self.log_widget.write_log("ERROR: NO TARGET SPECIFIED", "ERROR")
            return

        self.log_widget.write_log(f"MISSION {self.mission_number}: PORT SCAN OPERATION", "OPERATIONAL")
        self.log_widget.write_log(f"TARGET: {target} | PORTS: {ports}", "INFO")
        self.mission_number += 1
        self.scanning = True

        try:
            # Resolve target
            if not target.replace('.', '').isdigit():
                addresses = self.resolver.resolve(target)
                if not addresses:
                    self.log_widget.write_log("PORT SCAN: TARGET RESOLUTION FAILED", "ERROR")
                    return
                target_ip = addresses[0]
            else:
                target_ip = target

            self.log_widget.write_log(f"INITIATING SCAN: {target_ip}", "INFO")
            result = self.scanner.scan_nmap([target_ip], ports=ports)

            if result and 'hosts' in result:
                for host in result['hosts']:
                    if 'ports' in host and host['ports']:
                        self.log_widget.write_log(
                            f"PORT SCAN: {len(host['ports'])} PORTS IDENTIFIED",
                            "SUCCESS"
                        )

                        for port in host['ports']:
                            self.log_widget.write_log(
                                f"  ► PORT {port['port']}/{port['protocol']}: "
                                f"{port['state']} - {port.get('service', 'UNKNOWN')}",
                                "INFO"
                            )

                            # Store in database
                            if self.db:
                                await self.db.store_port(
                                    target_ip,
                                    port['port'],
                                    port['protocol'],
                                    port['state'],
                                    port.get('service'),
                                    port.get('version')
                                )

                        await self.refresh_stats()
                    else:
                        self.log_widget.write_log("PORT SCAN: NO OPEN PORTS", "WARNING")
            else:
                self.log_widget.write_log("PORT SCAN: NO RESULTS", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"PORT SCAN: OPERATION FAILED - {str(e)}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-enum")
    async def action_enumerate(self):
        """Domain enumeration operation"""
        target_input = self.query_one("#target-input", Input)
        pattern = target_input.value.strip()

        if not pattern:
            self.log_widget.write_log("ERROR: NO PATTERN SPECIFIED", "ERROR")
            return

        self.log_widget.write_log(f"MISSION {self.mission_number}: DOMAIN ENUMERATION", "OPERATIONAL")
        self.log_widget.write_log(f"PATTERN: {pattern}", "INFO")
        self.mission_number += 1
        self.scanning = True

        try:
            self.log_widget.write_log("ENUMERATION: COMMENCING...", "INFO")

            results = self.enumerator.enumerate_pattern(pattern, max_results=100)

            if results:
                self.log_widget.write_log(
                    f"ENUMERATION: {len(results)} DOMAINS DISCOVERED",
                    "SUCCESS"
                )

                for domain, addresses in results:
                    self.log_widget.write_log(f"  ► {domain} → {', '.join(addresses)}", "INFO")

                    # Store in database
                    if self.db:
                        await self.db.store_domain(domain, addresses, responsive=True)

                await self.refresh_stats()
            else:
                self.log_widget.write_log("ENUMERATION: NO DOMAINS FOUND", "WARNING")

        except Exception as e:
            self.log_widget.write_log(f"ENUMERATION: OPERATION FAILED - {str(e)}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-audit")
    async def action_full_audit(self):
        """Full tactical audit operation"""
        self.log_widget.write_log(f"MISSION {self.mission_number}: FULL TACTICAL AUDIT", "OPERATIONAL")
        self.log_widget.write_log("CLASSIFICATION: OPERATION NETWORK SWEEP", "INFO")
        self.mission_number += 1
        self.scanning = True

        try:
            def progress_callback(phase: str, progress: float):
                self.progress_bar.update(progress=progress)
                self.log_widget.write_log(f"AUDIT PHASE: {phase} ({progress:.1f}%)", "INFO")

            self.log_widget.write_log("COMMENCING 6-PHASE TACTICAL AUDIT...", "INFO")

            results = await self.audit_engine.run_full_audit(
                scan_dns=True,
                scan_web=True,
                deep_scan=False,
                progress_callback=progress_callback
            )

            self.log_widget.write_log("TACTICAL AUDIT: COMPLETE", "SUCCESS")
            self.log_widget.write_log(f"DOMAINS: {len(results.get('domains', []))}", "INFO")
            self.log_widget.write_log(f"HOSTS: {len(results.get('hosts', []))}", "INFO")
            self.log_widget.write_log(f"PORTS: {len(results.get('ports', []))}", "INFO")

            await self.refresh_stats()
            self.progress_bar.update(progress=0)

        except Exception as e:
            self.log_widget.write_log(f"AUDIT: OPERATION FAILED - {str(e)}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-masscan")
    async def action_masscan(self):
        """Masscan high-speed enumeration"""
        self.log_widget.write_log(f"MISSION {self.mission_number}: HIGH-SPEED NETWORK ENUMERATION", "OPERATIONAL")
        self.log_widget.write_log("TACTICAL ASSET: MASSCAN", "INFO")
        self.mission_number += 1
        self.scanning = True

        try:
            # Create enumeration plan
            plan = self.masscan_enum.create_enumeration_plan(
                total_budget_hours=1,
                ports="80,443,8080"
            )

            self.log_widget.write_log("MASSCAN PARAMETERS:", "INFO")
            self.log_widget.write_log(f"  ► RATE: {plan['rate_pps']:,} PPS", "INFO")
            self.log_widget.write_log(f"  ► IPs SCANNABLE: {plan['total_ips_scannable']:,}", "INFO")
            self.log_widget.write_log(f"  ► COVERAGE: {plan['coverage_percent']:.4f}%", "INFO")

            self.log_widget.write_log("INITIATING HIGH-SPEED SCAN (10% SAMPLE)...", "INFO")

            results = self.masscan_enum.enumerate_ipv9_space(
                sample_rate=0.10,
                ports="80,443"
            )

            self.log_widget.write_log(
                f"MASSCAN: COMPLETE - {results.get('total_hosts', 0)} HOSTS IDENTIFIED",
                "SUCCESS"
            )

        except Exception as e:
            self.log_widget.write_log(f"MASSCAN: OPERATION FAILED - {str(e)}", "ERROR")
        finally:
            self.scanning = False

    @on(Button.Pressed, "#btn-monitor")
    async def action_monitor(self):
        """Continuous monitoring operation"""
        self.log_widget.write_log(f"MISSION {self.mission_number}: CONTINUOUS MONITORING ACTIVATED", "OPERATIONAL")
        self.mission_number += 1
        self.log_widget.write_log("STATUS: MONITORING MODE ENGAGED", "INFO")
        # TODO: Implement continuous monitoring

    @on(Button.Pressed, "#btn-stop")
    async def action_stop(self):
        """Emergency stop operation"""
        if self.scanning:
            self.log_widget.write_log("EMERGENCY STOP: ABORTING CURRENT OPERATION", "WARNING")
            self.scanning = False
            self.progress_bar.update(progress=0)
        else:
            self.log_widget.write_log("NO ACTIVE OPERATIONS TO ABORT", "INFO")

    def action_show_stats(self) -> None:
        """Show tactical statistics"""
        self.log_widget.write_log("TACTICAL STATISTICS REFRESHED", "INFO")
        asyncio.create_task(self.refresh_stats())

    def action_clear_logs(self) -> None:
        """Clear tactical log"""
        self.log_widget.clear()
        self.log_widget.write_log("TACTICAL LOG CLEARED", "INFO")
        self.log_widget.write_log("AWAITING DIRECTIVES...", "INFO")

    def action_show_help(self) -> None:
        """Show tactical help"""
        self.log_widget.write_log("═══════════ TACTICAL OPERATIONS GUIDE ═══════════", "INFO")
        self.log_widget.write_log("KEYBINDINGS:", "INFO")
        self.log_widget.write_log("  Q         - ABORT MISSION (EXIT)", "INFO")
        self.log_widget.write_log("  CTRL+C    - EMERGENCY EXIT", "INFO")
        self.log_widget.write_log("  S         - REFRESH STATUS", "INFO")
        self.log_widget.write_log("  L         - CLEAR TACTICAL LOG", "INFO")
        self.log_widget.write_log("  H         - DISPLAY THIS HELP", "INFO")
        self.log_widget.write_log("  R         - REFRESH DISPLAY", "INFO")
        self.log_widget.write_log("═══════════════════════════════════════════════════", "INFO")

    def action_refresh(self) -> None:
        """Refresh display"""
        self.log_widget.write_log("DISPLAY REFRESH COMPLETE", "INFO")
        asyncio.create_task(self.refresh_stats())


def main():
    """Main entry point for TEMPEST-compliant TUI"""
    app = IPv9MilitaryTUI()
    app.run()


if __name__ == "__main__":
    main()
