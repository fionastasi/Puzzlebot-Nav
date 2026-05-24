# puzzlebot_description

This package holds the URDF/Xacro robot description, meshes, and the robot_state_publisher launch file for Puzzlebot. It is shared by simulation and the real robot, and it does not contain Gazebo plugins or hardware drivers directly in the package manifest.

## Package structure

```
puzzlebot_description/
├── urdf/
│   ├── macros.xacro
│   ├── puzzlebot_control.xacro
│   ├── puzzlebot.xacro
│   ├── puzzlebot.urdf.xacro
│   ├── sensors.xacro
│   ├── sensors_properties.xacro
│   └── URDF_GUIDE.md
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

- `puzzlebot.urdf.xacro` is the primary robot model file used by the package launch file.
- `puzzlebot.urdf.xacro` includes `macros.xacro`, `puzzlebot_control.xacro`, and `sensors.xacro`.
- `puzzlebot_control.xacro` contains Gazebo plugin configuration for diff-drive, sensors, and joint state publishing.
- `puzzlebot.xacro` is a thin wrapper around `puzzlebot.urdf.xacro`.
- `sensors_properties.xacro` holds additional sensor and chassis parameter defaults and is not included by default in the main launch path.

The launch file `puzzlebot_description.launch.xml` loads `puzzlebot.urdf.xacro` directly.

## TF tree

The URDF defines these robot frames:

- `base_footprint`
- `base_link`
  - `right_wheel_link`
  - `left_wheel_link`
  - `caster_link`
  - `lidar_base_link`
    - `laser_frame`

## Launch file arguments

| Argument     | Default | Description |
|--------------|---------|-------------|
| `use_sim_time` | `false` | Use the simulation clock on `/clock` |
| `rviz`         | `false` | Start RViz with the package RViz profile |
| `joint_gui`    | `false` | Start `joint_state_publisher_gui` for joint inspection |
| `gazebo`       | `false` | Launch Gazebo and include simulation behavior |

## Simulation-only sections

The following are simulation-only and are relevant when the robot description is used inside Gazebo:

- `puzzlebot_control.xacro` plugins
- `<gazebo>` tags in `sensors.xacro`

## Usage

Launch the robot description and state publisher with:

```bash
ros2 launch puzzlebot_description puzzlebot_description.launch.xml
```

For RViz and joint GUI in simulation workflows, use the corresponding launch arguments.

