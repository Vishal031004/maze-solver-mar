import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('maze_solver')
    world_file = os.path.join(pkg_dir, 'worlds', 'maze.sdf')

    # 1. Start Gazebo
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '--render-engine', 'ogre', world_file], 
        output='screen'
    )

    # 2. Updated Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/model/diff_robot/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        remappings=[('/model/diff_robot/pose', '/tf')],
        output='screen'
    )

    # 3. STATIC TRANSFORMS (The Glue for RViz)
    # This manually connects 'odom' to the robot's base frame
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'chassis']
    )

    # 4. Pledge Node & RViz
    solver = Node(package='maze_solver', executable='pledge_node', output='screen')
    rviz = Node(package='rviz2', executable='rviz2', output='screen')

    return LaunchDescription([
        gazebo, bridge, static_tf, solver, rviz
    ])