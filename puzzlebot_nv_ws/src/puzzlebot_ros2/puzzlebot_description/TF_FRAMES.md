# Puzzlebot TF Frames Guide

This document describes the actual TF frames used by Puzzlebot and who publishes them.

## Frames in this repo

- `map`
  - Global world frame used by localization and global planning.
  - Produced by SLAM or map-localization nodes, not by the robot URDF.

- `odom`
  - Local odometry reference for the robot pose over time.
  - In simulation, `puzzlebot_control.xacro` / Gazebo diff-drive publishes odometry.
  - On the real robot, the odometry node / joint_state_publisher publishes `odom -> base_footprint`.

- `base_footprint`
  - Planar robot base frame at the floor level.
  - Child of `odom` in the live TF tree.
  - Used by navigation as the robot pose reference in the plane.

- `base_link`
  - Physical robot body frame from the URDF.
  - Published by `robot_state_publisher` from the fixed joint between `base_footprint` and `base_link`.
  - Used by sensors, robot geometry, RViz, and some navigation components.

- `right_wheel_link` / `left_wheel_link` / `caster_link`
  - Wheel and caster frames defined in the URDF.
  - Published by `robot_state_publisher` as child links of `base_link`.

- `lidar_base_link`
  - LiDAR mount link attached to `base_link`.
  - Defined in `sensors.xacro` and published by `robot_state_publisher`.

- `laser_frame`
  - Actual LiDAR beam / scan frame.
  - Child of `lidar_base_link` and referenced by the laser scanner output.

## What publishes these frames

- `robot_state_publisher`
  - Publishes the URDF static transforms for `base_footprint -> base_link` and all child links.
  - This includes wheels, caster, `lidar_base_link`, and `laser_frame`.

- Gazebo diff-drive plugin (`puzzlebot_control.xacro`)
  - Publishes odometry and the transform from `odom` to `base_footprint` in simulation.
  - The plugin also produces joint-state information for the wheel joints.

- `ros_gz_bridge`
  - Bridges Gazebo TF messages into ROS on `/tf`.
  - In this repo, Gazebo TF is mapped into ROS so the robot and navigation stack see the same TF tree.

- Real robot odometry node / joint_state_publisher
  - For real hardware, the code publishes `odom -> base_footprint` from wheel odometry.

- LiDAR driver / sensor plugin
  - Publishes scans in the `laser_frame` coordinate frame.

## What these frames mean

- `base_footprint` is the robot pose for 2D navigation and odometry.
- `base_link` is the robot body frame used for URDF geometry and sensors.
- `laser_frame` is the LiDAR measurement frame.
- `odom` is the moving local frame that carries drift over time.
- `map` is the fixed global frame used by localization and planners.

## Notes for this repo

- The repo uses both `base_footprint` and `base_link` together.
- `base_footprint` is the frame used by the live odometry source.
- `base_link` is the frame used by the robot description and sensors.
- Keep configuration consistent: navigation should use `base_footprint` if the odometry source publishes that frame.

## Quick checks

- `ros2 run tf2_tools view_frames`
- `ros2 run tf2_ros tf2_echo odom base_footprint`
- `ros2 run tf2_ros tf2_echo odom base_link`
- `ros2 run tf2_ros tf2_echo map odom`

If `base_footprint` is missing, navigation or odometry consumers will fail to locate the robot pose.

