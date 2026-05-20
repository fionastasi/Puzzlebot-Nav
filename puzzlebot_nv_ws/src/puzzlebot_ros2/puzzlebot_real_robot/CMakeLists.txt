cmake_minimum_required(VERSION 3.8)
project(puzzlebot_real_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install launch, config, maps, rviz directories
install(
  DIRECTORY
    launch
    config
    maps
    rviz
  DESTINATION share/${PROJECT_NAME}/
)

# Install Python scripts as executables so ros2 launch can find them
# This is separate from the DIRECTORY install above
install(
  PROGRAMS
    scripts/puzzlebot_localization.py
    scripts/puzzlebot_joint_state_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()