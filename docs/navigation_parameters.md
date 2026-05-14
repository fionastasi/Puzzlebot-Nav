# Navigation Parameters

This file explains the current navigation-related parameters used by the Puzzlebot ROS 2 workspace.

Current sources:
- [puzzlebot_navigation2/config/nav2_params.yaml](../puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml)
- [puzzlebot_navigation2/config/slam_toolbox.yaml](../puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml)
- [puzzlebot_navigation2/maps/map_maze.yaml](../puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml)
- [puzzlebot_navigation2/launch/nav2.launch.xml](../puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/launch/nav2.launch.xml)
- [puzzlebot_navigation2/launch/slam.launch.xml](../puzzlebot_nv_ws/src/puzzlebot_ros2/puzzlebot_navigation2/launch/slam.launch.xml)

## Navigation Modes

The workspace currently supports two navigation modes:

- AMCL + Nav2: localization against a prebuilt map, then route planning and control.
- SLAM Toolbox: live mapping while driving the robot and building a map.

The standard Nav2 launch uses `nav2_params.yaml` and `map_maze.yaml`. The SLAM launch uses `slam_toolbox.yaml`.

## AMCL Parameters

AMCL is responsible for localization on a known map.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `set_initial_pose` | `true` | Publishes an initial pose estimate when AMCL starts. |
| `initial_pose.x` | `1.35` | Initial robot X position in the map frame. |
| `initial_pose.y` | `0.0` | Initial robot Y position in the map frame. |
| `initial_pose.z` | `0.0` | Initial robot Z position. |
| `initial_pose.yaw` | `3.1416` | Initial heading in radians. |
| `use_sim_time` | `true` | Uses simulation clock instead of wall clock. |
| `alpha1` | `0.05` | Odometry noise from rotation during rotation. |
| `alpha2` | `0.05` | Odometry noise from rotation during translation. |
| `alpha3` | `0.05` | Odometry noise from translation during translation. |
| `alpha4` | `0.05` | Odometry noise from translation during rotation. |
| `alpha5` | `0.02` | Extra noise term used by the differential motion model. |
| `base_frame_id` | `base_link` | Robot base frame used by AMCL. |
| `beam_skip_distance` | `0.5` | Distance threshold for skipping inconsistent laser beams. |
| `beam_skip_error_threshold` | `0.9` | Error threshold that enables beam skipping logic. |
| `beam_skip_threshold` | `0.3` | Fraction of beams that must agree before beam skipping is used. |
| `do_beamskip` | `false` | Disables beam skipping in the current setup. |
| `global_frame_id` | `map` | Global reference frame for localization. |
| `lambda_short` | `0.1` | Weight for the short-range laser model component. |
| `laser_likelihood_max_dist` | `1.0` | Maximum distance used in the likelihood field sensor model. |
| `laser_max_range` | `8.0` | Maximum laser range considered by AMCL. |
| `laser_min_range` | `0.15` | Minimum laser range considered by AMCL. |
| `laser_model_type` | `likelihood_field` | Laser model used for localization. |
| `max_beams` | `36` | Number of laser beams evaluated per update. |
| `max_particles` | `800` | Upper bound on the particle filter size. |
| `min_particles` | `200` | Lower bound on the particle filter size. |
| `odom_frame_id` | `odom` | Odometry reference frame. |
| `pf_err` | `0.05` | Error bound used by the particle filter. |
| `pf_z` | `0.99` | Probability mass used by the particle filter. |
| `recovery_alpha_fast` | `0.0` | Fast recovery term; disabled here. |
| `recovery_alpha_slow` | `0.0` | Slow recovery term; disabled here. |
| `resample_interval` | `1` | Resamples every update cycle. |
| `robot_model_type` | `nav2_amcl::DifferentialMotionModel` | Motion model for a differential-drive robot. |
| `save_pose_rate` | `0.5` | Frequency for saving pose estimates. |
| `sigma_hit` | `0.15` | Standard deviation for the hit component of the laser model. |
| `tf_broadcast` | `true` | Publishes the `map -> odom` transform. |
| `transform_tolerance` | `0.2` | TF lookup tolerance in seconds. |
| `update_min_a` | `0.1` | Minimum angular motion before AMCL updates. |
| `update_min_d` | `0.1` | Minimum linear motion before AMCL updates. |
| `z_hit` | `0.7` | Weight for accurate laser hits. |
| `z_max` | `0.05` | Weight for max-range readings. |
| `z_rand` | `0.2` | Weight for random laser measurements. |
| `z_short` | `0.05` | Weight for unexpectedly short laser readings. |
| `scan_topic` | `scan` | Laser scan topic used by AMCL. |

