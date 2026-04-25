import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

class EStopNode(Node):
    def __init__(self):
        super().__init__('e_stop_node')
        
        # We subscribe to the algorithm's commands
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel_auto',
            self.auto_cmd_callback,
            10)
            
        # We publish to the actual robot motors
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.e_stop_active = False
        self.settings = termios.tcgetattr(sys.stdin)
        
        # Timer to constantly check for keyboard input
        self.timer = self.create_timer(0.1, self.check_keystroke)
        
        self.get_logger().info('Emergency Stop Node Initialized.')
        self.get_logger().info('--------------------------------')
        self.get_logger().info('Press [SPACEBAR] to toggle E-STOP.')
        self.get_logger().info('Press [CTRL+C] to quit.')

    def auto_cmd_callback(self, msg):
        # If E-Stop is OFF, pass the autonomous commands through
        if not self.e_stop_active:
            self.publisher.publish(msg)
        else:
            # E-Stop is ON: Actively jam the signal with zeros!
            self.halt_robot()
    def check_keystroke(self):
        key = self.getKey()
        if key == ' ':
            self.e_stop_active = not self.e_stop_active
            if self.e_stop_active:
                self.get_logger().warn('🚨 E-STOP ENGAGED! ROBOT HALTED. 🚨')
                self.halt_robot()
            else:
                self.get_logger().info('✅ E-STOP DISENGAGED. Resuming autonomous control.')
        elif key == '\x03': # CTRL+C
            rclpy.shutdown()

    def halt_robot(self):
        # Publish pure zeros to lock the motors
        halt_msg = Twist()
        halt_msg.linear.x = 0.0
        halt_msg.angular.z = 0.0
        self.publisher.publish(halt_msg)

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        # Check if a key is actually pressed before trying to read
        rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''  # Return empty string if no key is pressed
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
def main(args=None):
    rclpy.init(args=args)
    node = EStopNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
