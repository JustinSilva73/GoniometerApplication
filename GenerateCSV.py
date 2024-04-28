#Purpose: Generate CSV files for testing the data pipeline
# We were doing sweeps and trying to replicate flight data so the two sections are those two separate codes 

#Replicates a back and forth going to the farthest limit of 5.72 and back to 0 in 0.1 seconds
"""
import pandas as pd
import numpy as np

# Create a sequence of seconds
seconds = np.arange(0.1, 10, 0.1)

# Create a pattern of values
pattern = [5.72, 0, -5.72, 0]

# Repeat the pattern for the desired number of seconds
values = [pattern[i % len(pattern)] for i in range(len(seconds))]

# Create a DataFrame
df = pd.DataFrame({
    'Seconds': seconds,
    'Values': values
})

# Save the DataFrame to a .csv file without headers
file_path = 'pattern_data.csv'
df.to_csv(file_path, index=False, header=False)

file_path
"""

#Replicates flight data with range of 5.72 which is calculation the max range of in 0.1 seconds
"""
import pandas as pd
import numpy as np

# Create a sequence of seconds
seconds = np.arange(0.1, 30, 0.1)

# Initialize the first value
values = [np.random.uniform(-9.5, 9.5)]

# Generate the remaining values
for _ in range(1, len(seconds)):
    # Calculate the range for the next value
    min_val = max(values[-1] - 5.72, -9.5)
    max_val = min(values[-1] + 5.72, 9.5)
    
    # Generate the next value within the calculated range
    next_val = np.random.uniform(min_val, max_val)
    
    # Append the next value to the list
    values.append(next_val)

# Shift all values by 6 in the positive direction
values = [value + 6 for value in values]

# Create a DataFrame
df = pd.DataFrame({
    'Seconds': seconds,
    'Values': values
})

# Save the DataFrame to a .csv file without headers
file_path = 'FlightDataOffset.csv'
df.to_csv(file_path, index=False, header=False)

file_path
"""