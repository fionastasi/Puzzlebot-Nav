# puzzlebot_description Troubleshooting

This guide focuses on common model and TF problems in the description package.

## Why prefixes exist

Prefixes are used to namespace links, joints, and topics so multiple robots can coexist without name collisions.

In this workspace, the most visible prefix parameter is in:
- urdf/puzzlebot_control.xacro (`params="prefix"`)

If you set a prefix like `robot1/`, generated topic names become:
- `robot1/cmd_vel`
- `robot1/odom`
- `robot1/joint_states`
- `robot1/base_footprint`

## What happens if prefix changes

Changing a prefix in robot control/plugin config without updating the rest of the stack can break:
- bridge mappings (topic name mismatch),
- Nav2/SLAM topic subscriptions,
- TF frame lookups.

Typical symptom:
- topics exist but expected consumers receive no data.

## Common issues and fixes

## 1) Robot appears, but TF is incomplete

Possible causes:
- wrong frame names between description and navigation configs,
- missing base_footprint transform path,
- robot_state_publisher not running with the expected xacro output.

Check:
- `ros2 run tf2_tools view_frames`
- `ros2 run tf2_ros tf2_echo odom base_link`
- `ros2 run tf2_ros tf2_echo odom base_footprint`

Fix:
- keep frame names consistent across xacro, odometry source, AMCL, and costmaps.

## 2) Visual model looks correct, but collisions/physics feel off

Possible causes:
- visual mesh and collision geometry are intentionally different,
- changed dimensions/mass without adjusting inertia assumptions.

Fix:
- when changing size or mass values, keep inertial macros aligned with updated dimensions.

## 3) Joint state GUI runs, but behavior is odd

Possible causes:
- GUI is for manual testing and does not replace real simulation control,
- joint hierarchy mismatch after xacro edits.

Fix:
- validate parent/child joints in xacro files and verify TF tree after edits.

## Value-change guidance

## Changing geometry values

Examples:
- base_length, base_width, base_height
- wheel_radius, wheel_separation, wheel_drop
- lidar_x, lidar_z

Effects:
- changes robot footprint and kinematics assumptions,
- affects turn behavior and planning footprint consistency,
- can require retuning of nav parameters.

## Changing frame names

Examples:
- base_link to custom name,
- base_footprint naming conventions.

Effects:
- requires synchronized updates in Nav2, SLAM, and any TF consumers.

## Safe workflow

1. Edit one group of parameters at a time.
2. Launch description package and verify TF first.
3. Then launch simulation/navigation and verify topic flow.
4. Only then tune navigation behavior.

## Simulation vs real robot changes

The description package itself usually needs few changes between simulation and hardware, but frame and naming consistency still matters.

## What usually stays the same

- Link and joint names in xacro files.
- Main URDF geometry structure.
- Sensor mounting transforms (for example lidar relative to base_link).

## What often changes for real robot

- `use_sim_time`
	- Simulation: `true`
	- Real robot: `false`
- Optional simulation-only plugin/control macros
	- Keep in simulation model path.
	- Exclude or isolate from hardware model path when not needed.
- Prefixes/namespaces
	- If using multi-robot hardware, prefixes may be required and must match all consumer configs.

## If you switch to hardware and forget these

- Leaving `use_sim_time=true` without `/clock` causes stale or invalid timing behavior.
- Frame names that worked in simulation may fail on hardware odometry/localization if base frame naming differs.

## Recommended hardware transition checklist

1. Set `use_sim_time=false` in hardware launches.
2. Verify base frame convention (`base_link` vs `base_footprint`) matches localization and controllers.
3. Confirm sensor frame IDs published by real drivers match the model TF tree.
4. If prefix is used, update all downstream topic and frame references.

## Related docs

- XACRO_OVERVIEW.md
- TF_FRAMES.md
- urdf/README.md
