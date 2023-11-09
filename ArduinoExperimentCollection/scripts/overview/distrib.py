import os
import sys
import statistics
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def getDataFileNameFromArgs(folder, dir):
    argsFile = open(folder+"/"+dir+"/args.txt")
    args = argsFile.readline().split(" ")
    argsFile.close()
    
    return folder+"/"+dir+"/"+args[1]

def getSignalFromFile(fileName, sensorName):
    file = open(fileName, 'r')
    Lines = file.readlines()
    
    idx_headers = [i for i, l in enumerate(Lines) if ":" in l]+[len(Lines)]
    names = []
    sensors = []

    for i, idx in enumerate(idx_headers[:-1]):
        temp = Lines[idx+1:idx_headers[i+1]]
        values = [float(l) for l in temp]
        names.append(Lines[idx])
        if sensorName in Lines[idx]:
            return values
    
    print("Sensor:", sensorName, "not found")
    print("available sensors:", names)
    exit(-1)

def getSignals(folder, filter, sensor, collect = lambda x: x):
    results = []
    for dir in os.listdir(folder):
        if filter in dir:
            dataFile = getDataFileNameFromArgs(folder, dir)
            data = getSignalFromFile(dataFile, sensor)
            result = collect(data)
            
            print(dataFile)
            #print(data)
            print(result)
            print()
            results.append(result)
    return results


def fold(f, a, xs):
    accumulator = a
    return [accumulator := f(accumulator, x) for x in xs][-1]

def fit_normal(results):
    mu, std = norm.fit(results)
    plt.hist(results, bins=25, density=True, alpha=0.6, color='g')

    # Plot the PDF.
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
    plt.title(title)

    plt.show()

def main():
    print("distrib")
    
    if len(sys.argv) < 4:
        print("Expected atleast 4 arguments")
        print("usage: python distrib.py <folder> <partial expiriment name> <sensor name>")
        exit(1)
    
    #results = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
    results = getSignals(sys.argv[1], sys.argv[2], sys.argv[3], lambda x: fold(max, 0, x[1:]))
    
    fit_normal(results)
    
    #mean = statistics.mean(results)
    #standard_deviation = statistics.stdev(results)
    #print(mean, standard_deviation)
    
    
    

if __name__ == "__main__":
    main()