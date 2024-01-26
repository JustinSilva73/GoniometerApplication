import pandas as pd
import time
from ModeRun import RunManager
from PyQt5 import QtCore
import logging
import os
import serial
# Create a logger
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

class FilesRun(RunManager):
    run_type_id = 'Files'

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self.current_file_index = 0
        self.current_file = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.execute_command)
        self.start_time = None
        self.next_time = None
        self.next_angle = None
        self.load_next_file()

    def log_sent_data(self):
        logger.info(f"Sent time: {self.next_time}, Sent angle: {self.next_angle}")

    def schedule_next_command(self):
        try:
            row = next(self.current_file).iloc[0]
            print("Row data:", row)  # Debugging line
            self.next_time = row['time']
            self.next_angle = row['angle']
            self.timer.start(max(0, int((self.next_time - (time.time() - self.start_time)) * 1000)))
        except StopIteration:
            self.load_next_file()

    def execute_command(self):
    # Execute the command
        actual_time = time.time() - self.start_time  # Calculate actual time elapsed since start
        actual_time_seconds = int(actual_time)
        actual_time_milliseconds = int((actual_time - actual_time_seconds) * 1000)
        log_message = f"Executing at {self.next_time}s (scheduled), {actual_time_seconds}s {actual_time_milliseconds}ms (actual): Set angle to {self.next_angle} degrees"
        print(log_message)
        logger.info(log_message)  # Print to log file
        RunManager.current_angle = self.next_angle
        self.send_angle_to_arduino()
        self.schedule_next_command()
    
    def load_next_file(self):
        if self.current_file_index < len(self.file_paths):
            # Reading CSV without headers
            self.current_file = pd.read_csv(self.file_paths[self.current_file_index], 
                                            header=None, 
                                            names=['time', 'angle'],
                                            iterator=True, 
                                            chunksize=1)
            self.start_time = time.time()
            self.schedule_next_command()
            self.current_file_index += 1
        else:
            self.timer.stop()  # Stop the timer if all files are processed

    def load_all_files(self):
        while self.current_file_index < len(self.file_paths):
            self.current_file = pd.concat([self.current_file, pd.read_csv(self.file_paths[self.current_file_index], 
                                            header=None, 
                                            names=['time', 'angle'],
                                            iterator=True, 
                                            chunksize=1)])
            self.current_file_index += 1
        
        self.current_file['end'] = True  # Add 'end' column with value True to indicate end of information
        logger.info(f"Current file:{self.current_file}")
        self.send_file_data_to_arduino()
        self.log_sent_data()
    
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

    