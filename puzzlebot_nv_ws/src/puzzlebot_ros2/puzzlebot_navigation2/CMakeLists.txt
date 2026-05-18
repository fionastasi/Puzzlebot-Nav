cmake_minimum_required(VERSION 3.8)
project(puzzlebot_navigation2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

install(
  DIRECTORY launch config maps rviz scripts nodes tools
  DESTINATION share/${PROJECT_NAME}/
)

# Install Python nodes
install(
  PROGRAMS nodes/puzzlebot_logger.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
