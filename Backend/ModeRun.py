from PyQt5 import QtWidgets
from Connection import StartingRunChecks
import serial
import time

class RunManager:
    def __init__(self):
        self.current_run_type = None
        self.current_angle = 90  # Initial angle, adjust as necessary

    def set_run_type(self, run_type):
        self.current_run_type = run_type

    def get_run_type(self):
        return self.current_run_type

    def adjust_angle_if_indefinite(self, angle_change):
        new_angle = self.current_angle + angle_change
        # Ensure the new angle is within the valid range (0 to 180)
        new_angle = max(0, min(180, new_angle))
        
        # Move the servo to the new angle
        self.move_servo_to_angle(new_angle)

        # Update the current angle
        self.current_angle = new_angle

    def send_angle_to_arduino(self):
        try:
            with serial.Serial('COM4', 115200, timeout=1) as ser:
                time.sleep(3)
                command = f"{self.current_angle}\n"  # Command with a newline delimiter
                ser.write(command.encode())
                print(f"Sent angle {self.current_angle} to Arduino")
                time.sleep(2)
                while ser.in_waiting:
                    response = ser.readline().decode().strip()
                    print("Received from Arduino:", response)

        except serial.SerialException as e:
            print(f"Serial communication error: {e}")

run_manager = RunManager()

def handle_start_button_click(run_options_dialog):
    run_type = None
    if run_options_dialog.ui.radioButtonSteps.isChecked():
        run_type = 'Steps'
    elif run_options_dialog.ui.radioButtonFiles.isChecked():
        run_type = 'Files'
    elif run_options_dialog.ui.radioButtonIndefinite.isChecked():
        run_type = 'Indefinite'

    if run_type is None:
        QtWidgets.QMessageBox.warning(run_options_dialog, "Warning", "Please select a run type.")
    else:
        run_manager.set_run_type(run_type)
        run_options_dialog.parent().logDisplay.appendPlainText(f"Mode selected: {run_type}")
        run_options_dialog.accept()  # This will close the dialog

    log_display = run_options_dialog.parent().logDisplay
    run_checks = StartingRunChecks(log_display, "COM4", 115200)  # Adjust COM port and baud rate as necessary
    run_checks.check_serial_connection()

    # Close the dialog or other actions
    run_options_dialog.accept()

def get_current_run_type():
    """
    Function to retrieve the current run type.
    """
    return run_manager.get_run_type()
