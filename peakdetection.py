import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# csv constants
# 300 entries per second
csv_interval = 300 # Samples per second

# Initialize plot
fig, ax = plt.subplots()
line, = ax.plot([], [], label='Data')
ax.set_xlabel('Time')
ax.set_ylabel('Value')
ax.legend()

def process_csv_data(data):
    # Process the CSV data (example: extract time and value)
    # Does so by emulating real time, I was unaware of the timing convention, but can also do this dynamically
    # if needed --> preprocess data to find out times, then update variables    value = float(data[0])
    value = float(data[0])

    if xdata:
        time_stamp = xdata[-1] + 1.0 / csv_interval
    else:
        time_stamp = 0  # Initial timestamp if xdata is empty
    return time_stamp, value

def update_plot(frame):
    try:
        row = next(csv_reader)     # Read next row from CSV file
    except StopIteration:
        ani.event_source.stop()
        return

    time_stamp, value = process_csv_data(row)
    
    # Update plot
    xdata.append(time_stamp)
    ydata.append(value)
    line.set_data(xdata, ydata)
    
    # Adjust plot limits
    ax.relim()
    ax.autoscale_view()

def emulate_real_time(csv_file):
    global csv_reader
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file) # Read CSV file
        ani = FuncAnimation(fig, update_plot, interval=1)  # Update plot every millisecond
        plt.show()

if __name__ == "__main__":
    csv_file = "vs_8x5_003_Tx20_ECG.csv"  # CSV file from Fidel
    xdata, ydata = [], []
    emulate_real_time(csv_file)
