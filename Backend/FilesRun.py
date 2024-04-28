#Purpose is set up File run and indefinite run to read all the needed files and send it to the run manager

import pandas as pd
import time
from PyQt5 import QtCore
import logging


# Create a logger and set the log level ouput 
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


class FilesRun:
    run_type_id = 'Files'

    # Initialize the FilesRun object a lot are unused varuables that were for original serial connection but might help better timing later
    def __init__(self, run_manager=None, file_paths=None, indefinite=False):
        super().__init__()
        self.run_manager = run_manager  # Use the passed RunManager instance
        self.file_paths = file_paths
        self.current_file_index = 0
        self.current_file = None
        self.timer = QtCore.QTimer()
        self.start_time = None
        self.next_time = None
        self.next_angle = None
        if indefinite == False:
            self.run_files()
        else:
            self.run_indefinite()

    def log_sent_data(self):
        logger.info(f"Sent time: {self.next_time}, Sent angle: {self.next_angle}")

    # Load all files and concatenate them into a single DataFrame to be sent over
    def load_all_files(self):
        # List to hold the DataFrames from each file
        data_frames = []
        # Variable to keep track of the end time of the last file
        last_time = 0
        
        print("Starting Read")
        while self.current_file_index < len(self.file_paths):
            # Load the data in chunks from the current file
            data_iter = pd.read_csv(self.file_paths[self.current_file_index],
                                    header=None,
                                    names=['time', 'angle'],
                                    iterator=True,
                                    chunksize=1)

            print("Reading file")
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
    
    # Regular file mode sending of data
    def run_files(self):
        runData = self.load_all_files()
        self.run_manager.runFileData(runData)
        self.log_sent_data()

    # Indefinite file mode sending of data loop
    def run_indefinite(self):
        runData = self.load_all_files()
        
        while self.run_manager.runCheck:
            print("Running indefinitely...")
            self.run_manager.runFileData(runData, True)
            self.log_sent_data()

    