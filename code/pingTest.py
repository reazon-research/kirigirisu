from dynamixel_sdk import *

portHandler = PortHandler("/dev/ttyUSB0")
packetHandler = PacketHandler(2.0)
portHandler.openPort()
portHandler.setBaudRate(57600)
dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, 1)

if dxl_comm_result == COMM_SUCCESS:
    print(f"Ping successful, model number: {dxl_model_number}")
else:
    print("Ping failed")
