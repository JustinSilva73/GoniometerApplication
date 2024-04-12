from ModeRun import RunManager
from PyQt5 import QtCore
import logging
import pandas as pd

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

class StepsRun(RunManager):
    run_type_id = 'Steps'
    
    def __init__(self, steps, file_path):
        super().__init__()
        self.steps = steps
        self.file_path = file_path
        self.current_step = 0
        self.current_angle = 0
        self.timer = QtCore.QTimer()
        self.start_time = None
        self.next_time = None
        self.next_angle = None
        self.load_file(steps)

    def log_sent_data(self):
        logger.info(f"Sent time: {self.next_time}, Sent angle: {self.next_angle}")

    def load_file(self, num_steps):
    # Use pd.concat to concatenate the chunks into a single DataFrame
        data_iter = pd.read_csv(self.file_path, 
                                header=None, 
                                names=['time', 'angle'],
                                iterator=True, 
                                chunksize=1)
        all_data = pd.concat([chunk for _, chunk in zip(range(num_steps), data_iter)])

        logger.info(f"File data: {all_data}")
        self.runFileData(all_data)  # Now all_data is a DataFrame
        self.log_sent_data()

