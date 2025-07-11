import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class TurtleBotController(Node):
    def __init__(self):
        super().__init__('turtlebot_controller')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

    def move_back(self, speed, duration):
        msg = Twist()
        msg.linear.x = -speed
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        time.sleep(duration)
        msg.linear.x = 0.0
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = TurtleBotController()
    controller.move_back(0.5, 5.0)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
