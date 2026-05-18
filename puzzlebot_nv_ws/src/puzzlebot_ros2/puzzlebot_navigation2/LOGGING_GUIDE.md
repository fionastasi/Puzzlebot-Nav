# Puzzlebot Structured Logging & Diagnostics System

Complete guide to the structured logging system and diagnostic tools for Puzzlebot Navigation Stack (ROS 2 Humble).

## Overview

The system consists of three components:

1. **puzzlebot_logger.py** - A lifecycle ROS 2 node that captures all system logs
2. **nav2_diagnostic.py** - A standalone diagnostic tool that analyzes logs
3. **Launch integration** - Automatic startup via nav2_core.launch.xml

## Component A: Puzzlebot Logger Node

### What it does

- Subscribes to `/rosout` and captures ALL log messages from every node
- Creates a structured JSONL log file at: `~/.ros/puzzlebot_logs/session_YYYYMMDD_HHMMSS.jsonl`
- Takes startup snapshot of all nodes, topics, and services
- Polls every 2 seconds for new/lost entities
- Gracefully handles shutdown with file flushing
- Implements lifecycle node pattern (CONFIGURE → ACTIVATE → DEACTIVATE → CLEANUP)

### Log File Format

Each line is a valid JSON object. Two types of entries:

**Type 1: Log Messages**
```json
{
  "ts": 1234567890.123,
  "level": "INFO",
  "node": "/amcl",
  "msg": "Received map from map_server",
  "file": "amcl.cpp",
  "line": 456
}
```

**Type 2: Entity Events**
```json
{
  "ts": 1234567890.456,
  "event": "startup_snapshot",
  "type": "node",
  "entity": "/amcl"
}
```

Log levels: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`

### Running the Logger

#### Option 1: Automatic (Recommended)
The logger is automatically started with Nav2:
```bash
ros2 launch puzzlebot_navigation2 nav2.launch.xml
```

Or disable it if needed:
```bash
ros2 launch puzzlebot_navigation2 nav2.launch.xml enable_logging:=False
```

#### Option 2: Manual
Start it directly:
```bash
ros2 run puzzlebot_navigation2 puzzlebot_logger.py
```

As a lifecycle node, you can control it:
```bash
# Configure
ros2 service call /puzzlebot_logger/change_state lifecycle_msgs/srv/ChangeState "{transition: 1}"

# Activate
ros2 service call /puzzlebot_logger/change_state lifecycle_msgs/srv/ChangeState "{transition: 3}"

# Deactivate
ros2 service call /puzzlebot_logger/change_state lifecycle_msgs/srv/ChangeState "{transition: 4}"

# Cleanup
ros2 service call /puzzlebot_logger/change_state lifecycle_msgs/srv/ChangeState "{transition: 5}"
```

## Component B: Nav2 Diagnostic Tool

### What it does

Analyzes a session log and produces a comprehensive diagnostic JSON report with:

- **Session info**: start/end times, duration
- **Node status**: track each node's errors/warnings
- **Topic status**: which topics are publishing/lost
- **Critical checks**: navigation-specific health checks
  - Map received
  - AMCL active
  - Transform tree healthy
  - Scan/odom publishing
  - Costmaps publishing
  - Nav2 lifecycle nodes active
- **Error/warning summaries**
- **Overall status**: healthy / degraded / failed

### Running the Diagnostic

#### Auto-pick most recent log
```bash
python3 nav2_diagnostic.py
```

#### Specify log file
```bash
python3 nav2_diagnostic.py ~/.ros/puzzlebot_logs/session_20260518_123456.jsonl
```

The tool will:
1. Parse the JSONL log
2. Generate diagnostic JSON → `~/.ros/puzzlebot_logs/diagnostic_YYYYMMDD_HHMMSS.json`
3. Print human-readable summary with ANSI colors
4. Show command to pretty-print the JSON

### Diagnostic Output JSON Schema

```json
{
  "session": {
    "start_ts": 1234567890.123,
    "end_ts": 1234567890.999,
    "duration_sec": 0.876,
    "source_file": "/path/to/session_file.jsonl"
  },
  "nodes": {
    "/amcl": {
      "status": "ok|failed",
      "first_seen_ts": 1234567890.123,
      "last_seen_ts": 1234567890.999,
      "errors": [{"ts": 1234567890.5, "msg": "error message"}],
      "warnings": [{"ts": 1234567890.5, "msg": "warning message"}]
    }
  },
  "topics": {
    "/map": {
      "type": "nav_msgs/msg/OccupancyGrid",
      "first_seen_ts": 1234567890.123,
      "status": "publishing|lost"
    }
  },
  "critical_checks": {
    "map_received": true,
    "amcl_active": true,
    "tf_map_to_odom": true,
    "scan_publishing": true,
    "odom_publishing": true,
    "global_costmap_publishing": true,
    "local_costmap_publishing": true,
    "nav2_lifecycle_nodes_active": true
  },
  "errors_summary": [{"ts": 1234567890.5, "node": "/amcl", "msg": "..."}],
  "warnings_summary": [{"ts": 1234567890.5, "node": "/amcl", "msg": "..."}],
  "overall_status": "healthy|degraded|failed"
}
```

### Overall Status Logic

- **healthy**: All critical checks pass AND no FATAL logs AND no node errors
- **degraded**: Critical checks mostly pass but some warnings/errors exist
- **failed**: Any critical check failed OR FATAL log exists OR core services missing

## Component C: Launch Integration

The logger is integrated into `nav2_core.launch.xml` and automatically starts with Nav2.

### How it works

1. **puzzlebot_logger.py** launches as a lifecycle node
2. **lifecycle_manager_logger** automatically manages its state transitions:
   - CONFIGURE: Opens log file, sets up subscriptions
   - ACTIVATE: Starts polling for entities, subscribes to /rosout
   - DEACTIVATE: Stops subscriptions when shutting down
   - CLEANUP: Flushes and closes log file
3. Logger starts BEFORE Nav2 bringup so it captures all boot logs
4. When nav2.launch.xml finishes, logger is already active

### Launch Parameters

```bash
# With logging (default)
ros2 launch puzzlebot_navigation2 nav2.launch.xml

