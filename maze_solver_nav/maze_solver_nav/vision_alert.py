import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np
import os


class VisionAlert(Node):

    def __init__(self):
        super().__init__('vision_alert')

        self.alert_spoken = False

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info("Vision Alert Node Started")

    def image_callback(self, msg):
        try:
            # Convert ROS image to OpenCV image
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='passthrough'
            )

            # Convert RGB -> HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

            # Red range 1
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])

            # Red range 2
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])

            # Create masks
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

            mask = mask1 + mask2

            # Count red pixels
            red_pixels = cv2.countNonZero(mask)

            hazard_found = False

            if red_pixels > 500:

                contours, _ = cv2.findContours(
                    mask,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    area = cv2.contourArea(contour)

                    if area > 300:
                        hazard_found = True

                        x, y, w, h = cv2.boundingRect(contour)

                        cv2.rectangle(
                            frame,
                            (x, y),
                            (x + w, y + h),
                            (0, 0, 255),
                            2
                        )

                if hazard_found:

                    cv2.putText(
                        frame,
                        "HAZARD DETECTED!",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3
                    )

                    self.get_logger().warn("RED HAZARD DETECTED!")

                    # Speak only once while visible
                    if not self.alert_spoken:
                        os.system('espeak "Warning. Hazard detected ahead." &')
                        self.alert_spoken = True

            else:
                # Reset when object disappears
                self.alert_spoken = False

            # Show camera feed
            cv2.imshow("Robot Camera Feed", frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(str(e))


def main(args=None):
    rclpy.init(args=args)

    node = VisionAlert()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()