## BT Navigator Parameters

The behavior tree navigator receives goals and coordinates the overall navigation flow.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `global_frame` | `map` | Global frame for planning and goal evaluation. |
| `robot_base_frame` | `base_link` | Base frame for navigation transforms. |
| `odom_topic` | `/odom` | Odometry topic consumed by navigation components. |
| `bt_loop_duration` | `10` | Behavior tree loop period in milliseconds. |
| `default_server_timeout` | `20` | Timeout used for action server calls. |
| `navigators` | `navigate_to_pose, navigate_through_poses` | Enabled navigator plugins. |

## Controller Server Parameters

The controller server converts planned paths into velocity commands.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `controller_frequency` | `20.0` | Controller update frequency in Hz. |
| `min_x_velocity_threshold` | `0.001` | Minimum forward velocity considered valid. |
| `min_theta_velocity_threshold` | `0.001` | Minimum rotational velocity considered valid. |
| `progress_checker_plugins` | `progress_checker` | Progress checker plugin list. |
| `goal_checker_plugins` | `general_goal_checker` | Goal checker plugin list. |
| `controller_plugins` | `FollowPath` | Active controller plugin list. |
| `progress_checker.required_movement_radius` | `0.5` | Required movement before progress is considered made. |
| `progress_checker.movement_time_allowance` | `10.0` | Time window for progress checking. |
| `general_goal_checker.xy_goal_tolerance` | `0.15` | Position tolerance for goal acceptance. |
| `general_goal_checker.yaw_goal_tolerance` | `0.2` | Heading tolerance for goal acceptance. |
| `general_goal_checker.stateful` | `true` | Keeps goal checker state between updates. |
| `FollowPath.plugin` | `nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController` | Controller implementation used to track paths. |
| `FollowPath.desired_linear_vel` | `0.15` | Nominal forward speed. |
| `FollowPath.lookahead_dist` | `0.4` | Default lookahead distance. |
| `FollowPath.min_lookahead_dist` | `0.3` | Minimum lookahead distance. |
| `FollowPath.max_lookahead_dist` | `0.6` | Maximum lookahead distance. |
| `FollowPath.lookahead_time` | `1.5` | Time-based lookahead scaling. |
| `FollowPath.rotate_to_heading_angular_vel` | `0.8` | Angular speed used for heading alignment. |
| `FollowPath.transform_tolerance` | `0.2` | TF tolerance used by the controller. |
| `FollowPath.use_velocity_scaled_lookahead_dist` | `false` | Disables velocity-scaled lookahead. |
| `FollowPath.min_approach_linear_velocity` | `0.05` | Minimum speed while approaching the goal. |
| `FollowPath.approach_velocity_scaling_dist` | `0.5` | Distance over which approach speed is scaled. |
| `FollowPath.use_collision_detection` | `true` | Enables collision checks. |
| `FollowPath.max_allowed_time_to_collision_up_to_carrot` | `1.0` | Maximum collision prediction horizon. |
| `FollowPath.use_regulated_linear_velocity_scaling` | `true` | Enables linear speed regulation. |
| `FollowPath.use_fixed_curvature_lookahead` | `false` | Uses adaptive rather than fixed curvature lookahead. |
| `FollowPath.curvature_lookahead_dist` | `0.25` | Curvature lookahead distance. |
| `FollowPath.use_cost_regulated_linear_velocity_scaling` | `false` | Disables cost-based speed scaling. |
| `FollowPath.regulated_linear_scaling_min_radius` | `0.9` | Minimum radius for speed regulation. |
| `FollowPath.regulated_linear_scaling_min_speed` | `0.25` | Minimum speed during regulation. |
| `FollowPath.use_rotate_to_heading` | `true` | Enables rotate-to-heading behavior. |
| `FollowPath.allow_reversing` | `false` | Prevents reversing. |
| `FollowPath.rotate_to_heading_min_angle` | `0.785` | Minimum angle before rotate-to-heading activates. |
| `FollowPath.max_angular_accel` | `1.2` | Maximum angular acceleration. |
| `FollowPath.max_robot_pose_search_dist` | `10.0` | Search distance used for robot pose lookup. |

