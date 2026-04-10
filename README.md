# Puzzlebot ROS2 – Final Project  
# Simulation, Description, and Autonomous Navigation Workspace

## Team Members
- Member 1 – Student ID – Role  
- Member 2 – Student ID – Role  
- Member 3 – Student ID – Role  

------------------------------------------------------------
1. Project Overview
------------------------------------------------------------

This repository contains all components required to run a Puzzlebot robot in **ROS 2 Humble**, organized into three main packages:

- puzzlebot_description → 3D model, URDF/Xacro, frames, sensors, RViz config.  
- puzzlebot_gazebo → Simulation environment, world file, robot spawning, Gazebo bridge.  
- puzzlebot_navigation2 → SLAM, Nav2, maps, YAML configs, RViz profiles.

This structure is modular, maintainable, and scalable for future development.

------------------------------------------------------------
2. Workspace Structure
------------------------------------------------------------

puzzlebot_ws/
└── src/
    └── puzzlebot_ros2/
        ├── puzzlebot_description/
        ├── puzzlebot_gazebo/
        ├── puzzlebot_navigation2/
        └── README.md

------------------------------------------------------------
3. Requirements
------------------------------------------------------------

Software:
- Ubuntu 22.04  
- ROS 2 Humble  
- Gazebo Classic (gz11)  
- gazebo_ros_pkgs  
- SLAM Toolbox  
- Nav2  
- RViz2  
- Colcon  
- python3-numpy  
- python3-transforms3d  

Clone and build:
cd ~/puzzlebot_ws/src  
git clone <repo>  
cd ~/puzzlebot_ws  
colcon build  
source install/setup.bash  

------------------------------------------------------------
4. Package: puzzlebot_description
------------------------------------------------------------

This package contains the full robot description, including URDF/Xacro files, frames, links, sensors, meshes, and RViz visualization.

Structure:

puzzlebot_description/
├── launch/
│   └── puzzlebot_description.launch.xml
├── meshes/
│   ├── base/
│   ├── wheels/
│   ├── sensors/
│   └── misc/
├── rviz/
│   └── puzzlebot_description.rviz
└── urdf/
    ├── robot_base.xacro
    ├── wheels.xacro
    ├── sensors.xacro
    ├── macros.xacro
    └── puzzlebot.urdf.xacro

Run robot description:
ros2 launch puzzlebot_description puzzlebot_description.launch.xml

------------------------------------------------------------
5. Package: puzzlebot_gazebo
------------------------------------------------------------

This package is responsible for the robot simulation, including the world, bridge configuration, and launch files.

Structure:

puzzlebot_gazebo/
├── config/
│   └── gazebo_bridge.yaml
├── launch/
│   └── puzzlebot_gazebo.launch.xml
└── worlds/
    └── maze.world

Run simulation:
ros2 launch puzzlebot_gazebo puzzlebot_gazebo.launch.xml

------------------------------------------------------------
6. Package: puzzlebot_navigation2
------------------------------------------------------------

This package integrates SLAM, navigation, RViz profiles, and map management.

Structure:

puzzlebot_navigation2/
├── config/
│   ├── nav2_params.yaml
│   └── slam_toolbox.yaml
├── launch/
│   ├── slam.launch.xml
│   └── nav2.launch.xml
├── maps/
│   ├── map_maze.yaml
│   └── map_maze.pgm
├── rviz/
│   ├── slam.rviz
│   └── nav2.rviz
└── scripts/
    ├── set_initial_pose.py
    └── send_goal.py

------------------------------------------------------------
7. SLAM Mode (Map Creation)
------------------------------------------------------------

Start SLAM:
ros2 launch puzzlebot_navigation2 slam.launch.xml

SLAM RViz profile:
rviz2 -d <path>/rviz/slam.rviz

------------------------------------------------------------
8. Navigation Mode (Using Generated Map)
------------------------------------------------------------

Start Nav2:
ros2 launch puzzlebot_navigation2 nav2.launch.xml

Navigation RViz profile:
rviz2 -d <path>/rviz/nav2.rviz

------------------------------------------------------------
9. Tool Versions
------------------------------------------------------------

Ubuntu: 22.04  
ROS 2: Humble  
Gazebo Classic: 11  
SLAM Toolbox: Humble version  
Nav2: Humble version  
RViz2: Included with Humble  
Python: 3.10  
Colcon: Latest  

------------------------------------------------------------
10. Recommended Workflow
------------------------------------------------------------

1. Load Robot Description  
ros2 launch puzzlebot_description puzzlebot_description.launch.xml

2. Run Simulation  
ros2 launch puzzlebot_gazebo puzzlebot_gazebo.launch.xml

3. SLAM Mode  
ros2 launch puzzlebot_navigation2 slam.launch.xml

4. Navigation Mode  
ros2 launch puzzlebot_navigation2 nav2.launch.xml

------------------------------------------------------------
11. Final Notes
------------------------------------------------------------

- Each package may include its own README.md for clarity.  
- The workspace organization is clean and maintainable.  
- If the world is modified, regenerate the map using SLAM.  
