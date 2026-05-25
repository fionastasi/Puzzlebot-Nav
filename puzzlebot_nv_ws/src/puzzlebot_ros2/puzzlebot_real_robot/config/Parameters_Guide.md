# Robot Configuration Parameters Guide

This document explains the key parameters that are shared or related across both `slam_toolbox_real.yaml` and `nav2_params_real.yaml` configuration files for the Puzzlebot real robot.

---

## Shared/Related Parameters

### 1. **Frame Definitions**

These parameters define the coordinate frames used by the robot system for localization and navigation.

| Parameter | File(s) | Value | Explanation |
|-----------|---------|-------|-------------|
| `odom_frame` / `odom_frame_id` | SLAM Toolbox / AMCL | `odom` | The odometry frame represents the robot's pose in its local coordinate system, typically fixed to the starting position. SLAM Toolbox publishes scans in this frame, while AMCL uses it to track incremental robot motion. Defined in both to ensure consistent frame hierarchies. |
| `map_frame` / `global_frame_id` | SLAM Toolbox / AMCL | `map` | The global map frame is the fixed world coordinate system where the static map exists. SLAM Toolbox creates the map by matching scans, while AMCL aligns the robot within this pre-existing map. Both need to reference the same frame for proper tf transforms. |
| `base_frame` / `base_frame_id` / `robot_base_frame` | SLAM Toolbox / AMCL / Navigation2 | `base_footprint` | The robot's base frame, typically at the center of the robot on the ground plane. This is the reference point for laser scans and motion planning. All three systems must use the same base frame for consistent localization and control. |
| **Why Defined in Both**: These frames form the tf (transform) tree. SLAM Toolbox creates the `map → odom` transform, AMCL refines it, and Navigation2 controllers use these frames for path planning and execution. |

---

### 2. **Laser Scan Configuration**

These parameters configure how the robot's LiDAR/laser scanner data is processed.

| Parameter | File(s) | Value | Explanation |
|-----------|---------|-------|-------------|
| `scan_topic` | SLAM Toolbox / AMCL / Costmap Layers | `/scan` | The ROS topic name where raw laser scan data is published by the laser driver. Both SLAM (for mapping) and AMCL (for localization) subscribe to this topic. The costmap layers also use scans for obstacle detection. Defined consistently to ensure all components read from the same sensor data stream. |
| `min_laser_range` | SLAM Toolbox / Local Costmap Obstacle Layer | 0.2 / 0.10 | Minimum valid laser range in meters. Readings closer than this are filtered out to avoid noise from near-field reflections or sensor artifacts. SLAM Toolbox uses 0.2m to filter close reflections during mapping; the costmap uses 0.10m for more detailed local obstacle detection. Both need this to prevent spurious data. |
| `max_laser_range` | SLAM Toolbox / Local Costmap Obstacle Layer | 8.0 / 2.5 | Maximum valid laser range in meters. Readings beyond this distance are discarded. SLAM Toolbox uses 8.0m for broader mapping range; the local costmap uses 2.5m since the local planner only needs near-field data. Prevents noisy far-field readings from affecting their respective processes. |
| `laser_max_range` (AMCL) | AMCL / Global Costmap Obstacle Layer | 4.0 / 2.5 | AMCL's specific laser max range for particle filter likelihood calculation. Global costmap uses 2.5m for consistency with local costmap. These are defined to match laser sensor capabilities and prevent stale/noisy data. |
| **Why Defined in Both**: All three systems (SLAM, AMCL, Costmaps) need valid laser data. By defining ranges consistently, the robot ensures reliable mapping, localization, and obstacle detection. |

---

### 3. **Transform and Time Tolerance**

These parameters handle timing synchronization and transform buffering across the system.

| Parameter | File(s) | Value | Explanation |
|-----------|---------|-------|-------------|
| `transform_timeout` / `transform_tolerance` | SLAM Toolbox / Controller Server / Costmaps | 0.2s / 0.5s / 1.0s | Time tolerance for waiting on TF transforms. SLAM Toolbox uses 0.2s for tight loop closure timing. Controller Server and costmaps use 0.5-1.0s to allow for minor delays in the transform tree. These are defined to handle network/computation latency without failing—critical for real hardware where delays are common. |
| `tf_buffer_duration` | SLAM Toolbox | 30.0s | Duration for which the TF buffer stores historical transforms. SLAM Toolbox keeps 30 seconds of history to allow loop closure detection even if scans arrive slightly delayed. Defined to ensure enough temporal window for loop matching. |
| `transform_publish_period` | SLAM Toolbox | 0.02s (50 Hz) | Frequency at which SLAM Toolbox publishes TF transforms. 50 Hz ensures smooth, continuous updates to the `map → odom` transform. This needs to be defined to provide timely transform data to downstream consumers like the controller and costmap layers. |
| **Why Defined in Both**: Real robots have communication delays and jitter. These parameters create buffers and tolerances so that all systems gracefully handle timing variations without losing sync. |

