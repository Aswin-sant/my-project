"""Collect basic machine diagnostics and print a text or JSON report."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def check_command(command: str) -> dict[str, Any]:
    """Return whether a developer command can be found and its version, if available."""
    path = shutil.which(command)
    result: dict[str, Any] = {"installed": path is not None, "path": path}
    if path:
        try:
            completed = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            output = (completed.stdout or completed.stderr).strip()
            result["version"] = output.splitlines()[0] if output else "Version not reported"
        except (OSError, subprocess.TimeoutExpired):
            result["version"] = "Could not read version"
    return result


def inspect_disk(path: str | Path = ".") -> dict[str, Any]:
    """Return disk usage for the drive containing path."""
    try:
        usage = shutil.disk_usage(Path(path).resolve())
        return {
            "path": str(Path(path).resolve()),
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "error": None,
        }
    except OSError as exc:
        return {
            "path": str(path),
            "total_bytes": None,
            "used_bytes": None,
            "free_bytes": None,
            "free_gb": None,
            "error": str(exc),
        }


def load_config(config_path: str | Path | None) -> dict[str, Any]:
    """Load an optional JSON config and report missing or malformed files clearly."""
    if config_path is None:
        return {"status": "not_requested", "path": None, "data": None, "error": None}

    path = Path(config_path)
    if not path.exists():
        return {"status": "missing", "path": str(path), "data": None,
                "error": "Configuration file does not exist"}
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            return {"status": "malformed", "path": str(path), "data": None,
                    "error": "Configuration JSON must contain an object"}
        return {"status": "valid", "path": str(path), "data": data, "error": None}
    except (json.JSONDecodeError, OSError) as exc:
        return {"status": "malformed", "path": str(path), "data": None, "error": str(exc)}


def collect_diagnostics(config_path: str | Path | None = None) -> dict[str, Any]:
    """Collect system details, environment-variable names, tools, disk, and config status."""
    # For privacy, report environment-variable NAMES, not their values (which may be secrets).
    env_names = sorted(os.environ.keys())
    tools = {name: check_command(name) for name in ("git", "pip", "pytest")}
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "system": {
            "operating_system": platform.system(),
            "os_release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
        },
        "disk": inspect_disk("."),
        "environment": {
            "variable_count": len(env_names),
            "variable_names": env_names,
            "note": "Values are hidden to avoid exposing passwords, tokens, or other secrets.",
        },
        "developer_tools": tools,
        "configuration": load_config(config_path),
    }


def format_text_report(report: dict[str, Any]) -> str:
    """Format the report so it is easy for a person to read."""
    system = report["system"]
    disk = report["disk"]
    lines = [
        "PYTHON SYSTEM DIAGNOSTIC REPORT",
        "=" * 32,
        f"Generated (UTC): {report['generated_at_utc']}",
        "",
        "SYSTEM",
        f"  Operating system : {system['operating_system']} {system['os_release']}",
        f"  Machine          : {system['machine']}",
        f"  Python version   : {system['python_version']}",
        f"  Python executable: {system['python_executable']}",
        "",
        "DISK",
        f"  Checked path: {disk['path']}",
        f"  Total space : {disk['total_bytes']} bytes",
        f"  Used space  : {disk['used_bytes']} bytes",
        f"  Free space  : {disk['free_bytes']} bytes ({disk['free_gb']} GB)",
    ]
    if disk["error"]:
        lines.append(f"  Error       : {disk['error']}")

    lines.extend(["", "DEVELOPER TOOLS"])
    for name, info in report["developer_tools"].items():
        status = "installed" if info["installed"] else "NOT FOUND"
        lines.append(f"  {name}: {status}")
        if info.get("version"):
            lines.append(f"    Version: {info['version']}")
        if info.get("path"):
            lines.append(f"    Path   : {info['path']}")

    config = report["configuration"]
    lines.extend([
        "",
        "CONFIGURATION",
        f"  Status: {config['status']}",
    ])
    if config["path"]:
        lines.append(f"  Path  : {config['path']}")
    if config["error"]:
        lines.append(f"  Error : {config['error']}")

    lines.extend([
        "",
        "ENVIRONMENT",
        f"  Variable count: {report['environment']['variable_count']}",
        "  Variable names are included in JSON; values are hidden for privacy.",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect basic system information and create a diagnostic report."
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text",
        help="Report format (default: text)",
    )
    parser.add_argument(
        "--output", "-o", help="Optional output file; otherwise print to the terminal",
    )
    parser.add_argument(
        "--config", help="Optional JSON configuration file to validate",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = collect_diagnostics(args.config)
    output = (
        json.dumps(report, indent=2, ensure_ascii=False)
        if args.format == "json"
        else format_text_report(report)
    )

    if args.output:
        try:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Error: could not write report: {exc}", file=sys.stderr)
            return 2
        print(f"Report saved to: {args.output}")
    else:
        print(output)

    # A missing or malformed optional config is reported but does not crash the tool.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
