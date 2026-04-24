# puzzlebot_description

Robot description package for Puzzlebot (URDF/Xacro, meshes, TF tree, and RViz profile).

## What this package provides

- Modular robot model using Xacro includes.
- Robot state publishing from generated URDF.
- Optional RViz and joint state GUI launch options.

## Important files

- `urdf/puzzlebot.urdf.xacro`: top-level robot model.
- `urdf/robot_base.xacro`: base link/body.
- `urdf/wheels.xacro`: wheel links/joints.
- `urdf/sensors.xacro`: sensor links/joints.
- `XACRO_OVERVIEW.md`: xacro architecture, composition flow, conventions, and references.
- `TF_FRAMES.md`: explanation of map/odom/base_footprint/base_link and frame conventions.
- `TROUBLESHOOTING.md`: common issues, prefix/frame impacts, and safe change workflow.
- `urdf/URDF_GUIDE.md`: component-by-component guide for all xacro/URDF files in this folder.
- `launch/LAUNCH_GUIDE.md`: launch behavior, arguments, and usage notes.
- `rviz/RVIZ_GUIDE.md`: RViz profile purpose and workflow usage.
- `meshes/MESHES_GUIDE.md`: mesh assets and how they are used.
- `launch/puzzlebot_description.launch.xml`: launch entry point.
- `rviz/puzzlebot_description.rviz`: RViz profile.

## Folder guides

- [urdf/URDF_GUIDE.md](urdf/URDF_GUIDE.md)
- [launch/LAUNCH_GUIDE.md](launch/LAUNCH_GUIDE.md)
- [rviz/RVIZ_GUIDE.md](rviz/RVIZ_GUIDE.md)
- [meshes/MESHES_GUIDE.md](meshes/MESHES_GUIDE.md)
- [XACRO_OVERVIEW.md](XACRO_OVERVIEW.md)
- [TF_FRAMES.md](TF_FRAMES.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## How to run

```bash
ros2 launch puzzlebot_description puzzlebot_description.launch.xml
```

With RViz and joint GUI:

```bash
ros2 launch puzzlebot_description puzzlebot_description.launch.xml rviz:=true joint_gui:=true
```

## Key launch snippet

```xml
<node pkg="robot_state_publisher" exec="robot_state_publisher" output="screen">
    <param name="robot_description" value="$(command 'xacro $(var urdf_path)')" />
    <param name="use_sim_time" value="$(var use_sim_time)" />
</node>

<node pkg="rviz2" exec="rviz2" output="screen" if="$(var rviz)" args="-d $(var rviz_config_path)">
    <param name="use_sim_time" value="$(var use_sim_time)" />
</node>
```

## Xacro composition snippet

```xml
<xacro:include filename="$(find puzzlebot_description)/urdf/macros.xacro" />
<xacro:include filename="$(find puzzlebot_description)/urdf/robot_base.xacro" />
<xacro:include filename="$(find puzzlebot_description)/urdf/wheels.xacro" />
<xacro:include filename="$(find puzzlebot_description)/urdf/sensors.xacro" />

<xacro:robot_base />
<xacro:puzzlebot_wheels />
<xacro:puzzlebot_sensors />
```

## Launch argument definitions

- `rviz`: opens RViz with package profile when true.
- `joint_gui`: opens `joint_state_publisher_gui` for manual joint testing.
- `use_sim_time`: uses simulation clock (`/clock`) when true.
- `urdf_path`: Xacro path used to generate `robot_description`.
- `rviz_config_path`: RViz config path for robot visualization.

## Tuning notes

- If TF appears static or delayed in simulation, set `use_sim_time:=true`.
- If visualization is heavy for your machine, keep `rviz:=false` in this launch and open RViz only from nav/sim workflows.