---

### 4. **Resolution and Discretization**

| Parameter | File(s) | Value | Explanation |
|-----------|---------|-------|-------------|
| `resolution` | SLAM Toolbox / Global Costmap / Local Costmap | 0.05m | Grid resolution (5 cm per cell) for occupancy grids. SLAM Toolbox uses this for its occupancy grid during mapping; costmaps use it for path planning and obstacle inflation. Defined identically across all to ensure consistent spatial representation—a mismatch would cause misaligned navigation. |
| **Why Defined in Both**: The map created by SLAM Toolbox (0.05m resolution) must match the resolution used by Navigation2 costmaps. Otherwise, obstacles appear scaled or misaligned during planning. |

---

### 5. **Interactive Mode and Debug Settings**

| Parameter | File(s) | Value | Explanation |
|-----------|---------|-------|-------------|
| `enable_interactive_mode` | SLAM Toolbox | `true` | Enables manual loop closure corrections via RViz. For real robot operation, this allows operators to fix mapping errors by dragging poses in the visualization tool. Defined to support hands-on debugging during real-world mapping sessions. |
| `debug_logging` | SLAM Toolbox | `false` | Disables verbose debug output to reduce log spam and improve performance. Set to `false` on real hardware to minimize overhead; only enabled for troubleshooting. |
| **Why Defined**: These are operational settings specific to real robot deployment—enabling operator control while keeping system overhead low. |

---

## 6. **Ceres Solver Configuration (SLAM Optimization)**

SLAM Toolbox uses **Ceres Solver**, a C++ library for solving large optimization problems. The Ceres solver is responsible for refining robot pose estimates and map consistency by solving the SLAM graph optimization problem. Below are all the Ceres-related parameters:

### Ceres Solver Core Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `solver_plugin` | `solver_plugins::CeresSolver` | Specifies which optimization library to use. Ceres Solver is chosen because it's efficient for non-linear least-squares problems like SLAM, where the goal is to find the best robot poses and map landmarks that minimize scan-to-map misalignment. |

### Linear Solver Strategy

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `ceres_linear_solver` | `SPARSE_NORMAL_CHOLESKY` | **What it does**: Chooses the algorithm for solving the linear system $$Ax = b$$ that arises during optimization. **Why SPARSE_NORMAL_CHOLESKY**: SLAM creates sparse systems (most matrix entries are zero because loop closures only connect nearby poses). This solver exploits sparsity for efficiency. Cholesky decomposition is numerically stable for symmetric positive-definite matrices common in SLAM. **Alternatives**: `DENSE_QR` (slower, for small problems), `SPARSE_SCHUR` (good for large, highly sparse problems). |

### Preconditioner Type

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `ceres_preconditioner_type` | `SCHUR_JACOBI` | **What it does**: A preconditioner speeds up iterative solvers by transforming the problem into one that's easier to solve (better conditioned). **Why SCHUR_JACOBI**: Uses a block-structured preconditioner based on the Schur complement, exploiting SLAM's block structure (poses vs. landmarks). Jacobi variant applies independent scaling to each block, making it fast and memory-efficient. **Alternatives**: `IDENTITY` (no preconditioning, slower), `SCHUR_FULL_JACOBI` (more accurate but slower). |

### Trust Region Strategy (Search Regionfor Updates)

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `ceres_trust_strategy` | `LEVENBERG_MARQUARDT` | **What it does**: Controls the "trust region"—how far the optimizer allows parameter updates in each iteration. It's a method for balancing between gradient descent (stable but slow) and Newton's method (fast but can diverge). **Why LEVENBERG_MARQUARDT**: Blends Newton's method (when optimization is going well) with gradient descent (when it's not). Particularly robust for SLAM where initial guesses can be poor and cost functions are non-linear. **Alternatives**: `DOGLEG` (another trust region method, sometimes faster), `LINE_SEARCH` (different philosophy, slower but sometimes more stable). |

### Dogleg Strategy (Refinement within Trust Region)

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `ceres_dogleg_strategy` | `TRADITIONAL_DOGLEG` | **What it does**: Specifies how to compute the next step within the trust region (only used if `ceres_trust_strategy` is `DOGLEG`). Even though we use `LEVENBERG_MARQUARDT`, this parameter is typically configured for consistency. **TRADITIONAL_DOGLEG**: Uses the classical Cauchy + Newton direction blending—computes a step along Cauchy direction (gradient descent) and Newton direction, choosing the path that respects the trust region radius. **Alternatives**: `SUBSPACE_DOGLEG` (considers a 2D subspace for more flexibility, slower). |

