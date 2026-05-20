# puzzlebot_description

This package holds the URDF/Xacro robot description, meshes, and the robot_state_publisher launch file for Puzzlebot. It is shared by simulation and the real robot, and it does not contain Gazebo plugins or hardware drivers.

## Package structure

```
puzzlebot_description/
├── urdf/
│   ├── puzzlebot.xacro
│   ├── puzzlebot.urdf.xacro
│   ├── puzzlebot_control.xacro
│   ├── sensors.xacro
│   ├── wheels.xacro
│   ├── robot_base.xacro
│   └── macros.xacro
├── meshes/
│   ├── Puzzlebot_Jetson_Lidar_Edition_Base.stl
│   ├── Puzzlebot_Wheel.stl
│   ├── Puzzlebot_Caster_Wheel.stl
│   └── RPLidar.stl
├── launch/
│   └── puzzlebot_description.launch.xml
└── rviz/
    └── puzzlebot_description.rviz
```

## URDF architecture

The top-level description is assembled through Xacro includes.

- `puzzlebot.xacro` loads `puzzlebot.urdf.xacro` and `puzzlebot_control.xacro`.
- `puzzlebot.urdf.xacro` includes the core robot structure: `robot_base.xacro`, `wheels.xacro`, `sensors.xacro`, and `macros.xacro`.
- `puzzlebot_control.xacro` contains Gazebo-only plugins for differential drive, joint state publishing, and simulated sensors.

This package is used by both simulation and real robot workflows. The real robot launch bypasses `puzzlebot_control.xacro` by loading `puzzlebot.urdf.xacro` directly.

## TF tree

The URDF defines the robot frame chain in this order:

- `map`
- `odom`
- `base_footprint`
- `base_link`
  - `wheel_l_joint`
  - `wheel_r_joint`
  - `caster_joint`
- `lidar_base_link`
  - `laser_frame`

## Launch file arguments

| Argument     | Default | Description |
|--------------|---------|-------------|
| `use_sim_time` | `false` | Use the simulation clock on `/clock` |
| `rviz`         | `false` | Start RViz with the package RViz profile |
| `joint_gui`    | `false` | Start `joint_state_publisher_gui` for joint inspection |
| `gazebo`       | `false` | Enable any simulation-specific launch behavior |

## Simulation-only sections

The following are simulation-only and must not run on real hardware:

- `puzzlebot_control.xacro` plugins
- `<gazebo>` tags in `sensors.xacro`

## Usage

Launch the robot description and state publisher with:

```bash
ros2 launch puzzlebot_description puzzlebot_description.launch.xml
```

For RViz and joint GUI in simulation workflows, use the corresponding launch arguments.

