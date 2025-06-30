import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import sys
import os
import json
from pathlib import Path
from urdf_parser_py.urdf import URDF

import launch_ros
from launch_ros.substitutions import FindPackageShare
import xacro

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from control.dynamixel_port import DynamixelPort

# Control table addresses (for X-series motors like XM430-W210)
ADDR_PRESENT_POSITION = 132  # 4 bytes


MOTOR_IDS = [0, 1, 2, 10, 11, 12]
MOTOR_TO_JOINT = {
    0: 'left_rev6',
    1: 'left_rev7',
    2: ['left_left_pris1', 'left_right_pris2'],
    10: 'right_rev6',
    11: 'right_rev7',
    12: ['right_left_pris1', 'right_right_pris2'],
    # add more as needed
}
# Optional per-joint transformations: {joint_name: (scale, offset)}
    # (-1.0, 0.0),  # invert
    # (-1.0, 0.1),  # invert + offset
JOINT_TRANSFORMS = {
    "right_rev6": (-1, 0),
    "left_rev6": (-1,0),
    "left_right_pris2": (-1, 0),
    "right_left_pris1": (-1, -0.05),
    "right_right_pris2": (1, 0.05),
    # Add others as needed
}


class ros2Bridge(Node):
    def __init__(self):
        super().__init__('kirigirisu_ros2_bridge')

        calibration_path = Path(__file__).resolve().parents[2] / "static" / "calibration.json"
        if not calibration_path.exists():
            self.get_logger().error(f"Calibration file not found: {calibration_path}")
            rclpy.shutdown()
            return

        with open(calibration_path) as f:
            self.encoder_limits = json.load(f)

        # ROS publisher that sends joint states to /joint_states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        # Runs every 20ms (50 Hz)
        self.timer = self.create_timer(0.02, self.publish_joint_states)

        self.motor = DynamixelPort(
            device="/dev/ttyUSB0",
            dxl_ids=MOTOR_IDS,
            motor_with_torque=MOTOR_IDS
        )

        self.portHandler = self.motor.portHandler
        self.packetHandler = self.motor.packetHandler

        self.motor_to_joint = MOTOR_TO_JOINT
        
        # Store joint limits from urdf
        pkg_share = Path(
            launch_ros.substitutions.FindPackageShare(package="openarm_bimanual_description").find(
                "openarm_bimanual_description"
            )
        )
        default_model_path = pkg_share / "urdf/openarm_bimanual.urdf.xacro"
        doc = xacro.process_file(str(default_model_path))
        robot_description_xml = doc.toxml()
        robot = URDF.from_xml_string(robot_description_xml)

        self.joint_angle_limits = {
            joint.name: (joint.limit.lower, joint.limit.upper)
            for joint in robot.joints
            if joint.limit is not None
        }

        for joint in robot.joints:
            if joint.limit:
                print(joint.name, joint.limit.lower, joint.limit.upper)

    def publish_joint_states(self):
        try:
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()

            joint_names = []
            positions_rad = []

            TICKS_PER_REV = 4096.0
            RAD_PER_TICK = 2 * 3.1415926 / TICKS_PER_REV
            positions_rad = []

            for motor_id in MOTOR_IDS:
                try:
                    dxl_position, dxl_comm_result, dxl_error = self.motor.packetHandler.read4ByteTxRx(
                        self.motor.portHandler, motor_id, ADDR_PRESENT_POSITION
                    )

                    if dxl_comm_result != 0:
                        raise Exception(f"Comm failed: {dxl_comm_result}")
                    if dxl_error != 0:
                        raise Exception(f"Dynamixel error: {dxl_error}")

                    if dxl_position > 0x7FFFFFFF:
                        dxl_position -= 0x100000000

                    joint_names_for_motor = self.motor_to_joint.get(motor_id, [])
                    if joint_names_for_motor is None:
                        self.get_logger().warn(f"No joint mapping for motor ID {motor_id}")
                        continue

                    
                    if isinstance(joint_names_for_motor, str):
                        joint_names_for_motor = [joint_names_for_motor]

                    # 1. Get encoder min/max
                    raw_min = self.encoder_limits[str(motor_id)]["min"]
                    raw_max = self.encoder_limits[str(motor_id)]["max"]

                    # 2. Normalize
                    clamped = max(raw_min, min(raw_max, dxl_position))
                    ratio = (clamped - raw_min) / (raw_max - raw_min)

                    # 3. Map to joint angle
                    # For every joint controlled by this motor
                    for joint_name in joint_names_for_motor:
                        # Get joint angle limits
                        joint_min, joint_max = self.joint_angle_limits[joint_name]

                        # Map normalized value to joint angle range
                        # Map normalized value to joint angle range
                        angle = joint_min + ratio * (joint_max - joint_min)

                        # Apply transform if defined
                        if joint_name in JOINT_TRANSFORMS:
                            scale, offset = JOINT_TRANSFORMS[joint_name]
                            angle = angle * scale + offset

                        joint_names.append(joint_name)
                        positions_rad.append(angle)

                except Exception as motor_error:
                    self.get_logger().warn(f"Motor ID {motor_id} read failed: {motor_error}")
                    # Append zero angles for all joints controlled by this motor
                    joint_names_for_motor = self.motor_to_joint.get(motor_id, [])
                    if isinstance(joint_names_for_motor, str):
                        joint_names_for_motor = [joint_names_for_motor]
                    for joint_name in joint_names_for_motor:
                        joint_names.append(joint_name)
                        positions_rad.append(0.0)


            msg.name = joint_names
            msg.position = positions_rad
            self.joint_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f"publish_joint_states() failed: {e}")





def main(args=None):
    rclpy.init(args=args)
    node = ros2Bridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
