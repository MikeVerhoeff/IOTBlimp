import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.fftpack import fft

title = os.path.basename(os.path.realpath(sys.argv[1]).split(".")[0])

assert sys.argv[2]=="-f"
frequency = int(sys.argv[3])

Lines = open(sys.argv[1], 'r').readlines()

idx_headers = [i for i, l in enumerate(Lines) if ":" in l]+[len(Lines)]
names = []
sensors = []

for i, idx in enumerate(idx_headers[:-1]):
    temp = Lines[idx+1:idx_headers[i+1]]
    values = [float(l) for l in temp]
    sensors.append(values)
    names.append(Lines[idx])

assert sys.argv[6]=="-i"
plt.title("frequncy: "+title+" @ "+sys.argv[7])
plt.xlabel("Frequency (Hz)")
plt.ylabel("Strength")





for i, sensor in enumerate(sensors):
    
    count = len(sensors[i])
    time = count/frequency
    if sys.argv[4]=="-t":
        time = int(sys.argv[5])
    
    N = count
    # sample spacing
    T = 1.0 / frequency
    x = np.linspace(0.0, N*T, N)
    
    y = sensor
    yf = scipy.fftpack.fft(y)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    #print("frequencys:")
    #print(yf)

    plt.plot(xf, 2.0/N * np.abs(yf[:N//2]), label=Lines[idx_headers[i]])
    # plt.plot(np.linspace(0, time, count), sensor, label=Lines[idx_headers[i]])

#plt.show()
plt.legend()

plt.savefig('frequency.png')
