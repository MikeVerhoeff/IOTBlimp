import sys
import os
import matplotlib.pyplot as plt
import numpy as np

title = os.path.basename(os.path.realpath(sys.argv[1]).split(".")[0])

assert sys.argv[2]=="-f"
frequency = int(sys.argv[3])


file1 = open(sys.argv[1], 'r')
Lines = file1.readlines()

values = np.array([[float(v) for v in l.split(',')] for l in Lines]).T

plots = len(values)
if plots<2:
    exit()

count = len(values[0])
time = count/frequency
if sys.argv[4]=="-t":
    time = int(sys.argv[5])

print("values:")
print(values)

assert sys.argv[6]=="-i"
plt.title("signal: "+title+" @ "+sys.argv[7])
plt.xlabel("Time (s)")
plt.ylabel("Value")

labels = [None]*plots

if sys.argv[7]=="IMU" and plots==6:
    labels=["ax", "ay", "az", "rx", "ry", "rz"]
    print("using IMU labels")

for i in range(plots):
    plt.plot(np.linspace(0, time, count), values[i], label=labels[i])

leg = plt.legend(loc='upper right')
#plt.show()
plt.savefig('signals.png')
