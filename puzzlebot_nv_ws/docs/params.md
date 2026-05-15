# Workspace Parameters

Generated from YAML and XACRO sources under `puzzlebot_nv_ws/`.

| Parameter | Value | File |
| --- | --- | --- |
| box_inertial.mass |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| box_inertial.x |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| box_inertial.y |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| box_inertial.z |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| cylinder_inertial.length |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| cylinder_inertial.mass |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| cylinder_inertial.radius |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| sphere_inertial.mass |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| sphere_inertial.radius |  | src/puzzlebot_ros2/puzzlebot_description/urdf/macros.xacro |
| prefix |  | src/puzzlebot_ros2/puzzlebot_description/urdf/puzzlebot.xacro |
| robot_base.base_height | 0.06 | src/puzzlebot_ros2/puzzlebot_description/urdf/robot_base.xacro |
| robot_base.base_length | 0.24 | src/puzzlebot_ros2/puzzlebot_description/urdf/robot_base.xacro |
| robot_base.base_mass | 1.5 | src/puzzlebot_ros2/puzzlebot_description/urdf/robot_base.xacro |
| robot_base.base_width | 0.16 | src/puzzlebot_ros2/puzzlebot_description/urdf/robot_base.xacro |
| robot_base.mesh_scale | 0.001 | src/puzzlebot_ros2/puzzlebot_description/urdf/robot_base.xacro |
| puzzlebot_sensors.lidar_mass | 0.05 | src/puzzlebot_ros2/puzzlebot_description/urdf/sensors.xacro |
| puzzlebot_sensors.lidar_x | 0.06 | src/puzzlebot_ros2/puzzlebot_description/urdf/sensors.xacro |
| puzzlebot_sensors.lidar_z | 0.055 | src/puzzlebot_ros2/puzzlebot_description/urdf/sensors.xacro |
| puzzlebot_wheels.caster_mass | 0.02 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.caster_radius | 0.015 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.caster_x | -0.08 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.wheel_drop | 0.03 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.wheel_mass | 0.08 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.wheel_radius | 0.033 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.wheel_separation | 0.16 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| puzzlebot_wheels.wheel_width | 0.012 | src/puzzlebot_ros2/puzzlebot_description/urdf/wheels.xacro |
| amcl.ros_parameters.scan_topic | scan | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| amcl.ros_parameters.z_short | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| amcl_map_client.ros__parameters.use_sim_time | false | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| amcl_rclcpp_node.ros__parameters.use_sim_time | false | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| behavior_server.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| bt_navigator.ros__parameters.global_frame | map | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| bt_navigator.ros__parameters.odom_topic | /odom | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| bt_navigator.ros__parameters.robot_base_frame | base_link | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| bt_navigator.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| controller_server.ros__parameters.controller_frequency | 20.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| controller_server.ros__parameters.min_theta_velocity_threshold | 0.001 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| controller_server.ros__parameters.min_x_velocity_threshold | 0.001 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| controller_server.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| global_costmap.global_costmap.ros__parameters.global_frame | map | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| global_costmap.global_costmap.ros__parameters.resolution | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| global_costmap.global_costmap.ros__parameters.robot_base_frame | base_link | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| global_costmap.global_costmap.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| lifecycle_manager_navigation.ros__parameters.autostart | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| lifecycle_manager_navigation.ros__parameters.node_names | controller_server, planner_server, behavior_server, bt_navigator, map_server | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| lifecycle_manager_navigation.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.global_frame | odom | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.height | 5.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.resolution | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.robot_base_frame | base_link | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.rolling_window | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| local_costmap.local_costmap.ros__parameters.width | 5.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| map_server.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| planner_server.ros__parameters.expected_planner_frequency | 20.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| planner_server.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/nav2_params.yaml |
| slam_toolbox.ros__parameters.base_frame | base_link | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.enable_interactive_mode | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.map_frame | map | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.map_update_interval | 2.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.max_laser_range | 12.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.minimum_time_interval | 0.5 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.mode | mapping | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.odom_frame | odom | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.resolution | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.scan_topic | /scan | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.tf_buffer_duration | 30.0 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.transform_publish_period | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| slam_toolbox.ros__parameters.use_sim_time | true | src/puzzlebot_ros2/puzzlebot_navigation2/config/slam_toolbox.yaml |
| free_thresh | 0.25 | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| image | my_map.pgm | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| mode | trinary | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| negate | 0 | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| occupied_thresh | 0.65 | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| origin | -1.72, -1.64, 0 | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
| resolution | 0.05 | src/puzzlebot_ros2/puzzlebot_navigation2/maps/map_maze.yaml |
