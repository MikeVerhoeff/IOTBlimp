import os
import sys
import statistics
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from types import ModuleType
import math

def mic_filter(y):
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

def getDataFileNameFromArgs(folder, dir):
    argsFile = open(folder+"/"+dir+"/args.txt")
    args = argsFile.readline().split(" ")
    argsFile.close()
    
    if args[2]=="-f" and args[4]=="-t":
        return folder+"/"+dir+"/"+args[1], int(args[5]), int(args[3])
    elif args[2]=="-f" and args[4]=="-c":
        return folder+"/"+dir+"/"+args[1], int(args[5])/int(args[3]), int(args[3])
    else:
        return folder+"/"+dir+"/"+args[1], None, None

def getSignalFromFile(fileName, sensorName):
    
    file = open(fileName, 'r')
    Lines = file.readlines()
    
    idx_headers = [i for i, l in enumerate(Lines) if ":" in l]+[len(Lines)]
    names = []
    sensors = []
    
    allValues = []
    
    for i, idx in enumerate(idx_headers[:-1]):
        temp = Lines[idx+1:idx_headers[i+1]]
        values = [float(l) for l in temp]
        names.append(Lines[idx])
        if sensorName in Lines[idx]:
            #print(Lines[idx], values)
            #return values
            allValues.append(values)
    
    if len(allValues)==1:
        return allValues[0]
    elif len(allValues)>1:
        return list(map(lambda vec: np.linalg.norm(vec), np.array(allValues).T))
    
    print("Sensor:", sensorName, "not found")
    print("available sensors:", names)
    exit(-1)

def getSignals(folder, filter, sensor, collect = lambda x: x):
    results = []
    fs = []
    ts = []
    for dir in os.listdir(folder):
        if filter in dir:
            dataFile, t, f = getDataFileNameFromArgs(folder, dir)
            data = getSignalFromFile(dataFile, sensor)
            result = collect(data)
            
            print(dataFile)
            #print(data)
            if isinstance(result, list):
                print("list:", result[:10], "...")
            else:
                print(result)
            print()
            results.append(result)
            fs.append(f)
            ts.append(t)
    return results, ts, fs


def fold(f, a, xs):
    accumulator = a
    return [accumulator := f(accumulator, x) for x in xs][-1]

def fit_normal(results, color='g', label=None, onlyLines=False, doFit=True, doHist=True, bins=25, xlim=None, ylim=None, scaleToOne=False):
    mu, std = norm.fit(results)
    
    if xlim != None or ylim != None:
        ax = plt.gca()
        if xlim != None:
            ax.set_xlim(xlim)
        if ylim != None:
            ax.set_ylim(ylim)
    
    # Plot the PDF.
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 1000)
    p = norm.pdf(x, mu, std)
    
    if doHist:
        if scaleToOne:
            plt.hist(results, bins=bins, density=False, alpha=0.6, color=color, label=label, weights=0.1*np.ones_like(results))
        else:
            plt.hist(results, bins=bins, density=True, alpha=0.6, color=color, label=label)
    
    
    
    if scaleToOne:
        scale = std * math.sqrt(2*math.pi)
        p = p * scale
    
    if doFit:
        lbl = None
        if onlyLines and label != None:
            lbl=label+" (mu = %.2f,  std = %.2f)" % (mu, std)
        alpha = 1
        if doFit and onlyLines and not doHist:
            alpha = 0.6
        plt.plot(x, p, 'k', color=color, label=lbl, alpha=alpha)
        
    
    if not onlyLines:
        title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
        plt.title(title)
    
    if label != None:
        leg = plt.legend(loc='upper center')
    
    if not onlyLines:
        plt.show()
    
    return (mu, std)

