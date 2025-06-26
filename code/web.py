from flask import Flask, render_template, jsonify
import threading
import time
import json
import shutil
import os

import numpy as np
from control.dynamixel_port import DynamixelPort

app = Flask(__name__)

controller = None
MOTOR_IDS = [1, 2, 3] # Starting from the wrist

try:
    print("[INIT] Attempting to initialize Dynamixel controller... (If fails: check power connection to board)")
    from control.dynamixel_port import DynamixelPort

    controller = DynamixelPort(
        device="/dev/ttyUSB0",
        dxl_ids=MOTOR_IDS,
        motor_with_torque=MOTOR_IDS
    )
    controller.disable_torque(MOTOR_IDS)
    print("[INIT] Dynamixel controller initialized successfully.")

except Exception as e:
    print("[ERROR] Failed during Dynamixel controller setup.")
    print("        Details:", e)

if controller is None:
    print("[EXIT] Dynamixel controller not available. Aborting.")
    raise SystemExit()


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
    time.sleep(1)
    calibrating = False

def save_results():
    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        return obj

    cleaned = {
        motor: {
            "min": convert(values["min"]),
            "max": convert(values["max"])
        }
        for motor, values in min_max_values.items()
    }

    temp_path = os.path.join(os.path.dirname(__file__), "calibration_temp.json")
    static_path = os.path.join(os.path.dirname(__file__), "static", "calibration.json")

    with open(temp_path, "w") as f:
        json.dump(cleaned, f, indent=2)

    shutil.move(temp_path, static_path)
    print("Calibration saved:", cleaned)
    return cleaned


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/toggle_calibration", methods=["POST"])
def toggle_calibration():
    global calibrating, calibration_thread, min_max_values

    if not calibrating:
        print("[FLASK] Calibration starting")
        calibrating = True
        min_max_values = {i: {"min": float("inf"), "max": float("-inf")} for i in range(3)}

        calibration_thread = threading.Thread(target=calibrate_motors)
        calibration_thread.start()

        return jsonify(status="started")

    else:
        print("[FLASK] Calibration stopping, waiting for thread to finish...")
        calibrating = False  # signal thread to stop

        if calibration_thread and calibration_thread.is_alive():
            calibration_thread.join()  # BLOCK until done

        cleaned = save_results()
        print(f"[FLASK] Calibration stopped, results: {cleaned}")
        return jsonify(status="stopped", calibration=cleaned)


def delayed_save(thread):
    thread.join()
    save_results()

def delayed_save_and_return():
    calibration_thread.join()
    cleaned = save_results()
    print("Delayed calibration result:", cleaned)


@app.route("/status")
def status():
    # Only include calibration data if calibration is done
    if not calibrating:
        with open(os.path.join(app.static_folder, "calibration.json")) as f:
            calibration = json.load(f)
        return jsonify(running=calibrating, calibration=calibration)

    return jsonify(running=calibrating)



@app.route("/encoder_values")
def encoder_values():
    controller.fetch_present_status()
    joint_positions = {
        f"motor_{i+1}": int(pos) for i, pos in enumerate(controller.present_positions)
    }
    return jsonify(joint_positions)

@app.route('/calibration-data')
def serve_calibration_data():
    return app.send_static_file('calibration.json')

#app.run
if __name__ == "__main__":
    #hides flask's logger from appearing
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        controller.cleanup()
