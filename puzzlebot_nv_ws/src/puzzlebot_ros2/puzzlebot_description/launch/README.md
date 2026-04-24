# Launch Folder Guide

This folder contains entry launch files for the robot description stack.

## File

- puzzlebot_description.launch.xml
  - Starts robot_state_publisher using xacro-generated robot_description.
  - Optionally starts RViz and joint_state_publisher_gui.
  - Supports use_sim_time for simulation workflows.

## Main parameters

- rviz: enables RViz session when true.
- joint_gui: enables manual joint GUI publisher.
- use_sim_time: binds to simulation clock when true.

## Typical use

- Description-only visualization and TF checks.
- Validating xacro edits before running full simulation or navigation.

## Related docs

- ../urdf/README.md
- ../XACRO_OVERVIEW.md
