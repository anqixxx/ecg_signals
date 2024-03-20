import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy import signal
import scipy
import numpy as np


# ECG Data Constants
csv_interval = 300 # 300 entries per second

# TMS Filter Constants
cutoff_frequency = 4.0  # Hz I think we said resting heart beat frequency is 1-2 Hz? Increase to 4 Hz to be safe
nyquist_frequency = 150.0  # Hz (assuming a sampling frequency of 300 Hz, I got this from the 2.01.2024 Notes)
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
num_taps = 150  # Number of filter taps, I got this from stack overflow

# Initialize Plot
fig, (ax_signal, ax_filtered) = plt.subplots(2, 1)
line_signal, = ax_signal.plot([], [], label='Original Data', color='blue')
line_filtered, = ax_filtered.plot([], [], label='Filtered Data', color='red')
ax_signal.set_ylabel('Original Signal')
ax_filtered.set_xlabel('Time')
ax_filtered.set_ylabel('Filtered Signal')
ax_signal.legend()
ax_filtered.legend()

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

def apply_filter(data):
    # Design the filter
    b = signal.firwin(num_taps, cutoff=normalized_cutoff_frequency)
    
    # Initialize the filter state
    zi = signal.lfilter_zi(b, 1)
    
    # Apply the filter to the data
    filtered_data, _ = signal.lfilter(b, 1, data, zi=zi)
    
    return filtered_data

def update_plot(frame):
    try:
        row = next(csv_reader)  # Read next row from CSV file
    except StopIteration:
        ani.event_source.stop()
        return

    time_stamp, value = process_csv_data(row)
    
    # Update plot data
    xdata.append(time_stamp)
    ydata.append(value)
    
    # Apply filter to the original data
    filtered_value = apply_filter([value])[0]

    # Update lines
    line_signal.set_data(xdata, ydata)
    line_filtered.set_data(xdata, [filtered_value] * len(xdata))

    # Adjust plot limits
    ax_signal.relim()
    ax_signal.autoscale_view()
    ax_filtered.relim()
    ax_filtered.autoscale_view()

def emulate_real_time(csv_file):
    global csv_reader
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file) # Read CSV file
        ani = FuncAnimation(fig, update_plot, interval=1)  # Update plot every millisecond
        plt.show()

def stack_filter():
    signal_data = np.loadtxt(csv_file, delimiter=',', usecols=(0,))
    filtered_result = apply_filter(signal_data)

    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(signal_data, label='Original Signal', color='blue')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.title('Original Signal')
    plt.legend()
    plt.grid(True)

    # Plot the filtered signal
    plt.subplot(2, 1, 2)
    plt.plot(filtered_result, label='Filtered Signal', color='red')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.title('Filtered Signal')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()  # Adjust layout to prevent overlap
    
    # Enable zooming
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=None, hspace=0.5)
    plt.subplots_adjust(wspace=0.5, hspace=0.5)
    plt.show()

def sam_filter(csv_file):
    yraw = np.loadtxt(csv_file, delimiter=',', usecols=(0,))
    fs = 300  # Sampling frequency
    num_samples = len(yraw)

    ts = np.linspace(0, num_samples / fs, num_samples)  # time vector - 5 seconds

    b, a = scipy.signal.iirfilter(4, Wn=2.5, fs=fs, btype="low", ftype="butter")
    print(b, a, sep="\n")
    y_lfilter = scipy.signal.lfilter(b, a, yraw)

    plt.figure(figsize=[6.4, 2.4])

    plt.plot(ts, yraw, label="Raw signal")
    plt.plot(ts, y_lfilter, alpha=0.8, lw=3, label="SciPy lfilter")

    plt.xlabel("Time / s")
    plt.ylabel("Amplitude")
    plt.legend(loc="lower center", bbox_to_anchor=[0.5, 1],
            ncol=2, fontsize="smaller")
if __name__ == "__main__":
    csv_file = "vs_8x5_003_Tx20_ECG.csv"  # CSV file from Fidel
    xdata, ydata = [], []
