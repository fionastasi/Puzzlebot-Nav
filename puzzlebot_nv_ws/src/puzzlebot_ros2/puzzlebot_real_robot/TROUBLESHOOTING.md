# Troubleshooting Guide - Puzzlebot Real Robot

Comprehensive debugging guide for common issues in hardware bringup.

## Issue Categories

1. [Hardware Connectivity](#hardware-connectivity)
2. [Odometry & TF](#odometry--tf)
3. [SLAM Mapping](#slam-mapping)
4. [Navigation](#navigation)
5. [Performance & Tuning](#performance--tuning)

---

## Hardware Connectivity

### Motor Controller Not Responding

**Symptoms:**
- Motor doesn't move when sending `/cmd_vel`
- Motor controller node crashes or won't start
- Serial port permission errors

**Debugging Steps:**

1. **Check port exists and is accessible:**
   ```bash
   ls -la /dev/ttyUSB*
   
   # If no permission:
   sudo usermod -a -G dialout $USER
   # Then log out and log back in
   ```

2. **Verify motor controller is running:**
   ```bash
   ros2 node list | grep motor
   ```

3. **Check for error messages:**
   ```bash
   ros2 launch puzzlebot_real_robot real_robot_core.launch.xml 2>&1 | grep -i error
   ```

4. **Test serial connection manually:**
   ```bash
   # Install minicom if needed
   sudo apt install minicom
   minicom -D /dev/ttyUSB0 -b 115200
   
   # Send test command to motor controller
   # (depends on your motor protocol)
   ```

5. **Verify config/robot_hw.yaml has correct port:**
   ```yaml
   motor_port: /dev/ttyUSB0  # Match actual port
   motor_baudrate: 115200     # Match motor controller speed
   ```

**Solution:**
- Update port name in `config/robot_hw.yaml`
- Check motor controller firmware/settings
- Verify USB cable connection
- Add user to dialout group (see above)

---

### Lidar Not Publishing Data

**Symptoms:**
- No `/scan` topic appearing
- RViz shows no laser scan visualization
- Lidar driver crashes

**Debugging Steps:**

1. **Check lidar driver is running:**
   ```bash
   ros2 node list | grep lidar
   ```

2. **Monitor scan topic:**
   ```bash
   ros2 topic echo /scan | head -20
   ```

3. **Check lidar connection:**
   ```bash
   ls -la /dev/ttyUSB*
   
   # If not present, lidar not connected
   ```

4. **Test lidar directly:**
   ```bash
   # Use lidar manufacturer's tools or minicom
   minicom -D /dev/ttyUSB1
   ```

5. **Check config/robot_hw.yaml:**
   ```yaml
   lidar_port: /dev/ttyUSB1
   lidar_frame: laser
   ```

**Solution:**
- Verify USB connection
- Check port name in configuration
- Verify lidar driver is properly installed
- Check lidar power supply

---

## Odometry & TF

### Odometry Not Publishing

**Symptoms:**
- No `/odom` topic
- Navigation can't localize
- RViz shows no odometry markers

**Debugging Steps:**

1. **Check odometry node exists:**
   ```bash
   ros2 node list | grep odometry
   ```

2. **Monitor odometry topic:**
   ```bash
   ros2 topic echo /odom
   ```

3. **Check motor controller is publishing encoder data:**
   ```bash
   # If motor controller also publishes encoder data
   ros2 topic list | grep encoder
   ```

4. **Check for errors in core launch:**
   ```bash
   ros2 launch puzzlebot_real_robot real_robot_core.launch.xml 2>&1 | tee launch.log
   grep -i error launch.log
   ```

**Solution:**
- Implement odometry_node in `puzzlebot_real_robot` package
- Ensure encoders are connected to motor controller
- Verify encoder calibration in `config/robot_hw.yaml`
- Check that motor controller is reading encoder values

---

### Odometry Drifts or Jumps

**Symptoms:**
- Robot travels 1m but `/odom` shows 0.8m or 1.2m
- Odometry gradually drifts over time
- Position estimate jumps suddenly

**Cause:** Wheel calibration error or encoder malfunction

**Calibration Steps:**

1. **Measure actual distance traveled:**
   ```bash
   # Mark robot starting position
   # Run: ros2 topic echo /odom > odom.log
   # Manually push robot forward exactly 1.0 meter
   # Stop and save odom log
   # Check final position in log
   ```

2. **Compare and adjust:**
   ```
   If actual: 1.0m, recorded: 0.8m
   → wheel_radius is TOO SMALL
   → multiply radius by (1.0 / 0.8) = 1.25
   
   If actual: 1.0m, recorded: 1.2m
   → wheel_radius is TOO LARGE
   → multiply radius by (1.0 / 1.2) = 0.833
   ```

3. **Update config/robot_hw.yaml:**
   ```yaml
   left_wheel_radius: 0.033  # Adjust this value
   right_wheel_radius: 0.033
   ```

4. **Rebuild and test:**
   ```bash
   colcon build --packages-select puzzlebot_real_robot
   ros2 launch puzzlebot_real_robot real_robot_core.launch.xml
   ```

**Solution:**
- Recalibrate wheel radius
- Check for encoder ticks_per_rev accuracy
- Verify encoders aren't slipping
- Check for loose wheels

---

### TF Tree Problems

**Symptoms:**
- RViz shows "No transform from base_link to odom"
- `/tf` topic not publishing
- Navigation can't find transforms

**Debugging Steps:**

1. **Check TF is publishing:**
   ```bash
   ros2 topic echo /tf | head -10
   ```

2. **View TF tree:**
   ```bash
   # Show current TF tree
   ros2 run tf2_tools view_frames
   
   # View as tree format
   ros2 run tf2_ros tf2_echo odom base_link
   ```

3. **Check robot_state_publisher is running:**
   ```bash
   ros2 node list | grep state_publisher
   ```

4. **Verify URDF is correct:**
   ```bash
   # Display current URDF
   ros2 param get /robot_state_publisher robot_description | head -20
   ```

**Solution:**
- Ensure `robot_state_publisher` is running in core launch
- Check `puzzlebot_description.launch.xml` is included correctly
- Verify URDF file exists and is valid
- Check for frame naming mismatches

---

### Robot Curves Left or Right

**Symptoms:**
- When sending straight `/cmd_vel`, robot veers to one side
- After moving 1m forward, robot has moved sideways

**Cause:** Encoder calibration mismatch between left and right wheels

**Debugging Steps:**

1. **Test each wheel separately:**
   - Send `/cmd_vel` with only linear velocity
   - Observe which direction the robot curves
   - Curve indicates slower wheel on that side

2. **Measure drift distance:**
   - Move robot 1m straight
   - Measure perpendicular distance drifted
   - Calculate ratio: drifted / 1.0 = correction factor

3. **Adjust encoder scaling:**
   ```yaml
   # If curves RIGHT (left is slower):
   # Increase left wheel speed or decrease right wheel speed
   encoder_scale_left: 1.05   # Increase
   encoder_scale_right: 1.0
   
   # If curves LEFT (right is slower):
   # Increase right wheel speed or decrease left wheel speed
   encoder_scale_left: 1.0
   encoder_scale_right: 1.05  # Increase
   ```

**Solution:**
- Adjust `encoder_scale_left` and `encoder_scale_right` in `robot_hw.yaml`
- Verify encoders aren't slipping
- Check motor speeds are balanced
- Recalibrate motor gains

---

## SLAM Mapping

### SLAM Not Starting

**Symptoms:**
- No `/map` topic after running with `slam:=true`
- SLAM nodes don't appear in `ros2 node list`
- RViz shows error about missing map frame

**Debugging Steps:**

1. **Check slam_toolbox is installed:**
   ```bash
   ros2 pkg list | grep slam_toolbox
   ```

2. **Check nodes are running:**
   ```bash
   ros2 node list | grep slam
   ros2 node list | grep cartographer  # Alternative SLAM
   ```

3. **Check if scan topic is present:**
   ```bash
   ros2 topic echo /scan | head -5
   ```

4. **Check configuration:**
   ```bash
   cat config/slam_toolbox_real.yaml
   ```

**Solution:**
- Ensure `slam_toolbox` is installed: `sudo apt install ros-humble-slam-toolbox`
- Verify lidar is publishing `/scan` data
- Check `real_robot_slam.launch.xml` includes slam_core correctly
- Ensure `slam_toolbox_real.yaml` exists and is valid

---

### SLAM Map Is Inconsistent

**Symptoms:**
- Map has jumps or discontinuities
- Loop closures are incorrect
- Map drifts as robot moves

**Cause:** SLAM tuning not suitable for real sensor noise

**Tuning Steps:**

1. **Increase sensor trust:**
   ```yaml
   # config/slam_toolbox_real.yaml
   correlation_variance_multiplier: 3.0  # Increase from 1.0
   ```

2. **Improve scan matching:**
   ```yaml
   use_scan_matching: true
   scan_time: 0.1  # Time window for scan
   ```

3. **Adjust loop closure:**
   ```yaml
   loop_match_min_chain_size: 5  # More conservative
   ```

4. **Test and iterate:**
   ```bash
   ros2 launch puzzlebot_real_robot real_robot_slam.launch.xml
   # Drive slowly and observe map quality
   ```

**Solution:**
- Tune parameters iteratively (one at a time)
- Test in open areas first (fewer ambiguities)
- Reduce robot speed during mapping
- Use high-quality lidar data (no dropouts)

---

### Can't Save SLAM Map

**Symptoms:**
- Save service call succeeds but no map files generated
- Map files not found in expected location
- `~/.local/share/` directory doesn't exist

**Debugging Steps:**

1. **Verify service exists:**
   ```bash
   ros2 service list | grep save_map
   ```

2. **Check directory permissions:**
   ```bash
   mkdir -p ~/.local/share
   chmod 755 ~/.local/share
   ls -la ~/.local/share
   ```

3. **Call save service with debug:**
   ```bash
   ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: test_map}}" --rate 1
   ```

4. **Check if map is actually in home directory:**
   ```bash
   ls -la ~/ | grep map
   ls -la /tmp/ | grep map
   ```

**Solution:**
- Create `~/.local/share` directory if missing
- Ensure write permissions on home directory
- Check map name doesn't have invalid characters
- Check SLAM has actually created a map (use RViz to verify)

---

## Navigation

### Navigation Can't Localize

**Symptoms:**
- "Cannot locate" message in Nav2
- Initial pose estimate in RViz doesn't stick
- Robot doesn't know where it is on map

**Debugging Steps:**

1. **Verify odometry accuracy:**
   ```bash
   # Manually drive robot in straight line
   # Check /odom remains accurate
   ros2 topic echo /odom
   ```

2. **Check map is loaded:**
   ```bash
   ros2 topic echo /map | head -20
   ```

3. **Check lidar scan matches map:**
   ```bash
   # In RViz, enable /scan display
   # Should see laser points overlaid on map
   ```

4. **Check AMCL parameters:**
   ```bash
   ros2 param list | grep amcl
   ros2 param get /amcl_node max_beams
   ```

**Solution:**
- Ensure odometry is accurate (recalibrate if needed)
- Set initial pose in RViz (2D Pose Estimate tool)
- Check map file is correct for the environment
- Increase AMCL particle count in `config/nav2_params_real.yaml`
- Verify lidar is providing good data

---

### Robot Doesn't Reach Navigation Goal

**Symptoms:**
- Robot starts moving but gets stuck
- Path planner thinks goal is unreachable
- Robot stops before reaching goal

**Debugging Steps:**

1. **Check costmap:**
   ```bash
   # In RViz, enable Costmap and Footprint
   # Should see clear area around goal
   ```

2. **Verify path planning:**
   ```bash
   ros2 topic echo /plan | head -20
   ```

3. **Check controller output:**
   ```bash
   ros2 topic echo /cmd_vel
   # Should see velocity commands being sent
   ```

4. **Check for obstacles:**
   ```bash
   # In RViz, view costmap
   # Red areas are obstacles/inflation
   # Green is free space
   ```

**Solution:**
- Increase `costmap_inflation_radius` if walls are blocking (conservative margin)
- Reduce `max_vel_x` and `max_vel_theta` for smoother control
- Verify costmap is accurate to real environment
- Check for unexpected obstacles or sensor noise creating false obstacles

---

### Navigation Is Jerky or Oscillates

**Symptoms:**
- Robot overshoots goals
- Robot oscillates around path
- Navigation is not smooth

**Tuning Steps:**

1. **Reduce velocity limits:**
   ```yaml
   # config/nav2_params_real.yaml
   max_vel_x: 0.2        # Reduce from 0.5
   max_vel_theta: 0.5    # Reduce from 1.0
   ```

2. **Increase acceleration limit:**
   ```yaml
   acceleration_limit: 0.1  # Smoother ramp
   ```

3. **Adjust DWB controller parameters:**
   ```yaml
   dwb_local_planner:
     max_acc_x: 0.2
     max_acc_y: 0.0
     max_acc_theta: 0.1
   ```

4. **Increase costmap inflation:**
   ```yaml
   inflation_radius: 0.4  # More conservative
   ```

**Solution:**
- Tune parameters incrementally
- Test in safe open space first
- Balance between responsiveness and stability
- Consider your motor acceleration limits

---

## Performance & Tuning

### High CPU Usage

**Symptoms:**
- SLAM/Nav2 processes consuming 80%+ CPU
- Lag in TF transforms
- RViz is sluggish

**Optimization Steps:**

1. **Reduce lidar scan rate:**
   ```yaml
   # config/robot_hw.yaml
   lidar_update_rate: 5  # Reduce from 10 Hz
   ```

2. **Reduce costmap update rate:**
   ```yaml
   # config/nav2_params_real.yaml
   update_frequency: 2.0  # Reduce from 10.0
   publish_frequency: 2.0
   ```

3. **Reduce SLAM processing:**
   ```yaml
   # config/slam_toolbox_real.yaml
   num_threads: 2  # Reduce from 4
   ```

4. **Disable unnecessary RViz displays:**
   - Remove scan visualization if not needed
   - Disable costmap visualization during runtime

**Solution:**
- Profile which process uses most CPU: `top` or `ros2 top`
- Reduce scan rate for non-critical mapping tasks
- Use lower costmap resolution for faster updates
- Consider reducing robot speed (less aggressive planning needed)

---

### Network/ROS 2 Latency

**Symptoms:**
- Transforms are delayed
- Motor commands lag behind goal
- Robot overshoots or undershoots

**Debugging:**

1. **Check network:**
   ```bash
   ping localhost  # Should be < 1ms
   ```

2. **Profile ROS 2 middleware:**
   ```bash
   # Monitor DDS communication
   ros2 topic bw /cmd_vel  # Check bandwidth
   ```

3. **Check node processing time:**
   ```bash
   # Enable timing statistics
   ros2 node info /motor_controller
   ```

**Solution:**
- Use localhost for local communication
- Check ROS domain ID: `echo $ROS_DOMAIN_ID`
- Reduce number of active ROS 2 nodes
- Consider using rmw_cyclonedds_cpp for better performance

---

### Tuning for Your Robot

**General workflow:**

1. **Start conservative:** Low speeds, high safety margins
2. **Test incrementally:** Change one parameter at a time
3. **Monitor carefully:** Watch for instability
4. **Document changes:** Keep notes on what works/doesn't
5. **Save working configs:** Backup YAML files that work well

**Key parameters to tune:**

| Parameter | Effect | Real Robot vs Sim |
|-----------|--------|-------------------|
| `max_vel_x` | Max forward speed | Reduce for real robot |
| `costmap_inflation_radius` | Safety margin | Increase for real robot |
| `amcl_particles` | Localization particles | Increase for real drift |
| `update_min_d` | Distance threshold | Increase for real odometry noise |
| `correlation_variance_multiplier` | SLAM sensor trust | Increase for real noise |

---

## Getting Help

1. Check `/var/log/ros/` for system logs
2. Enable debug output: `ros2 launch puzzlebot_real_robot ... --log-level DEBUG`
3. Record rosbag for offline analysis: `ros2 bag record /tf /odom /scan /cmd_vel`
4. Share configuration files and symptom description in issue reports
