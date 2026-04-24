# Launch Folder Guide

This folder contains the main simulation launch entry point.

## File

- puzzlebot_gazebo.launch.xml
  - Starts Gazebo with the selected world.
  - Includes puzzlebot_description launch to publish robot_description.
  - Spawns robot into Gazebo with ros_gz_sim create.
  - Starts ros_gz_bridge parameter_bridge with config/gazebo_bridge.yaml.

## Main parameters

- world: selected SDF world file.
- headless: run with reduced graphics stack when true.
- x_pose, y_pose: initial spawn position.
- use_sim_time: enables synchronization with simulation clock.
