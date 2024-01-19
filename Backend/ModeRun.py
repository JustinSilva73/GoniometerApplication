from PyQt5 import QtWidgets
import serial
import time
import serial.tools.list_ports
import pandas as pd
from Connection import StartingRunChecks
from dotenv import load_dotenv
import os
import logging
import sys

logger = logging.getLogger(os.getenv("logFile"))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
comPort = os.getenv("comPort")
baudRate = os.getenv("baudRate")
class RunManager:
    ser = None  
    current_angle = 90  

    
    def set_run_type(self, run_type):
        self.run_type_id = run_type

    def get_run_type(self):
        # Returns the current run type instance
        return self.run_type_idW
    
    def load_flight_data(self, file_path):
        self.flight_data = pd.read_csv(file_path)
        print("Flight data loaded successfully.")

    
    def open_serial_connection(self):
        if not RunManager.ser or not RunManager.ser.isOpen():
            try:
                RunManager.ser = serial.Serial(comPort, baudRate, timeout=1)
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

    def send_file_data_to_arduino(self):
        if not RunManager.ser or not RunManager.ser.isOpen():
            print("Serial connection not open. Attempting to open...")
            self.open_serial_connection()
            if not RunManager.ser or not RunManager.ser.isOpen():
                print("Failed to open serial connection.")
                return
        try:
            for index, row in self.flight_data.iterrows():
                command = f"{row['Angle']}\n"
                RunManager.ser.write(command.encode())
                print(f"Sent command: {command}")
                time.sleep(row['Time'])
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")

    def create_run_type(self, run_type_str, file_paths=None):
        if run_type_str == 'Axis Control':
            from AxisControlRun import AxisControlRun
            return AxisControlRun()
        elif run_type_str == 'Steps':
            from StepsRun import StepsRun
            return StepsRun()
        elif run_type_str == 'Files':
            from FilesRun import FilesRun
            return FilesRun(file_paths)  # Pass file paths to FilesRun
        return None

    def start_run_type(self, run_type_str, log_display, run_options_dialog, selected_files=None):
        if run_type_str == 'Files':
            if selected_files:
                log_display.appendPlainText(f"Selected file paths: {selected_files}")
            else:
                log_display.appendPlainText("No files selected.")
        elif run_type_str == 'Steps':
            pass  # Initialize Steps run if necessary
        elif run_type_str == 'Axis Control':
            pass  # Initialize Axis Control run if necessary
        log_display.appendPlainText(f"Starting {run_type_str} mode")
        run_checks = StartingRunChecks(log_display, comPort, baudRate)
        if run_checks.check_serial_connection():
            self.open_serial_connection()  # Open serial connection after successful checks
            run_options_dialog.accept()
            run_type_instance = self.create_run_type(run_type_str, selected_files)
            self.set_run_type(run_type_instance)


run_manager = RunManager()
