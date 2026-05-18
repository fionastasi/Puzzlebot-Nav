#!/usr/bin/env python3
"""
Puzzlebot Logger - Simple CLI Wrapper

This wrapper script makes it easier to run the diagnostic tool.
It can be placed in a bin/ directory or called directly.

Usage:
  python3 run_diagnostic.py
  python3 run_diagnostic.py /path/to/session_YYYYMMDD_HHMMSS.jsonl
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Get the tools directory
    tools_dir = Path(__file__).parent
    diagnostic_script = tools_dir / "nav2_diagnostic.py"
    
    if not diagnostic_script.exists():
        print(f"Error: nav2_diagnostic.py not found at {diagnostic_script}", file=sys.stderr)
        sys.exit(1)
    
    # Pass through all arguments
    cmd = [sys.executable, str(diagnostic_script)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