def plotValues(folder, file, sensor, timeOffset=0, index=0, label=None, color=None, alpha=None, plt=plt, xlim=None, ylim=None):
    results, ts, fs = getSignals(folder, file, sensor, lambda x: x)
    results = results[index]
    print(fs, ts)
    f = fs[index]
    t = ts[index]
    
    if xlim != None or ylim != None:
        ax = plt
        if isinstance(plt, ModuleType):
            ax = plt.gca()
        if xlim != None:
            ax.set_xlim(xlim)
        if ylim != None:
            ax.set_ylim(ylim)
    
    if not isinstance(plt, ModuleType):
        plt.set_title(label)
    
    plt.plot(np.linspace(0-timeOffset, t-timeOffset, len(results)), results, label=label, alpha=alpha, color=color)

def flatten(l):
    return [item for sublist in l for item in sublist]
    

def main():
    print("distrib")
    
    if len(sys.argv) < 5 and len(sys.argv) !=2:
        print("Expected atleast 4 arguments")
        print("usage: python distrib.py <folder> <partial expiriment name> <sensor name> <vals/max>")
        exit(1)
    
    #results = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
    
    if len(sys.argv) >= 5:
    
        if sys.argv[4] == "vals":
            results, ts, fs = getSignals(sys.argv[1], sys.argv[2], sys.argv[3], lambda x: x)
            
            if len(sys.argv)>=6 and sys.argv[5]=="filter":
                print("Filtering")
                results = list(map(mic_filter, results))
            
            fit_normal(flatten(results), color='r')
            for i in range(len(results)):
                plt.plot(np.linspace(0, ts[i], len(results[i])), results[i])
                plt.show()
            
            
        elif sys.argv[4] == "max":
            results, ts, fs = getSignals(sys.argv[1], sys.argv[2], sys.argv[3], lambda x: fold(max, -2**16, x[1:]))
            if len(sys.argv)>=6 and sys.argv[5]=="filter":
                results = list(map(mic_fillter, results))
            fit_normal(results)
            
            
        elif sys.argv[4] == "min":
            results, ts, fs = getSignals(sys.argv[1], sys.argv[2], sys.argv[3], lambda x: fold(min, 2**32, x[1:]))
            if len(sys.argv)>=6 and sys.argv[5]=="filter":
                results = list(map(mic_fillter, results))
            fit_normal(results)
        
    else:
        if sys.argv[1] == "PROX":
            #-----------------------------------------------------------------------------------------------------------
        
            plt.title("Proximity Balloon: Present vs Absent")
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "baseline_absent", "PROX", lambda x: x)
            fit_normal(flatten(results_no_balloon), onlyLines=True, label="No Balloon", color='r', bins=list(range(256)), xlim=[-1,256])
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "gray_baseline_present", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Balloon Present", color='g', doFit=False, bins=list(range(256)), xlim=[-1,256])
            
            plt.savefig('prox_Present_vs_Absent.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # IR LED FP
            plt.title("Proximity Balloon: Absent vs IR LED")
            
            bins = list(range(120, 256))
            xlim=[120,256]
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "baseline_absent", "PROX", lambda x: x)
            fit_normal(flatten(results_no_balloon), onlyLines=True, label="No Balloon", color='r', bins=bins, xlim=xlim)
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "gray_IR_LED_direct_full", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Balloon Present, Full Power IR LED", color='b', doFit=False, bins=bins, xlim=xlim)
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "IR_LED_direct_under_powered", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Balloon Absent, Underpowered IR LED", color='orange', doFit=False, bins=bins, xlim=xlim)
            
            plt.savefig('prox_Absent_vs_IR_LED.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX stick
            plt.title("Proximity Balloon: Present vs Weaving Object (maximal value in 10 runs)")
            
            bins = list(range(0, 100))
            xlim=[-1,101]
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "gray_stick", "PROX", lambda x: fold(max, 0, x[1:]))
            fit_normal(results_no_balloon, onlyLines=True, label="Balloon Present, weaving object above sensor", color='m', doFit=False, bins=bins, xlim=xlim)
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "gray_baseline_present", "PROX", lambda x: fold(max, 0, x[1:]))
            fit_normal(results_balloon_present, onlyLines=True, label="Balloon Present", color='g', doFit=False, bins=bins, xlim=xlim)
            
            plt.savefig('prox_Present_vs_Weaving_Object.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX Examples
            plt.title("Proximity Balloon: Examples of popping")
            
            zero = 0.36
            alpha = 0.7
            
            results_no_balloon, ts, fs = getSignals("../../pop", "all_(1)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(0-zero, t-zero, len(results_no_balloon)), results_no_balloon, label="Proximity", alpha=alpha, color='blue')
            
            results_no_balloon, ts, fs = getSignals("../../pop", "all_(7)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(-0.285-zero, t-0.285-zero, len(results_no_balloon)), results_no_balloon, label="Proximity", alpha=alpha, color='orange')
            
            results_no_balloon, ts, fs = getSignals("../../pop", "all_(8)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(-0.075-zero, t-0.075-zero, len(results_no_balloon)), results_no_balloon, label="Proximity", alpha=alpha, color='green')
            
            plt.savefig('prox_Examples.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX Responce to mirror
            
            plt.title("Proximity Balloon: Raise and Lower")
            
            alpha = 0.7
            
            results_no_balloon, ts, fs = getSignals("../../fp_tests", "fp_red_(6)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(0, t, len(results_no_balloon)), results_no_balloon, label="Red Balloon", alpha=alpha, color='blue')
            
            results_no_balloon, ts, fs = getSignals("../../fp_tests", "fp_transparent_edge_(5)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(0+0.08, t+0.08, len(results_no_balloon)), results_no_balloon, label="Edge of transparent Balloon", alpha=alpha, color='orange')
            
            results_no_balloon, ts, fs = getSignals("../../fp_tests", "fp_mirror_angle_(7)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(0, t, len(results_no_balloon)), results_no_balloon, label="Mirror at 45 degrees", alpha=alpha, color='green')
            
            leg = plt.legend(loc='lower center')
            
            plt.savefig('prox_Raise_and_lower.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
        elif sys.argv[1] == "PIEZO":
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO Effect of Parallel Resistance
            
            fig, (ax1, ax2, ax3) = plt.subplots(3)
            fig.suptitle("Piezo: Effect of Parallel Resistance")
            fig.tight_layout()
            
            xlim = [-0.2, 0.6]
            ylim = [0, 1023]
            
            plotValues("../../dataPartyBalloonPiezo/50K-PiozoHard-tapenormal",  "PiezoH_pop_(3)", "PIEZO", plt=ax1, timeOffset=0.57, label="50K Ohm",  xlim=xlim, ylim=ylim)
            plotValues("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop_(2)", "PIEZO", plt=ax2, timeOffset=0.77, label="100K Ohm", xlim=xlim, ylim=ylim)
            plotValues("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_1M_pop",  "PIEZO", plt=ax3, timeOffset=0.4,  label="1M Ohm",   xlim=xlim, ylim=ylim)
            
            plt.savefig('piezo_Parallel_Resistance.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO still vs vibration
            
            plt.title("Piezo: Maximal Value From 10 Runs: Still vs Vibrations")
            
            xlim = [0, 17]
            bins = list(range(0,18))
            
            results, ts, fs = getSignals("../../dataPiezo", "still", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Still",                color='g', doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPiezo", "vibration_dremel_5t", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Rotary Tool 5000 RPM", color='b', doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Drone Motors",         color='r', doFit=True, xlim=xlim, bins=bins)
            
            plt.savefig('piezo_vibration.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO dists scaled
            
            plt.title("Piezo: Book Hits")
            
            alpha = 0.6
            xlim = [-20, 120]
            bins = list(range(-20,121, 5))
            
            results, ts, fs = getSignals("../../dataPiezo", "still", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Still",                  color='g',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "fp_bookface_soft", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Bookface Soft",          color='r',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "fp_bookside_non", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Bookside not on Sensor", color='orange', ylim=[0, 0.15], xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "fp_bookside_on", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Bookside on Sensor",     color='blue',   ylim=[0, 0.15], xlim=xlim, bins=bins)
            
            plt.legend(loc='upper right')
            
            plt.savefig('piezo_book.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO hit position
            
            plt.title("Piezo: Maximal Value From 10 Runs: Hitting ballon in diffrent positions")
            
            xlim = [0, 1000]
            ylim = [0, 0.025]
            bins = list(range(0,1000, 30))
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_disk_side", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit, side",            color='orange', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Small Balloon Popping (4 runs)",        color='purple', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            
            plt.savefig('piezo_nerf.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO dists scaled
            
            plt.title("Piezo: Distributions Scaled to Same Hieght")
            
            alpha = 0.6
            
            results, ts, fs = getSignals("../../dataPiezo", "still", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Still",                                 color='g',      doHist=False, doFit=True, xlim=[0, 1023], scaleToOne=True)
            
            results, ts, fs = getSignals("../../dataPiezo", "vibration_dremel_5t", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Rotary Tool 5000 RPM",                  color='b',      doHist=False, doFit=True, xlim=[0, 1023], scaleToOne=True)
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_disk_side", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit",                  color='orange', doHist=False, doFit=True, xlim=[0, 1023], scaleToOne=True)
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doHist=False, doFit=True, xlim=[0, 1023], scaleToOne=True)
            
            results, ts, fs = getSignals("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Small Balloon Popping",                 color='purple', doHist=False, doFit=True, xlim=[0, 1023], scaleToOne=True)
            
            plt.savefig('piezo_Scaled.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
        
        elif sys.argv[1] == "ACC":
            
            #-----------------------------------------------------------------------------------------------------------
            
            # ACC movement
            
            plt.title("Accelerometer: Movement")
           
            xlim=[0.6, 1]
            bins=np.linspace(xlim[0], xlim[1], num=40)
            
            results, ts, fs = getSignals("../../acc", "fp_1ms_side", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Moving Side to Side (+/- 1 m/s)",  color='orange', doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../acc", "fp_1ms_up_down", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Drone Motors on, Still",           color='purple', doFit=True, xlim=xlim, bins=bins)
            
            
            #results, ts, fs = getSignals("../../fp_tests", "fp_bookface", "ACC", lambda x: fold(min, 2**32, x[1:]))
            #fit_normal(results, onlyLines=True, label="Hit with Face of Book",            color='green', doFit=True, xlim=xlim, bins=bins)
            
            #results, ts, fs = getSignals("../../fp_tests", "fp_bookside", "ACC", lambda x: fold(min, 2**32, x[1:]))
            #fit_normal(results, onlyLines=True, label="Hit with Side of Book",            color='blue', doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "fp_book", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Hit with a Book",            color='green', doFit=True, xlim=xlim, bins=bins)
            
            #results, ts, fs = getSignals("../../fp_tests", "fp_nerf", "ACC", lambda x: fold(min, 2**32, x[1:]))
            #fit_normal(results, onlyLines=True, label="Hit a Neft Disk",            color='yellow', doFit=True, xlim=xlim, bins=bins)
            
            plt.legend(loc='upper left')
            
            plt.savefig('acc_move.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # ACC pop
            
            plt.title("Accelerometer: Pop")
           
            xlim=[-0.1, 1.1]
            bins=np.linspace(xlim[0], xlim[1], num=50)
            
            results, ts, fs = getSignals("../../acc", "fp_1ms_up_down", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Drone Motors on, Still",           color='purple', doFit=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../pop", "all", "ACC", lambda x: fold(min, 2**32, x[1:]))
            fit_normal(results, onlyLines=True, label="Balloon pop",           color='blue', doFit=True, xlim=xlim, bins=bins)
            
            plt.legend(loc='upper left')
            
            plt.savefig('acc_pop.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
        elif sys.argv[1] == "MIC":
            
            #-----------------------------------------------------------------------------------------------------------
            
            # MIC pop
            
            plt.title("Microphone: Pop Balloon at Diffrent Distances")
            
            xlim = [-1000, 14000]
            bins=np.linspace(xlim[0], xlim[1], num=30)
            
            #results, ts, fs = getSignals("../../fp_tests", "fp_1m", "MIC", lambda x: x)
            #results = list(map(mic_filter, results))
            #results = list(map(lambda x: fold(max, -2**16, x[1:]), results))
            #fit_normal(results, onlyLines=True, label="pop at 1m")
            
            results, ts, fs = getSignals("../../dataMic", "still_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            fit_normal(results, onlyLines=True, label="still",              color='b',      scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataMic", "300hz_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            fit_normal(results, onlyLines=True, label="300Hz tone",         color='g',      scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataMic", "150cm_pop_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            fit_normal(results, onlyLines=True, label="pop ballon @ 150cm", color='orange', scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataMic", "30cm_pop_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            fit_normal(results, onlyLines=True, label="pop ballon @ 30cm",  color='r',      scaleToOne=True, xlim=xlim, bins=bins)
            
            pop_results = []
            results, ts, fs = getSignals("../../pop", "all_(2)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            results, ts, fs = getSignals("../../pop", "all_(5)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            results, ts, fs = getSignals("../../pop", "all_(6)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            results, ts, fs = getSignals("../../pop", "all_(8)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            results, ts, fs = getSignals("../../pop", "all_small", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            pop_results.append(results[1])
            results, ts, fs = getSignals("../../pop", "mic", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            pop_results.append(results[1])
            pop_results.append(results[3])
            fit_normal(pop_results, onlyLines=True, label="pop own ballon (motor on)",  color='purple',      scaleToOne=True, xlim=xlim, bins=bins)
            
            #results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "MIC", lambda x: x)
            #results = list(map(mic_filter, results))
            #results = list(map(lambda x: fold(max, -2**16, x[1:]), results))
            #fit_normal(results, onlyLines=True, label="Drone Motors")
            
            plt.savefig('mic_dists.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # mic noize
            
            plt.title("Microphone: Value distribution Filtered vs Unfiltered")
            
            xlim = [-14000, 14000]
            bins=np.linspace(xlim[0], xlim[1], num=100)
            
            results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "MIC", lambda x: x)
            fit_normal(flatten(results), onlyLines=True, label="Unfiltered (motors on, still)", color='r', xlim=xlim, bins=bins)
            results = list(map(mic_filter, results))
            fit_normal(flatten(results), onlyLines=True, label="Filtered (motors on, still)", color='g', xlim=xlim, bins=bins)
            
            plt.savefig('mic_noize.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
            
            # Example of effect fillter
            
            plt.title("Microphone: Effect of Filter When Balloon Pops")
            
            results, ts, fs = getSignals("../../../Sound detection/", "data_formated", "MIC", lambda x: x)
            
            t = 2
            #plt.plot(results[0][:32000], label="Un Filtered", color='r')
            plt.plot(np.linspace(0, t, len(results[0][:32000])), results[0][:32000], label="Un Filtered", color='r')
            
            results = list(map(mic_filter, results))
            plt.plot(np.linspace(0, t, len(results[0][:32000])), results[0][:32000], label="Filltered", color='b')
            
            plt.savefig('mic_filter_example.png')
            plt.show()
            plt.clf()
            
            #-----------------------------------------------------------------------------------------------------------
    #mean = statistics.mean(results)
    #standard_deviation = statistics.stdev(results)
    #print(mean, standard_deviation)
    
    
    

if __name__ == "__main__":
    main()