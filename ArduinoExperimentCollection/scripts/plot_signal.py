import sys
import os
import matplotlib.pyplot as plt
import numpy as np

title = os.path.basename(os.path.realpath(sys.argv[1]).split(".")[0])

assert sys.argv[2]=="-f"
frequency = int(sys.argv[3])

file1 = open(sys.argv[1], 'r')
Lines = file1.readlines()

print("lines:")
print(Lines[:50])

idx_headers = [i for i, l in enumerate(Lines) if ":" in l]+[len(Lines)]
names = []
sensors = []

for i, idx in enumerate(idx_headers[:-1]):
    temp = Lines[idx+1:idx_headers[i+1]]
    values = [float(l) for l in temp]
    sensors.append(values)
    names.append(Lines[idx])

count = len(sensors[0])
time = count/frequency
if sys.argv[4]=="-t":
    time = int(sys.argv[5])

print("sensors:")
print(sensors[:50])

assert sys.argv[6]=="-i"
plt.title("signal: "+title+" @ "+sys.argv[7])
plt.xlabel("Time (s)")
plt.ylabel("Value")
for i, sensor in enumerate(sensors):
    plt.plot(np.linspace(0, time, count), sensor, label=Lines[idx_headers[i]])
plt.legend()

#plt.show()
plt.savefig('signal.png')
