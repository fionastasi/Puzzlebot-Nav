#!/usr/bin/env python3
"""
Joint state publisher for the physical Puzzlebot.

Subscribes to:
  /odom  (nav_msgs/Odometry) — published by puzzlebot_localization

Publishes:
  /joint_states  (sensor_msgs/JointState) — wheel angles for robot_state_publisher
  TF: odom -> base_footprint
"""
import rclpy
import math
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class PuzzlebotJointStatePublisher(Node):
    """Publish joint states and odom->base_footprint TF from odometry."""

    def __init__(self):
        super().__init__('puzzlebot_joint_state_publisher')

        # Accumulated wheel angles (rad)
        self._angle_l = 0.0
        self._angle_r = 0.0

        # Robot parameters (must match physical robot)
        self.r = 0.05  # Wheel radius (m)
        self.l = 0.19  # Wheel separation (m)

        # Current robot velocities from odometry
        self._v = 0.0
        self._w = 0.0

        # Subscription
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Publishers
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer at 100 Hz
        self._dt = 0.01
        self.create_timer(self._dt, self._publish)

        self.get_logger().info('puzzlebot_joint_state_publisher started')

    def odom_callback(self, msg):
        self._v = msg.twist.twist.linear.x
        self._w = msg.twist.twist.angular.z

        # Broadcast odom -> base_footprint TF immediately on each odom message
        t = TransformStamped()
        t.header.stamp    = msg.header.stamp
        t.header.frame_id = 'odom'
        t.child_frame_id  = 'base_footprint'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = 0.0
        t.transform.rotation      = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(t)

    def _publish(self):
        # Inverse kinematics: robot v,w -> wheel angular velocities
        wr = (self._v + self._w * self.l / 2.0) / self.r
        wl = (self._v - self._w * self.l / 2.0) / self.r

        # Integrate wheel angles
        self._angle_l += wl * self._dt
        self._angle_r += wr * self._dt

        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name         = ['wheel_left_joint', 'wheel_right_joint']
        js.position     = [self._angle_l, self._angle_r]
        self.joint_pub.publish(js)


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotJointStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()