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
2. (Recommended) Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Install Dynamixel SDK (C++ + Python)
```bash
# Install C++ SDK for Dynamixel
sudo apt install -y cmake build-essential libusb-1.0-0-dev

# Clone SDK
cd ~
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git

# Build and install C++ SDK
cd DynamixelSDK/c++/build
cmake ..
make
sudo make install

# Install Python SDK
cd ~/DynamixelSDK/python
pip install
```
5. Serial port permissions
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyUSB0

#May need to login logout or sudo reboot here
```
