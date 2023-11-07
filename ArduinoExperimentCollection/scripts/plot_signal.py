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


figures = {}

plotCount = 0
print("sensors:")
for i, sensor in enumerate(sensors):
    name = Lines[idx_headers[i]]
    type = name[0:3]
    if type not in figures.keys():
        plotCount+=1
        figures[type] = plt.figure(plotCount)
    


assert sys.argv[6]=="-i"

lastType = ""
for i, sensor in enumerate(sensors):
    count = len(sensor)
    name = Lines[idx_headers[i]]
    type = name[0:3]
    if type != lastType:
        if lastType!= "":
            plt.legend()
            plt.savefig('signal_'+lastType+'.png')
            plt.clf()
    
        plt.title("signal: "+title+" @ "+sys.argv[7]+" - "+type)
        plt.xlabel("Time (s)")
        plt.ylabel("Value")
    plt.plot(np.linspace(0, time, count), sensor, label=Lines[idx_headers[i]])
    lastType = type
plt.legend()
#plt.show()
plt.savefig('signal_'+lastType+'.png')
    
