# Navigation Parameters Guide

This file summarizes the most important parameters in `nav2_params.yaml` and `slam_toolbox.yaml`.
It is meant as a quick reference when tuning localization or mapping behavior.

## AMCL / Particle Filter Parameters

AMCL estimates the robot pose on a known map using particles.

| Parameter | What it controls | If you increase it | If you decrease it |
|---|---|---|---|
| `min_particles` | Minimum number of particles | More robustness, slower update | Faster updates, less robustness |
| `max_particles` | Maximum number of particles | Better recovery in hard cases, more CPU | Less CPU, less ability to recover |
| `alpha1` to `alpha5` | Motion noise from odom and turning | Pose estimate becomes less confident, particles spread more | Pose estimate becomes tighter, but may be too optimistic |
| `laser_model_type` | How laser scans are compared with the map | Usually not a numeric tuning change, but different model behavior | Same |
| `laser_max_range` | Maximum laser distance used by AMCL | Farther scan data is considered, but noisy measurements may hurt | Only nearby obstacles are used |
| `laser_min_range` | Minimum laser distance used by AMCL | Very close returns are ignored | More close-range data is used, but may include invalid readings |
| `max_beams` | Number of laser rays used per update | More accurate, slower | Faster, less accurate |
| `z_hit` | Weight for good laser matches | The filter trusts correct measurements more | The filter trusts them less |
| `z_rand` | Weight for random measurements | More tolerance to unexpected readings | Less tolerance to noise |
| `update_min_d` | Minimum translation before AMCL updates | Fewer updates, less CPU | More frequent updates, smoother pose |
| `update_min_a` | Minimum rotation before AMCL updates | Fewer updates during small turns | More frequent updates during small turns |
| `resample_interval` | How often particles are resampled | Less resampling, can keep diversity longer | More frequent resampling, more reactive |
| `transform_tolerance` | TF delay tolerance | More tolerant to timing delays | Stricter timing, may expose TF issues |
| `tf_broadcast` | Whether AMCL publishes map->odom TF | Needed for standard Nav2 localization | Turning it off usually breaks navigation |

### Practical AMCL tuning notes

- If localization feels jumpy, increase `min_particles` and review `alpha1` to `alpha5`.
- If the robot is slow to recover after a wrong pose, increase `max_particles`.
- If CPU usage is high, lower `max_beams` or reduce particle counts.
- If the map is accurate but the pose still drifts, check `laser_max_range`, `z_hit`, and `z_rand`.
- If the robot moves in a very small area, the current low particle counts are reasonable for a small map.

### New Nav2 AMCL support nodes

These two entries were added to the Nav2 config so AMCL can work cleanly inside the Nav2 lifecycle setup.

| Parameter group | What it does | If you change it |
|---|---|---|
| `amcl_map_client` | Lifecycle helper that lets AMCL request or access the map through Nav2 services | If you rename or remove it, AMCL may stop connecting to the map server correctly |
| `amcl_rclcpp_node` | Internal AMCL node wrapper used by Nav2/RCLCPP integration | If you change its runtime settings, you can affect how AMCL is started and managed, but it is usually left alone |

- In practice, these are not the first parameters you tune for localization quality.
- They matter more for startup, lifecycle management, and how Nav2 wires AMCL into the rest of the system.
- For pose quality, tune the main AMCL parameters above first.

## SLAM Toolbox Parameters

SLAM Toolbox builds and updates the map while also estimating robot pose.

| Parameter | What it controls | If you increase it | If you decrease it |
|---|---|---|---|
| `mode` | Operation mode | `mapping` creates/updates a map | Other modes are for localization workflows |
| `map_frame` | Global map frame name | Only change if your TF tree uses another frame name | Same |
| `odom_frame` | Odometry frame name | Only change to match your TF tree | Same |
| `base_frame` | Robot base frame name | Only change to match your robot URDF / TF | Same |
| `scan_topic` | Laser scan topic used by SLAM | Only change if your scan topic differs | Same |
| `transform_publish_period` | How often SLAM publishes transforms | Smoother TF updates, more CPU | Less CPU, slower TF updates |
| `map_update_interval` | How often the map is updated | More frequent map updates, more CPU | Less CPU, slower visible map updates |
| `resolution` | Map resolution in meters per cell | More detail, larger map and more CPU | Smaller map and less detail |
| `max_laser_range` | Maximum usable laser distance | Farther data is used, but distant noise can hurt | Only closer data is used |
| `minimum_time_interval` | Minimum time between SLAM updates | Fewer updates, less CPU | More updates, more responsiveness |
| `tf_buffer_duration` | TF history kept by SLAM | Better tolerance for delays, more memory | Less memory, less tolerance for delays |
| `enable_interactive_mode` | Allows interactive map editing tools | Easier manual interaction while mapping | Less interactive behavior |

