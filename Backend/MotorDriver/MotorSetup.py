import odrive
import time
from odrive.enums import *
from odrive.utils import dump_errors

class Motor:
    def __init__(self, serial_number):
        self.odrive = odrive.find_any()
        print(f"Connected to ODrive with serial number {self.odrive.serial_number}")
        self.axis = self.odrive.axis0
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")

    def startMotor(self):
        self.axis.controller.config.control_mode = ControlMode.POSITION_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 200
        self.axis.config.enable_watchdog = True
        self.axis.controller.input_pos = 0
        self.axis.controller.config.vel_limit = 1
        time.sleep(0.5)
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")


    def set_velocity(self, velocity):
        self.axis.controller.input_vel = velocity

    def set_position(self, position, time_frame):
        print(f"Setting position to {position}")
        if -10.0 <= position <= 10.0:
            mapped_position = (position / 10) * 0.5
            print(f"Setting position to {mapped_position}")
            self.axis.controller.input_pos = mapped_position
        else:
            print("Position out of bounds. Must be between -0.5 and 0.5.")

    def stop(self):
        self.axis.controller.input_vel = 0
        self.axis.requested_state = AxisState.IDLE

    def get_position(self):
        return self.axis.encoder.pos_estimate
    
    def get_voltage(self):
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")
