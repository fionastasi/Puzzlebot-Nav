#!/usr/bin/env python3
"""
Nav2 Diagnostic Extractor

Standalone diagnostic tool (pure stdlib, no ROS dependencies) that processes
structured JSONL logs from puzzlebot_logger and generates a diagnostic JSON report.

Features:
  - Accepts log file path as argument or auto-picks most recent session
  - Generates diagnostic JSON with detailed status of all nodes/topics/services
  - Performs critical health checks for Nav2 stack
  - Outputs human-readable summary with ANSI color codes
  - Saves detailed report to: ~/.ros/puzzlebot_logs/diagnostic_<timestamp>.json

Usage:
  python3 nav2_diagnostic.py /path/to/session_YYYYMMDD_HHMMSS.jsonl
  python3 nav2_diagnostic.py    # Auto-picks most recent

Output:
  1. Diagnostic JSON: ~/.ros/puzzlebot_logs/diagnostic_<timestamp>.json
  2. Human-readable summary to stdout
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class ANSI:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def find_most_recent_log() -> Path:
    """Find the most recent session log file."""
    log_dir = Path.home() / ".ros" / "puzzlebot_logs"
    if not log_dir.exists():
        raise FileNotFoundError(f"Log directory not found: {log_dir}")
    
    log_files = sorted(log_dir.glob("session_*.jsonl"), reverse=True)
    if not log_files:
        raise FileNotFoundError(f"No session log files found in {log_dir}")
    
    return log_files[0]


def parse_log_file(log_path: Path) -> List[Dict[str, Any]]:
    """Parse JSONL log file."""
    entries = []
    with open(log_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def extract_diagnostics(entries: List[Dict]) -> Dict[str, Any]:
    """Extract diagnostics from log entries."""
    
    # Initialize diagnostic structure
    diagnostic = {
        "session": {
            "start_ts": None,
            "end_ts": None,
            "duration_sec": None,
            "source_file": None,
        },
        "nodes": {},
        "topics": {},
        "critical_checks": {
            "map_received": False,
            "amcl_active": False,
            "tf_map_to_odom": False,
            "scan_publishing": False,
            "odom_publishing": False,
            "global_costmap_publishing": False,
            "local_costmap_publishing": False,
            "nav2_lifecycle_nodes_active": False,
        },
        "errors_summary": [],
        "warnings_summary": [],
        "overall_status": "unknown",
    }
    
    if not entries:
        return diagnostic
    
    # Extract time bounds
    timestamps = [e.get("ts") for e in entries if "ts" in e]
    if timestamps:
        diagnostic["session"]["start_ts"] = min(timestamps)
        diagnostic["session"]["end_ts"] = max(timestamps)
        diagnostic["session"]["duration_sec"] = (
            diagnostic["session"]["end_ts"] - diagnostic["session"]["start_ts"]
        )
    
    # Track nodes and their logs
    nodes_dict: Dict[str, Any] = {}
    topics_dict: Dict[str, Any] = {}
    entity_timestamps: Dict[str, float] = {}
    
    # First pass: collect all entities and their timestamps
    for entry in entries:
        if entry.get("event") in ["startup_snapshot", "new_entity"]:
            entity = entry.get("entity", "")
            entity_type = entry.get("type", "")
            ts = entry.get("ts", 0)
            
            if entity_type == "node":
                key = f"node:{entity}"
                if key not in entity_timestamps:
                    entity_timestamps[key] = ts
            elif entity_type == "topic":
                parts = entity.split(":", 1)
                topic_name = parts[0]
                topic_type = parts[1] if len(parts) > 1 else ""
                key = f"topic:{topic_name}"
                if key not in entity_timestamps:
                    entity_timestamps[key] = ts
                    topics_dict[topic_name] = {
                        "type": topic_type,
                        "first_seen_ts": ts,
                        "status": "publishing",
                    }
    
    # Second pass: collect logs by node
    for entry in entries:
        if "level" in entry:  # This is a log message
            node = entry.get("node", "unknown")
            level = entry.get("level", "")
            msg = entry.get("msg", "")
            ts = entry.get("ts", 0)
            
            if node not in nodes_dict:
                nodes_dict[node] = {
                    "status": "ok",
                    "first_seen_ts": ts,
                    "last_seen_ts": ts,
                    "errors": [],
                    "warnings": [],
                }
            
            nodes_dict[node]["last_seen_ts"] = max(nodes_dict[node]["last_seen_ts"], ts)
            
            if level == "ERROR":
                nodes_dict[node]["errors"].append({"ts": ts, "msg": msg})
                diagnostic["errors_summary"].append({"ts": ts, "node": node, "msg": msg})
            elif level == "WARN":
                nodes_dict[node]["warnings"].append({"ts": ts, "msg": msg})
                diagnostic["warnings_summary"].append({"ts": ts, "node": node, "msg": msg})
            
            if level == "FATAL":
                nodes_dict[node]["status"] = "failed"
    
    # Detect lost entities
    for entry in entries:
        if entry.get("event") == "lost_entity":
            entity = entry.get("entity", "")
            entity_type = entry.get("type", "")
            
            if entity_type == "topic":
                if entity in topics_dict:
                    topics_dict[entity]["status"] = "lost"
    
    diagnostic["nodes"] = nodes_dict
    diagnostic["topics"] = topics_dict
    
    # Perform critical checks
    diagnostic["critical_checks"]["map_received"] = "/map" in topics_dict
    diagnostic["critical_checks"]["scan_publishing"] = "/scan" in topics_dict
    diagnostic["critical_checks"]["odom_publishing"] = "/odom" in topics_dict
    diagnostic["critical_checks"]["global_costmap_publishing"] = (
        "/global_costmap/costmap" in topics_dict
    )
    diagnostic["critical_checks"]["local_costmap_publishing"] = (
        "/local_costmap/costmap" in topics_dict
    )
    
    # Check AMCL
    amcl_present = "/amcl" in nodes_dict
    amcl_errors = False
    if amcl_present:
        amcl_errors = nodes_dict["/amcl"]["status"] == "failed" or any(
            err for err in nodes_dict["/amcl"]["errors"]
        )
    diagnostic["critical_checks"]["amcl_active"] = amcl_present and not amcl_errors
    
    # Check for tf transforms
    tf_issues = False
    for entry in entries:
        if "level" in entry:
            msg = entry.get("msg", "")
            if "Could not find transform" in msg or "waitForTransform" in msg:
                tf_issues = True
                break
    diagnostic["critical_checks"]["tf_map_to_odom"] = not tf_issues
    
    # Check Nav2 lifecycle nodes
    lifecycle_nodes = ["/bt_navigator", "/controller_server", "/planner_server", "/behavior_server"]
    all_active = all(node in nodes_dict for node in lifecycle_nodes)
    diagnostic["critical_checks"]["nav2_lifecycle_nodes_active"] = all_active
    
    # Determine overall status
    critical_checks_pass = all(diagnostic["critical_checks"].values())
    has_fatal = any(
        node_data["status"] == "failed" for node_data in nodes_dict.values()
    )
    has_errors = any(
        node_data["errors"] for node_data in nodes_dict.values()
    )
    
    if has_fatal or not all([
        diagnostic["critical_checks"]["map_received"],
        diagnostic["critical_checks"]["scan_publishing"],
        diagnostic["critical_checks"]["odom_publishing"],
    ]):
        diagnostic["overall_status"] = "failed"
    elif critical_checks_pass and not has_errors:
        diagnostic["overall_status"] = "healthy"
    else:
        diagnostic["overall_status"] = "degraded"
    
    return diagnostic


def print_summary(diagnostic: Dict[str, Any]):
    """Print human-readable diagnostic summary."""
    
    status_color = {
        "healthy": ANSI.GREEN,
        "degraded": ANSI.YELLOW,
        "failed": ANSI.RED,
    }
    
    overall = diagnostic.get("overall_status", "unknown")
    color = status_color.get(overall, ANSI.BLUE)
    
    print(f"\n{ANSI.BOLD}=== Puzzlebot Navigation Diagnostics ==={ANSI.RESET}")
    print(f"Overall Status: {color}{overall.upper()}{ANSI.RESET}")
    
    session = diagnostic.get("session", {})
    if session.get("duration_sec") is not None:
        print(f"Duration: {session['duration_sec']:.2f} seconds")
    
    print(f"\n{ANSI.BOLD}Critical Checks:{ANSI.RESET}")
    for check, status in diagnostic.get("critical_checks", {}).items():
        check_color = ANSI.GREEN if status else ANSI.RED
        check_symbol = "✓" if status else "✗"
        print(f"  {check_color}{check_symbol} {check}{ANSI.RESET}")
    
    nodes = diagnostic.get("nodes", {})
    print(f"\n{ANSI.BOLD}Nodes ({len(nodes)}):{ANSI.RESET}")
    for node_name, node_data in sorted(nodes.items()):
        status_color_node = (
            ANSI.RED if node_data.get("status") == "failed"
            else ANSI.YELLOW if node_data.get("errors")
            else ANSI.GREEN
        )
        print(
            f"  {status_color_node}{node_name}{ANSI.RESET} "
            f"(errors: {len(node_data.get('errors', []))}, "
            f"warnings: {len(node_data.get('warnings', []))})"
        )
    
    topics = diagnostic.get("topics", {})
    print(f"\n{ANSI.BOLD}Topics ({len(topics)}):{ANSI.RESET}")
    for topic_name, topic_data in sorted(topics.items()):
        status_symbol = "✓" if topic_data.get("status") == "publishing" else "✗"
        topic_type = topic_data.get("type", "")
        print(f"  {status_symbol} {topic_name} ({topic_type})")
    
    errors = diagnostic.get("errors_summary", [])
    if errors:
        print(f"\n{ANSI.BOLD}{ANSI.RED}Errors ({len(errors)}):{ANSI.RESET}")
        for err in errors[:10]:
            print(f"  [{err.get('node')}] {err.get('msg', '')[:80]}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    warnings = diagnostic.get("warnings_summary", [])
    if warnings:
        print(f"\n{ANSI.BOLD}{ANSI.YELLOW}Warnings ({len(warnings)}):{ANSI.RESET}")
        for warn in warnings[:5]:
            print(f"  [{warn.get('node')}] {warn.get('msg', '')[:80]}")
        if len(warnings) > 5:
            print(f"  ... and {len(warnings) - 5} more")
    
    print(f"\n{ANSI.BOLD}Diagnostic Report:{ANSI.RESET}")
    log_dir = Path.home() / ".ros" / "puzzlebot_logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diag_file = log_dir / f"diagnostic_{timestamp}.json"
    print(f"  Saved to: {diag_file}")
    print(f"  View: cat {diag_file} | python3 -m json.tool")


def main():
    # Determine log file to process
    if len(sys.argv) > 1:
        log_path = Path(sys.argv[1])
        if not log_path.exists():
            print(f"Error: Log file not found: {log_path}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            log_path = find_most_recent_log()
            print(f"Using most recent log: {log_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Parse log file
    try:
        entries = parse_log_file(log_path)
        if not entries:
            print("Error: No valid log entries found", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error reading log file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract diagnostics
    diagnostic = extract_diagnostics(entries)
    diagnostic["session"]["source_file"] = str(log_path)
    
    # Save diagnostic report
    log_dir = Path.home() / ".ros" / "puzzlebot_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diagnostic_file = log_dir / f"diagnostic_{timestamp}.json"
    
    try:
        with open(diagnostic_file, "w") as f:
            json.dump(diagnostic, f, indent=2)
    except Exception as e:
        print(f"Error writing diagnostic file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print summary
    print_summary(diagnostic)
    print(f"\nRun: cat {diagnostic_file} | python3 -m json.tool")


if __name__ == "__main__":
    main()
