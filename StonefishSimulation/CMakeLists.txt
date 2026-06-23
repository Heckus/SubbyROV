cmake_minimum_required(VERSION 3.8)
project(stonefish_qut_rov)
find_package(ament_cmake REQUIRED)
install(
  DIRECTORY launch scenarios cad_model_data
  DESTINATION share/${PROJECT_NAME}
)
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)
install(PROGRAMS
     ros_nodes/teleop.py
     ros_nodes/station_keeping_node.py
     ros_nodes/imu_data_stability_plot.py
     ros_nodes/depth_plotter.py
     ros_nodes/camera.py
     ros_nodes/ball_centering.py
     DESTINATION lib/${PROJECT_NAME}
   )
install(FILES
  ros_nodes/pid_controller.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
