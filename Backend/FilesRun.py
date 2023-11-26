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
        self.current_file = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.execute_command)
        self.start_time = None
        self.next_time = None
        self.next_angle = None
        self.load_next_file()

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
        print(f"Executing at {self.next_time} (scheduled), {actual_time:.2f} (actual): Set angle to {self.next_angle}")
        RunManager.current_angle = self.next_angle
        self.send_angle_to_arduino()
        self.schedule_next_command()

