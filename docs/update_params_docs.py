#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[1]))


def workspace_root() -> Path:
    return Path(os.environ.get("WORKSPACE_ROOT", repo_root() / "puzzlebot_nv_ws"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def scalar_to_str(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(scalar_to_str(item) for item in value)
    return str(value)


def walk_yaml(data, prefix: str = ""):
    if isinstance(data, dict):
        for key, value in data.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_yaml(value, next_prefix)
    elif isinstance(data, list):
        yield prefix, scalar_to_str(data)
    else:
        yield prefix, scalar_to_str(data)


def parse_yaml_rows(path: Path):
    try:
        data = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        return [(f"YAML parse error in {path.name}", str(exc), path.relative_to(workspace_root()).as_posix())]
    rows = []
    if isinstance(data, dict):
        for parameter, value in walk_yaml(data):
            if parameter and value != "":
                rows.append((parameter, value, path.relative_to(workspace_root()).as_posix()))
    return rows


def parse_xacro_rows(path: Path):
    text = read_text(path)
    rows = []
    for match in re.finditer(r'<xacro:macro\s+name="([^"]+)"\s+params="([^"]*)"', text):
        macro_name = match.group(1)
        for token in match.group(2).split():
            if ":=" in token:
                name, value = token.split(":=", 1)
            else:
                name, value = token, ""
            rows.append((f"{macro_name}.{name}", value, path.relative_to(workspace_root()).as_posix()))
    for match in re.finditer(r'<xacro:args\s+name="([^"]+)"(?:\s+default="([^"]*)")?', text):
        rows.append((match.group(1), match.group(2) or "", path.relative_to(workspace_root()).as_posix()))
    return rows


def collect_rows():
    root = workspace_root()
    rows = []
    for path in sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml")):
        rows.extend(parse_yaml_rows(path))
    for path in sorted(root.rglob("*.xacro")):
        rows.extend(parse_xacro_rows(path))
    return rows


def main() -> int:
    docs_dir = repo_root() / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    rows = collect_rows()
    rows.sort(key=lambda item: (item[2], item[0]))

    lines = [
        "# Workspace Parameters",
        "",
        "Generated from YAML and XACRO sources under `puzzlebot_nv_ws/`.",
        "",
        "| Parameter | Value | File |",
        "| --- | --- | --- |",
    ]

    for parameter, value, file_name in rows:
        safe_parameter = parameter.replace("|", "\\|")
        safe_value = value.replace("|", "\\|")
        safe_file = file_name.replace("|", "\\|")
        lines.append(f"| {safe_parameter} | {safe_value} | {safe_file} |")

    output_path = docs_dir / "params.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())