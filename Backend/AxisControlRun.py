#Purpose: Axis Control mode to just pass the angle change to the motor
# CURRENTLY NOT SET UP RIGHT WITH RUN THREAD SO DOES NOT WORK FULLY

from ModeRun import RunManager
class AxisControlRun():
    run_type_id = 'Axis Control'

    def __init__(self, run_manager):
        self.run_manager = run_manager

    def adjust_angle(self, angle_change):
        self.run_manager.axis_control(angle_change)