# Disable logging
ros2 launch puzzlebot_navigation2 nav2.launch.xml enable_logging:=False

# With custom map
ros2 launch puzzlebot_navigation2 nav2.launch.xml map_path:=/path/to/map.yaml
```

## Workflow: Logging + Diagnostics

### Typical session:

```bash
# 1. Start logging (automatic with nav2.launch.xml)
ros2 launch puzzlebot_navigation2 nav2.launch.xml

# 2. Let it run while you test navigation
# ... run some nav goals, test behaviors, etc ...

# 3. Stop the launch (Ctrl+C)
# Logger automatically flushes and closes the file

# 4. Run diagnostics on the session
cd ~/ros2_ws/src/puzzlebot_ros2/puzzlebot_navigation2/tools
python3 nav2_diagnostic.py

# 5. View the results
cat ~/.ros/puzzlebot_logs/diagnostic_*.json | python3 -m json.tool
```

## Troubleshooting

### Log file not created

- Ensure `~/.ros/puzzlebot_logs/` directory exists (created automatically)
- Check that nav2.launch.xml runs without `enable_logging:=False`
- Check logger status: `ros2 node list | grep logger`

### Diagnostic tool crashes

- Ensure log file is valid JSONL (check with `head -5 session_file.jsonl`)
- Verify no special characters in node/topic names
- Try with explicit file: `python3 nav2_diagnostic.py /path/to/session_file.jsonl`

### Lifecycle manager not controlling logger

- Verify nav2_lifecycle_manager is installed: `ros2 pkg prefix nav2_lifecycle_manager`
- Check lifecycle node status: `ros2 lifecycle list`
- Check lifecycle transitions: `ros2 lifecycle list puzzlebot_logger`

## File Locations

```
~/.ros/puzzlebot_logs/
  ├── session_20260518_123456.jsonl        # Log from session 1
  ├── session_20260518_234567.jsonl        # Log from session 2
  ├── diagnostic_20260518_123457.json      # Diagnostic from session 1
  └── diagnostic_20260518_234568.json      # Diagnostic from session 2

Workspace:
  puzzlebot_navigation2/
  ├── nodes/
  │   └── puzzlebot_logger.py              # Logger node
  ├── tools/
  │   ├── nav2_diagnostic.py               # Diagnostic tool
  │   └── run_diagnostic.py                # CLI wrapper
  └── launch/
      └── nav2_core.launch.xml             # Updated with logger
```

## Dependencies

### puzzlebot_logger.py
- rclpy
- lifecycle_msgs
- rcl_interfaces
- nav2_lifecycle_manager (for launch integration)
- Standard library: json, os, signal, datetime, pathlib

### nav2_diagnostic.py
- Python 3.8+
- Standard library only (json, sys, pathlib, datetime, typing)
- NO ROS dependencies

## Platform Notes

### Windows + WSL
- Log files created in WSL filesystem at `~/.ros/puzzlebot_logs/`
- Diagnostic tool works identically on WSL and native Windows Python
- Ensure proper line endings (JSONL handles both \n and \r\n)

### Ubuntu
- Works natively; logs stored in user home directory
- ANSI color codes in diagnostic output supported by most terminals

## Advanced Usage

### Batch diagnostics

```bash
# Run diagnostics on all session logs
for log in ~/.ros/puzzlebot_logs/session_*.jsonl; do
  python3 nav2_diagnostic.py "$log"
done
```

### Filtering log entries

```bash
# Extract only ERROR logs
grep '"level": "ERROR"' ~/.ros/puzzlebot_logs/session_*.jsonl

# Find all transforms issues
grep "Could not find transform" ~/.ros/puzzlebot_logs/session_*.jsonl
```

### Custom analysis

```bash
# Load diagnostic JSON in Python
import json
with open('~/.ros/puzzlebot_logs/diagnostic_*.json') as f:
    diagnostic = json.load(f)
    print(diagnostic['overall_status'])
```

## Performance Notes

- Logger adds minimal overhead (~1-2% CPU)
- Log file size typically ~100-500 KB per hour of operation
- Polling every 2 seconds means minimal latency in entity detection
- File writes are buffered (flushed on every write via line buffering)

---

For issues or questions, check the ROS 2 Humble documentation:
- https://docs.ros.org/en/humble/
- https://nav2.readthedocs.io/
