# puzzlebot_gazebo Troubleshooting

This guide focuses on simulation startup, bridge mapping, and topic direction issues.

## Prefixes and naming in simulation

If robot/plugin topics are prefixed (for example `robot1/cmd_vel`) but bridge config still expects unprefixed names (`/cmd_vel`), command and sensor flow will break.

Why this matters:
- ros_gz_bridge requires exact topic name matches.
- Prefix changes must be propagated to bridge YAML and navigation configs.

## Common issues and fixes

## 1) Robot does not move on cmd_vel

Possible causes:
- bridge direction or topic name mismatch,
- command is published to `/cmd_vel` but Gazebo listens to prefixed topic.

Check:
- `ros2 topic echo /cmd_vel`
- bridge YAML topic names and directions.

Fix:
- keep `ROS_TO_GZ` for command topics,
- align topic names between plugin output and bridge mapping.

## 2) Sensors or odom missing in ROS 2

Possible causes:
- wrong bridge direction on sensor/state topics,
- wrong message type mapping,
- topic name mismatch after prefix changes.

Fix:
- keep sensor/state flows as `GZ_TO_ROS`,
- verify ros_type and gz_type pairs,
- confirm topic names exactly match producers in Gazebo.

## 3) Time synchronization issues

Possible causes:
- `/clock` bridge missing or broken,
- use_sim_time mismatch across nodes.

Fix:
- ensure `/clock` mapping exists and is `GZ_TO_ROS`,
- set `use_sim_time=true` in simulation/navigation stacks.

## 4) Spawn pose or orientation seems wrong

Possible causes:
- x_pose/y_pose or spawn yaw in launch arguments not matching map/world expectation.

Fix:
- tune spawn values in launch file and retest.

## Value-change guidance

## Changing world physics

In world files, changing update rates, step size, friction, or gravity can affect:
- odometry smoothness,
- controller stability,
- map consistency.

## Changing bridge direction

Direction is not symmetric:
- commands should typically be `ROS_TO_GZ`,
- simulated data should typically be `GZ_TO_ROS`.

Wrong direction usually results in empty topics or ignored commands.

## Safe workflow

1. Launch Gazebo package only.
2. Verify bridge topics are present and active.
3. Test cmd_vel path first.
4. Test scan/odom/tf streams.
5. Then launch higher-level navigation.

## Simulation vs real robot changes

This package is simulation-specific, so most of it is replaced or disabled on hardware.

## What to use in simulation

- Gazebo world and spawn flow.
- ros_gz_bridge topic mappings.
- `/clock` from Gazebo with `use_sim_time=true`.

## What to change for real robot

- Do not launch Gazebo world/spawn nodes.
- Do not rely on ros_gz_bridge as the main data source.
- Replace simulated topics with real driver topics from robot hardware.
- Set `use_sim_time=false` unless you have an external clock source.

## Topic transition examples

- `/scan`
	- Simulation source: Gazebo sensor through bridge.
	- Real source: lidar driver node.
- `/odom`
	- Simulation source: Gazebo diff-drive odometry.
	- Real source: wheel odometry / robot base controller.
- `/joint_states`
	- Simulation source: Gazebo joint state publisher plugin.
	- Real source: hardware interface or robot_state_publisher inputs.

## If simulation settings leak into hardware

- Nav stack may wait for bridged topics that do not exist.
- Timing issues occur if `use_sim_time=true` but no `/clock` is published.
- Command path may fail if expecting Gazebo-side topic names/directions.

## Recommended hardware transition checklist

1. Launch hardware drivers first (lidar, odometry, base control).
2. Confirm `/scan`, `/odom`, `/tf`, and `/cmd_vel` paths end-to-end.
3. Ensure Nav2 configs reference hardware topic names.
4. Keep Gazebo package out of production hardware launch chains.

## Related docs

- config/PARAMETERS.md
- config/CONFIG_GUIDE.md
- launch/LAUNCH_GUIDE.md
- worlds/WORLDS_GUIDE.md

