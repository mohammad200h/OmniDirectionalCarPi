#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    """Node that publishes 'Hi from raspberrypi' on the /hello topic."""

    def __init__(self):
        super().__init__('hello_talker')
        self.publisher = self.create_publisher(String, 'hello', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.msg = String()
        self.msg.data = 'Hi from raspberrypi'

    def timer_callback(self):
        self.publisher.publish(self.msg)
        self.get_logger().info(f"Publishing: '{self.msg.data}'")


def main(args=None):
    rclpy.init(args=args)
    node = TalkerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
