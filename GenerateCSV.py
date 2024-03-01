import pandas as pd
import numpy as np

# Create a sequence of seconds
seconds = np.arange(1, 101)

# Create a sequence of values
# Replace this with your actual values
values = np.random.uniform(-10, 10, 100)

# Create a DataFrame
df = pd.DataFrame({
    'Seconds': seconds,
    'Values': values
})

# Save the DataFrame to a .csv file without headers
file_path = 'random_data.csv'
df.to_csv(file_path, index=False, header=False)

file_path