from flask import Flask, render_template, jsonify
import threading
import time
import json

import numpy as np
from control.dynamixel_port import DynamixelPort

app = Flask(__name__)

controller = DynamixelPort(
    device="/dev/ttyUSB0",
    dxl_ids=[1, 2, 3],
    motor_with_torque=[1, 2, 3]
)

controller.disable_torque([1, 2, 3])

# Calibration state
calibrating = False
calibration_thread = None
min_max_values = {i: {"min": float("inf"), "max": float("-inf")} for i in range(3)}

def calibrate_motors():
    global calibrating, min_max_values
    start_time = time.time()
    while calibrating and (time.time() - start_time < 10):
        controller.fetch_present_status()
        for i, motor_id in enumerate([1, 2, 3]):
            pos = controller.present_positions[i]
            min_max_values[i]["min"] = min(min_max_values[i]["min"], pos)
            min_max_values[i]["max"] = max(min_max_values[i]["max"], pos)
        time.sleep(1)
    save_results()
    calibrating = False

def save_results():
    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        return obj

    # Convert all values to plain ints
    cleaned = {
        motor: {
            "min": convert(values["min"]),
            "max": convert(values["max"])
        }
        for motor, values in min_max_values.items()
    }

    with open("calibration.json", "w") as f:
        json.dump(cleaned, f, indent=2)

    print("Calibration saved:", cleaned)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/toggle_calibration", methods=["POST"])
def toggle_calibration():
    global calibrating, calibration_thread, min_max_values

    if not calibrating:
        print("Calibration started")
        calibrating = True
        min_max_values = {i: {"min": float("inf"), "max": float("-inf")} for i in range(3)}
        calibration_thread = threading.Thread(target=calibrate_motors)
        calibration_thread.start()
        return jsonify(status="started")
    else:
        print("Calibration stopped manually")
        calibrating = False
        return jsonify(status="stopped")

@app.route("/status")
def status():
    return jsonify(running=calibrating)

@app.route("/encoder_values")
def encoder_values():
    controller.fetch_present_status()
    joint_positions = {
        f"motor_{i+1}": int(pos) for i, pos in enumerate(controller.present_positions)
    }
    return jsonify(joint_positions)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        controller.cleanup()
