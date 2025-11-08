import numpy as np
import adi
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Configuration ---
fs = 1.2e6  # Hz
fc = 438.304e6  # Hz
fftsize = 10000
frames = 100 # Reduced for faster initial display if needed
update_interval_ms = 7 # ms between frames

# --- SDR Setup ---
try:
    sdr = adi.Pluto('ip:192.168.2.1')
except Exception as e:
    print(f"Error connecting to PlutoSDR: {e}")
    print("Please ensure the device is connected and the IP address is correct.")
    exit()

sdr.gain_control_mode_chan0 = 'manual'
sdr.rx_hardwaregain_chan0 = 20.0  # dB 
sdr.rx_lo = int(fc)
sdr.sample_rate = int(fs)
sdr.rx_rf_bandwidth = int(fs)
sdr.rx_buffer_size = fftsize

# --- Frequency Axis ---
# Calculate frequency bins corresponding to the FFT output
f = np.fft.fftshift(np.fft.fftfreq(fftsize, 1/fs)) / 1e6 # Frequencies in MHz

# --- Plot Setup ---
fig, ax = plt.subplots()
# Initialize spectrogram data (can be empty or zeros)
spectrogram_data = np.zeros((frames, fftsize))

# *** FIX: Set explicit vmin and vmax for color scaling ***
# Adjust these values based on expected signal/noise power
vmin_db = 20
vmax_db = 150

img = ax.imshow(
    spectrogram_data,
    aspect='auto',
    extent=[f[0], f[-1], 0, frames], # Freq min, Freq max, Time start, Time end
    cmap='viridis',
    origin='lower', # Puts frame 0 at the bottom
    vmin=vmin_db,  # Minimum dB value for color mapping
    vmax=vmax_db   # Maximum dB value for color mapping
)
fig.colorbar(img, ax=ax, label='Power') # Add a colorbar for reference
ax.set_xlabel("Frequency [MHz]")
ax.set_ylabel("Time Frames")
ax.set_title("Real-time Spectrogram")

# --- Update Function ---
def update(frame):
    try:
        samples = sdr.rx() # Receive samples off Pluto
        # Ensure samples are complex numbers
        if samples.dtype != np.complex64 and samples.dtype != np.complex128:
             # Pluto might return int16, scale and convert
             samples = (samples[0] + 1j * samples[1]) / 2**11 # Adjust scaling if needed

        # Calculate PSD
        psd = np.abs(np.fft.fftshift(np.fft.fft(samples)))**2
        # Convert to dB, adding a small epsilon to avoid log10(0)
        psd_dB = 10 * np.log10(psd + 1e-12)

        # Update the spectrogram data array
        global spectrogram_data
        # Roll old data up (axis 0)
        spectrogram_data = np.roll(spectrogram_data, -1, axis=0)
        # Add new data at the bottom (or top if origin='upper')
        spectrogram_data[-1, :] = psd_dB[(f>-20e3) & (f<20e3)]

        # Update the image data
        img.set_data(spectrogram_data)
        # Optional: Print min/max for debugging
        # print(f"Frame {frame}: min={np.min(psd_dB):.2f}, max={np.max(psd_dB):.2f}")

    except Exception as e:
        print(f"Error during update: {e}")
        # Optionally stop animation or handle error
        # ani.event_source.stop()
    return [img] # Return the updated image artist

# --- Animation ---
# Try with blit=False first if blit=True causes issues
ani = animation.FuncAnimation(fig, update, interval=update_interval_ms, blit=True, cache_frame_data=False)

try:
    plt.show()
except Exception as e:
    print(f"Error displaying plot: {e}")
finally:
    # Clean up SDR resources if the script exits
    print("Closing SDR connection.")
    del sdr # Ensure Pluto object is deleted
