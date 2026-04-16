import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class PledgeSolver(Node):
    def __init__(self):
        super().__init__('pledge_solver')

        self.cmd_pub  = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        self.state = 'MOVE_STRAIGHT'

        self.front_dist       = 10.0
        self.front_left_dist  = 10.0
        self.front_right_dist = 10.0
        self.right_dist       = 10.0
        self.left_dist        = 10.0

        self.initial_yaw_set    = False
        self.preferred_yaw      = 0.0
        self.current_yaw        = 0.0
        self.prev_yaw           = 0.0
        self.total_angle_turned = 0.0

        self.turn_target_yaw = 0.0
        self.turn_direction  = 1.0

        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info("Maze solver ready.")

    def odom_cb(self, msg):
        q = msg.pose.pose.orientation
        siny = 2 * (q.w * q.z + q.x * q.y)
        cosy = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw  = math.atan2(siny, cosy)

        if not self.initial_yaw_set:
            self.preferred_yaw   = yaw
            self.prev_yaw        = yaw
            self.initial_yaw_set = True

        delta = yaw - self.prev_yaw
        if delta >  math.pi: delta -= 2 * math.pi
        if delta < -math.pi: delta += 2 * math.pi

        self.total_angle_turned += delta
        self.current_yaw = yaw
        self.prev_yaw    = yaw

    def scan_cb(self, msg):
        n = len(msg.ranges)

        def clean(idxs):
            vals  = [msg.ranges[i % n] for i in idxs]
            valid = [r for r in vals if 0.12 < r < 10.0]
            return min(valid) if valid else 10.0

        self.front_dist       = clean(range(165, 196))
        self.front_left_dist  = clean(range(195, 226))
        self.front_right_dist = clean(range(135, 166))
        self.left_dist        = clean(range(255, 286))
        self.right_dist       = clean(range(75,  106))

    def control_loop(self):
        msg = Twist()

        COLLISION = 0.35
        WALL_STOP = 0.65
        PREFER    = 0.50

        if self.front_dist < COLLISION:
            self.get_logger().warn(f"EMERGENCY STOP  front={self.front_dist:.2f}m")
            self.cmd_pub.publish(msg)
            return

        if   self.state == 'MOVE_STRAIGHT': self._move_straight(msg, WALL_STOP)
        elif self.state == 'TURN':          self._turn(msg)
        elif self.state == 'WALL_FOLLOW':   self._wall_follow(msg, WALL_STOP, PREFER)

        self.cmd_pub.publish(msg)

    def _move_straight(self, msg, wall_stop):
        if self.front_dist < wall_stop:
            self._begin_turn(+math.pi / 2)
            self.get_logger().info("Wall ahead -> TURN 90 deg left")
            return
        msg.linear.x  = 0.3
        msg.angular.z = 0.0

    def _begin_turn(self, delta_yaw):
        target = self.current_yaw + delta_yaw
        target = math.atan2(math.sin(target), math.cos(target))
        self.turn_target_yaw = target
        self.turn_direction  = 1.0 if delta_yaw >= 0 else -1.0
        self.state = 'TURN'

    def _turn(self, msg):
        yaw_err = self.turn_target_yaw - self.current_yaw
        yaw_err = math.atan2(math.sin(yaw_err), math.cos(yaw_err))

        TURN_DONE  = 0.05
        TURN_SPEED = 0.45

        if abs(yaw_err) < TURN_DONE:
            self.total_angle_turned = 0.0
            self.state = 'WALL_FOLLOW'
            self.get_logger().info("Turn done -> WALL_FOLLOW")
            return

        msg.linear.x  = 0.0
        msg.angular.z = TURN_SPEED * self.turn_direction

    def _wall_follow(self, msg, wall_stop, prefer):
        if self.front_dist < wall_stop:
            self._begin_turn(+math.pi / 2)
            self.get_logger().info("Front blocked -> TURN 90 deg left")
            return

        if self.front_right_dist < wall_stop:
            self._begin_turn(+math.pi / 4)
            return

        err        = self.right_dist - prefer
        correction = max(-0.3, min(0.3, -0.9 * err))

        msg.linear.x  = 0.22
        msg.angular.z = correction

        if (abs(self.total_angle_turned) < 0.20 and
                self.front_dist > wall_stop + 0.3):
            self.state = 'MOVE_STRAIGHT'
            self.get_logger().info(
                f"Pledge escape! turns={self.total_angle_turned:.2f} -> MOVE_STRAIGHT")

def main(args=None):
    rclpy.init(args=args)
    node = PledgeSolver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()