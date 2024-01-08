import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import scipy.fftpack


TIME_FIELD_NAME = "TIMESTAMPS"
MIC_FREQUENCY_HZ = 16000
SCALE_MIN_MAX = False


def read_labled_data(lines, label):
    for line in lines:
        line_split = line.split(":")
        if len(line_split) == 2:
            name, value_line = line_split
            if name==label:
                value_strings = [ v.strip() for v in value_line.split(",") ]
                floats = any([ "." in v for v in value_strings ])
                values = [ float(v) if floats else int(v) for v in value_strings if len(v) > 0 and v.isnumeric()]
                return values
    
def read_mic_log(file_name):
    with open(file_name, "r") as fd:
        lines = fd.readlines()[1:]
        time_stamps = read_labled_data(lines, "TIMESTAMPS")
        mic_values = read_labled_data(lines, "MIC")
        return (time_stamps, mic_values)

def simple_filter(vals):
    res = []
    n = 1500
    for i in range(len(vals)-n):
        s = 0
        for j in range(n):
            s += vals[i+j]
        res.append(s/n)
    return res
    
def bw_filter(y):
    b = [9.62491303e-07, 1.92498261e-06, 9.62491303e-07]
    a = [-1, 1.9972232,  -0.99722705]
    
    Nb = len(b)
    yfilt = np.zeros(len(y));
    for m in range(3,len(y)):
        yfilt[m] = b[0]*y[m];
        for i in range(1,Nb):
            yfilt[m] += a[i]*yfilt[m-i] + b[i]*y[m-i];
    return yfilt

# filter as implemented on arduino
def bw_2_filter(y):
    b = [9.62491303e-07, 1.92498261e-06, 9.62491303e-07]
    a = [-1, 1.9972232,  -0.99722705]
    
    yfilt = np.zeros(len(y));
    yhist = [0]*3
    reshist = [0]*3
    
    for m in range(3,len(y)):
        yhist[0] = y[m]
        yhist[1] = yhist[0]
        yhist[2] = yhist[1]
        
        reshist[2] = reshist[1]
        reshist[1] = reshist[0]
        
        reshist[0] = b[0]*yhist[0] + b[1]*yhist[1] + b[2]*yhist[2] + a[1]*reshist[1] + a[2]*reshist[2];   
        
        
        yfilt[m] = int(reshist[0])
        
    return yfilt

def delta_filter(vals):
    res = []
    d = 750
    for i in range(len(vals)-d):
        res.append(vals[i+d]-vals[i])
    return res

def main():
    #(times, values) = read_mic_log(sys.argv[1])
    
    (_, motor) = read_mic_log("drone.log")
    filtered_motor = np.correlate(motor, [1]*1024)
    print("avg drone:", sum(motor)/len(motor))
    
    (_, motor_pop) = read_mic_log("drone_balloon.log")
    filtered_motor_pop = np.correlate(motor_pop, [1]*1024)
    print("avg drone balloon:", sum(motor_pop)/len(motor_pop))

    
    #f = plt.figure(1)
    #plt.plot(filtered_motor_pop)
    #f.show()
    
    #f = plt.figure(2)
    #plt.plot(filtered_motor)
    #f.show()
    
    #f = plt.figure(3)
    #plt.plot(scipy.fftpack.fft(motor))
    #f.show()
    
    #f = plt.figure(4)
    #plt.plot(scipy.fftpack.fft(motor_pop))
    #f.show()
    
    #f = plt.figure(5)
    #plt.plot(scipy.fftpack.fft(filtered_motor_pop))
    #f.show()
    
    
    f = plt.figure(6)
    plt.plot(motor)
    f.show()
    
    f = plt.figure(7)
    plt.plot(motor_pop)
    f.show()
    
    
    #f = plt.figure(8)
    #plt.plot(simple_filter(motor))
    #f.show()
    
    #f = plt.figure(9)
    #plt.plot(simple_filter(motor_pop))
    #f.show()
    
    
    #f = plt.figure(10)
    #plt.plot(delta_filter(simple_filter(motor)))
    #f.show()
    
    #f = plt.figure(11)
    #plt.plot(delta_filter(simple_filter(motor_pop)))
    #f.show()
    
    
    #f = plt.figure(12)
    #plt.plot(bw_filter(motor))
    #f.show()
    
    #f = plt.figure(13)
    #plt.plot(bw_filter(motor_pop))
    #f.show()
    
    f = plt.figure(14)
    plt.plot(bw_2_filter(motor))
    f.show()
    
    f = plt.figure(15)
    plt.plot(bw_2_filter(motor_pop))
    f.show()
    
    
    f = plt.figure(14)
    plt.plot(delta_filter(bw_2_filter(motor)))
    f.show()
    
    f = plt.figure(15)
    plt.plot(delta_filter(bw_2_filter(motor_pop)))
    f.show()
    
    
    
    
    plt.show()

if __name__ == "__main__":
    main()