### Practical SLAM tuning notes

- If the map looks noisy or unstable, lower `max_laser_range` and increase `minimum_time_interval`.
- If mapping is too slow, reduce `map_update_interval` or `minimum_time_interval`.
- If the map lacks detail, decrease `resolution` carefully, but expect higher CPU and memory use.
- If TF-related warnings appear, check `map_frame`, `odom_frame`, `base_frame`, and `tf_buffer_duration`.

## Costmap Parameters (Global and Local)

Global and local costmaps use many of the same fields, but with different goals.
Global costmap supports long-range planning, while local costmap supports near-obstacle avoidance.

| Parameter | What it controls | If you increase it | If you decrease it |
|---|---|---|---|
| `global_frame` | Frame used as reference for the costmap | Usually only changed to match your TF tree | Wrong value can break planning or transform lookups |
| `robot_base_frame` | Robot frame used for footprint/pose in the map | Usually only changed to match URDF/TF naming | Wrong value causes bad obstacle alignment around robot |
| `resolution` | Cell size in meters | More map detail, more CPU and memory | Less detail, lower CPU and memory |
| `update_frequency` | How often costmap is recomputed | Faster reactions, more CPU usage | Slower reactions, lower CPU usage |
| `publish_frequency` | How often costmap is published for visualization/consumers | Smoother visualization and updates, more bandwidth/CPU | Lower overhead, but less frequent published updates |
| `width` and `height` | Size of the costmap window in meters (user asked width/weight) | Covers more area, more CPU and memory | Covers less area, less CPU and memory |
| `rolling_window` | Whether map window moves with robot | Good for local dynamic planning around robot | Static window; may miss nearby context if robot leaves area |
| `plugins` | Layer stack (static/obstacle/inflation/etc.) | More layers can improve behavior but add compute and complexity | Fewer layers are simpler but may miss needed behavior |

### Costmap tuning notes

- Keep `global_frame: map` for global costmap and `global_frame: odom` for local costmap unless your TF setup is different.
- Use smaller `resolution` for tighter spaces only if your CPU budget allows it.
- Increase `update_frequency` first on local costmap when obstacle avoidance feels delayed.
- Expand `width` and `height` when the local planner cannot see enough around corners.
- Validate plugin order and enabled layers when behavior seems inconsistent.

## NavFnPlanner Key Parameters

NavFnPlanner is the global planner in Nav2. It generates a path on the global costmap.

| Parameter | What it controls | If you increase/enable it | If you decrease/disable it |
|---|---|---|---|
| `tolerance` | How far from the exact goal NavFn can accept as valid | Planner can find a path more easily near blocked goals | Planner is stricter; can fail if goal cell is occupied |
| `use_astar` | Whether NavFn uses A* behavior (`true`) instead of classic Dijkstra (`false`) | Often gives more directed search and faster practical planning | More exhaustive/uniform search behavior |
| `allow_unknown` | Whether path can go through unknown cells | Planner can route through unmapped zones | Planner stays in known free space only |
| `planner_frequency` | How often global plan is recomputed | Faster replanning to map/goal changes, more CPU | Less CPU, but slower response to changes |
| `costmap_resolution` | Effective grid detail used by global planning (from global costmap `resolution`) | Finer paths and obstacle detail, more CPU/memory | Coarser paths, less CPU/memory |

### Where these are configured

- `planner_frequency` is usually set under `planner_server` (in your file this appears as `expected_planner_frequency`).
- `costmap_resolution` comes from `global_costmap.global_costmap.ros__parameters.resolution`.
- `tolerance`, `use_astar`, and `allow_unknown` are typically in the NavFn planner plugin block inside `planner_server` params.

### Practical NavFn tuning notes

- If the goal is close to walls/obstacles and planning fails, increase `tolerance` slightly.
- If planning through unexplored space is unsafe for your project, keep `allow_unknown` disabled.
- If global plans feel stale when obstacles or goals change, raise `planner_frequency` moderately.
- Tune `costmap_resolution` together with map quality; very fine grids can be expensive.

### A* vs Dijkstra

- `A*` is usually faster because it uses a heuristic to guide the search toward the goal.
- `Dijkstra` explores more uniformly and guarantees the shortest path on the grid, but it is often slower.
- In NavFn, `use_astar: true` generally gives quicker planning, while `false` behaves more like classic Dijkstra search.

## Quick Rule of Thumb

- Use SLAM when you are creating or updating a map.
- Use AMCL when the map already exists and you only need localization.
- Increase particle counts and scan usage when pose is unstable.
- Reduce update frequency and beams/rays when CPU is limited.
- Always keep frame names aligned with your URDF and TF tree.
