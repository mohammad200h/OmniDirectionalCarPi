from setuptools import setup
import os
from glob import glob

package_name = 'imu_publisher'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.rviz')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='pi',
    maintainer_email='pi@raspberrypi.local',
    description='ROS2 publisher for Yahboom 10-axis IMU Module (USB)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'imu_publisher_node = imu_publisher.imu_publisher_node:main',
        ],
    },
)
