from ModeRun import RunManager
class AxisControlRun(RunManager):
    run_type_id = 'Axis Control Run'

    def adjust_angle(self, angle_change):
        new_angle = RunManager.current_angle + angle_change
        new_angle = max(0, min(180, new_angle))
        RunManager.current_angle = new_angle
        self.send_angle_to_arduino()