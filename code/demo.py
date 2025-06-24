from control.dynamixel_port import DynamixelPort
import time
import numpy as np


controller = DynamixelPort(
    device="/dev/ttyUSB0",
    dxl_ids=[1,2,3],
    motor_with_torque=[1,2,3]
)

controller.disable_torque([1,2,3])

try:
    while True:
        controller.fetch_present_status()
        print("Positions:", controller.present_positions)
        print("Currents:", controller.present_currents)

        #goal_positions = np.array([2048, 2048])  # midpoint for most Dynamixels
        #controller.set_goal_positions(goal_positions)
        time.sleep(0.05)

except KeyboardInterrupt:
    controller.cleanup()
