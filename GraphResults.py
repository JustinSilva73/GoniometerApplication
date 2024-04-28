# Purpose: This makes 3 separate graphs for expected input and actual output
# First is Position vs Time
# Second is Velocity vs Time
# Third is Acceleration vs Time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # For using pi

# Read the .csv file
df = pd.read_csv('output5.csv', header=None, names=['Time Difference', 'Time Elapsed', 'Angle', 'Final Angle'])

# Ensure columns are numeric
df['Time Difference'] = pd.to_numeric(df['Time Difference'], errors='coerce')
df['Time Elapsed'] = pd.to_numeric(df['Time Elapsed'], errors='coerce')
df['Angle'] = pd.to_numeric(df['Angle'], errors='coerce')
df['Final Angle'] = pd.to_numeric(df['Final Angle'], errors='coerce')

# Drop any rows with NaN (if conversion fails)
df.dropna(inplace=True)

# Calculate cumulative time if it's not already cumulative
df['Time Difference'] = df['Time Difference'].cumsum()
df['Time Elapsed'] = df['Time Elapsed'].cumsum()

# Calculate velocity and acceleration with angle in radians
df['Velocity'] = (df['Angle'] * (2*np.pi / 180)) / df['Time Difference'].diff()
df['Acceleration'] = df['Velocity'] / df['Time Difference'].diff()

df['Final Velocity'] = (df['Final Angle'] * (2*np.pi / 180)) / df['Time Elapsed'].diff()
df['Final Acceleration'] = df['Final Velocity'] / df['Time Elapsed'].diff()

plt.figure(figsize=(10, 6))
plt.plot(df['Time Difference'], df['Angle'], label='Time Difference vs Angle')
plt.plot(df['Time Elapsed'], df['Final Angle'], label='Time Elapsed vs Final Angle', color='red')
plt.ylabel('Angle (Degrees)')
plt.xlabel('Cumulative Time')
plt.legend()
plt.savefig('angle_plot.png')
plt.show()

# Plot velocities
plt.figure(figsize=(10, 6))
plt.plot(df['Time Difference'], df['Velocity'], label='Velocity over Time', color='green')
plt.plot(df['Time Elapsed'], df['Final Velocity'], label='Final Velocity over Time', color='blue')
plt.ylabel('Velocity (radians/sec)')
plt.xlabel('Cumulative Time')
plt.legend()
plt.savefig('velocity_plot.png')
plt.show()

# Plot accelerations
plt.figure(figsize=(10, 6))
plt.plot(df['Time Difference'], df['Acceleration'], label='Acceleration over Time', color='purple')
plt.plot(df['Time Elapsed'], df['Final Acceleration'], label='Final Acceleration over Time', color='orange')
plt.xlabel('Cumulative Time')
plt.ylabel('Acceleration (radians/sec²)')
plt.legend()
plt.savefig('acceleration_plot.png')
plt.show()