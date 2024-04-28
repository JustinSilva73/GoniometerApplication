import odrive
import time
from odrive.enums import *
from odrive.utils import dump_errors
from UserTextUpdate import log_signal, angle_text
from PyQt5.QtWidgets import QApplication  # Import QApplication
import ModeRun as run_manager

# PID controller variables
I_error = 0
past_error = 0
error = 0
kp = 0.53
ki = 0.025
kd = 0.0001


class Motor:
    def __init__(self, serial_number):
        self.odrive = odrive.find_any()
        self.axis = self.odrive.axis0
        self.leftLimit =None
        self.rightLimit = None
        self.midPoint = None
        print("NEW INSTANCE OF MOTOR CREATED")
        self.offset = 0

    # This start motor is specifically for position control for offset and such
    def startMotor(self):
        self.axis.controller.config.input_mode = InputMode.PASSTHROUGH
        self.axis.controller.config.control_mode = ControlMode.POSITION_CONTROL
        self.axis.config.enable_watchdog = True
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.controller.config.vel_limit = 10
        time.sleep(0.5)
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")
        print(dump_errors(self.odrive))
        self.odrive.clear_errors()
    
    # This start motor is specifically for velocity control so main file replication movement
    def startMotorVelocity(self):
        self.axis.controller.config.input_mode = InputMode.PASSTHROUGH
        self.axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        self.axis.config.enable_watchdog = True
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.controller.config.vel_limit = 10
        time.sleep(0.5)
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")
        print(dump_errors(self.odrive))
        self.odrive.clear_errors()

    # This is the main driver of file mode replication to the send the position and determin the velocity from it to send to the motor
    def set_position_velocity(self, position, time_frame):
        time_frame = time_frame
        mapped_position = self.map_angle_to_position(position)
        initial_position = self.axis.pos_estimate
        initial_angle = self.map_position_to_angle(initial_position)
        print(f"Initial position: {initial_position}")
        print(f"Setting position to {mapped_position}")

        if time_frame == 0:
            print("Error: Time frame cannot be zero.")
            return
        
        # Motor calculations for velocity
        velocity = ((position - initial_angle) / time_frame) * 0.0458
        if velocity > 5.92:
            velocity = 5.92

        startTime = time.time()
        while time.time() - startTime < time_frame:
            self.axis.controller.input_vel = velocity + self.errorFind(velocity) # Uses bottom PID controller to adjust velocity
            
            #TODO: This is where the problem arises with the timing since we are always making it sleep by the time interval
            #This makes it so the PID error only gets calculated once since after the sleep the while condition is false
            #This is why the motor is not moving in the correct time frame
            #But removing it will make the motor much louder and adds computational time to sending the command to the motor the more the motor is called
            #I do think the sleep HAS to be here and it cant be 0 but 0.1 is too long and everytime this changes there is a change in PID
            #You could get rid of this and do no while but again the PID will only ever be calculated once and for higher accuracy it might be needed for it to run more
            #Fixing time will deal with adjusting the PID and everything in this while loop or looking into odrive interpolation 
            time.sleep(0.1)
            
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))
            QApplication.processEvents() 
            self.axis.controller.input_vel = 0
        endTime = time.time()
        print("Final position reached.")

        return endTime-startTime, self.map_position_to_angle(self.get_position())
        
    # This was the main driver through position control but it was struggling to vary the velocity but again interpolation can help
    """
    def set_position(self, position, time_frame):
        mapped_position = self.map_angle_to_position(position)
        initial_position = self.axis.pos_estimate
        print(f"Initial position: {initial_position}")
        print(f"Setting position to {mapped_position}")
    
        if time_frame == 0:
            print("Error: Time frame cannot be zero.")
            return
    
        distance = mapped_position - initial_position

        velocity = distance / time_frame
        velocity = velocity / 16.5
        if velocity > 5.25:
            velocity = 5.25
        
        startTime = time.time()
        self.axis.controller.input_pos = mapped_position
        #self.axis.controller.input_vel = velocity
        while abs(self.axis.pos_estimate - mapped_position) > 0.01:
            print(f"Current estimate: {self.axis.pos_estimate}")
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))
            QApplication.processEvents()
            print(f"Current velocity is {self.axis.vel_estimate}")
            print(f"Calculated velocity is {velocity}")
            self.axis.controller.input_pos = mapped_position
    
        endTime = time.time()
        print("Final position reached.")
        return endTime-startTime, self.map_position_to_angle(self.get_position())
    
        """
    
    # Stops the motor
    def stop(self):
        self.axis.requested_state = AxisState.IDLE

    # Gets the position of the motor
    def get_position(self):
        return self.axis.pos_estimate
    
    # Gets the voltage of the motor
    def get_voltage(self):
        print("Bus voltage is " + str(self.odrive.vbus_voltage) + "V")

    # Gets the limits of the motor by setting a current limit and determining the left and right limits with the spike over the limit
    def getLimits(self):
        self.axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 30
        self.axis.config.enable_watchdog = True
    
        previous_current = self.axis.motor.foc.Iq_measured
        current_limit = 0.8  # Use a value slightly below the current limit
        # Find left limit
        print("Finding left limit")
        self.axis.controller.input_vel = -0.3
        while True:
            time.sleep(0.1)  # Short delay
            current = self.axis.motor.foc.Iq_measured
            if abs(current) > current_limit:  # Detect spikes from current limit
                self.leftLimit = self.axis.pos_estimate
                QApplication.processEvents() 
                break
            print(f"Previous current: {previous_current}, Current: {current}")
            previous_current = current
    
        self.axis.controller.input_vel = 0
    
        # Find right limit
        print("Finding right limit")
        self.axis.controller.input_vel = 0.3
        time.sleep(3)
        while True:
            time.sleep(0.1)  # Short delay
            current = self.axis.motor.foc.Iq_measured
            if abs(current) > current_limit:  # Detect spikes from current limit
                self.rightLimit = self.axis.pos_estimate
                QApplication.processEvents() 
                break
            previous_current = current
    
        self.axis.controller.input_vel = 0
        print("Stopped")
    
        print (f"Left limit: {self.leftLimit}, Right limit: {self.rightLimit}")
        self.midPoint = (self.rightLimit + self.leftLimit) / 2
        print(f"Mid point: {self.midPoint}")
        self.axis.controller.config.control_mode = ControlMode.POSITION_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 15
        self.axis.config.enable_watchdog = True

    # Sets motor to 0 position
    def setMiddlePoint(self):
        self.axis.controller.input_pos = self.midPoint
        print("Setting middle point")
        while abs(self.axis.pos_estimate - self.midPoint) >= 0.0001:
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))  # Call the function with the correct name
            QApplication.processEvents()
            
    # Calibrates the motor but does not do odrive calibration since IT NEEDS TO BE MOVED TO DO SO CANT DO FROM MIDDLE
    #TODO: Odrive calibration look at the side without the motor and line the top stage right side flush with the bottom stage right side then run odrive calibration
    def calibrateMotor(self):
        self.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 30
        #self.axis.requested_state = AxisState.FULL_CALIBRATION_SEQUENCE
        #time.sleep(12)
        #self.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.setHardLimits()

        print(dump_errors(self.odrive))

    # Fake calibration incase could not do the real calibration but it works
    def fakeCalibrate(self):
        self.getLimits()
        self.setMiddlePoint()
        
    # Maps the angle to the position of the motor
    #TODO: This is the main function that needs to be changed for different limits passed in since -10 to 10 is not always the case for range and be fixed for offset scenarios
    def map_angle_to_position(self, angle):
        return ((angle - (-10)) / (10 - (-10))) * (self.rightLimit - self.leftLimit) + self.leftLimit
    
    # Maps the position to the angle of the motor
    #TODO: This is the main function that needs to be changed for different limits passed in since -10 to 10 is not always the case for range and be fixed for offset scenarios
    def map_position_to_angle(self, position):
        if self.leftLimit is None or self.rightLimit is None:
            print("Error: Limits not set.")
            return 0  # Return a default value or handle this error appropriately
        return ((position - self.leftLimit) / (self.rightLimit - self.leftLimit)) * (10 - (-10)) + (-10)

    # Sets the watchdog for the motor every time or else if timer runs out then motor turns off
    def setWatchDog(self, timeout):
        self.axis.config.watchdog_timeout = timeout
        self.axis.config.enable_watchdog = True

    # Sets the position for axis control mode
    def set_move_angle(self, angle_change):
        mapped_position = self.map_angle_to_position((self.map_position_to_angle(self.get_position()) + angle_change))
        self.axis.controller.input_pos = mapped_position
        
        while abs(self.axis.pos_estimate - mapped_position) > 0.01:
            print(f"Current estimate: {self.axis.pos_estimate}")
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))  # Call the function with the correct name
            QApplication.processEvents()

    # Temp way to set the limits before get limits
    def setHardLimits(self):
        self.leftLimit = -0.5
        self.rightLimit = 0.3
        self.midPoint = (self.rightLimit + self.leftLimit) / 2
        print(f"Left limit: {self.leftLimit}, Right limit: {self.rightLimit}, Mid point: {self.midPoint}")
        time.sleep(2)

    # Sets the offset for the motor
    #TODO: This is the main function currently just sets the first position to offset but does not change the position of the motor based off offset
    def setOffset(self, offset):
        if (offset < 10 and offset > -10):
            self.offset = self.map_angle_to_position(offset)

    # Moves the motor to the offset
    def moveToOffset(self):
        self.axis.controller.input_pos = self.offset
        print("Setting offset")
        while abs(self.axis.pos_estimate - self.offset) >= 0.01:
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))

    # PID controller for velocity control
    def errorFind(self, angle):
        global error, I_error, past_error, kp, ki, kd  # Use global declaration to modify these variables
        past_error = error
        error = angle
        I_error = I_error + error
        D_error = error - past_error
        return kp*past_error + ki*I_error + kd*D_error
    
    # Checks if the motor is connected if estopped
    def checkConnection(self):
        if self.odrive is None:
            print("Error: No ODrive connected.")
            return False
        return True

    # Clears the errors of the motor
    def clearErros(self):
        print(dump_errors(self.odrive))

    # Checks if the motor is calibrated and if not cant run
    def checkCalibration(self):
        if self.leftLimit is None or self.rightLimit is None:
            print("Error: Limits not set.")
            return False
        return True

    # This was a position control method for main file movement trying to vary velocity that didnt work but could help later potentially by splitting into steps
    """
    def set_position(self, position, time_frame):
        mapped_position = self.map_angle_to_position(position)
        initial_position = self.axis.pos_estimate
        print(f"Initial position: {initial_position}")
        print(f"Setting position to {mapped_position}")

        distance = mapped_position - initial_position
        if time_frame == 0:
            print("Error: Time frame cannot be zero.")
            return

        velocity = distance / time_frame  # Calculate needed velocity
        num_steps = int(time_frame / 0.01)  # Number of steps based on a 0.01s time step
        for i in range(num_steps):
            step_position = initial_position + (i + 1) * distance / num_steps
            step_velocity = velocity * (i + 1) / num_steps  # Gradually increase the velocity
            self.axis.controller.input_vel = step_velocity  # Set the velocity
            self.axis.controller.input_pos = step_position  # Set the position
            time.sleep(0.01)  # Wait for the time step

        while abs(self.axis.pos_estimate - mapped_position) > 0.001:
            print(f"Current estimate: {self.axis.pos_estimate}")
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))  # Call the function with the correct name
            QApplication.processEvents()
    """

    # Well we had to make a fake limits grabbing for the motor since the real one was not working originally so that is this but it works now 
    def getFakeLimits(self):
        leftLimit = None
        rightLimit = None
        self.axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 30
        self.axis.config.enable_watchdog = True

        previous_current = self.axis.motor.foc.Iq_measured
        current_limit = 0.8  # Use a value slightly below the current limit

        start_time = time.time()
        print("Finding left limit")
        self.axis.controller.input_vel = -0.1
        while time.time() - start_time < 4:  # Run for 4 seconds
            time.sleep(0.1)  # Short delay

        self.axis.controller.input_vel = 0
        self.axis.controller.input_vel = 0.1

        start_time = time.time()
        print("Finding right limit")
        while time.time() - start_time < 8:  # Run for 8 seconds
            time.sleep(0.1)  # Short delay

        self.axis.controller.input_vel = 0
        print("Stopped")

        """
        start_time = time.time()
        print("Finding left limit")
        while time.time() - start_time < 4:
            time.sleep(0.1)  # Run for 4 seconds
            current = self.axis.motor.foc.Iq_measured
            if abs(current - previous_current) > current_limit:  # Detect spikes from current limit
                self.axis.controller.input_vel = -0.0001  # Slow down the motor
                time.sleep(1)  # Wait for the motor to slow down
            previous_current = current
            time.sleep(0.1)
        self.axis.controller.input_vel = 0
        self.axis.controller.input_vel = 0.05
        previous_current = self.axis.motor.foc.Iq_measured

        
        start_time = time.time()
        print("Finding right limit")
        while time.time() - start_time < 8:
            time.sleep(0.1)  # Run for 8 seconds
            current = self.axis.motor.foc.Iq_measured
            if abs(current - previous_current) > current_limit:  # Detect spikes from current limit
                self.axis.controller.input_vel = -0.0001  # Slow down the motor
                time.sleep(1)  # Wait for the motor to slow down
            previous_current = current
            time.sleep(0.1)  # Short delay # Short delay to allow for current changes
        print("Stopped")
        while abs(self.axis.pos_estimate - self.midPoint) >= 0.0001:
            angle_text.append_angle.emit(str(round(self.map_position_to_angle(self.axis.pos_estimate), 2)))  # Call the function with the correct name
            QApplication.processEvents()
        print (f"Left limit: {self.leftLimit}, Right limit: {self.rightLimit}, Mid point: {self.midPoint}")
        """
        self.axis.controller.config.control_mode = ControlMode.POSITION_CONTROL
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL
        self.axis.config.watchdog_timeout = 15
        self.axis.config.enable_watchdog = True
