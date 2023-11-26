from PyQt5 import QtWidgets
import serial
import time
import serial.tools.list_ports
import pandas as pd
from Connection import StartingRunChecks

def get_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print("imported_files.txt not found.")
            return []

class RunManager:
    ser = None  # class-level attribute for the serial connection
    current_angle = 90  # class-level attribute for the angle

    
    def set_run_type(self, run_type):
        self.run_type_id = run_type

    def get_run_type(self):
        # Returns the current run type instance
        return self.run_type_id
    
    def load_flight_data(self, file_path):
        self.flight_data = pd.read_csv(file_path)
        print("Flight data loaded successfully.")

    
    def open_serial_connection(self):
        if not RunManager.ser or not RunManager.ser.isOpen():
            try:
                RunManager.ser = serial.Serial('COM4', 115200, timeout=1)
                print("Serial connection opened.")
            except serial.SerialException as e:
                print(f"Error opening serial connection: {e}")

    def close_serial_connection(self):
        if RunManager.ser and RunManager.ser.isOpen():
            RunManager.ser.close()
            print("Serial connection closed.")

    def send_angle_to_arduino(self):
        if not RunManager.ser or not RunManager.ser.isOpen():
            print("Serial connection not open. Attempting to open...")
            self.open_serial_connection()
            if not RunManager.ser or not RunManager.ser.isOpen():
                print("Failed to open serial connection.")
                return

        try:
            command = f"{RunManager.current_angle}\n"
            RunManager.ser.write(command.encode())
            print(f"Sent command: {command}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")


    def create_run_type(self, run_type_str):
            if run_type_str == 'Indefinite':
                from IndefiniteRun import IndefiniteRun
                return IndefiniteRun()
            elif run_type_str == 'Steps':
                from StepsRun import StepsRun
                return StepsRun()
            elif run_type_str == 'Files':
                from FilesRun import FilesRun
                return FilesRun()
            return None
    
    def start_run_type(self, run_type_str, log_display, run_options_dialog):
    # method implementation
        file_paths = self.get_file_paths()
        run_type_instance = self.create_run_type(run_type_str)
        
        if run_type_instance:
            if run_type_str == 'Files':
                run_type_instance.initialize_with_files(file_paths)
                log_display.appendPlainText(f"Loaded file paths from imported_files.txt")
            elif run_type_str == 'Steps':
                pass  # Initialize Steps run if necessary
            elif run_type_str == 'Indefinite':
                pass  # Initialize Indefinite run if necessary

            log_display.appendPlainText(f"Starting {run_type_str} mode")
            self.set_run_type(run_type_instance)

            run_checks = StartingRunChecks(log_display, "COM4", 115200)
            if run_checks.check_serial_connection():
                self.open_serial_connection()  # Open serial connection after successful checks
            run_options_dialog.accept()
    
        else:
            log_display.appendPlainText(f"Run type {run_type_str} not recognized.")

run_manager = RunManager()
