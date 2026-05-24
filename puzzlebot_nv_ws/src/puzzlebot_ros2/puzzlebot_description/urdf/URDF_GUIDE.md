# URDF and Xacro Folder Guide

This folder defines the Puzzlebot robot model using modular xacro files.

## Files and roles

- macros.xacro
  - Shared inertial helper macros for box, cylinder, and sphere.
- sensors_properties.xacro
  - Legacy property definitions for chassis, wheels, caster, and sensors; not currently included by default.
- sensors.xacro
  - Defines the `puzzlebot_sensors` LiDAR macro, including `lidar_base_link`, `laser_frame`, and the Gazebo lidar sensor.
  - Current mounting offsets: `base_link -> lidar_base_link` at `0 0 0.070`, then `lidar_base_link -> laser_frame` at `0 0 0.035`.
- puzzlebot_control.xacro
  - Gazebo plugin macro for diff-drive, sensor systems, and joint state publishing.
- puzzlebot.urdf.xacro
  - Primary robot model file used by launch files; includes the robot links, wheels, caster, sensors, and control plugin.
- puzzlebot.xacro
  - Thin wrapper around `puzzlebot.urdf.xacro` for alternative entry-point use.

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


