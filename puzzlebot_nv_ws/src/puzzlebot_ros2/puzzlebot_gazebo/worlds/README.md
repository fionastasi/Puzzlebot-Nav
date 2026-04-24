# Worlds Folder Guide

This folder stores Gazebo world definitions for simulation.

## File

- maze.world
  - The main simulation environment used by package launch files.

## What it defines

- Physics and world update settings.
- Ground and lighting.
- Static maze geometry and obstacles.

## Why this matters

World geometry and physics directly affect:
- lidar observations,
- odometry behavior,
- navigation difficulty and map quality.
