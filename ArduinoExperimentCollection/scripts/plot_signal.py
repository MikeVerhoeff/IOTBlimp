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
print(Lines)

values = [int(l) for l in Lines]

count = len(values)
time = count/frequency
if sys.argv[4]=="-t":
    time = int(sys.argv[5])

print("values:")
print(values)

assert sys.argv[6]=="-i"
plt.title("signal: "+title+" @ "+sys.argv[7])
plt.xlabel("Time (s)")
plt.ylabel("Value")
plt.plot(np.linspace(0, time, count), values)

#plt.show()
plt.savefig('signal.png')
