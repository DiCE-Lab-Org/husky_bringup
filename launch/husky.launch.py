import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_setup(context, *args, **kwargs):
    moveit_config_share = get_package_share_directory("husky_dual_ur_moveit_config")

    urdf_path = os.path.join(moveit_config_share, "config", "a200_0876.urdf.xacro")
    rviz_config_path = os.path.join(moveit_config_share, "config", "moveit.rviz")
    ros2_controllers_path = os.path.join(moveit_config_share, "config", "ros2_controllers.yaml")

    # Resolve launch args to strings now (we are inside OpaqueFunction context)
    use_dummy = LaunchConfiguration("use_dummy").perform(context)
    usb_port  = LaunchConfiguration("usb_port").perform(context)
    baud_rate = LaunchConfiguration("baud_rate").perform(context)

    # Generate URDF from xacro with args passed through
    robot_description = {
        "robot_description": xacro.process_file(
            urdf_path,
            mappings={
                "use_dummy": use_dummy,
                "usb_port":  usb_port,
                "baud_rate": baud_rate,
            },
        ).toxml()
    }

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # Static TF: world -> base_link
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["--frame-id", "world", "--child-frame-id", "base_link"],
    )

    # ros2_control node
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, ros2_controllers_path],
        output="screen",
    )

    # Spawn controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    arm_0_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_0_controller"],
    )
    arm_1_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_1_controller"],
    )
    arm_0_gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_0_gripper_controller"],
    )
    arm_1_gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_1_gripper_controller"],
    )
    neck_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["neck_controller"],
    )

    # Include MoveIt move_group launch
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_config_share, "launch", "move_group.launch.py")
        )
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config_path],
    )

    # Arm teleop node
    arm_teleop_node = Node(
        package="husky_commander",
        executable="arm_teleop_node",
        output="screen",
    )

    return [
        robot_state_publisher,
        static_tf,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        arm_0_spawner,
        arm_1_spawner,
        arm_0_gripper_spawner,
        arm_1_gripper_spawner,
        neck_spawner,
        move_group_launch,
        rviz_node,
        arm_teleop_node,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_dummy", default_value="true",
                              description="If true, neck runs without real Dynamixels."),
        DeclareLaunchArgument("usb_port",  default_value="/dev/ttyUSB0",
                              description="Serial port for U2D2."),
        DeclareLaunchArgument("baud_rate", default_value="57600",
                              description="Dynamixel bus baud rate."),
        OpaqueFunction(function=launch_setup),
    ])
