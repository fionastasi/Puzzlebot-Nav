# Puzzlebot ROS2 – Final Project

## Overview

This repository contains the full ROS 2 workspace used for the Puzzlebot project. It brings together the robot model, the simulation environment, and the navigation stack needed to build, test, and run Puzzlebot in a consistent way.

The workspace is organized so each part of the system stays focused: `puzzlebot_description` defines the robot, `puzzlebot_gazebo` runs the simulation, and `puzzlebot_navigation2` handles SLAM and autonomous navigation. Together, they support the full workflow from visualization and simulation to map creation and goal-based navigation.

ROS 2 Humble workspace for the Puzzlebot robot, split into three packages:

- `puzzlebot_description`: robot model, URDF/Xacro, and visualization.
- `puzzlebot_gazebo`: simulation world, spawning, and Gazebo bridge.
- `puzzlebot_navigation2`: SLAM, Nav2, maps, and navigation config.

## Quick Links

- [puzzlebot_description README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_description/README.md)
- [puzzlebot_gazebo README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_gazebo/README.md)
- [puzzlebot_navigation2 README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/README.md)
- [Navigation parameters guide](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/PARAMETERS.md)
- [Nav2 parameters file](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml)
- [SLAM parameters file](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml)

## Workspace Structure

```text
puzzlebot_nv_ws/
└── src/
    └── puzzlebot_ros2/
        ├── puzzlebot_description/
        ├── puzzlebot_gazebo/
        └── puzzlebot_navigation2/
```

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic (gz11)
- SLAM Toolbox
- Nav2
- RViz2

## Basic Setup

```bash
cd ~/puzzlebot_nv_ws/src
git clone <repo>
cd ~/puzzlebot_nv_ws
colcon build
source install/setup.bash
```

## Run Flow

1. Robot description: `ros2 launch puzzlebot_description puzzlebot_description.launch.xml`
2. Simulation: `ros2 launch puzzlebot_gazebo puzzlebot_gazebo.launch.xml`
3. SLAM: `ros2 launch puzzlebot_navigation2 slam.launch.xml`
4. Navigation: `ros2 launch puzzlebot_navigation2 nav2.launch.xml`

## Notes

- Package-level details, snippets, and parameter explanations live in each package README.
- Use the navigation parameter guide for tuning AMCL, SLAM, costmaps, and NavFn planner settings.
- If the map or world changes, regenerate the map with SLAM before running Nav2.