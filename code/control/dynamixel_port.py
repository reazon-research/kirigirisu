from dynamixel_sdk import *
import numpy as np
import random
import socket
import sys

ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_GOAL_PWM = 100
ADDR_GOAL_CURRENT = 102
ADDR_POSITION_D_GAIN = 80
ADDR_POSITION_I_GAIN = 82
ADDR_POSITION_P_GAIN = 84
ADDR_PRESENT_CURRENT = 126
ADDR_PRESENT_POSITION = 132
PROTOCOL_VERSION = 2.0
BAUDRATE = 57600
BIMANUAL_PORT = 9000
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
ADDR_OPERATING_MODE = 11
CURRENT_CONTROL_MODE = 0
CURRENT_BASE_POSITION_CONTROL_MODE = 5
EXTENDED_POSITION_CONTROL_MODE = 4
PWM_CONTROL_MODE = 16

def logprint(message):
    pass
    # print(message, file=sys.stderr)

class DynamixelPort:
    method_dict = {
        1 : "write1ByteTxRx",
        2 : "write2ByteTxRx",
        4 : "write4ByteTxRx"
    }

    def __init__(self, device, dxl_ids, motor_with_torque,
                 control_mode=PWM_CONTROL_MODE):
        self.device = device
        self.dxl_ids = dxl_ids
        self.motor_with_torque = motor_with_torque
        self.portHandler = PortHandler(device)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        self.control_mode=control_mode
        if self.portHandler.openPort():
            logprint("Succeeded to open the port")
        else:
            logprint("Failed to open the port")
            logprint("Press any key to terminate...")
            quit()
        if self.portHandler.setBaudRate(BAUDRATE):
            logprint("Succeeded to change the baudrate")
        else:
            logprint("Failed to change the baudrate")
            logprint("Press any key to terminate...")
            quit()
        self.setup()
        self.pos_writer = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_GOAL_POSITION, 4)
        self.cur_writer = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_GOAL_CURRENT, 2)
        self.pwm_writer = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_GOAL_PWM, 2)
        self.groupSyncRead = GroupSyncRead(self.portHandler, self.packetHandler, ADDR_PRESENT_CURRENT, 10)
        for dxl_id in dxl_ids:
            dxl_addparam_result = self.groupSyncRead.addParam(dxl_id)
            if dxl_addparam_result != True:
                logprint("[ID:%03d] groupSyncRead addparam failed" % dxl_id)
                quit()
        self.present_currents = np.zeros((16), np.int16)
        self.present_positions = np.zeros((16), np.int32)

    def writeTxRx(self, dxl_id, addr, value):
        dxl_comm_result, dxl_error = self.packetHandler.__getattribute__(self.method_dict[value.itemsize])(self.portHandler, dxl_id, addr, int(value))
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            exit()
        elif dxl_error != 0:
            logprint("%s" % self.packetHandler.getRxPacketError(dxl_error))
            exit()

    def setup(self):
        for dxl_id in self.dxl_ids:
            self.writeTxRx(dxl_id, ADDR_TORQUE_ENABLE, np.int8(TORQUE_DISABLE))
            #self.writeTxRx(dxl_id, ADDR_OPERATING_MODE, np.int8(CURRENT_BASE_POSITION_CONTROL_MODE))
            #self.writeTxRx(dxl_id, ADDR_OPERATING_MODE, np.int8(PWM_CONTROL_MODE))
            self.writeTxRx(dxl_id, ADDR_OPERATING_MODE, np.int8(self.control_mode))
            self.writeTxRx(dxl_id, ADDR_POSITION_D_GAIN, np.int16(1000))
            self.writeTxRx(dxl_id, ADDR_POSITION_I_GAIN, np.int16(10))
            self.writeTxRx(dxl_id, ADDR_POSITION_P_GAIN, np.int16(100))
            if dxl_id in self.motor_with_torque:
                self.writeTxRx(dxl_id, ADDR_TORQUE_ENABLE, np.int8(TORQUE_ENABLE))

    def cleanup(self):
        for dxl_id in self.dxl_ids:
            self.writeTxRx(dxl_id, ADDR_TORQUE_ENABLE, np.int8(TORQUE_DISABLE))
        self.portHandler.closePort()

    def fetch_present_status(self):
        dxl_comm_result = self.groupSyncRead.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            return
        for i, dxl_id in enumerate(self.dxl_ids):
            if self.groupSyncRead.isAvailable(dxl_id, ADDR_PRESENT_CURRENT, 10):
                self.present_currents[i] = np.array(self.groupSyncRead.getData(dxl_id, ADDR_PRESENT_CURRENT, 2)).astype(np.int16)
                self.present_positions[i] = np.array(self.groupSyncRead.getData(dxl_id, ADDR_PRESENT_POSITION, 4)).astype(np.int32)

    def set_goal_positions(self, pos):
        for dxl_id, p in zip(self.dxl_ids, pos):
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(p)), DXL_HIBYTE(DXL_LOWORD(p)), DXL_LOBYTE(DXL_HIWORD(p)), DXL_HIBYTE(DXL_HIWORD(p))]
            if self.pos_writer.addParam(dxl_id, param_goal_position) != True:
                logprint("[ID:%03d] pos_writer addparam failed" % dxl_id)
        dxl_comm_result = self.pos_writer.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        self.pos_writer.clearParam()

    def set_goal_positions_currents(self, pos, cur):
        for dxl_id, p, c in zip(self.dxl_ids, pos, cur):
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(p)), DXL_HIBYTE(DXL_LOWORD(p)), DXL_LOBYTE(DXL_HIWORD(p)), DXL_HIBYTE(DXL_HIWORD(p))]
            param_goal_current = [DXL_LOBYTE(DXL_LOWORD(c)), DXL_HIBYTE(DXL_LOWORD(c))]
            if self.pos_writer.addParam(dxl_id, param_goal_position) != True:
                logprint("[ID:%03d] pos_writer addparam failed" % dxl_id)
            if self.cur_writer.addParam(dxl_id, param_goal_current) != True:
                logprint("[ID:%03d] cur_writer addparam failed" % dxl_id)
        dxl_comm_result = self.pos_writer.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        self.pos_writer.clearParam()
        dxl_comm_result = self.cur_writer.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        self.cur_writer.clearParam()

    def set_goal_currents(self, cur):
        for dxl_id, c in zip(self.dxl_ids, cur):
            param_goal_current = [DXL_LOBYTE(DXL_LOWORD(c)), DXL_HIBYTE(DXL_LOWORD(c))]
            if self.cur_writer.addParam(dxl_id, param_goal_current) != True:
                logprint("[ID:%03d] cur_writer addparam failed" % dxl_id)
        dxl_comm_result = self.cur_writer.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        self.cur_writer.clearParam()

    def set_goal_pwms(self, pwm):
        for dxl_id, c in zip(self.dxl_ids, pwm):
            param_goal_pwm = [DXL_LOBYTE(DXL_LOWORD(c)), DXL_HIBYTE(DXL_LOWORD(c))]
            if self.pwm_writer.addParam(dxl_id, param_goal_pwm) != True:
                logprint("[ID:%03d] pwm_writer addparam failed" % dxl_id)
        dxl_comm_result = self.pwm_writer.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logprint("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        self.pwm_writer.clearParam()

    def disable_torque(self, ids):
        for dxl_id in ids:
            self.packetHandler.write1ByteTxRx(
                self.portHandler, dxl_id, 64, 0
            )

