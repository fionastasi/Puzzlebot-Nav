# Scripts Explanations: QoS and Quaternion Math

This file explains QoS settings used in the localization scripts and the math behind `quaternion_from_euler()`.

## QoSProfile (ROS 2)

- `QoSProfile` configures topic communication behavior in ROS 2. It controls how messages are delivered, stored, and retransmitted.

Key fields used in `puzzlebot_localization.py`:

- `reliability`
  - `ReliabilityPolicy.BEST_EFFORT`: messages are sent without guaranteed delivery. Packets may be dropped under congestion. Use for high-rate sensor streams where late messages are worthless (e.g., raw IMU or encoder data from micro-ROS).
  - `ReliabilityPolicy.RELIABLE`: ensures delivery (retransmits lost packets). Use for important commands or state that must be received.

- `durability`
  - `DurabilityPolicy.VOLATILE`: new subscribers do not receive previously sent messages; only future messages are delivered. This is typical for sensors where only current data matters.
  - `DurabilityPolicy.TRANSIENT_LOCAL`: the middleware stores the last messages and will replay them to new subscribers. Useful for latched configuration messages or the last-known state.

- `depth`
  - The queue size used by the middleware to buffer messages when the consumer is slower than the publisher. Higher depth reduces message loss at the cost of more memory and latency.

### Why `BEST_EFFORT` + `VOLATILE` for micro-ROS encoders

The microcontroller publishing encoder velocities often uses constrained networking (e.g., UDP or lossy transport). The encoder topic is high-frequency and each message quickly becomes stale. Matching the publisher's QoS with the subscriber's QoS (`BEST_EFFORT`, `VOLATILE`) avoids compatibility issues (in ROS 2 QoS profiles must be compatible otherwise subscription receives nothing). Choosing `BEST_EFFORT` reduces overhead; `VOLATILE` avoids storing old encoder values when a new node subscribes.

### Example (from `puzzlebot_localization.py`)

```python
qos_sensor = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
)
```

- `depth=10` provides a small buffer to smooth occasional jitter without adding much latency.

**Compatibility note:** If the encoder publisher uses `RELIABLE` but the subscriber uses `BEST_EFFORT`, they are incompatible and messages will not be received. Always match or accept the publisher's guarantees when possible.

---

## `quaternion_from_euler(roll, pitch, yaw)` — math and implementation notes

Robotics commonly represents orientation using quaternions to avoid singularities and to efficiently compose rotations. Converting Euler angles (roll, pitch, yaw) to a quaternion follows a standard formula.

Using the convention that the Euler angles are applied in the order: roll ($\phi$) about X, pitch ($\theta$) about Y, then yaw ($\psi$) about Z, the quaternion components $(x, y, z, w)$ are:

```text
q_w = cos(phi/2) * cos(theta/2) * cos(psi/2) + sin(phi/2) * sin(theta/2) * sin(psi/2)
q_x = cos(theta/2) * sin(phi/2) * cos(psi/2) - sin(theta/2) * cos(phi/2) * sin(psi/2)
q_y = cos(phi/2) * cos(psi/2) * sin(theta/2) + sin(phi/2) * sin(psi/2) * cos(theta/2)
q_z = cos(phi/2) * cos(theta/2) * sin(psi/2) - sin(phi/2) * sin(theta/2) * cos(psi/2)
```

(Equivalently, many implementations compute intermediate sines/cosines for half-angles and then build the quaternion.)

### Important implementation notes

- The order of Euler rotations matters. The formulas above assume `roll` then `pitch` then `yaw` (X-Y-Z intrinsic rotations). If your system uses another order, the formula changes.
- Quaternions should be normalized after numerical operations to avoid drift:

$$q \leftarrow \frac{q}{\|q\|}$$

- Beware of array/shape bugs. The implementation in `puzzlebot_localization.py` allocates `q = np.empty((4,0))` which creates an empty 4x0 array and then attempts to assign `q[0]` etc.; this will raise an indexing error or produce invalid results. A correct allocation would be `q = np.empty(4)` or `q = np.zeros(4)`.

### Corrected Python snippet

```python
import math
import numpy as np

def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> np.ndarray:
    hr = roll / 2.0
    hp = pitch / 2.0
    hy = yaw / 2.0
    cr, sr = math.cos(hr), math.sin(hr)
    cp, sp = math.cos(hp), math.sin(hp)
    cy, sy = math.cos(hy), math.sin(hy)

    qx = cp * sr * cy - sp * cr * sy
    qy = cp * cr * sy + sp * sr * cy
    qz = cp * sr * sy - sp * cr * cy
    qw = cp * cr * cy + sp * sr * sy

    q = np.array([qx, qy, qz, qw], dtype=float)
    # normalize
    q /= np.linalg.norm(q)
    return q
```

### Why quaternions are used instead of Euler angles

- Avoid gimbal lock (singularities in Euler representations).
- Efficient to compose rotations and interpolate (slerp).
- Compact (4 values) and stable for integration.

---

## Where this applies in the repo

- The `QoSProfile` explanation maps to `puzzlebot_localization.py` (publisher/subscriber QoS settings).
- The quaternion math maps to the `quaternion_from_euler()` helper used when publishing `Odometry` messages and broadcasting TFs in `puzzlebot_joint_state_publisher.py`.
