import odrive
import time
from odrive.enums import *
from odrive.utils import dump_errors

class Motor:
    def __init__(self, serial_number):
        self.odrive = odrive.find_any()
        print(f"Connected to ODrive with serial number {self.odrive.serial_number}")
        self.axis = self.odrive.axis0
        self.limitLeft 
        self.limitRight
        self.midPoint
        self.getLimits()

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
        mapped_position = (self.map_angle_to_position(position) / 10) * 0.5
        required_velocity = abs((self.get_position - mapped_position) / time_frame)
        while abs(self.axis.pos_estimate - mapped_position) >= 0.01:
            self.axis.controller.config.vel_limit = required_velocity
            self.axis.controller.input_pos = mapped_position
    
    def stop(self):
        self.axis.controller.input_vel = 0
        self.axis.requested_state = AxisState.IDLE

    def get_position(self):
        return self.axis.encoder.pos_estimate
    
    def get_voltage(self):
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")

    def getLimits(self):
        self.axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 200
        self.axis.config.enable_watchdog = True
        self.axis.controller.input_vel = -0.05
    
        # Initialize leftLimit and rightLimit
        leftLimit = None
        rightLimit = None
    
        # Monitor current and save position when current spikes
        previous_current = self.axis.motor.current_control.Iq_measured
        while leftLimit is None:
            current = self.axis.motor.current_control.Iq_measured
            if abs(current - previous_current) > self.axis.motor.config.current_lim -0.2:
                leftLimit = self.axis.encoder.pos_estimate
            previous_current = current
    
        # Switch velocity direction
        self.axis.controller.input_vel = 0.05
    
        # Monitor current and save position when current spikes
        previous_current = self.axis.motor.current_control.Iq_measured
        while rightLimit is None:
            current = self.axis.motor.current_control.Iq_measured
            if abs(current - previous_current) > self.axis.motor.config.current_lim - 0.2:
                rightLimit = self.axis.encoder.pos_estimate
            previous_current = current
    
        self.rightLimit = rightLimit
        self.leftLimit = leftLimit

        self.midPoint = (self.rightLimit - self.leftLimit) / 2
        
    def map_angle_to_position(self, angle):
        return ((angle - (-10)) / (10 - (-10))) * (self.limitRight - self.limitLeft) + self.limitLeft