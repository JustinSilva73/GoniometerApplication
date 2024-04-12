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
from MotorDriver.MotorSetup import Motor

logger = logging.getLogger(os.getenv("logFile"))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
comPort = os.getenv("comPort")
baudRate = os.getenv("baudRate")


class RunManager:
    ser = None  
    current_angle = 90  
    #pitch = Motor(os.getenv("pitchSerial"))
    
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
    

    def send_file_data_to_arduino(self, runFile):
        if not RunManager.ser or not RunManager.ser.isOpen():
            print("Serial connection not open. Attempting to open...")
            self.open_serial_connection()
            if not RunManager.ser or not RunManager.ser.isOpen():
                print("Failed to open serial connection.")
                return
        try:
            RunManager.ser.write(runFile.encode())
            for index, row in self.flight_data.iterrows():
                angle = row['Angle']
                time = row['Time']
                command = f"{angle},{time}\n"
                RunManager.ser.write(command.encode())
                print(f"Sent command: {command}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")

    def runFileData(self, runFile):
        lastTime = 0
        # Since runFile is now a DataFrame, this should work without error
        for index, row in runFile.iterrows():
            angle = row['angle']  # Use 'angle' as defined in the names parameter of read_csv
            time = row['time']    # Use 'time' as defined in the names parameter of read_csv
            #pitchMotor.set_position(angle, time - lastTime)
            lastTime = time
            print(f"Sent angle: {angle}, Sent time: {time}")

    def create_run_type(self, run_type_str, file_paths=None, steps=None):
        if run_type_str == 'Axis Control':
            from AxisControlRun import AxisControlRun
            return AxisControlRun()
        elif run_type_str == 'Steps':
            from StepsRun import StepsRun
            if file_paths and len(file_paths) > 0:
                return StepsRun(steps, file_paths[0])
            else:
                raise ValueError("file_paths must be a non-empty list for 'Steps' run type.")
        elif run_type_str == 'Files':
            from FilesRun import FilesRun
            return FilesRun(file_paths)  # Pass file paths to FilesRun
        return None

    def start_run_type(self, run_type_str, log_display, run_options_dialog, selected_files=None, steps=None):
        if run_type_str == 'Files':
            if selected_files:
                log_display.appendPlainText(f"Selected file paths: {selected_files}")
            if not selected_files:
                log_display.appendPlainText("Error: No files selected. Please select at least one file.")
                return  # Early return to prevent further processing
        elif run_type_str == 'Steps':
            if selected_files:
                log_display.appendPlainText(f"Selected file paths: {selected_files}")
            if not selected_files:
                log_display.appendPlainText("Error: No files selected. Please select at least one file.")
                return  # Early return to prevent further processing
        elif run_type_str == 'Axis Control':
            pass  # Initialize Axis Control run if necessary
        log_display.appendPlainText(f"Starting {run_type_str} mode")
        #self.pitch.startMotor()
        print("Motor Start")
        run_type_instance = self.create_run_type(run_type_str, selected_files, steps)
        self.set_run_type(run_type_instance)
    

run_manager = RunManager()
