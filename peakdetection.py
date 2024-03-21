import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy import signal
import scipy
import numpy as np
import neurokit2 as nk

# ECG Data and Filter Constants
cutoff_frequency = 3.0  # Hz I think we said resting heart beat frequency is 1-2 Hz? Increase to 4 Hz to be safe
sampling_frequency = 300.0  # Hz
nyquist_frequency = sampling_frequency/2.0  # Hz (assuming a sampling frequency of 300 Hz, I got this from the 2.01.2024 Notes)
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
num_taps = 100  # Number of filter taps, I got this from stack overflow

# # Initialize Plot
fig, (ax_full, ax_signal, ax_filtered) = plt.subplots(3, 1, figsize=(10, 6))  # Adjust width and height here
line_full, = ax_full.plot([], [], label='Original Data', color='blue')
line_signal, = ax_signal.plot([], [], label='Original Data', color='blue')
line_filtered, = ax_filtered.plot([], [], label='Filtered Data', color='red')
scat = ax_filtered.scatter([], [], s=60)
ax_full.set_ylabel('Full Original Signal')
ax_signal.set_ylabel('Original Signal')
ax_filtered.set_xlabel('Time (s)')
ax_filtered.set_ylabel('Filtered Signal')
ax_signal.legend()
ax_filtered.legend()

# Initialize global variables
time_data, ydata = [], []
csv_reader = None
ani = None
rpeaks_annotations = []

def process_csv_data(data):
    # Process the CSV data (example: extract time and value)
    # Does so by emulating real time, I was unaware of the timing convention, but can also do this dynamically
    # if needed --> preprocess data to find out times, then update variables    value = float(data[0])
    value = float(data[0])
    if time_data:
        time_stamp = time_data[-1] + 1.0 / sampling_frequency
    else:
        time_stamp = 0  # Initial timestamp if xdata is empty
    return time_stamp, value

def apply_filter(signal_data):
   # Design the filter, using live filter from nk
    # Right now just filters all at once, can think of way to reduce computational time
    cleaned = nk.signal_filter(signal_data, sampling_rate=sampling_frequency, lowcut=4, highcut=0.5)
    return cleaned

def update_plot(frame):
    try:
        row = next(csv_reader)  # Read next row from CSV file
    except StopIteration:
        ani.event_source.stop()
        return

    time_stamp, value = process_csv_data(row)
    
    # Update plot data
    time_data.append(time_stamp)
    ydata.append(value)
    
    # Use library to find R-Peaks, waits 1 seconds to get enough data
    if len(time_data) > sampling_frequency:
        filtered_data = apply_filter(ydata)
        _, results = nk.ecg_peaks(filtered_data, sampling_rate=sampling_frequency)
        rpeaks = results["ECG_R_Peaks"]
    else:
        rpeaks = []
        filtered_data = []

    # Data, using 3000 as we have 300 samples per second, so 3000 is 10 seconds
    plot_time = time_data[max(-3000, -len(time_data)):]
    plot_ecg = ydata[max(-3000, -len(time_data)):]
    plot_filtered = filtered_data[max(-3000, -len(time_data)):]
    rpeaks = [int(x-(sampling_frequency*plot_time[0])) for x in rpeaks if x > (len(time_data) - 3000)]
    
    # Update lines
    line_full.set_data(time_data, ydata)
    line_signal.set_data(plot_time, plot_ecg)
    line_filtered.set_data(plot_time, plot_filtered)

    if len(time_data) > sampling_frequency:
        scat.set_offsets(np.column_stack((np.array(plot_time)[rpeaks], np.array(plot_filtered)[rpeaks])))

    # Adjust plot limits
    ax_full.relim()
    ax_full.autoscale_view()
    ax_signal.relim()
    ax_signal.autoscale_view()
    ax_filtered.relim()
    ax_filtered.autoscale_view()

def emulate_real_time(csv_file):
    global csv_reader, ani
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file) # Read CSV file
        ani = FuncAnimation(fig, update_plot, interval=1)  # Update plot every millisecond
        plt.show()

if __name__ == "__main__":
    csv_file = "vs_8x5_003_Tx20_ECG.csv"  # CSV file from Fidel
    time_data, ydata = [], []
    emulate_real_time(csv_file)
