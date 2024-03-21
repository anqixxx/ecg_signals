import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy import signal
import scipy
import numpy as np
import neurokit2 as nk


# ECG Data Constants
csv_interval = 300 # 300 entries per second

# TMS Filter Constants
cutoff_frequency = 3.0  # Hz I think we said resting heart beat frequency is 1-2 Hz? Increase to 4 Hz to be safe
sampling_frequency = 300.0  # Hz
nyquist_frequency = sampling_frequency/2.0  # Hz (assuming a sampling frequency of 300 Hz, I got this from the 2.01.2024 Notes)
normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
num_taps = 100  # Number of filter taps, I got this from stack overflow

# # Initialize Plot
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
    if time_data:
        time_stamp = time_data[-1] + 1.0 / csv_interval
    else:
        time_stamp = 0  # Initial timestamp if xdata is empty
    return time_stamp, value

def apply_filter(signal_data):
   # Design the filter, using live filter from nk
    # Right now just filters all at once, can think of way to reduce computational time
    cleaned = nk.signal_filter(signal_data, sampling_rate=300, lowcut=4, highcut=0.5)
    return cleaned


def update_plot(frame):
    try:
        row = next(csv_reader)  # Read next row from CSV file
    except StopIteration:
        ani.event_source.stop()
        return

    time_stamp, value = process_csv_data(row)
    
    # Update plot data, now takes a while as it does it piece by piece /
    # but it makes more time to do batches to sped it up
    time_data.append(time_stamp)
    ydata.append(value)
    
    # Use library to find R-Peaks, waits 1 seconds to get enough data
    if len(time_data) > sampling_frequency :
        filtered_data = (apply_filter(ydata))
        _, results = nk.ecg_peaks(filtered_data, sampling_rate=csv_interval)
        rpeaks = results["ECG_R_Peaks"]
    else:
        rpeaks = []
        filtered_data = []

    # Update lines
    line_signal.set_data(time_data, ydata)
    line_filtered.set_data(time_data, filtered_data)
    ax_filtered.scatter(np.array(time_data)[rpeaks], np.array(filtered_data)[rpeaks], color='green', marker='o', label='R-Peaks')
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

def nk_filt():
    signal_data = np.loadtxt(csv_file, delimiter=',', usecols=(0,))
    # Clean (filter and detrend)
    # signal_data = signal_data[:3000]  # Limit to 10 seconds of data
    signal_data = nk.ecg_clean(signal_data, sampling_rate=300, method='neurokit')
    cleaned = nk.signal_filter(signal_data, sampling_rate=300, lowcut=4, highcut=0.5)
    # cleaned = nk.signal_filter(cleaned, sampling_rate=300, lowcut=4, highcut=0.5)

    # Extract R-peaks locations
    signals, results = nk.ecg_peaks(signal_data, sampling_rate=300, method='neurokit', show=True)
    rpeaks = results["ECG_R_Peaks"]
    print(rpeaks)
    print(signals)

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
    plt.plot(signal_data, label='Filtered Signal', color='red')
    plt.scatter(rpeaks, signal_data[rpeaks], marker = 'o')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.title('Filtered Signal - NeuroKit2')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()  # Adjust layout to prevent overlap
    
    # Enable zooming
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=None, hspace=0.5)
    plt.subplots_adjust(wspace=0.5, hspace=0.5)
    plt.show()

if __name__ == "__main__":
    csv_file = "vs_8x5_003_Tx20_ECG.csv"  # CSV file from Fidel
    time_data, ydata = [], []
    emulate_real_time(csv_file)
    # nk_filt()
    # stack_filter()