### Loss Function (Outlier Robustness)

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `ceres_loss_function` | `None` | **What it does**: Determines how outliers are handled. A loss function downweights or smooths the contribution of bad measurements (e.g., reflections off moving objects, sensor noise). **Why None**: The default indicates no special outlier rejection; all measurements are weighted equally. This works well when laser data is generally reliable. **Alternatives**: `HuberLoss` (smoothly downweights large errors), `CauchyLoss` (more aggressive outlier rejection), `TukeyLoss` (complete rejection of severe outliers). For real robots with occasional sensor noise, `HuberLoss` is often better than `None`. |

### How Ceres Optimization Works in SLAM

1. **Problem Setup**: SLAM Toolbox builds a graph where nodes are robot poses, edges are relative pose constraints (from scan-to-scan matching or loop closures).

2. **Cost Function**: Minimize the sum of squared errors:
   $$\sum_{\text{constraints}} (\text{predicted relative pose} - \text{measured relative pose})^2$$

3. **Optimization Loop**:
   - Compute Jacobian (gradient of error w.r.t. poses)
   - Form normal equations: $$H \Delta x = -g$$ (where $H$ is Hessian, $g$ is gradient)
   - **Linear Solver** (`SPARSE_NORMAL_CHOLESKY`) solves for $$\Delta x$$
   - **Preconditioner** (`SCHUR_JACOBI`) improves convergence speed
   - **Trust Region** (`LEVENBERG_MARQUARDT`) decides step size
   - Update poses: $$x_{\text{new}} = x_{\text{old}} + \alpha \Delta x$$
   - Repeat until convergence

4. **Result**: Refined robot poses and corrected map

### Example Tuning Scenarios

| Scenario | Change | Why |
|----------|--------|-----|
| Optimization too slow | Change `ceres_linear_solver` to `SPARSE_SCHUR` or `ceres_preconditioner_type` to `IDENTITY` | Ceres is spending too much time in the linear solver. Trade speed for accuracy by simplifying the solver. |
| Optimization diverges (gets worse) | Change `ceres_trust_strategy` to `DOGLEG` or reduce `ceres_loss_function: None` to something like `HuberLoss` | The optimizer is taking too-large steps or being misled by outliers. Use more conservative steps or outlier rejection. |
| Map has visible jumps at loop closures | Ensure `minimum_travel_distance` and `minimum_travel_heading` are reasonable; adjust `loop_search_space_resolution` | Loop closure constraints conflict with local scan matching. These parameters control when loop closure is triggered, not Ceres itself, but they affect the optimization problem. |

---

## Parameter Relationship Diagram

```
Real Robot LiDAR
      ↓ (scan_topic: /scan)
      ├─→ SLAM Toolbox
      │   ├─ Creates: map → odom transform
      │   ├─ Uses: base_frame, map_frame, odom_frame
      │   ├─ Processes: min/max_laser_range
      │   ├─ Publishes at: transform_publish_period
      │   └─ Grid resolution: 0.05m
      │
      ├─→ AMCL Localization
      │   ├─ Refines: map → odom transform
      │   ├─ Uses: base_frame_id, global_frame_id, odom_frame_id
      │   ├─ Filters: min/max_laser_range
      │   └─ Tolerates: transform_tolerance delays
      │
      └─→ Costmap Layers
          ├─ Local Costmap
          │   ├─ Uses: base_footprint, odom frames
          │   ├─ Filters: min/max obstacle range
          │   └─ Grid: 0.05m resolution
          │
          └─ Global Costmap
              ├─ Uses: base_footprint, map frames
              ├─ Filters: min/max obstacle range
              └─ Grid: 0.05m resolution
```

---

## Summary: Why These Parameters Are Critical

1. **Consistency**: The robot's navigation stack (SLAM → AMCL → Nav2) forms a pipeline. If any component has different frame IDs, laser ranges, or resolutions, misalignments occur.

2. **Real Hardware Robustness**: Parameters like `transform_tolerance`, `tf_buffer_duration`, and range limits are tuned to handle real-world communication delays and sensor noise.

3. **Semantic Alignment**: Even though SLAM Toolbox and Nav2 use slightly different parameter names (`base_frame` vs `base_frame_id`), they describe the same conceptual entity—the robot's base frame.

4. **Performance**: Resolution and laser range limits are balanced to provide accurate mapping/localization without overwhelming the system with too much data.

---

## Notes for Future Modifications

- **Changing `resolution`**: Must be updated in both SLAM Toolbox AND costmap configs. A mismatch causes spatial inconsistencies.
- **Changing frame IDs**: Update all three files consistently (`base_frame`, `base_frame_id`, `robot_base_frame`).
- **Adjusting laser ranges**: Keep real robot values (e.g., `max_laser_range: 8.0`) for true sensor capabilities, even if local costmap uses smaller ranges for computation efficiency.
- **Real vs Simulation**: The `use_sim_time: false` setting confirms these are for real hardware (as opposed to Gazebo simulation).
