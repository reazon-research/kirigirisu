from control.dynamixel_port import DynamixelPort
import time
import numpy as np


MOTOR_IDS = [1, 2, 3] # Starting from the wrist

controller = DynamixelPort(
    device="/dev/ttyUSB0",
    dxl_ids=MOTOR_IDS,
    motor_with_torque=MOTOR_IDS
)

controller.disable_torque(MOTOR_IDS)

try:
    while True:
        controller.fetch_present_status()
        print("Positions:", controller.present_positions)
        print("Currents:", controller.present_currents)

        #goal_positions = np.array([2048, 2048])  # midpoint for most Dynamixels
        #controller.set_goal_positions(goal_positions)
        time.sleep(0.1)

except KeyboardInterrupt:
    controller.cleanup()
