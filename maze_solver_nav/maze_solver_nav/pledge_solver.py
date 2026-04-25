import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math


class PledgeSolver(Node):
    def __init__(self):
        super().__init__('pledge_solver_node')

        # ROS 2 Interfaces
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_auto', 10)
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            qos_profile_sensor_data
        )
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # State Machine Variables
        self.STATE_FORWARD = 0
        self.STATE_WALL_FOLLOW = 1
        self.state = self.STATE_FORWARD

        # Algorithm Variables
        self.initial_yaw = None
        self.current_yaw = 0.0
        self.last_yaw = 0.0
        self.accumulated_angle = 0.0

        # LiDAR Thresholds
        self.safe_dist = 0.45
        self.wall_dist = 0.45

        # (Unused placeholder variables kept from original file)
        self.hazard_x = 1.5
        self.hazard_y = 1.5
        self.hazard_found = False

        self.get_logger().info('Pledge Algorithm Node Active.')
        self.get_logger().info('Searching for Base Heading...')

    def odom_callback(self, msg):
        # Extract yaw from quaternion
        q = msg.pose.pose.orientation

        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)

        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

        # Initialize heading once
        if self.initial_yaw is None:
            self.initial_yaw = self.current_yaw
            self.last_yaw = self.current_yaw
            self.get_logger().info(
                f'Base Heading Locked: {math.degrees(self.initial_yaw):.1f}°'
            )
            return

        # Heading delta with wraparound handling
        dyaw = self.current_yaw - self.last_yaw

        if dyaw > math.pi:
            dyaw -= 2 * math.pi
        elif dyaw < -math.pi:
            dyaw += 2 * math.pi

        self.accumulated_angle += dyaw
        self.last_yaw = self.current_yaw

    def laser_callback(self, msg):
        if self.initial_yaw is None:
            return

        clean_ranges = [
            r if r < 12.0 and not math.isnan(r) else 10.0
            for r in msg.ranges
        ]

        # Front and right sectors
        front_dist = min(clean_ranges[175:185])
        right_dist = min(clean_ranges[80:100])

        msg_cmd = Twist()

        # =============================
        # FAST TUNED PLEDGE ALGORITHM
        # =============================

        if self.state == self.STATE_FORWARD:

            if front_dist < self.safe_dist:
                self.get_logger().info(
                    'Obstacle detected. Switching to Wall Follow.'
                )
                self.state = self.STATE_WALL_FOLLOW

            else:
                # FASTER FORWARD SPEED
                msg_cmd.linear.x = 0.30
                msg_cmd.angular.z = 0.0

        elif self.state == self.STATE_WALL_FOLLOW:

            # Break away when heading resolved
            if abs(self.accumulated_angle) < 0.17 and front_dist > self.safe_dist:
                self.get_logger().info(
                    'Angle resolved (0°). Breaking away from wall!'
                )
                self.state = self.STATE_FORWARD
                msg_cmd.linear.x = 0.30
                msg_cmd.angular.z = 0.0

            else:
                # Right-hand wall follow

                if front_dist < self.safe_dist:
                    # Sharp left turn
                    msg_cmd.linear.x = 0.0
                    msg_cmd.angular.z = 1.6

                elif right_dist < (self.wall_dist - 0.1):
                    # Too close to wall
                    msg_cmd.linear.x = 0.22
                    msg_cmd.angular.z = 0.45

                elif right_dist > (self.wall_dist + 0.4):
                    # Lost wall -> aggressive right hook
                    msg_cmd.linear.x = 0.18
                    msg_cmd.angular.z = -1.6

                elif right_dist > (self.wall_dist + 0.1):
                    # Slight drift away
                    msg_cmd.linear.x = 0.24
                    msg_cmd.angular.z = -0.45

                else:
                    # Cruise
                    msg_cmd.linear.x = 0.30
                    msg_cmd.angular.z = 0.0

        self.cmd_pub.publish(msg_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = PledgeSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()