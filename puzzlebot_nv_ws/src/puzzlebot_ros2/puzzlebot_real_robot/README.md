# puzzlebot_real_robot

Hardware bringup package for the physical Puzzlebot (Jetson + RPLidar A1 edition).

This package replaces `puzzlebot_gazebo` in the execution flow. Its sole responsibility
is to start all real hardware drivers and connect them to the Nav2 stack. It does not
replace `puzzlebot_description` (URDF/TF) or `puzzlebot_navigation2` (Nav2/SLAM).

---

## Package structure

```
puzzlebot_real_robot/
├── config/
│   ├── nav2_params_real.yaml            — Nav2 parameters tuned for real hardware
│   ├── slam_toolbox_real.yaml           — SLAM Toolbox parameters for real hardware
│   └── robot_hw.yaml                    — Hardware ports, wheel params, frame names
├── launch/
│   ├── real_robot_core.launch.xml       — Hardware bringup (run on Jetson)
│   ├── real_robot_slam.launch.xml       — SLAM mode (run on laptop)
│   └── real_robot_nav2.launch.xml       — Navigation mode (run on laptop)
├── maps/
│   └── (place real environment maps here after running SLAM)
├── scripts/
│   ├── puzzlebot_localization.py        — Odometry from encoder velocities
│   └── puzzlebot_joint_state_publisher.py — Joint states + odom→base_footprint TF
├── CMakeLists.txt
└── package.xml
```

---

## Operating modes

### SLAM — generate a new map

```bash
# On Jetson
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml

# On laptop
ros2 launch puzzlebot_real_robot real_robot_slam.launch.xml

# Save map when done
ros2 run nav2_map_server map_saver_cli -f src/puzzlebot_real_robot/maps/map_real
```

### Navigation — autonomous navigation

```bash
# On Jetson
ros2 launch puzzlebot_real_robot real_robot_core.launch.xml

# On laptop
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml

# Override map if needed
ros2 launch puzzlebot_real_robot real_robot_nav2.launch.xml map_path:=/path/to/map.yaml
```

---

## Node graph

| Node | Subscribes | Publishes |
|---|---|---|
| `puzzlebot_localization` | `/VelocityEncR`, `/VelocityEncL` (Float32) | `/odom` (Odometry) |
| `puzzlebot_joint_state_publisher` | `/odom` (Odometry) | `/joint_states` (JointState), TF `odom→base_footprint` |
| `rplidar_node` | — | `/scan` (LaserScan), frame: `laser_frame` |
| `robot_state_publisher` | — | TF `base_footprint→base_link` and all static transforms |
| `micro_ros_agent` | `/cmd_vel` | `/VelocityEncR`, `/VelocityEncL` |

---

## Physical parameters

These values must be consistent across the URDF, scripts, and config files.

| Parameter | Value | Where used |
|---|---|---|
| Wheel radius | 0.033 m | `puzzlebot_localization.py`, `puzzlebot_joint_state_publisher.py` |
| Wheel separation | 0.16 m | `puzzlebot_localization.py`, `puzzlebot_joint_state_publisher.py` |
| Joint names | `left_wheel_joint`, `right_wheel_joint` | `wheels.xacro`, `puzzlebot_joint_state_publisher.py` |
| LiDAR frame | `laser_frame` | `sensors.xacro`, `real_robot_core.launch.xml` |
| LiDAR port | `/dev/ttyUSB1` | `real_robot_core.launch.xml` |
| micro-ROS port | `/dev/ttyUSB0` | `micro_ros_agent.launch.py` |

Verify ports before launching:

```bash
ls /dev/ttyUSB*
```

---

## Key differences from simulation

| Parameter | Simulation | Real robot |
|---|---|---|
| `use_sim_time` | `true` | `false` |
| `base_frame` (SLAM) | `base_link` | `base_footprint` |
| `transform_tolerance` | 0.2 s | 0.5 s |
| `max_beams` (AMCL) | 36 | 120 |
| `controller_frequency` | 20.0 Hz | 10.0 Hz |
| `desired_linear_vel` | 0.15 m/s | 0.10 m/s |
| Odom source | Gazebo diff-drive plugin | `puzzlebot_localization.py` |
| `/scan` source | Gazebo gpu_lidar plugin | `rplidar_ros` driver |

---

## Simulation-only components

The following must NOT be active when running on real hardware:

- `puzzlebot_control.xacro` — Gazebo diff-drive and joint state publisher plugins
- Any node or launch file from `puzzlebot_gazebo`
- `puzzlebot.xacro` as the URDF entry point (use `puzzlebot.urdf.xacro` directly)

`real_robot_core.launch.xml` already handles this by loading `puzzlebot.urdf.xacro`
directly, bypassing the Gazebo plugin includes.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No `/odom` topic | micro-ROS not connected | Check USB port and run `micro_ros_agent` manually |
| No `/scan` topic | LiDAR port wrong or unplugged | Run `ls /dev/ttyUSB*` and update port in `real_robot_core.launch.xml` |
| TF error: no transform `odom→base_footprint` | `puzzlebot_joint_state_publisher` not running | Check `real_robot_core` launched correctly on Jetson |
| Two sources publishing same TF | Duplicate node active | Ensure Gazebo is not running alongside real robot |
| Robot spins in place | Wheel direction sign wrong | Swap sign of `wr` or `wl` in `puzzlebot_localization.py` |
| AMCL not converging | Bad initial pose | Set initial pose manually in RViz using "2D Pose Estimate" |
| Nav2 transform timeout | TF latency too high | Increase `transform_tolerance` in `nav2_params_real.yaml` |
| `/cmd_vel` published but robot does not move | micro-ROS bridge not forwarding | Verify micro-ROS agent is running and MCU firmware is correct |
| Map misaligned with environment | Map generated with drift | Re-run SLAM and save a new map |
