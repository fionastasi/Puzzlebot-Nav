#!/usr/bin/env python3
"""
Puzzlebot Structured Logging Node

This ROS 2 Humble lifecycle node subscribes to /rosout and captures ALL log output
from every node in the system. It writes structured JSONL (one JSON per line) to:
    ~/.ros/puzzlebot_logs/session_<timestamp>.jsonl

Features:
  - Captures all logs from /rosout (rcl_interfaces/msg/Log)
  - On startup: snapshots all active nodes, topics, and services
  - Polls every 2 seconds for NEW/LOST entities
  - Graceful shutdown with file flushing
  - Lifecycle node pattern (can be managed by lifecycle_manager)

Usage:
  ros2 run puzzlebot_navigation2 puzzlebot_logger.py
  Or launched via:
  ros2 launch puzzlebot_navigation2 nav2_core.launch.xml

Log file format: JSONL with entries:
  { "ts": float, "level": str, "node": str, "msg": str, "file": str, "line": int }
  { "ts": float, "event": str, "type": str, "entity": str }  (for snapshots)
"""

import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

import rclpy
from lifecycle_msgs.srv import GetState
from rcl_interfaces.msg import Log
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn
from rclpy.parameter import Parameter


class PuzzlebotLogger(LifecycleNode):
    """Lifecycle node for structured logging of all ROS 2 messages."""

    def __init__(self):
        super().__init__("puzzlebot_logger")
        
        # Logging file setup
        self.log_dir = Path.home() / ".ros" / "puzzlebot_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{timestamp}.jsonl"
        
        # File handle
        self.log_handle = None
        
        # Entity tracking (for detecting new/lost entities)
        self.known_nodes: Set[str] = set()
        self.known_topics: Dict[str, str] = {}  # topic -> type
        self.known_services: Set[str] = set()
        
        # ROS subscriptions
        self.rosout_subscription = None
        self.poll_timer = None
        
        # Graceful shutdown
        self.shutting_down = False
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        
        self.get_logger().info(f"Puzzlebot Logger initialized. Log file: {self.log_file}")

    def _handle_sigterm(self, signum, frame):
        """Handle SIGTERM signal."""
        self.get_logger().warn("SIGTERM received, initiating shutdown...")
        self.shutting_down = True
        rclpy.shutdown()

    def on_configure(self, state):
        """Lifecycle: Configure state."""
        try:
            self.get_logger().info("Configuring Puzzlebot Logger...")
            self.log_handle = open(self.log_file, "w", buffering=1)
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to configure: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_activate(self, state):
        """Lifecycle: Activate state."""
        try:
            self.get_logger().info("Activating Puzzlebot Logger...")
            
            # Subscribe to /rosout
            self.rosout_subscription = self.create_subscription(
                Log,
                "/rosout",
                self._rosout_callback,
                rclpy.qos.QoSProfile(depth=1000, durability=rclpy.qos.DurabilityPolicy.VOLATILE),
            )
            
            # Start entity polling timer (2 seconds)
            self.poll_timer = self.create_timer(2.0, self._poll_entities)
            
            # Initial snapshot
            self._take_startup_snapshot()
            
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to activate: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_deactivate(self, state):
        """Lifecycle: Deactivate state."""
        try:
            self.get_logger().info("Deactivating Puzzlebot Logger...")
            
            if self.poll_timer:
                self.destroy_timer(self.poll_timer)
                self.poll_timer = None
            
            if self.rosout_subscription:
                self.destroy_subscription(self.rosout_subscription)
                self.rosout_subscription = None
            
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to deactivate: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_cleanup(self, state):
        """Lifecycle: Cleanup state."""
        try:
            self.get_logger().info("Cleaning up Puzzlebot Logger...")
            if self.log_handle:
                self.log_handle.flush()
                self.log_handle.close()
                self.log_handle = None
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to cleanup: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_shutdown(self, state):
        """Lifecycle: Shutdown state."""
        try:
            self.get_logger().info("Shutting down Puzzlebot Logger...")
            if self.log_handle:
                self.log_handle.flush()
                self.log_handle.close()
                self.log_handle = None
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Failed to shutdown: {e}")
            return TransitionCallbackReturn.FAILURE

    def _rosout_callback(self, msg: Log):
        """Callback for /rosout messages."""
        if not self.log_handle or self.shutting_down:
            return
        
        try:
            level_names = {
                Log.DEBUG: "DEBUG",
                Log.INFO: "INFO",
                Log.WARN: "WARN",
                Log.ERROR: "ERROR",
                Log.FATAL: "FATAL",
            }
            
            log_entry = {
                "ts": msg.stamp.sec + msg.stamp.nanosec / 1e9,
                "level": level_names.get(msg.level, "UNKNOWN"),
                "node": msg.name,
                "msg": msg.msg,
                "file": msg.file,
                "line": msg.line,
            }
            
            self.log_handle.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.get_logger().error(f"Error writing log entry: {e}")

    def _take_startup_snapshot(self):
        """Take initial snapshot of nodes, topics, services."""
        try:
            nodes, topics, services = self._get_graph_snapshot()
            
            # Log nodes
            for node in nodes:
                self._log_event("startup_snapshot", "node", node)
                self.known_nodes.add(node)
            
            # Log topics
            for topic, topic_type in topics.items():
                self._log_event("startup_snapshot", "topic", f"{topic}:{topic_type}")
                self.known_topics[topic] = topic_type
            
            # Log services
            for service in services:
                self._log_event("startup_snapshot", "service", service)
                self.known_services.add(service)
            
            self.get_logger().info(
                f"Startup snapshot: {len(nodes)} nodes, {len(topics)} topics, {len(services)} services"
            )
        except Exception as e:
            self.get_logger().error(f"Error taking startup snapshot: {e}")

    def _poll_entities(self):
        """Poll for new/lost entities every 2 seconds."""
        if self.shutting_down:
            return
        
        try:
            nodes, topics, services = self._get_graph_snapshot()
            
            # Check for new nodes
            current_nodes = set(nodes)
            new_nodes = current_nodes - self.known_nodes
            lost_nodes = self.known_nodes - current_nodes
            
            for node in new_nodes:
                self._log_event("new_entity", "node", node)
                self.known_nodes.add(node)
            
            for node in lost_nodes:
                self._log_event("lost_entity", "node", node)
                self.known_nodes.discard(node)
            
            # Check for new topics
            current_topics = set(topics.keys())
            new_topics = current_topics - set(self.known_topics.keys())
            lost_topics = set(self.known_topics.keys()) - current_topics
            
            for topic in new_topics:
                topic_type = topics[topic]
                self._log_event("new_entity", "topic", f"{topic}:{topic_type}")
                self.known_topics[topic] = topic_type
            
            for topic in lost_topics:
                self._log_event("lost_entity", "topic", topic)
                del self.known_topics[topic]
            
            # Check for new services
            current_services = set(services)
            new_services = current_services - self.known_services
            lost_services = self.known_services - current_services
            
            for service in new_services:
                self._log_event("new_entity", "service", service)
                self.known_services.add(service)
            
            for service in lost_services:
                self._log_event("lost_entity", "service", service)
                self.known_services.discard(service)
        except Exception as e:
            self.get_logger().debug(f"Error polling entities: {e}")

    def _get_graph_snapshot(self) -> Tuple[list, dict, list]:
        """Get current nodes, topics, services from the ROS graph."""
        graph = self.get_graph_names_and_types()
        nodes = graph.node_names_and_namespaces
        topic_list = graph.topic_names_and_types
        service_list = graph.service_names_and_types
        
        node_names = [f"{ns}{name}" for name, ns in nodes]
        topics = {name: types[0] if types else "" for name, types in topic_list}
        services = [name for name, _ in service_list]
        
        return node_names, topics, services

    def _log_event(self, event: str, entity_type: str, entity: str):
        """Log a structured event."""
        if not self.log_handle or self.shutting_down:
            return
        
        try:
            ts = self.get_clock().now().to_msg()
            event_entry = {
                "ts": ts.sec + ts.nanosec / 1e9,
                "event": event,
                "type": entity_type,
                "entity": entity,
            }
            self.log_handle.write(json.dumps(event_entry) + "\n")
        except Exception as e:
            self.get_logger().error(f"Error logging event: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = PuzzlebotLogger()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