## Planner Server Parameters

The planner server computes paths on the map.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `expected_planner_frequency` | `20.0` | Expected planning rate in Hz. |
| `planner_plugins` | `GridBased` | Active planner plugin list. |
| `GridBased.plugin` | `nav2_navfn_planner::NavfnPlanner` | Global planner implementation. |
| `GridBased.tolerance` | `0.5` | Goal tolerance used by the planner. |
| `GridBased.use_astar` | `false` | Uses Dijkstra-style planning instead of A*. |
| `GridBased.allow_unknown` | `true` | Allows planning through unknown map cells. |

## Behavior Server Parameters

The behavior server provides recovery and utility behaviors.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `behavior_plugins` | `spin, back_up, drive_on_heading, wait` | Enabled recovery behaviors. |
| `local_frame_id` | `odom` | Local reference frame. |
| `global_frame_id` | `map` | Global reference frame. |
| `robot_base_frame` | `base_link` | Robot base frame. |
| `transform_tolerance` | `0.1` | TF tolerance for behavior execution. |
| `simulate_ahead_time` | `2.0` | Time horizon for behavior simulation. |
| `max_rotational_vel` | `1.0` | Maximum rotational speed. |
| `min_rotational_vel` | `0.4` | Minimum rotational speed. |
| `rotational_acc_lim` | `3.2` | Rotational acceleration limit. |

## Local Costmap Parameters

The local costmap tracks nearby obstacles for short-range navigation.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `global_frame` | `odom` | Local costmap frame. |
| `robot_base_frame` | `base_link` | Robot base frame. |
| `rolling_window` | `true` | Keeps the local map centered on the robot. |
| `width` | `3` | Local costmap width in meters. |
| `height` | `3` | Local costmap height in meters. |
| `resolution` | `0.05` | Costmap resolution in meters/cell. |
| `robot_radius` | `0.12` | Robot radius used for obstacle inflation. |
| `plugins` | `obstacle_layer, inflation_layer` | Active local costmap layers. |
| `obstacle_layer.enabled` | `true` | Enables obstacle updates from sensors. |
| `obstacle_layer.observation_sources` | `scan` | Observation source list. |
| `obstacle_layer.scan.topic` | `/scan` | Laser scan topic used by the obstacle layer. |
| `obstacle_layer.scan.max_obstacle_height` | `2.0` | Maximum height for obstacle observations. |
| `obstacle_layer.scan.clearing` | `true` | Enables clearing free space from scans. |
| `obstacle_layer.scan.marking` | `true` | Enables marking obstacles from scans. |
| `obstacle_layer.scan.data_type` | `LaserScan` | Sensor message type. |
| `obstacle_layer.scan.raytrace_max_range` | `3.0` | Maximum clearing raytrace range. |
| `obstacle_layer.scan.raytrace_min_range` | `0.0` | Minimum clearing raytrace range. |
| `obstacle_layer.scan.obstacle_max_range` | `2.5` | Maximum obstacle marking range. |
| `obstacle_layer.scan.obstacle_min_range` | `0.0` | Minimum obstacle marking range. |
| `inflation_layer.cost_scaling_factor` | `3.0` | Rate at which obstacle cost decays. |
| `inflation_layer.inflation_radius` | `0.3` | Radius of inflated obstacle cells. |
| `always_send_full_costmap` | `true` | Sends the full local costmap every update. |

## Global Costmap Parameters

