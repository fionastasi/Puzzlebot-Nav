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
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class PuzzlebotJointStatePublisher(Node):
    """Publish joint states and odom->base_footprint TF from odometry."""

    # Must match wheels.xacro defaults and puzzlebot_localization.py
    WHEEL_RADIUS     = 0.033  # m
    WHEEL_SEPARATION = 0.16   # m

    # Must match joint names in wheels.xacro
    JOINT_NAMES = ['left_wheel_joint', 'right_wheel_joint']

    def __init__(self):
        super().__init__('puzzlebot_joint_state_publisher')

        # Accumulated wheel angles (rad)
        self._angle_l = 0.0
        self._angle_r = 0.0

        # Current robot velocities from odometry
        self._v = 0.0
        self._w = 0.0

        # Latest odometry message for TF broadcast
        self._last_odom: Odometry | None = None

        # Subscription
        self.create_subscription(Odometry, '/odom', self._cb_odom, 10)

        # Publishers
        self._joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self._tf_broadcaster = TransformBroadcaster(self)

        # Timer at 100 Hz
        self._dt = 0.01
        self.create_timer(self._dt, self._publish)

        self.get_logger().info('puzzlebot_joint_state_publisher started — '
                               'joints: %s' % self.JOINT_NAMES)

    def _cb_odom(self, msg: Odometry):
        self._v = msg.twist.twist.linear.x
        self._w = msg.twist.twist.angular.z
        self._last_odom = msg

        # Broadcast odom -> base_footprint TF immediately on each odom message
        t = TransformStamped()
        t.header.stamp    = msg.header.stamp
        t.header.frame_id = 'odom'
        t.child_frame_id  = 'base_footprint'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = 0.0
        t.transform.rotation      = msg.pose.pose.orientation
        self._tf_broadcaster.sendTransform(t)

    def _publish(self):
        r = self.WHEEL_RADIUS
        l = self.WHEEL_SEPARATION

        # Inverse kinematics: robot v,w -> wheel angular velocities
        wr = (self._v + self._w * l / 2.0) / r
        wl = (self._v - self._w * l / 2.0) / r

        # Integrate wheel angles
        self._angle_l += wl * self._dt
        self._angle_r += wr * self._dt

        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name         = self.JOINT_NAMES
        js.position     = [self._angle_l, self._angle_r]
        self._joint_pub.publish(js)


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotJointStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()