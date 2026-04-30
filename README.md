# husky_bringup

Launch files for the Husky A200 with dual UR5e arms, Robotiq grippers, and Dynamixel pan/tilt neck.

`husky.launch.py` starts everything: robot_state_publisher, ros2_control_node with mock arms + dummy neck, all controller spawners, MoveIt move_group, RViz, and the VR arm teleop node.

## Run
ros2 launch husky_bringup husky.launch.py

## Dependencies

- [husky_description](https://github.com/DiCE-Lab-Org/husky_description)
- [husky_dual_ur_moveit_config](https://github.com/DiCE-Lab-Org/husky_dual_ur_moveit_config)
- [husky_commander](https://github.com/DiCE-Lab-Org/husky_commander)
- [dynamixel_hardware](https://github.com/dynamixel-community/dynamixel_hardware) (humble branch)

