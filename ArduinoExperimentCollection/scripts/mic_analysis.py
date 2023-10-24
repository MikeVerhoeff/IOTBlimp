import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.fftpack import fft

if sys.argv[7]!="MIC":
    exit(0)

title = os.path.basename(os.path.realpath(sys.argv[1]).split(".")[0])

assert sys.argv[2]=="-f"
frequency = int(sys.argv[3])

values = [int(line) for line in open(sys.argv[1], 'r').readlines()]

count = len(values)
time = count/frequency
if sys.argv[4]=="-t":
    time = int(sys.argv[5])

assert sys.argv[6]=="-i"
plt.title("smooth signal: "+title+" @ "+sys.argv[7])

plt.xlabel("Time (t)")
plt.ylabel("Strength (smooth over 1024 samples)")
y = np.correlate(values, [1]*1024)
x = np.linspace(0, time, count)
plt.plot(x[1023:], y)

#plt.show()
plt.savefig('smoothValues.png')
