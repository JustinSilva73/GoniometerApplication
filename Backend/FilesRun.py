import pandas as pd
import time
from ModeRun import RunManager
from PyQt5 import QtCore
import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and set the log level
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

class FilesRun(RunManager):
    run_type_id = 'Files'

    def __init__(self, file_paths, Indefinite=False):
        super().__init__()
        self.file_paths = file_paths
        self.current_file_index = 0
        self.current_file = None
        self.timer = QtCore.QTimer()
        self.start_time = None
        self.next_time = None
        self.next_angle = None
        if Indefinite == False:
            self.run_files()
        else:
            self.run_indefinite()

    def log_sent_data(self):
        logger.info(f"Sent time: {self.next_time}, Sent angle: {self.next_angle}")

    def load_all_files(self):
        # List to hold the DataFrames from each file
        data_frames = []
        # Variable to keep track of the end time of the last file
        last_time = 0
        
        # Iterate over all file paths and load data
        while self.current_file_index < len(self.file_paths):
            # Load the data in chunks from the current file
            data_iter = pd.read_csv(self.file_paths[self.current_file_index],
                                    header=None,
                                    names=['time', 'angle'],
                                    iterator=True,
                                    chunksize=1)
            
            # Create a DataFrame for the current file
            file_data = pd.concat([chunk for chunk in data_iter])
            
            # Adjust the 'time' column by adding the last time from the previous file
            if last_time != 0:  # Skip this for the first file
                file_data['time'] += last_time
            
            # Update the last_time for the next file
            last_time = file_data['time'].iloc[-1]
            
            # Append the adjusted DataFrame to the list
            data_frames.append(file_data)
            
            # Increment to move to the next file
            self.current_file_index += 1
        
        # Concatenate all DataFrames from each file into a single DataFrame
        all_data = pd.concat(data_frames)
        
        # Log the combined DataFrame
        logger.info(f"All files data: {all_data}")
        
        return all_data
    
    def run_files(self):
        runData = self.load_all_files()
        self.runFileData(runData)
        self.log_sent_data()

    def run_indefinite(self):
        runData = self.load_all_files()
        
        while True:
            self.runFileData(runData)
            self.log_sent_data()

    