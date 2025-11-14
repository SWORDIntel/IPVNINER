"""
Data Exporter

Export IPv9 scan data to various formats.
"""

import json
import csv
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DataExporter:
    """Export data to various formats"""

    @staticmethod
    def to_json(data: Any, output_path: str, indent: int = 2):
        """
        Export data to JSON

        Args:
            data: Data to export
            output_path: Output file path
            indent: JSON indentation
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)

            logger.info(f"Exported to JSON: {output_path}")

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise

    @staticmethod
    def to_csv(data: List[Dict], output_path: str, fieldnames: Optional[List[str]] = None):
        """
        Export data to CSV

        Args:
            data: List of dictionaries
            output_path: Output file path
            fieldnames: CSV column names (auto-detected if None)
        """
        if not data:
            logger.warning("No data to export")
            return

        try:
            # Auto-detect fieldnames
            if not fieldnames:
                fieldnames = list(data[0].keys())

            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"Exported to CSV: {output_path} ({len(data)} rows)")

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise

    @staticmethod
    def to_xml(data: Dict, output_path: str, root_tag: str = "ipv9_data"):
        """
        Export data to XML

        Args:
            data: Data to export
            output_path: Output file path
            root_tag: Root XML tag
        """
        try:
            import xml.etree.ElementTree as ET

            def dict_to_xml(parent, data_dict):
                """Recursively convert dict to XML"""
                for key, value in data_dict.items():
                    if isinstance(value, dict):
                        child = ET.SubElement(parent, str(key))
                        dict_to_xml(child, value)
                    elif isinstance(value, list):
                        for item in value:
                            child = ET.SubElement(parent, str(key))
                            if isinstance(item, dict):
                                dict_to_xml(child, item)
                            else:
                                child.text = str(item)
                    else:
                        child = ET.SubElement(parent, str(key))
                        child.text = str(value)

            root = ET.Element(root_tag)
            dict_to_xml(root, data)

            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)

            logger.info(f"Exported to XML: {output_path}")

        except Exception as e:
            logger.error(f"XML export failed: {e}")
            raise

    @staticmethod
    def to_markdown(data: Dict, output_path: str, title: str = "IPv9 Scan Report"):
        """
        Export data to Markdown report

        Args:
            data: Data to export
            output_path: Output file path
            title: Report title
        """
        try:
            with open(output_path, 'w') as f:
                # Title
                f.write(f"# {title}\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Statistics
                if 'statistics' in data:
                    f.write("## Statistics\n\n")
                    stats = data['statistics']
                    for key, value in stats.items():
                        f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
                    f.write("\n")

                # Findings
                if 'findings' in data:
                    f.write("## Findings\n\n")
                    for finding in data['findings']:
                        severity = finding.get('severity', 'info').upper()
                        f.write(f"### [{severity}] {finding.get('type', 'Unknown')}\n\n")
                        for key, value in finding.items():
                            if key not in ['type', 'severity']:
                                f.write(f"- **{key}**: {value}\n")
                        f.write("\n")

                # Hosts
                if 'hosts' in data:
                    f.write("## Discovered Hosts\n\n")
                    f.write("| IP Address | Hostname | Status | OS |\n")
                    f.write("|------------|----------|--------|----|\n")
                    for host in data['hosts']:
                        f.write(f"| {host.get('ip_address', 'N/A')} | "
                                f"{host.get('hostname', 'N/A')} | "
                                f"{'Alive' if host.get('alive') else 'Down'} | "
                                f"{host.get('os', 'Unknown')} |\n")
                    f.write("\n")

            logger.info(f"Exported to Markdown: {output_path}")

        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            raise

    @staticmethod
    def to_html(data: Dict, output_path: str, title: str = "IPv9 Scan Report"):
        """
        Export data to HTML report

        Args:
            data: Data to export
            output_path: Output file path
            title: Report title
        """
        try:
            with open(output_path, 'w') as f:
                # HTML header
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .stat {{ display: inline-block; margin: 10px 20px 10px 0; padding: 15px; background: #e8f5e9; border-radius: 4px; }}
        .stat-label {{ font-size: 0.9em; color: #666; }}
        .stat-value {{ font-size: 1.5em; font-weight: bold; color: #4CAF50; }}
        .finding {{ margin: 15px 0; padding: 15px; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
        .severity-warning {{ border-left-color: #ff9800; }}
        .severity-error {{ border-left-color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
""")

                # Statistics
                if 'statistics' in data:
                    f.write("<h2>Statistics</h2>\n")
                    stats = data['statistics']
                    for key, value in stats.items():
                        f.write(f'<div class="stat">')
                        f.write(f'<div class="stat-label">{key.replace("_", " ").title()}</div>')
                        f.write(f'<div class="stat-value">{value}</div>')
                        f.write(f'</div>\n')

                # Findings
                if 'findings' in data:
                    f.write("<h2>Findings</h2>\n")
                    for finding in data['findings']:
                        severity = finding.get('severity', 'info')
                        f.write(f'<div class="finding severity-{severity}">\n')
                        f.write(f'<strong>[{severity.upper()}] {finding.get("type", "Unknown")}</strong><br>\n')
                        for key, value in finding.items():
                            if key not in ['type', 'severity']:
                                f.write(f'<em>{key}:</em> {value}<br>\n')
                        f.write('</div>\n')

                # Hosts table
                if 'hosts' in data:
                    f.write("<h2>Discovered Hosts</h2>\n")
                    f.write("<table>\n")
                    f.write("<tr><th>IP Address</th><th>Hostname</th><th>Status</th><th>OS</th></tr>\n")
                    for host in data['hosts']:
                        f.write(f"<tr>")
                        f.write(f"<td>{host.get('ip_address', 'N/A')}</td>")
                        f.write(f"<td>{host.get('hostname', 'N/A')}</td>")
                        f.write(f"<td>{'Alive' if host.get('alive') else 'Down'}</td>")
                        f.write(f"<td>{host.get('os', 'Unknown')}</td>")
                        f.write(f"</tr>\n")
                    f.write("</table>\n")

                # HTML footer
                f.write("""
    </div>
</body>
</html>
""")

            logger.info(f"Exported to HTML: {output_path}")

        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            raise

    @staticmethod
    def export_audit_results(audit_results: Dict, output_dir: str, formats: List[str] = ['json', 'csv', 'html']):
        """
        Export audit results to multiple formats

        Args:
            audit_results: Audit results dictionary
            output_dir: Output directory
            formats: List of formats to export ('json', 'csv', 'xml', 'html', 'markdown')
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"ipv9_audit_{timestamp}"

        exporter = DataExporter()

        try:
            if 'json' in formats:
                exporter.to_json(audit_results, str(output_path / f"{base_name}.json"))

            if 'csv' in formats and 'hosts' in audit_results:
                exporter.to_csv(audit_results['hosts'], str(output_path / f"{base_name}_hosts.csv"))

            if 'xml' in formats:
                exporter.to_xml(audit_results, str(output_path / f"{base_name}.xml"))

            if 'html' in formats:
                exporter.to_html(audit_results, str(output_path / f"{base_name}.html"))

            if 'markdown' in formats:
                exporter.to_markdown(audit_results, str(output_path / f"{base_name}.md"))

            logger.info(f"Exported audit results to {output_dir} in formats: {formats}")

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
