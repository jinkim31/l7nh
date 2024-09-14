from framework.multithreading import ThreadWorker, ItcReceiver, ItcTransmitter
import pysoem
import time
import ctypes


class L7NH(object):
    def __init__(self):
        self.__worker = L7NHWorker()
        self.__motion_command_transmitter = ItcTransmitter()
        self.__motion_status_receiver = ItcReceiver(1)
        self.__is_open = False
        self.__device = None

        # inter-thread links
        self.__motion_command_transmitter.link(self.__worker.motion_command_receiver)
        self.__worker.motion_status_transmitter.link(self.__motion_status_receiver)

    def open(self, ethernet_adapter_id):
        if self.__is_open:
            return False
        if not self.__worker.open_ethercat(ethernet_adapter_id):
            return False
        self.__is_open = True
        self.__worker.start()
        return True

    def close(self):
        if not self.__is_open:
            return False
        self.__worker.stop()
        return True

    def move_to_position(self,
                         target_position,
                         profile_velocity=200000,
                         profile_acceleration=200000, profile_deceleration=200000):
        self.__motion_command_transmitter.transmit((
            target_position, profile_velocity, profile_acceleration, profile_deceleration))

    def get_status(self, timeout=0.0):
        return self.__motion_status_receiver.receive(timeout)


class L7NHWorker(ThreadWorker):
    def __init__(self):
        super().__init__(loop_interval=0.01)
        self.motion_command_receiver = ItcReceiver(1)
        self.motion_status_transmitter = ItcTransmitter()
        self.__master = pysoem.Master()

    def open_ethercat(self, ethernet_adapter_id, device_index=0):
        self.__master.open(ethernet_adapter_id)
        self.__master.config_init()
        if len(self.__master.slaves) == 0:
            return False
        self.__device = self.__master.slaves[device_index]
        print(self.__device.name)
        return True

    def _user_on_start(self):
        # give pysoem some time
        time.sleep(0.1)

        # use default pdo mapping 1
        self.__device.sdo_write(0x1C12, 0, bytes(ctypes.c_uint16(0x00)))
        self.__device.sdo_write(0x1C13, 0, bytes(ctypes.c_uint16(0x00)))
        self.__device.sdo_write(0x1C12, 1, bytes(ctypes.c_uint16(0x1600)))  # rxpdo1
        self.__device.sdo_write(0x1C13, 1, bytes(ctypes.c_uint16(0x1A00)))  # txpdo1
        self.__device.sdo_write(0x1C12, 0, bytes(ctypes.c_uint16(0x01)))
        self.__device.sdo_write(0x1C13, 0, bytes(ctypes.c_uint16(0x01)))

        # transition to safe-op state
        self.__master.config_map()
        self.__master.state_check(pysoem.SAFEOP_STATE, 5000000)

        # transition to op state
        self.__master.send_processdata()
        self.__master.state = pysoem.OP_STATE
        self.__master.write_state()
        self.__master.state_check(pysoem.OP_STATE, 5000000)

        # servo on
        self.__device.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0006)))
        self.__device.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0007)))
        self.__device.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x000F)))

    def _user_on_loop(self):

        # check for new motion command
        if self.motion_command_receiver.available():
            motion_command = self.motion_command_receiver.receive()
            # set profile parameters through sdo
            self.__device.sdo_write(0x6081, 0,  bytes(ctypes.c_uint32(motion_command[1])))
            self.__device.sdo_write(0x6083, 0,  bytes(ctypes.c_uint32(motion_command[2])))
            self.__device.sdo_write(0x6084, 0,  bytes(ctypes.c_uint32(motion_command[3])))
            target_position = ctypes.c_int32(motion_command[0])
            controlword = ctypes.c_uint16(0x001F)
        else:
            target_position = ctypes.c_int32(0)
            controlword = ctypes.c_uint16(0x000F)

        # send pdo
        target_torque = ctypes.c_int16(10000)
        drive_mode = ctypes.c_int8(1)
        touch_probe_function = ctypes.c_uint16(0)
        self.__device.output = \
            bytes(controlword) \
            + bytes(target_torque) \
            + bytes(target_position) \
            + bytes(drive_mode) \
            + bytes(touch_probe_function)
        self.__master.send_processdata()

        # receive pdo
        self.__master.receive_processdata()
        statusword = ctypes.c_uint16.from_buffer_copy(self.__device.input[:2])
        actual_torque = ctypes.c_int16.from_buffer_copy(self.__device.input[2:4])
        actual_position = ctypes.c_int32.from_buffer_copy(self.__device.input[4:8])
        position_error = ctypes.c_int32.from_buffer_copy(self.__device.input[8:12])
        digital_input = ctypes.c_int32.from_buffer_copy(self.__device.input[12:16])
        actual_drive_mode = ctypes.c_int8.from_buffer_copy(self.__device.input[16:17])
        velocity_command = ctypes.c_int16.from_buffer_copy(self.__device.input[17:19])
        actual_velocity = ctypes.c_int16.from_buffer_copy(self.__device.input[19:21])

        # transmit motion status
        reached = bool(statusword.value >> 10 & 0x01)
        motion_status = (actual_position.value, reached)
        self.motion_status_transmitter.transmit(motion_status)

    def _user_on_stop(self):
        pass
