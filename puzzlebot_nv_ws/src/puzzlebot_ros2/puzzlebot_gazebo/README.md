# puzzlebot_gazebo

Simulation package for Puzzlebot in Gazebo (world launch, robot spawn, ROS<->Gazebo bridge).

## What this package provides

- Loads the simulation world.
- Spawns Puzzlebot from `robot_description`.
- Bridges critical topics (`/cmd_vel`, `/scan`, `/odom`, `/tf`, `/clock`).

## Important files

- `worlds/maze.world`: Gazebo world.
- `launch/puzzlebot_gazebo.launch.xml`: simulation launch.
- `config/gazebo_bridge.yaml`: bridge topic mappings.
- `config/PARAMETERS.md`: detailed explanation of bridge parameters, topic origins, and directions.
- `TROUBLESHOOTING.md`: common simulation/bridge failures and impact of prefix/value changes.
- `config/README.md`: overview of bridge config files and data flow.
- `launch/README.md`: launch orchestration and argument behavior.
- `worlds/README.md`: simulation world structure and purpose.

## Folder guides

- `config/README.md`
- `config/PARAMETERS.md`
- `launch/README.md`
- `worlds/README.md`
- `TROUBLESHOOTING.md`

## How to run

Standard simulation:

```bash
ros2 launch puzzlebot_gazebo puzzlebot_gazebo.launch.xml
```

Headless simulation:

```bash
ros2 launch puzzlebot_gazebo puzzlebot_gazebo.launch.xml headless:=true
```

## Key launch snippet

```xml
<include file="$(var puzzlebot_description_path)">
    <arg name="use_sim_time" value="$(var use_sim_time)"/>
    <arg name="rviz" value="false"/>
    <arg name="gazebo" value="false"/>
</include>

<node pkg="ros_gz_sim" exec="create" output="screen"
      args="-name puzzlebot -topic robot_description -x $(var x_pose) -y $(var y_pose) -z 0.01 -Y 3.1416"/>

<node pkg="ros_gz_bridge" exec="parameter_bridge" output="screen">
    <param name="config_file" value="$(var gazebo_bridge_path)"/>
</node>
```

## Bridge configuration snippet

```yaml
- ros_topic_name: "/cmd_vel"
  gz_topic_name: "/cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ

- ros_topic_name: "/scan"
  gz_topic_name: "/scan"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS
```

## Launch argument definitions

- `world`: world file loaded by Gazebo.
- `headless`: runs without GUI when true.
- `x_pose`, `y_pose`: initial robot pose at spawn.
- `use_sim_time`: enables `/clock` synchronization.
- `gazebo_bridge_path`: bridge YAML file path.

## Tuning notes

- If robot appears in a wrong place, adjust `x_pose` and `y_pose`.
- If command velocity works but sensors do not, verify `gazebo_bridge.yaml` mappings and topic names.
- For CI or low-resource runs, prefer `headless:=true`.

## Notes from the launch file

- The launch file includes a commented headless Gazebo block that uses `-s` for server-only mode.
- That mode can improve performance on low-resource systems because it avoids the GUI.
- In practice, use `headless:=true` when you want a lighter simulation run.
