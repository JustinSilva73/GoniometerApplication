#Purpose: This file contains the StepsRun class that is responsible for running the steps 
#method is to just save the file up to the steps in an array and only allows one file for steps 
#


import pandas as pd
import logging

# Ensure your logger is set up correctly
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class StepsRun:
    run_type_id = 'Steps'
    
    # Initialize the StepsRun instance with the RunManager instance then start loading the file and run the steps
    def __init__(self, run_manager, steps, file_path):
        self.run_manager = run_manager  # Use the passed RunManager instance
        self.steps = steps
        self.file_path = file_path
        self.load_file(steps)

    def log_sent_data(self):
        logger.info(f"Sent time: {self.next_time}, Sent angle: {self.next_angle}")

    #load the file and grab the two columns of time and angle to an array to the num of steps 
    def load_file(self, num_steps):
        try:
            # Initialize the data iterator with chunksize of 1 to read the file row by row
            data_iter = pd.read_csv(self.file_path, header=None, names=['time', 'angle'], iterator=True, chunksize=1)
            
            # List to collect data chunks
            chunks = [chunk for _, chunk in zip(range(num_steps), data_iter)]
            
            if not chunks:
                logger.error("No data to concatenate. The file might be empty or has fewer rows than specified steps.")
                print("No data to concatenate. The file might be empty or has fewer rows than specified steps.")
                return  # Exit if there's nothing to process
            
            # Concatenate collected chunks into a DataFrame
            runData = pd.concat(chunks)
            
            # Log the loaded data
            logger.info(f"File data loaded and processed: {runData}")
            
            # Process the loaded data using the run manager directly
            self.run_manager.runFileData(runData)
            self.log_sent_data()
            
        except pd.errors.EmptyDataError:
            logger.error(f"No data in file {self.file_path}. Skipping.")
            print(f"No data in file {self.file_path}. Skipping.")
        except Exception as e:
            logger.error(f"Error reading file {self.file_path}: {e}")
            print(f"Error reading file {self.file_path}: {e}")

