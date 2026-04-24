# Maps Folder Guide

This folder stores map artifacts used by Nav2.

## Files

- map_maze.yaml
  - Map metadata file consumed by map_server.
- my_map.pgm
  - Occupancy image referenced by map_maze.yaml.

## How it works

map_maze.yaml points to my_map.pgm and defines:
- resolution,
- origin,
- occupancy/free thresholds,
- interpretation mode.

## Why this matters

Incorrect map metadata (origin, resolution, thresholds) can cause localization offsets, poor planning, or inconsistent obstacle interpretation.

