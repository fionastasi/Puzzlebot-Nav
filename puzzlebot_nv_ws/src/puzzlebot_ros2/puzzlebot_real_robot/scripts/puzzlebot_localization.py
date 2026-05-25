#!/usr/bin/env python3
"""
Odometry node for the physical Puzzlebot.

Subscribes to encoder velocities published by micro-ROS:
  /VelocityEncR  (std_msgs/Float32) — right wheel angular velocity (rad/s)
  /VelocityEncL  (std_msgs/Float32) — left wheel angular velocity (rad/s)

Publishes:
  /odom  (nav_msgs/Odometry) — integrated pose and velocity
"""
import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> np.ndarray:
    roll  /= 2.0
    pitch /= 2.0
    yaw   /= 2.0
    cr, sr = math.cos(roll),  math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw),   math.sin(yaw)
    q = np.empty(4)
    q[0] = cp * sr * cy - sp * cr * sy  # x
    q[1] = cp * cr * sy + sp * sr * cy  # y
    q[2] = cp * sr * sy - sp * cr * cy  # z 
    q[3] = cp * cr * cy + sp * sr * sy  # w
    return q


class PuzzlebotLocalization(Node):
    """Differential-drive odometry via encoder integration."""

    def __init__(self):
        super().__init__('puzzlebot_localization')

        # Pose state
        self.x     = 0.0
        self.y     = 0.0
        self.theta = 0.0

        # Robot parameters (must match physical robot)
        self.r = 0.05  # Wheel radius (m)
        self.l = 0.19  # Wheel separation (m)

        # Wheel angular velocities (rad/s) from encoders
        self.wr = 0.0  # right
        self.wl = 0.0  # left

        # micro-ROS publishes the encoder topics with BEST_EFFORT reliability.
        # The default subscription QoS is RELIABLE, which is INCOMPATIBLE and
        # results in zero messages received. This QoS profile must match.
        qos_sensor = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        # Subscriptions
        self.create_subscription(Float32, '/VelocityEncR', self._cb_wr, qos_sensor)
        self.create_subscription(Float32, '/VelocityEncL', self._cb_wl, qos_sensor)

        # Publisher
        self._odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # Timer at 100 Hz
        self._dt = 0.01
        self.create_timer(self._dt, self._update)

        self.get_logger().info('puzzlebot_localization started')

    def _cb_wr(self, msg: Float32):
        self.wr = msg.data

    def _cb_wl(self, msg: Float32):
        self.wl = msg.data

    def _update(self):
        r = self.r
        l = self.l

        # Forward kinematics
        v = r * (self.wr + self.wl) / 2.0
        w = r * (self.wr - self.wl) / l

        # Euler integration
        self.x     += v * math.cos(self.theta) * self._dt
        self.y     += v * math.sin(self.theta) * self._dt
        self.theta += w * self._dt

        q = quaternion_from_euler(0.0, 0.0, self.theta)

        odom = Odometry()
        odom.header.stamp            = self.get_clock().now().to_msg()
        odom.header.frame_id         = 'odom'
        odom.child_frame_id          = 'base_footprint'
        odom.pose.pose.position.x    = self.x
        odom.pose.pose.position.y    = self.y
        odom.pose.pose.orientation.x = float(q[0])
        odom.pose.pose.orientation.y = float(q[1])
        odom.pose.pose.orientation.z = float(q[2])
        odom.pose.pose.orientation.w = float(q[3])
        odom.twist.twist.linear.x    = v
        odom.twist.twist.angular.z   = w

        self._odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotLocalization()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()