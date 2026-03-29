#!/usr/bin/env python3
"""
ROS2 IMU Publisher for Yahboom 10-axis IMU Module (USB).

Based on: https://github.com/YahboomTechnology/10-axis_IMU_Module
Protocol: 0x55 frame header, 0x51=accel, 0x52=gyro, 0x53=angle
"""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Header

try:
    import serial
except ImportError:
    raise ImportError("pyserial is required. Install with: pip install pyserial")


# Yahboom 10-axis IMU protocol constants
BUF_LENGTH = 11
K_ACC = 16.0   # ±16g
K_GYRO = 2000.0  # ±2000 deg/s
K_ANGLE = 180.0  # ±180 deg
G = 9.80665     # m/s² per g


def euler_to_quaternion(roll_deg: float, pitch_deg: float, yaw_deg: float) -> tuple:
    """Convert Euler angles (degrees, roll-pitch-yaw) to quaternion (x, y, z, w)."""
    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return (x, y, z, w)


def parse_acc(data: list) -> tuple:
    """Parse acceleration data (returns g's)."""
    axl, axh = data[0], data[1]
    ayl, ayh = data[2], data[3]
    azl, azh = data[4], data[5]
    acc_x = (axh << 8 | axl) / 32768.0 * K_ACC
    acc_y = (ayh << 8 | ayl) / 32768.0 * K_ACC
    acc_z = (azh << 8 | azl) / 32768.0 * K_ACC
    if acc_x >= K_ACC:
        acc_x -= 2 * K_ACC
    if acc_y >= K_ACC:
        acc_y -= 2 * K_ACC
    if acc_z >= K_ACC:
        acc_z -= 2 * K_ACC
    return acc_x, acc_y, acc_z


def parse_gyro(data: list) -> tuple:
    """Parse gyro data (returns deg/s)."""
    wxl, wxh = data[0], data[1]
    wyl, wyh = data[2], data[3]
    wzl, wzh = data[4], data[5]
    gyro_x = (wxh << 8 | wxl) / 32768.0 * K_GYRO
    gyro_y = (wyh << 8 | wyl) / 32768.0 * K_GYRO
    gyro_z = (wzh << 8 | wzl) / 32768.0 * K_GYRO
    if gyro_x >= K_GYRO:
        gyro_x -= 2 * K_GYRO
    if gyro_y >= K_GYRO:
        gyro_y -= 2 * K_GYRO
    if gyro_z >= K_GYRO:
        gyro_z -= 2 * K_GYRO
    return gyro_x, gyro_y, gyro_z


def parse_angle(data: list) -> tuple:
    """Parse angle data (returns degrees: roll, pitch, yaw)."""
    rxl, rxh = data[0], data[1]
    ryl, ryh = data[2], data[3]
    rzl, rzh = data[4], data[5]
    angle_x = (rxh << 8 | rxl) / 32768.0 * K_ANGLE
    angle_y = (ryh << 8 | ryl) / 32768.0 * K_ANGLE
    angle_z = (rzh << 8 | rzl) / 32768.0 * K_ANGLE
    if angle_x >= K_ANGLE:
        angle_x -= 2 * K_ANGLE
    if angle_y >= K_ANGLE:
        angle_y -= 2 * K_ANGLE
    if angle_z >= K_ANGLE:
        angle_z -= 2 * K_ANGLE
    return angle_x, angle_y, angle_z


class IMUPublisherNode(Node):
    """Publishes IMU data from Yahboom 10-axis USB IMU to ROS2 /imu topic."""

    def __init__(self, port: str = '/dev/ttyUSB0', baud: int = 9600, frame_id: str = 'imu_link'):
        super().__init__('imu_publisher')
        self.declare_parameter('port', port)
        self.declare_parameter('baud', baud)
        self.declare_parameter('frame_id', frame_id)

        self.port = self.get_parameter('port').get_parameter_value().string_value
        self.baud = self.get_parameter('baud').get_parameter_value().integer_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        self.publisher = self.create_publisher(Imu, 'imu', 10)

        # Protocol state
        self.start = 0
        self.data_length = 0
        self.check_sum = 0
        self.rx_buff = [0] * BUF_LENGTH

        # Latest readings (g, deg/s, deg)
        self.acc = [0.0, 0.0, 0.0]
        self.gyro = [0.0, 0.0, 0.0]
        self.angle = [0.0, 0.0, 0.0]
        self.last_publish_time = None

        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.5)
            self.get_logger().info(f"Serial opened: {self.port} @ {self.baud}")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open {self.port}: {e}")
            raise

        self.timer = self.create_timer(0.01, self.read_and_publish)

    def _process_byte(self, byte_val: int) -> bool:
        """Process one byte. Returns True if a full frame was received."""
        if byte_val == 0x55 and self.start == 0:
            self.start = 1
            self.data_length = BUF_LENGTH
            self.check_sum = 0
            for i in range(BUF_LENGTH):
                self.rx_buff[i] = 0

        if self.start == 1:
            self.check_sum += byte_val
            self.rx_buff[BUF_LENGTH - self.data_length] = byte_val
            self.data_length -= 1
            if self.data_length == 0:
                self.check_sum = (self.check_sum - byte_val) & 0xFF
                self.start = 0
                if self.rx_buff[BUF_LENGTH - 1] == self.check_sum:
                    self._handle_frame(self.rx_buff)
                    return True
        return False

    def _handle_frame(self, buf: list):
        """Handle a complete 11-byte frame."""
        if buf[1] == 0x51:
            self.acc = parse_acc(buf[2:8])
        elif buf[1] == 0x52:
            self.gyro = parse_gyro(buf[2:8])
        elif buf[1] == 0x53:
            self.angle = parse_angle(buf[2:8])

    def read_and_publish(self):
        """Read serial data and publish when we have fresh readings."""
        try:
            while self.ser.in_waiting > 0:
                rx = self.ser.read(1)
                if len(rx) == 1:
                    byte_val = int(rx.hex(), 16)
                    self._process_byte(byte_val)
        except serial.SerialException as e:
            self.get_logger().error(f"Serial read error: {e}")
            return

        msg = Imu()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        # Linear acceleration: g -> m/s²
        msg.linear_acceleration.x = self.acc[0] * G
        msg.linear_acceleration.y = self.acc[1] * G
        msg.linear_acceleration.z = self.acc[2] * G
        msg.linear_acceleration_covariance[0] = -1.0  # unknown covariance

        # Angular velocity: deg/s -> rad/s
        deg_to_rad = math.pi / 180.0
        msg.angular_velocity.x = self.gyro[0] * deg_to_rad
        msg.angular_velocity.y = self.gyro[1] * deg_to_rad
        msg.angular_velocity.z = self.gyro[2] * deg_to_rad
        msg.angular_velocity_covariance[0] = -1.0

        # Orientation: Euler (deg) -> quaternion
        qx, qy, qz, qw = euler_to_quaternion(self.angle[0], self.angle[1], self.angle[2])
        msg.orientation.x = qx
        msg.orientation.y = qy
        msg.orientation.z = qz
        msg.orientation.w = qw
        msg.orientation_covariance[0] = -1.0

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    try:
        node = IMUPublisherNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
