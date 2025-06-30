# 🦗 kirigirisu

Kirigirisu is a Python-based toolkit for interacting with Dynamixel motors.

Read joint positions, calibrate motion ranges, and integration with ROS 2 for robot simulation and control.

---

## Requirements

- Python 3.8+
- [Dynamixel SDK (Python)](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)
- U2D2 + U2D2 Power Hub
- Dynamixel motors (ie: XC330-T181-T 12V or XC330-M077-T 5V)
- [ROS 2](https://github.com/reazon-research/openarm_ros2) (optional for sim)

---

## Setup
1. Clone repo
```bash
git clone https://github.com/reazon-research/kirigirisu.git
cd kirigirisu
```
2. Install python dependancies if you haven't
```bash
sudo apt install python3 python3-venv python3-pip
```
3. (Recommended) Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate #Don't forget to enter the ve each time (plug into the matrix)
```
4. Install core packages
```bash
pip install -r requirements.txt
```
5. Install Dynamixel SDK (C++ & Python)
```bash
sudo apt install -y cmake build-essential libusb-1.0-0-dev
```
```bash
cd ~
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git
```
```bash
#C++ installation:
cd DynamixelSDK/c++/build
cmake ..
make
sudo make install
```
```bash
#Python installation:
cd ~/DynamixelSDK/python
pip install .
```
5. Serial port permissions
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyUSB0

#May need to logout login or sudo reboot here
```

---

## Motor Setup

Warning: All new Dynamixel motors ship with the default ID 1.  
To avoid conflicts, assign each motor an unique ID using [Dynamixel Wizard 2](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/):  
1. Connect each motor one at a time and scan with baudrate set to 57600.  
2. Select motor's ID and change to another value on the panel to the right, scroll down and save.  
3. Once done, daisy chain all motors together through TTL and update MOTOR_IDS:
```bash
MOTOR_IDS = [0, 1, 2, 10, 11, 12] # Default, change in all files to the IDs you assignned
```
Make sure to check your motor's min/max voltages and supply accordingly!
```bash
[INFO] Hardware Error Status for ID 10: 1 -> ['Input Voltage Error'] # Means your supplied voltage is too low or high
```


## Calibration Web Interface

Kirigirisu includes a simple Flask + Three.js web UI to easily visualize and calibrate encoders to defined limits.

![Screenshot from 2025-06-26 01-30-17](https://github.com/user-attachments/assets/cf7d2ade-93af-42c3-8f58-068425bd80b3)

To start the web server:

```bash
source venv/bin/activate
python3 code/web.py
```
Then open http://localhost:5000 in your browser. (You may need to refresh the webpage.)

Press Ctrl+C in the terminal to stop the program.

1. Click “Start Calibrating” to begin automatically capturing encoder values.
2. Move the motors through their full range during the 10-second calibration window.
3. You can click the button again to stop early.
4. The recorded min/max positions will be saved and applied after a while to update the model.

---

## Run ROS 2 simulation
1. In one terminal window:
- go to kirigirisu
- source your verison of ros2, the ([openarm ros2](https://github.com/reazon-research/openarm_ros2)), and open the ve
- run the python bridge executable
```bash
cd kirigirisu

source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
source venv/bin/activate

python3 code/ros2Bridge/bridgeCode/bridge_node.py
```
2. Open another terminal window:
- go to openarm's ros2_ws
- source your verison of ros2, then itself
- run the kirigirisu launcher
```bash
cd ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 launch openarm_bimanual_description kirigirisu.launch.py
```
