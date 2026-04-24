# Config Folder Guide

This folder contains core parameter files for SLAM and Nav2.

## Files

- slam_toolbox.yaml
  - SLAM Toolbox parameters for mapping mode.
- nav2_params.yaml
  - AMCL and Nav2 stack parameters.
- PARAMETERS.md
  - Detailed parameter tuning guide and effects.

## Why this folder matters

These files define localization stability, map quality, and planning behavior. Most navigation tuning work happens here.

## Frame-related fields to keep consistent

- map, odom, and base frame names must match your TF tree.
- scan_topic and odom topic names must match the bridged simulation topics.

