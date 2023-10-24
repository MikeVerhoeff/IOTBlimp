import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.fftpack import fft

title = os.path.basename(os.path.realpath(sys.argv[1]).split(".")[0])

assert sys.argv[2]=="-f"
frequency = int(sys.argv[3])

values = [int(line) for line in open(sys.argv[1], 'r').readlines()]

count = len(values)
time = count/frequency
if sys.argv[4]=="-t":
    time = int(sys.argv[5])

assert sys.argv[6]=="-i"
plt.title("frequncy: "+title+" @ "+sys.argv[7])
plt.xlabel("Frequency (Hz)")
plt.ylabel("Strength")



N = count
# sample spacing
T = 1.0 / frequency
x = np.linspace(0.0, N*T, N)
y = values
yf = scipy.fftpack.fft(y)
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)


print("frequencys:")
print(yf)

plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))

#plt.show()
plt.savefig('frequency.png')
