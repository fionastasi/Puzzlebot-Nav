# puzzlebot_gazebo

This package is simulation-only. It launches Gazebo (gz-sim), spawns the Puzzlebot robot, and runs \os_gz_bridge\ to forward topics between Gazebo and ROS 2. Nothing in this package runs on real hardware.

## Package structure

`
puzzlebot_gazebo/
├── launch/
│   └── puzzlebot_gazebo.launch.xml
├── config/
│   └── gazebo_bridge.yaml
└── worlds/
    └── maze.world
`

## Bridge topics

| Topic | Direction | Message type |
|-------|-----------|--------------|
| /clock | GZ_TO_ROS | osgraph_msgs/msg/Clock |
| /cmd_vel | ROS_TO_GZ | geometry_msgs/msg/Twist |
| /odom | GZ_TO_ROS | 
av_msgs/msg/Odometry |
| /tf | GZ_TO_ROS | 	f2_msgs/msg/TFMessage |
| /joint_states | GZ_TO_ROS | sensor_msgs/msg/JointState |
| /scan | GZ_TO_ROS | sensor_msgs/msg/LaserScan |

## Launch file args

| Argument | Default | Description |
|----------|---------|-------------|
| headless | alse | Run Gazebo without GUI when true |

## Usage

Do not call this launch directly. It is included by puzzlebot_navigation2/launch/slam.launch.xml and puzzlebot_navigation2/launch/nav2.launch.xml.

## Simulation-only warning

This entire package is simulation-only. Do not include it as a dependency in real robot packages.
