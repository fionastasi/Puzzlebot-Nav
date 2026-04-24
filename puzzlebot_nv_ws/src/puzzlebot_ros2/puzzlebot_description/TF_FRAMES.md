# Puzzlebot TF Frames Guide

This guide explains frame names used in this repository, where each one comes from, why it exists, and how they differ.

## Big picture

In mobile robot navigation, the common TF chain is:

map -> odom -> base_footprint -> base_link -> sensors and wheels

Not every project uses all frames. Some use base_link directly under odom.

## Frame by frame

| Frame | What it represents | Who usually publishes it | Where it appears in this repo |
|---|---|---|---|
| map | Global, world-fixed frame used for localization and global planning | AMCL or SLAM Toolbox | puzzlebot_navigation2/config/nav2_params.yaml, puzzlebot_navigation2/config/slam_toolbox.yaml |
| odom | Local continuous frame from wheel integration, smooth but drifting over time | Gazebo diff drive or wheel odometry node | puzzlebot_description/urdf/puzzlebot_control.xacro, puzzlebot_navigation2/config/nav2_params.yaml, puzzlebot_navigation2/config/slam_toolbox.yaml |
| base_footprint | Robot base projected on the ground plane (ignores body height and often roll/pitch) | Odometry source or dedicated transform publisher | puzzlebot_description/urdf/puzzlebot_control.xacro, puzzlebot_navigation2/config/nav2_params.yaml |
| base_link | Physical robot body frame (3D body reference used by URDF links) | robot_state_publisher (from URDF joints) | puzzlebot_description/urdf/robot_base.xacro, wheels.xacro, sensors.xacro, puzzlebot_navigation2/config/nav2_params.yaml, puzzlebot_navigation2/config/slam_toolbox.yaml |
| lidar_link | Lidar sensor frame | robot_state_publisher | puzzlebot_description/urdf/sensors.xacro |
| left_wheel_link/right_wheel_link | Wheel link frames | robot_state_publisher | puzzlebot_description/urdf/wheels.xacro |

## Why both base_footprint and base_link exist

base_footprint and base_link are related but not identical.

base_footprint:
- Ground-contact reference for planar motion.
- Commonly used by localization for 2D navigation assumptions.
- Usually keeps z near zero and ignores roll/pitch.

base_link:
- True robot body reference frame from URDF.
- Used for sensor mounting geometry and full 3D kinematics.
- Has transforms to lidar_link, wheel links, caster, and other robot parts.

In practice:
- Localization and odom chains often use base_footprint.
- Costmaps, planners, and SLAM often use base_link.
- A transform between base_footprint and base_link is required if both are used.

## What is configured right now in this repo

Current configuration is mixed:

- AMCL uses base_frame_id: base_footprint.
- Nav2 behavior and costmaps use robot_base_frame: base_link.
- SLAM Toolbox uses base_frame: base_link.
- Gazebo diff-drive in puzzlebot_control.xacro sets child_frame_id to base_footprint.
- URDF explicitly defines base_link and child links, but base_footprint is not defined as a URDF link.

This can work only if the TF tree still provides all required transforms at runtime.

## Potential mismatch to watch

If base_footprint is referenced but not available in TF, components that depend on it will warn or fail transform lookups.

Typical symptoms:
- AMCL warnings about missing transform.
- Nav2 waiting on transforms.
- RViz TF tree missing one of map, odom, base_footprint, base_link.

## Recommended conventions

Choose one of these patterns and keep it consistent:

Option A (common in many robots):
- map -> odom -> base_footprint -> base_link
- AMCL base_frame_id: base_footprint
- Nav2 robot_base_frame: base_link
- Ensure base_footprint -> base_link is published

Option B (simpler chain):
- map -> odom -> base_link
- AMCL base_frame_id: base_link
- Nav2 robot_base_frame: base_link
- Do not reference base_footprint anywhere

Either is valid. Consistency matters more than the specific choice.

## How to verify the frames quickly

After launching simulation/navigation:

1. Print available TF frames:
   - ros2 run tf2_tools view_frames
2. Check transform availability:
   - ros2 run tf2_ros tf2_echo odom base_link
   - ros2 run tf2_ros tf2_echo odom base_footprint
   - ros2 run tf2_ros tf2_echo map odom
3. Confirm parameter values match your TF tree:
   - nav2_params.yaml for AMCL and costmaps
   - slam_toolbox.yaml for SLAM

## Practical rule of thumb

- Use base_link for robot geometry and sensors.
- Use base_footprint when you need a planar ground-projected base frame.
- Never leave frame naming half-migrated across AMCL, SLAM, costmaps, and odometry plugins.
