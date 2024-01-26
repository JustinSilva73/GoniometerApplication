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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and set the log level
file_handler = logging.FileHandler(os.getenv("logFile"))
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


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

    def stop_run_type(self):
        self.close_serial_connection()
        self.set_run_type(None)
        logger.info("Run stopped")

    

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
                logger.info(f"Selected file paths: {selected_files}")
            else:
                logger.info("No files selected.")
        elif run_type_str == 'Steps':
            pass  # Initialize Steps run if necessary
        elif run_type_str == 'Axis Control':
            pass  # Initialize Axis Control run if necessary
        logger.info(f"Starting {run_type_str} mode")
        run_checks = StartingRunChecks(log_display, comPort, baudRate)
        if run_checks.check_serial_connection():
            self.open_serial_connection()  # Open serial connection after successful checks
            run_options_dialog.accept()
            run_type_instance = self.create_run_type(run_type_str, selected_files)
            self.set_run_type(run_type_instance)
    
    

run_manager = RunManager()
