# Puzzlebot ROS 2 – Navigation Project

## Overview

ROS 2 Humble workspace for the Puzzlebot robot (Jetson + RPLidar A1 edition). Supports both simulation in Gazebo and autonomous navigation on the physical robot using Nav2 and SLAM Toolbox.

The workspace is split into four packages with clear separation between simulation and real hardware:

- `puzzlebot_description` — robot model, URDF/Xacro, TF tree, and visualization.
- `puzzlebot_gazebo` — simulation world, spawning, and Gazebo bridge. **Simulation only.**
- `puzzlebot_navigation2` — SLAM, Nav2, AMCL, maps, and navigation config. Shared by sim and real.
- `puzzlebot_real_robot` — hardware bringup for the physical Puzzlebot. Replaces `puzzlebot_gazebo` in the real robot flow.

## Workspace Structure

```text
puzzlebot_nv_ws/
└── src/
    └── puzzlebot_ros2/
        ├── puzzlebot_description/
        ├── puzzlebot_gazebo/
        ├── puzzlebot_navigation2/
        └── puzzlebot_real_robot/
```

## Quick Links

- [puzzlebot_description README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_description/README.md)
- [puzzlebot_gazebo README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_gazebo/README.md)
- [puzzlebot_navigation2 README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/README.md)
- [puzzlebot_real_robot README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/README.md)
- [Navigation parameters guide](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/PARAMETERS.md)

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo (gz-sim) — simulation only
- SLAM Toolbox
- Nav2
- RViz2
- rplidar_ros — real robot only

## Setup

```bash
cd ~/puzzlebot_nv_ws/src
git clone https://github.com/fionastasi/Puzzlebot-Nav.git
cd ~/puzzlebot_nv_ws
colcon build
source install/setup.bash
```

## Run Flow — Simulation

```bash
# SLAM (generate map)
ros2 launch puzzlebot_navigation2 slam.launch.xml

# Navigation (autonomous)
ros2 launch puzzlebot_navigation2 nav2.launch.xml
```

## Run Flow — Real Robot

```bash
# On the Jetson: start hardware drivers
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml

# On laptop: SLAM mode (generate map of physical environment)
ros2 launch puzzlebot_real_robot real_robot_slam.launch.xml

# On laptop: Navigation mode (autonomous navigation)
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml

# Save map after SLAM
ros2 run nav2_map_server map_saver_cli -f src/puzzlebot_real_robot/maps/map_real
```

## Notes

- Package-level details live in each package README.
- Simulation and real robot use separate config files — do not mix `use_sim_time` values.
- If the map or world changes, regenerate the map with SLAM before running Nav2.
- Real robot uses udev rules for stable USB device naming — see the [real_robot README](puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_real_robot/README.md) for setup.
