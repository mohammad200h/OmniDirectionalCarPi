#!/usr/bin/env python3
"""Launch IMU publisher and RViz2 with IMU visualization."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('imu_publisher')
    rviz_config = os.path.join(pkg_dir, 'config', 'imu_rviz.rviz')

    port_arg = DeclareLaunchArgument('port', default_value='/dev/ttyUSB0',
                                    description='Serial port for IMU')
    rviz_arg = DeclareLaunchArgument('rviz', default_value='true',
                                    description='Launch RViz2')

    imu_node = Node(
        package='imu_publisher',
        executable='imu_publisher_node',
        name='imu_publisher_node',
        parameters=[{
            'port': LaunchConfiguration('port'),
            'frame_id': 'imu_link',
        }],
    )

    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu_tf',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'imu_link'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        port_arg,
        rviz_arg,
        imu_node,
        static_tf,
        rviz_node,
    ])
