# puzzlebot_navigation2

Navigation package for Puzzlebot with SLAM Toolbox and Nav2.

## What this package provides

- SLAM workflow for map creation.
- Navigation workflow on a known map (AMCL + Nav2).
- RViz profiles for both modes.
- Central configuration files for AMCL, costmaps, and SLAM.

## Important files

- `launch/slam.launch.xml`: full SLAM mode launch.
- `launch/slam_core.launch.xml`: SLAM core nodes.
- `launch/nav2.launch.xml`: full Nav2 mode launch.
- `launch/nav2_core.launch.xml`: Nav2 bringup and RViz.
- `config/slam_toolbox.yaml`: SLAM parameters.
- `config/nav2_params.yaml`: AMCL/Nav2/costmap parameters.
- `config/PARAMETERS.md`: parameter explanation guide.
- `TROUBLESHOOTING.md`: frame/topic mismatch diagnosis and parameter change impacts.
- `maps/map_maze.yaml`: map metadata used by Nav2.
- `launch/README.md`: launch architecture and full/core flow.
- `config/README.md`: config file roles and consistency notes.
- `maps/README.md`: map artifacts and metadata interpretation.
- `rviz/README.md`: RViz profile purpose by workflow.

## Folder guides

- [launch/README.md](launch/README.md)
- [config/README.md](config/README.md)
- [config/PARAMETERS.md](config/PARAMETERS.md)
- [maps/README.md](maps/README.md)
- [rviz/README.md](rviz/README.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## How to run

SLAM mode (create/update map):

```bash
ros2 launch puzzlebot_navigation2 slam.launch.xml
```

Navigation mode (known map):

```bash
ros2 launch puzzlebot_navigation2 nav2.launch.xml
```

Use a different map path in Nav2 mode:

```bash
ros2 launch puzzlebot_navigation2 nav2.launch.xml map_path:=/absolute/path/to/map.yaml
```

## Key launch snippets

SLAM launcher includes simulation and SLAM core:

```xml
<include file="$(find-pkg-share puzzlebot_gazebo)/launch/puzzlebot_gazebo.launch.xml">
    <arg name="headless" value="$(var headless)"/>
</include>

<include file="$(find-pkg-share puzzlebot_navigation2)/launch/slam_core.launch.xml">
    <arg name="use_sim_time" value="$(var use_sim_time)"/>
    <arg name="slam_params_file" value="$(find-pkg-share puzzlebot_navigation2)/config/slam_toolbox.yaml"/>
    <arg name="rviz_config_path" value="$(find-pkg-share puzzlebot_navigation2)/rviz/slam.rviz" />
</include>
```

Nav2 launcher passes map and params into Nav2 core:

```xml
<arg name="map_path" default="$(find-pkg-share puzzlebot_navigation2)/maps/map_maze.yaml"/>
<arg name="nav2_params_file" default="$(find-pkg-share puzzlebot_navigation2)/config/nav2_params.yaml"/>

<include file="$(find-pkg-share puzzlebot_navigation2)/launch/nav2_core.launch.xml">
    <arg name="map_path" value="$(var map_path)"/>
    <arg name="nav2_params_file" value="$(var nav2_params_file)"/>
    <arg name="rviz_config_path" value="$(find-pkg-share puzzlebot_navigation2)/rviz/nav2.rviz"/>
    <arg name="use_sim_time" value="$(var use_sim_time)"/>
</include>
```

## Parameter definitions (quick)

### SLAM parameters (`config/slam_toolbox.yaml`)

- `mode`: set to `mapping` to build/update map.
- `resolution`: map cell size in meters.
- `max_laser_range`: maximum scan range used by SLAM.
- `map_update_interval`: map refresh interval.
- `minimum_time_interval`: minimum time between SLAM updates.

### AMCL and Nav2 parameters (`config/nav2_params.yaml`)

- `min_particles`, `max_particles`: particle filter robustness vs CPU.
- `alpha1` to `alpha5`: odometry motion noise model.
- `z_hit`, `z_rand`, `max_beams`: laser model behavior.
- `update_min_d`, `update_min_a`: pose update thresholds.
- `local_costmap` and `global_costmap`: local obstacle handling vs global route planning.

### Costmap parameters (most tuned)

- `global_frame`: `map` for global costmap, usually `odom` for local costmap.
- `robot_base_frame`: robot body frame in TF.
- `resolution`: detail vs compute cost.
- `update_frequency`: costmap update speed.
- `publish_frequency`: publication rate for consumers/visualization.
- `width` and `height`: local window size.
- `rolling_window`: if true, local window follows robot.
- `plugins`: active costmap layers.

For deeper explanations and tuning effects, see `config/PARAMETERS.md`.

## Tuning workflow suggestion

- Start with SLAM defaults and verify stable TF + scan data.
- Tune AMCL particle and laser parameters only after map quality is good.
- Tune local costmap update rate and window size before changing global planner settings.

## Notes from the launch files

- `slam.launch.xml` starts `teleop_twist_keyboard` in an `xterm`, so you need `xterm` available when running SLAM mode.
- Both SLAM and Nav2 launches use `use_sim_time:=true` by default so the stack stays synchronized with the Gazebo clock.
- The Nav2 launch passes the map and parameter file into the Nav2 core launch, which keeps the setup easy to swap without editing the launch file itself.
