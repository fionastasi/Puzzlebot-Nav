# Launch Folder Guide

This folder contains orchestration launch files for SLAM and Nav2 workflows.

## Files

- slam.launch.xml
  - Full SLAM workflow: starts Gazebo stack and slam_core launch.
- slam_core.launch.xml
  - Starts SLAM Toolbox, RViz, and keyboard teleop node.
- nav2.launch.xml
  - Full navigation workflow: starts Gazebo stack and nav2_core launch.
- nav2_core.launch.xml
  - Includes nav2_bringup bringup_launch.py and starts RViz.

## Why split into full and core launches

- Full launches combine simulation plus navigation/mapping stack.
- Core launches isolate stack internals and parameters for easier reuse.

## Key inputs

- map_path for known-map navigation.
- nav2_params_file and slam_params_file for behavior tuning.
- use_sim_time to sync with Gazebo clock.

