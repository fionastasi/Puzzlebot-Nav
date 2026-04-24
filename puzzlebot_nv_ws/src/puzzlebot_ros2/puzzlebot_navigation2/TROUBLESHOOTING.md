# puzzlebot_navigation2 Troubleshooting

This guide focuses on frame consistency, map usage, and parameter changes in SLAM/Nav2.

## Why prefixes and frame names matter here

Navigation depends on exact names for:
- frames (`map`, `odom`, `base_link` or `base_footprint`),
- topics (`/scan`, `/odom`, `/cmd_vel`),
- map path and parameter file paths.

If names change in simulation/description but not in Nav2 config, localization and planning degrade or fail.

## Common issues and fixes

## 1) Nav2 waits forever for transforms

Possible causes:
- mismatch between configured base frame and available TF,
- map/odom/base chain incomplete.

Check:
- frame fields in `config/nav2_params.yaml` and `config/slam_toolbox.yaml`.
- TF availability with tf2 tools.

Fix:
- keep frame names consistent across AMCL, costmaps, SLAM, and odometry source.

## 2) AMCL runs but pose is unstable

Possible causes:
- map metadata mismatch,
- laser range/model parameters too aggressive,
- odometry noise parameters (`alpha1` to `alpha5`) not suitable.

Fix:
- verify map resolution/origin,
- tune AMCL parameters incrementally,
- confirm scan and odom topics are healthy before tuning.

## 3) Robot plans but cannot follow paths reliably

Possible causes:
- local costmap window too small/large,
- update frequencies too low,
- base frame mismatch with robot footprint frame.

Fix:
- tune local costmap resolution, width/height, and update frequency first,
- verify `robot_base_frame` reflects your active TF base.

## 4) Nav2 launches but map is wrong or missing

Possible causes:
- wrong `map_path`,
- YAML points to missing/incorrect image,
- map origin/resolution incompatible with expected environment.

Fix:
- verify `maps/map_maze.yaml` image field and metadata,
- launch with explicit `map_path` to rule out path mistakes.

## Value-change guidance

## Changing frame parameters

Examples:
- AMCL `base_frame_id`, `odom_frame_id`, `global_frame_id`
- costmap `global_frame`, `robot_base_frame`
- SLAM `map_frame`, `odom_frame`, `base_frame`

Effects:
- immediate transform lookup failures if not synchronized.

## Changing scan/odom topic names

Effects:
- AMCL and SLAM stop updating if topics no longer match producers.

## Changing map resolution/origin

Effects:
- localization offset,
- planner behavior changes,
- apparent mismatch between robot and map in RViz.

## Safe tuning sequence

1. Validate TF tree first.
2. Validate scan and odom topics.
3. Validate map metadata.
4. Tune AMCL/SLAM parameters.
5. Tune costmaps and planner/controller behavior.

## Simulation vs real robot changes

The Nav2 stack is similar in both environments, but data sources and timing differ.

## What usually stays the same

- Global Nav2 architecture (AMCL/SLAM, costmaps, planner/controller).
- Most tuning concepts (particle counts, frame consistency, costmap dimensions).

## What must usually change for real robot

- `use_sim_time`
	- Simulation: `true`
	- Real robot: `false`
- Topic names if hardware drivers use different names.
	- Update `scan_topic`, `odom_topic`, and any remapped cmd_vel interfaces.
- Frame IDs if hardware localization/odometry uses different base frame naming.
	- Keep AMCL, SLAM, and costmaps aligned with actual TF.
- Motion/sensor noise parameters often need retuning on real data.
	- Real odometry and lidar noise differ from simulation.

## Map workflow differences

- Simulation maps are often cleaner and easier to localize against.
- Real maps may need more conservative AMCL tuning and filtering.
- If map origin/resolution was created in a different environment, check for alignment offsets.

## If sim config is reused directly on hardware

- Localization may oscillate or diverge due to noise mismatch.
- Planner may appear unstable if odom update behavior differs.
- Transform timeouts occur when frame/topic names do not match real drivers.

## Recommended hardware transition checklist

1. Set `use_sim_time=false` everywhere in Nav2/SLAM launch chains.
2. Confirm hardware `/scan`, `/odom`, and TF frames match config files.
3. Start with conservative AMCL parameters and retune incrementally.
4. Recheck local/global costmap frames and update rates under real sensor load.
5. Validate navigation behavior in a small controlled area before full deployment.

## Related docs

- config/PARAMETERS.md
- config/README.md
- launch/README.md
- maps/README.md
- rviz/README.md