The global costmap is used for long-range planning over the map.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `global_frame` | `map` | Global planning frame. |
| `robot_base_frame` | `base_link` | Robot base frame. |
| `resolution` | `0.05` | Global costmap resolution in meters/cell. |
| `robot_radius` | `0.12` | Robot radius used for planning clearance. |
| `plugins` | `static_layer, obstacle_layer, inflation_layer` | Active global costmap layers. |
| `static_layer.plugin` | `nav2_costmap_2d::StaticLayer` | Loads the static map. |
| `static_layer.map_subscribe_transient_local` | `true` | Subscribes to the map with transient local QoS. |
| `obstacle_layer.enabled` | `true` | Enables obstacle updates from sensors. |
| `obstacle_layer.observation_sources` | `scan` | Observation source list. |
| `obstacle_layer.scan.topic` | `/scan` | Laser scan topic used by the obstacle layer. |
| `obstacle_layer.scan.max_obstacle_height` | `2.0` | Maximum height for obstacle observations. |
| `obstacle_layer.scan.clearing` | `true` | Enables clearing free space from scans. |
| `obstacle_layer.scan.marking` | `true` | Enables marking obstacles from scans. |
| `obstacle_layer.scan.data_type` | `LaserScan` | Sensor message type. |
| `obstacle_layer.scan.raytrace_max_range` | `3.0` | Maximum clearing raytrace range. |
| `obstacle_layer.scan.raytrace_min_range` | `0.0` | Minimum clearing raytrace range. |
| `obstacle_layer.scan.obstacle_max_range` | `2.5` | Maximum obstacle marking range. |
| `obstacle_layer.scan.obstacle_min_range` | `0.0` | Minimum obstacle marking range. |
| `inflation_layer.cost_scaling_factor` | `3.0` | Rate at which obstacle cost decays. |
| `inflation_layer.inflation_radius` | `0.3` | Radius of inflated obstacle cells. |
| `always_send_full_costmap` | `true` | Sends the full global costmap every update. |

## Map Server Parameters

The map server loads the static map used during Nav2 localization.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `yaml_filename` | empty | Map file path is provided at launch. |

## Map Saver Parameters

The map saver stores a map created during SLAM or manual mapping.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `save_map_timeout` | `5.0` | Timeout for saving the map. |
| `free_thresh_default` | `0.25` | Default threshold for free cells when saving maps. |
| `occupied_thresh_default` | `0.65` | Default threshold for occupied cells when saving maps. |

## Lifecycle Manager Parameters

The lifecycle manager brings the navigation nodes up in the correct order.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `autostart` | `true` | Automatically activates managed nodes. |
| `node_names` | `controller_server, planner_server, behavior_server, bt_navigator, map_server, amcl` | Nodes managed by the lifecycle manager. |

## SLAM Toolbox Parameters

These parameters control live mapping with SLAM Toolbox.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `use_sim_time` | `true` | Uses simulation time. |
| `mode` | `mapping` | Runs SLAM Toolbox in mapping mode. |
| `map_frame` | `map` | Global map frame. |
| `odom_frame` | `odom` | Odometry frame. |
| `base_frame` | `base_link` | Robot base frame. |
| `scan_topic` | `/scan` | Laser scan topic used for SLAM. |
| `transform_publish_period` | `0.05` | TF publish period in seconds. |
| `map_update_interval` | `2.0` | Interval between map updates. |
| `resolution` | `0.05` | Map resolution in meters/cell. |
| `max_laser_range` | `12.0` | Maximum laser range used for mapping. |
| `minimum_time_interval` | `0.5` | Minimum time between SLAM updates. |
| `tf_buffer_duration` | `30.0` | TF buffer length in seconds. |
| `enable_interactive_mode` | `true` | Allows interactive editing and mapping operations. |
| `use_scan_matching` | `true` | Enables scan matching. |
| `use_scan_barycenter` | `false` | Disables barycenter-based scan processing. |

## Map Metadata

The static map used by Nav2 is defined in `map_maze.yaml`.

| Parameter | Current value | Purpose |
| --- | --- | --- |
| `image` | `my_map.pgm` | Occupancy grid image file. |
| `resolution` | `0.05` | Map resolution in meters/cell. |
| `origin` | `-1.72, -1.64, 0` | Map origin in world coordinates. |
| `negate` | `0` | Occupancy inversion flag. |
| `occupied_thresh` | `0.65` | Threshold for occupied cells. |
| `free_thresh` | `0.25` | Threshold for free cells. |
| `mode` | `trinary` | Occupancy interpretation mode. |

## Notes

- `nav2.launch.xml` and `slam.launch.xml` mostly select which configuration file is loaded.
- The Nav2 stack uses AMCL for localization, while SLAM Toolbox is used when building a map.
- If you change any config values, regenerate `docs/params.md` if you want the raw parameter table to stay in sync.
