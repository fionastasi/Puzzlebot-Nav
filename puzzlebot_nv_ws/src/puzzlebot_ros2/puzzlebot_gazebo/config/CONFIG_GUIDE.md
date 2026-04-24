# Config Folder Guide

This folder contains Gazebo-ROS bridge configuration.

## Files

- gazebo_bridge.yaml
  - Topic mappings between ROS 2 and Gazebo Transport.
- PARAMETERS.md
  - Full explanation of mapping fields, message types, and directions.

## Why this folder matters

Without these bridge mappings, ROS 2 and Gazebo run as separate systems and do not exchange commands/sensor data.

## Main data flow

- ROS to Gazebo: command topics such as cmd_vel.
- Gazebo to ROS: clock, odometry, TF, joint states, and laser scan.

