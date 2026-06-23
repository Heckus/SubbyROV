#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer')

        # Declare parameters so the topic/window are configurable
        self.declare_parameter('topic', '/qut_rov/left/image_color')
        self.declare_parameter('window_name', 'ROV Camera')

        topic = self.get_parameter('topic').get_parameter_value().string_value
        self.window_name = self.get_parameter('window_name').get_parameter_value().string_value

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            topic,
            self.image_callback,
            10
        )

        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        self.get_logger().info(f'Subscribed to {topic}')

    def image_callback(self, msg: Image):
        try:
            # Stonefish publishes in RGB; convert to BGR for OpenCV display
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()