# puzzlebot_navigation2

This package contains the Nav2 and SLAM stack for Puzzlebot. It provides two pairs of launch files: full simulation launchers that include Gazebo, and core launchers with no Gazebo and no hardware. The core launchers are reused by `puzzlebot_real_robot` for the physical robot.

## Package structure

```
puzzlebot_navigation2/
├── launch/
│   ├── slam.launch.xml       # simulation SLAM includes puzzlebot_gazebo + slam_core
│   ├── slam_core.launch.xml  # SLAM only, no simulation, reused by real robot
│   ├── nav2.launch.xml       # simulation Nav2 includes puzzlebot_gazebo + nav2_core
│   └── nav2_core.launch.xml  # Nav2 only, no simulation, reused by real robot
├── config/
│   ├── slam_toolbox.yaml     # SLAM parameters for simulation
│   └── nav2_params.yaml      # Nav2 parameters for simulation
├── maps/
│   ├── my_map.pgm
│   └── map_maze.yaml         # simulation map files
└── rviz/
    ├── slam.rviz
    └── nav2.rviz
```

## Launch architecture

The package uses a two-layer design.

- Full launchers (`slam.launch.xml`, `nav2.launch.xml`) start simulation and include the Gazebo layer plus the corresponding core layer.
- Core launchers (`slam_core.launch.xml`, `nav2_core.launch.xml`) start only the SLAM or Nav2 stack and are reusable by any bringup.
- `slam_core.launch.xml` accepts `use_sim_time`, `slam_params_file`, and `rviz_config_path`.
- `nav2_core.launch.xml` accepts `use_sim_time`, `nav2_params_file`, `map_path`, and `rviz_config_path`.
- The real robot does not call `slam.launch.xml` or `nav2.launch.xml`; it uses only the `_core` variants.

## Bridge topics

| Topic | Direction | Type |
|-------|-----------|------|
| `/clock` | GZ_TO_ROS | `rosgraph_msgs/msg/Clock` |
| `/cmd_vel` | ROS_TO_GZ | `geometry_msgs/msg/Twist` |
| `/odom` | GZ_TO_ROS | `nav_msgs/msg/Odometry` |
| `/tf` | GZ_TO_ROS | `tf2_msgs/msg/TFMessage` |
| `/joint_states` | GZ_TO_ROS | `sensor_msgs/msg/JointState` |
| `/scan` | GZ_TO_ROS | `sensor_msgs/msg/LaserScan` |

## Key config differences: sim vs real

| Parameter | Simulation | Real |
|-----------|------------|------|
| `use_sim_time` | `true` | `false` |
| `base_frame` | `base_link` | `base_footprint` |
| `transform_tolerance` | `0.2` | `0.5` |
| `max_beams` | `36` | `120` |
| `controller_frequency` | `20.0` | `10.0` |

## Launch file arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `headless` | `false` | Run Gazebo without GUI when true |

## Usage

Use `slam.launch.xml` and `nav2.launch.xml` for full Gazebo-based simulation. For hardware or external bringup, use the `_core` variants instead.

## Simulation-only warning

The full launchers in this package are simulation-only. `slam.launch.xml` and `nav2.launch.xml` depend on `puzzlebot_gazebo`, so they should not be used on real hardware.

