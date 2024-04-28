#Purpose is for general running of the modes and the class that is taken for the run thread to manage things like pause and if running
#Really meant for connection and checking between front end and motor driving with the run types or main functions 

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
from UserTextUpdate import angle_text, log_signal
import csv

logger = logging.getLogger(os.getenv("logFile"))
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
comPort = os.getenv("comPort")
baudRate = os.getenv("baudRate")
current_angle = 0

class RunManager:
    
    def __init__(self):
        self.runCheck = True
        self.pause = False
        print("Run Manager Initialized")
        self.pitch = Motor(os.getenv("self.pitchSerial"))
    
    #These were used for the old way of running the motor and are not used anymore with the thread use but might be useful for Axis Control
    def set_run_type(self, run_type):
        self.run_type_id = run_type

    def get_run_type(self):
        return self.run_type_id
    
    #These were an old method of loading flight data here but it is now done in the run types
    def load_flight_data(self, file_path):
        self.flight_data = pd.read_csv(file_path)
        print("Flight data loaded successfully.")

    #Stops the motor 
    def stop_run(self):
        self.pitch.stop()
    
    #All file running is done here with the run types depending on the array passed in with indef vals to check if should be doing finishing structure
    def runFileData(self, runFile, indefVal=False):
        lastTime = 0
        watchDogVal = runFile['time'].iloc[-1] + 100
        print(f"Watchdog value: {watchDogVal}")
        self.pitch.setWatchDog(watchDogVal)
        self.runCheck = True
        self.pause = False
        self.pitch.startMotor()
        self.pitch.moveToOffset()
        self.pitch.startMotorVelocity()

        time.sleep(1)
    
        # Open the CSV file in write mode. Great for testing and debugging but not needed for final and could contribute to computational time 
        with open('output6.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["Time Difference", "Time Elapsed", "Angle", "Final Angle"])
            for index, row in enumerate(runFile.itertuples(index=False), 1):  # Use enumerate to get the index
                while self.pause:
                    QtWidgets.QApplication.processEvents()
                    # Adjust watchdog to account for paused time
                if not self.runCheck:
                    print("RunCheck is false")
                    break
                print("RunCheck is true")
                
                angle = getattr(row, 'angle')  # Access by attribute name
                currentTime = getattr(row, 'time')
                print(f"Current Time: {currentTime}")   
                #Returns for writing to csv unneeded for final but useful for debugging and seeing accuracy
                timeElapsed, finalAngle = self.pitch.set_position_velocity(angle, currentTime - lastTime)            
                #self.pitch.set_position(angle, currentTime - lastTime)
                print(f"Sent angle: {angle}, Sent time: {currentTime - lastTime}")
    
                writer.writerow([currentTime - lastTime, timeElapsed, angle, finalAngle])
                lastTime = currentTime

        if not indefVal:
            self.runCheck = False
        
        #Doing finishing motor run methods
        if not self.runCheck:
            time.sleep(1)
            self.pitch.clearErros()
            self.pitch.stop()
            self.pitch.startMotor()
            time.sleep(3)
            self.pitch.setMiddlePoint()
            time.sleep(1)
            self.pitch.stop()

    #Calibrates the motors
    def calibrateMotors(self):
        log_signal.append_log.emit("Calibrating Motors")
        self.pitch.checkConnection()
        self.pitch.startMotor()
        self.pitch.fakeCalibrate()
        self.pitch.stop()
    
    #Homes the motors
    def homeMotors(self):
        self.pitch.checkConnection()
        self.pitch.startMotor()
        self.pitch.setMiddlePoint()
        self.pitch.stop()

    #Axis Control is movement since it is the only self input mode
    def axis_control(self, angle_change):
        self.pitch.set_move_angle(angle_change)
        self.pitch.setWatchDog(20)

    #Really just for regrabbing motor if disconnected
    def isCalibrated(self):
        return self.pitch.checkCalibration()
    
    # Creates the run type based on the string passed in to determine what type of run it is and then returns the instance of the run type
    def create_run_type(self, run_type_str, file_paths=None, steps=0):
        if run_type_str == 'Axis Control':

            from AxisControlRun import AxisControlRun
            self.run_type_id = AxisControlRun.run_type_id  # Set the string 'Axis Control'
            return AxisControlRun(run_manager)
        elif run_type_str == 'Steps':
            from StepsRun import StepsRun
            if file_paths and len(file_paths) > 0:
                print(f"fILE PATHS: {file_paths[0]}")
                return StepsRun(run_manager, steps, file_paths[0])
            else:
                raise ValueError("file_paths must be a non-empty list for 'Steps' run type.")
        elif run_type_str == 'Files':
            from FilesRun import FilesRun
            return FilesRun(run_manager,file_paths)
        elif run_type_str == 'Indefinite':
            from FilesRun import FilesRun
            return FilesRun(run_manager,file_paths, True)  # Pass file paths to FilesRun
        return None
    
    #Starts the run type based on the string passed in and then sets the run type to the instance of the run type
    def start_run_type(self, run_type_str, log_display, run_options_dialog, selected_files=None, steps=0, offset=0):
        self.pitch.setOffset(offset)
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
        elif run_type_str == 'Indefinite':
            if selected_files:
                log_display.appendPlainText(f"Selected file paths: {selected_files}")
            if not selected_files:
                log_display.appendPlainText("Error: No files selected. Please select at least one file.")
                return  # Early return to prevent 
        elif run_type_str == 'Axis Control':
            self.pitch.startMotor()
            pass  # Initialize Axis Control run if necessary
        log_display.appendPlainText(f"Starting {run_type_str} mode")
        print("Motor Start")
        run_type_instance = self.create_run_type(run_type_str, selected_files, steps)
        self.set_run_type(run_type_instance)
    

run_manager = RunManager()
