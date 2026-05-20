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
    q[2] = cp * sr * sy - sp * cr * cy  # z — fixed sign vs reference
    q[3] = cp * cr * cy + sp * sr * sy  # w
    return q


class PuzzlebotLocalization(Node):
    """Differential-drive odometry via encoder integration."""

    # Physical parameters — must match wheels.xacro defaults
    WHEEL_RADIUS    = 0.033  # m
    WHEEL_SEPARATION = 0.16  # m

    def __init__(self):
        super().__init__('puzzlebot_localization')

        # Pose state
        self.x     = 0.0
        self.y     = 0.0
        self.theta = 0.0

        # Wheel angular velocities (rad/s) from encoders
        self.wr = 0.0  # right
        self.wl = 0.0  # left

        # Subscriptions
        self.create_subscription(Float32, '/VelocityEncR', self._cb_wr, 10)
        self.create_subscription(Float32, '/VelocityEncL', self._cb_wl, 10)

        # Publisher
        self._odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # Timer at 100 Hz
        self._dt = 0.01
        self.create_timer(self._dt, self._update)

        self.get_logger().info('puzzlebot_localization started — r=%.3f m  l=%.3f m' %
                               (self.WHEEL_RADIUS, self.WHEEL_SEPARATION))

    def _cb_wr(self, msg: Float32):
        self.wr = msg.data

    def _cb_wl(self, msg: Float32):
        self.wl = msg.data

    def _update(self):
        r = self.WHEEL_RADIUS
        l = self.WHEEL_SEPARATION

        # Forward kinematics
        v = r * (self.wr + self.wl) / 2.0
        w = r * (self.wr - self.wl) / l

        # Euler integration
        self.x     += v * math.cos(self.theta) * self._dt
        self.y     += v * math.sin(self.theta) * self._dt
        self.theta += w * self._dt

        q = quaternion_from_euler(0.0, 0.0, self.theta)

        msg = Odometry()
        msg.header.stamp            = self.get_clock().now().to_msg()
        msg.header.frame_id         = 'odom'
        msg.child_frame_id          = 'base_footprint'
        msg.pose.pose.position.x    = self.x
        msg.pose.pose.position.y    = self.y
        msg.pose.pose.orientation.x = float(q[0])
        msg.pose.pose.orientation.y = float(q[1])
        msg.pose.pose.orientation.z = float(q[2])
        msg.pose.pose.orientation.w = float(q[3])
        msg.twist.twist.linear.x    = v
        msg.twist.twist.angular.z   = w

        self._odom_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotLocalization()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()