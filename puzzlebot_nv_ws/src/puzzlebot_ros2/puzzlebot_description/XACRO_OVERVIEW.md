# Puzzlebot Xacro Overview

This document explains how xacro is used in this repository:
- how files are organized,
- how robot parts are defined,
- why this modular style is used,
- and how it connects to Gazebo and navigation.

## Scope in this workspace

Xacro files were found only in this package:
- puzzlebot_description

So this is the package-level xacro guide for the project.

## File map and responsibilities

## Entry points

- urdf/puzzlebot.xacro
  - Thin wrapper file.
  - Includes urdf/puzzlebot.urdf.xacro.

- urdf/puzzlebot.urdf.xacro
  - Main composition file.
  - Includes building blocks and instantiates the robot macros.

## Shared utility macros

- urdf/macros.xacro
  - Defines reusable inertial helper macros:
    - box_inertial
    - cylinder_inertial
    - sphere_inertial
  - These compute inertia values from shape and mass.

## Robot components

- urdf/robot_base.xacro
  - Defines macro robot_base.
  - Creates base_link with visual mesh, collision box, and base inertia.

- urdf/wheels.xacro
  - Defines macro puzzlebot_wheels.
  - Creates left and right wheel links + joints.
  - Adds caster link + fixed joint.

- urdf/sensors.xacro
  - Defines macro puzzlebot_sensors.
  - Creates lidar_link + fixed joint to base_link.

## Gazebo/control extensions

- urdf/puzzlebot_control.xacro
  - Defines macro puzzlebot_control.
  - Contains Gazebo system plugin blocks (diff drive, sensors, joint states).
  - Configures control/odometry topic and frame settings for simulation.

Important current state:
- puzzlebot_control.xacro is defined but not currently included or instantiated by puzzlebot.urdf.xacro.
- That means those plugin settings only apply if this macro is explicitly included and called somewhere in the final robot description pipeline.

## How composition works

The model is assembled in urdf/puzzlebot.urdf.xacro by:

1. Including modular files with xacro:include.
2. Calling macros that emit XML blocks into the final URDF.

Current composition calls:
- robot_base
- puzzlebot_wheels
- puzzlebot_sensors

This style keeps each subsystem isolated and easier to maintain.

## Why this architecture is used

## 1) Reuse and parameterization

Each macro accepts parameters with defaults, so dimensions and masses can be tuned without rewriting file structure.

Examples:
- robot_base: base_length, base_width, base_height, base_mass, mesh_scale
- puzzlebot_wheels: wheel_radius, wheel_separation, wheel_mass, caster values
- puzzlebot_sensors: lidar position and mass

## 2) Separation of concerns

- Geometry and links are separated by subsystem.
- Inertial math is centralized in one utility file.
- Gazebo plugin/control concerns are isolated from pure kinematics.

## 3) Better debugging

When one part fails (for example wheel geometry), you can inspect a focused file rather than one very large URDF.

## How it is consumed at runtime

The launch file puzzlebot_description/launch/puzzlebot_description.launch.xml runs:
- robot_state_publisher with robot_description from xacro expansion.

That pipeline is:
1. xacro processes the top-level file.
2. Includes and macros are expanded into a final URDF XML.
3. robot_state_publisher publishes TF from that URDF.

## Frame and naming conventions in xacros

- base_link is defined as the physical body reference frame in robot_base.xacro.
- wheel links and lidar_link are attached to base_link.
- In puzzlebot_control.xacro, odometry child frame is configured as base_footprint.

This is valid, but only if the overall TF chain is consistent across:
- odometry source,
- localization config,
- SLAM config,
- Nav2 config.

See TF_FRAMES.md in this package for detailed frame-by-frame guidance.

## How to add a new component correctly

Recommended pattern:

1. Create a new file in urdf, for example camera.xacro.
2. Define one macro with parameters and sensible defaults.
3. Reuse inertial helpers from macros.xacro.
4. Include the new file in puzzlebot.urdf.xacro.
5. Instantiate the new macro in puzzlebot.urdf.xacro.
6. If simulation plugins are needed, isolate them in a dedicated control/plugin macro file.

## Common pitfalls

- Defining a macro but never instantiating it.
- Using inconsistent frame names between URDF, odometry plugins, and Nav2/SLAM.
- Duplicating inertial formulas in multiple files instead of reusing shared macros.
- Mixing wheel geometry parameters between visual and collision unintentionally.

## Quick checks after editing xacro

1. Launch puzzlebot_description and verify robot appears in RViz.
2. Verify TF tree contains expected links.
3. If running simulation, verify odometry, tf, and joint states topics are active.

## External references

- Xacro tutorial and syntax:
  https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-Xacro-to-Clean-Up-a-URDF-File.html

- URDF XML reference:
  https://wiki.ros.org/urdf/XML

- Robot state publisher package docs:
  https://docs.ros.org/en/humble/p/robot_state_publisher/

- TF frame conventions (REP-105):
  https://www.ros.org/reps/rep-0105.html

