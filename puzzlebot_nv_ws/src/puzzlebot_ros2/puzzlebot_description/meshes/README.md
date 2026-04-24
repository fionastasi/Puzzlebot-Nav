# Meshes Folder Guide

This folder stores STL meshes used by the robot visuals.

## Files

- Puzzlebot_Jetson_Lidar_Edition_Base.stl
  - Main base body mesh.
- Puzzlebot_Wheel.stl
  - Wheel mesh asset.
- Puzzlebot_Caster_Wheel.stl
  - Caster wheel mesh asset.

## How they are used

- Referenced by xacro/URDF visual elements.
- Rendered in RViz and Gazebo to represent robot appearance.

## Design note

Collision geometry can differ from visual mesh for simpler physics and better simulation performance.
