import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys


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

def main():
    (times, values) = read_mic_log(sys.argv[1])
    
    (_, motor) = read_mic_log("drone.log")
    filtered_motor = np.correlate(motor, [1]*1024)
    print("avg drone:", sum(motor)/len(motor))
    
    (_, motor_pop) = read_mic_log("drone_balloon.log")
    filtered_motor_pop = np.correlate(motor_pop, [1]*1024)
    print("avg drone balloon:", sum(motor_pop)/len(motor_pop))
    
    f = plt.figure(1)
    plt.plot(filtered_motor_pop)
    f.show()
    g = plt.figure(2)
    plt.plot(filtered_motor)
    g.show()
    
    
    
    plt.show()

if __name__ == "__main__":
    main()