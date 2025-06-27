import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from control.dynamixel_port import DynamixelPort

MOTOR_IDS = [0, 1, 2, 10, 11, 12] # Starting from the wrist

class ros2Bridge(Node):
    print("Hello world")
    def __init__(self):
        super().__init__('kirigirisu_ros2_bridge')

        # 🧠 ROS publisher that sends joint states to /joint_states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        # 🕒 Runs every 20ms (50 Hz)
        self.timer = self.create_timer(0.02, self.publish_joint_states)

        self.motor = DynamixelPort(
            device="/dev/ttyUSB0",
            dxl_ids=MOTOR_IDS,
            motor_with_torque=MOTOR_IDS
        )

        # 🚧 Joint names must match your URDF
        self.joint_names = ['left_rev1']

        self.get_logger().info("Bridge node started and publishing joint states.")

        self.position = 5.0  # start at +1.0 rad
        self.last_toggle_time = time.time()
        self.toggle_interval = 1.0  # seconds to hold each position



    def publish_joint_states(self):
        try:
            current_time = time.time()
            if current_time - self.last_toggle_time > self.toggle_interval:
                # Toggle position between +1.0 and -1.0
                self.position = -self.position
                self.last_toggle_time = current_time
            

            # Joint movement
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = ['left_rev1', 'right_rev1']
            msg.position = [self.position, self.position]
            self.joint_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f"Failed to publish test joint state: {e}")



def main(args=None):
    rclpy.init(args=args)
    node = ros2Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
