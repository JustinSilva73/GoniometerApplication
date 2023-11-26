import pandas as pd
import time
from ModeRun import RunManager
from PyQt5 import QtCore

class FilesRun(RunManager):
    run_type_id = 'Files'

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self.current_file_index = 0
        self.load_next_file()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.execute_command)
        self.start_time = None

    def load_next_file(self):
        if self.current_file_index < len(self.file_paths):
            file_path = self.file_paths[self.current_file_index]
            self.flight_data = pd.read_csv(file_path)
            self.current_index = 0
            self.current_file_index += 1
        else:
            self.timer.stop()  # Stop the timer if we've finished all files
            self.close_serial_connection()

    def execute_command(self):
        if self.current_index < len(self.flight_data):
            row = self.flight_data.iloc[self.current_index]
            if self.start_time is None:
                self.start_time = time.time()

            current_time = time.time() - self.start_time
            time_to_wait = row['Seconds']

            if current_time >= time_to_wait:
                angle_to_send = row['Angle']
                self.current_angle = angle_to_send
                self.send_angle_to_arduino()
                self.current_index += 1
        else:
            self.load_next_file()