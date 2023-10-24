
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys


TIME_FIELD_NAME = "TIMESTAMPS"
MIC_FREQUENCY_HZ = 16000
SCALE_MIN_MAX = False


sensor_df = pd.DataFrame()
mic_long_form_df = pd.DataFrame()


# read lines of data
# note: 'mic_piezo_balloon_pop' does not have piezo, 'mic_balloon_pop' does
with open(sys.argv[1], "r") as fd:
    for line in fd.readlines():
        if ":" not in line[:20]:
            continue
        name, value_line = line.split(":")
        value_strings = [ v.strip() for v in value_line.split(",") ]
        floats = any([ "." in v for v in value_strings ])
        values = [ float(v) if floats else int(v) for v in value_strings if len(v) > 0 ]
        if name == "MIC":
            mic_long_form_df["value"] = values
        else:
            sensor_df[name.strip()] = values

got_sensors = TIME_FIELD_NAME in sensor_df.columns
got_mic = mic_long_form_df.shape[0] > 0

# remove all rows from sensors where timestamp was 0
if got_sensors:
    sensor_df = sensor_df[sensor_df[TIME_FIELD_NAME] != 0]


# remove things you don't want maybe
# trim_mic_portions = [ 0.25, 0.4 ]
# mic_long_form_df = mic_long_form_df.iloc[int(mic_long_form_df.shape[0]*trim_mic_portions[0]):int(mic_long_form_df.shape[0]*trim_mic_portions[1])]
# sensor_df = sensor_df[[ TIME_FIELD_NAME, "ACC_X", "ACC_Y", "ACC_Z" ]]
# sensor_df = sensor_df[[ TIME_FIELD_NAME, "GYR_X", "GYR_Y", "GYR_Z" ]]
sensor_df = sensor_df[[ TIME_FIELD_NAME, "PROXIMITY" ]]



# for mic: processing to give the mic its own time stamps
latest = sensor_df[TIME_FIELD_NAME].max() if got_sensors else 0
if got_mic:
    mic_values_array = mic_long_form_df["value"].to_numpy()
    mic_times = [ latest - ((mic_long_form_df.shape[0] - i) / MIC_FREQUENCY_HZ)
                * 1_000_000 for i in range(mic_long_form_df.shape[0]) ]
    mic_long_form_df[TIME_FIELD_NAME] = mic_times
    mic_long_form_df["variable"] = "MIC"


# for proximty, replace any zeros with last non-zero value (temporary fix)
if "PROXIMITY" in sensor_df.columns:
    sensor_df["PROXIMITY"] = sensor_df["PROXIMITY"].replace(to_replace=0, method='ffill')


# optionally: convert all values to fractions for easy viewing
if SCALE_MIN_MAX:
    for col in sensor_df.columns:
        if col != TIME_FIELD_NAME:
            sensor_df[col] -= sensor_df[col].min()
            sensor_df[col] /= sensor_df[col].max()
    if got_mic:
        mic_long_form_df["value"] -= mic_long_form_df["value"].min()
        mic_long_form_df["value"] /= mic_long_form_df["value"].max()


# convert remaining stuff to long form, and plot it
sensor_long_form_df = pd.melt(sensor_df, [TIME_FIELD_NAME]) if got_sensors else pd.DataFrame()
total_long_form_df = pd.concat([ sensor_long_form_df, mic_long_form_df ])
total_long_form_df[TIME_FIELD_NAME] /= 1_000_000
sns.lineplot(x=TIME_FIELD_NAME, y='value', hue='variable', data=total_long_form_df)
plt.show()


# create spectrogram I guess
# Pxx, freqs, bins, im = plt.specgram(
#     mic_values_array, NFFT=2048, Fs=MIC_FREQUENCY_HZ * 1000)
# plt.show()

# sp = np.fft.fft(mic_values_array)
# freq = np.fft.fftfreq(mic_values_array.shape[-1], 1/MIC_FREQUENCY_HZ)
# plt.plot(freq, sp.real, freq, sp.imag)
# plt.show()