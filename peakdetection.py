import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def read_csv(filename, chunksize):
    # Read the CSV file in chunks
    chunks = pd.read_csv(filename, usecols=[0], header=None, chunksize=chunksize)
    return chunks

def detect_peaks(signal):
    # Find peaks in the signal
    peaks, _ = find_peaks(signal)
    
    # Create a binary signal with peaks = 1 and everything else = 0
    peaks_signal = np.zeros_like(signal)
    peaks_signal[peaks] = 1
    
    return peaks_signal

csv_filename = "vs_8x5_003_Tx20_ECG.csv" # Out File
total_indices = 30000
update_interval = 150

# Initial plot setup
plt.ion()  # Turn on interactive mode
fig, (ax_signal, ax_peaks) = plt.subplots(2, 1)

try:
    chunks = read_csv(csv_filename, update_interval)
    plotted_indices = 0
    for chunk in chunks:
        signal_chunk = chunk.values.flatten()
        
        # Detect peaks
        peaks_signal_chunk = detect_peaks(signal_chunk)
        
        # Plot original signal
        ax_signal.clear()
        ax_signal.plot(np.arange(plotted_indices, plotted_indices + update_interval), signal_chunk)
        ax_signal.set_title('Original Signal')
        ax_signal.set_xlabel('Time')
        ax_signal.set_ylabel('Amplitude')
        
        # Plot detected peaks
        ax_peaks.clear()
        ax_peaks.plot(np.arange(plotted_indices, plotted_indices + update_interval), peaks_signal_chunk, color='red')
        ax_peaks.set_title('Detected Peaks')
        ax_peaks.set_xlabel('Time')
        ax_peaks.set_ylabel('Peaks')
        
        plt.subplots_adjust(hspace=0.5)  # Adjust spacing between subplots
        
        plt.draw()
        plt.pause(0.1)
        
        # Update plotted indices
        plotted_indices += update_interval
        if plotted_indices >= total_indices:
            break

except KeyboardInterrupt:
    print("Keyboard interrupt. Exiting...")
