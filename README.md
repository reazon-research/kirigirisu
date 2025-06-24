# 🦗 kirigirisu

Kirigirisu is a Python-based toolkit for interacting with Dynamixel motors.

Read joint positions, calibrate motion ranges, and integration with ROS 2 for robot simulation and control.

---

## Requirements

- Python 3.8+
- [Dynamixel SDK (Python)](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/)
- U2D2 + U2D2 Power Hub
- Dynamixel motors (ie: XC330-T181-T)
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
python3 -m venv .venv
source .venv/bin/activate #Don't forget to enter the ve each time (plug into the matrix)
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
