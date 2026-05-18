# URDF and Xacro Folder Guide

This folder defines the Puzzlebot robot model using modular xacro files.

## Files and roles

- macros.xacro
  - Shared inertial helper macros for box, cylinder, and sphere.
- robot_base.xacro
  - Base body link and its collision/visual/inertial settings.
- wheels.xacro
  - Left and right wheel links, joints, and caster assembly.
- sensors.xacro
  - Lidar link and fixed mounting joint to base_link.
  - Current mounting offsets: `base_link -> lidar_base_link` at `0.06 0 0.055`, then `lidar_base_link -> laser_frame` at `0 0 0.021`.
- puzzlebot_control.xacro
  - Gazebo system plugin macro for diff-drive, sensors, and joint states.
- puzzlebot.urdf.xacro
  - Main composition file that includes and instantiates model macros.
- puzzlebot.xacro
  - Thin wrapper include around puzzlebot.urdf.xacro.

## How it works

1. A launch file runs xacro on the top-level robot file.
2. xacro expands includes and macro calls.
3. The generated URDF is passed to robot_state_publisher.
4. robot_state_publisher publishes TF for the link tree.

## Why this structure is used

- Keeps robot parts modular and easier to tune.
- Reuses inertial formulas in one place.
- Separates pure robot geometry from simulation plugin details.

## Important note

puzzlebot_control.xacro defines simulation plugin behavior, but it must be included and macro-called in the active robot description path to take effect.

## Related docs

- ../XACRO_OVERVIEW.md
- ../TF_FRAMES.md

