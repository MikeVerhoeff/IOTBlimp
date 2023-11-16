import os
import sys
import statistics
import numpy as np
import itertools
from scipy.stats import norm
import matplotlib.pyplot as plt
from types import ModuleType
import math

#config
hideHists = False
hideFit = False


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
        tmp = list(map(lambda vec: np.linalg.norm(vec), np.array(allValues).T))
        return list(itertools.dropwhile(lambda x: x==tmp[0], tmp))
    
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
            
            #print(dataFile)
            #print(data)
            if isinstance(result, list):
                print("list:", result[:10], "...", dataFile)
            else:
                print(result, dataFile)
            #print()
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
    
    
    if doHist and not hideHists:
        if scaleToOne:
            plt.hist(results, bins=bins, density=False, alpha=0.6, color=color, label=label, weights=0.1*np.ones_like(results))
        else:
            plt.hist(results, bins=bins, density=True, alpha=0.6, color=color, label=label)
    
    
    if scaleToOne:
        scale = std * math.sqrt(2*math.pi)
        p = p * scale
    
    if doFit and not hideFit:
        lbl = None
        if onlyLines and label != None:
            lbl=label #+" (mu = %.2f,  std = %.2f)" % (mu, std)
        alpha = 1
        if doFit and onlyLines and not doHist:
            alpha = 0.6
        if doHist and not hideHists:
            if lbl!=None:
                lbl="_"+lbl
            plt.plot(x, p, 'k', color=color, label=lbl, alpha=alpha)
        else:
            plt.plot(x, p, 'k', color=color, label=lbl, alpha=alpha)
    
    
    print(" - ", label, "Fit results: mu = %.2f,  std = %.2f" % (mu, std))
    
    if not onlyLines:
        title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
        plt.title(title)
    
    if label != None:
        leg = plt.legend(loc='upper center')
    
    if not onlyLines:
        plt.show()
    
    return (mu, std)

def plotValues(folder, file, sensor, timeOffset=0, index=0, label=None, color=None, alpha=None, plt=plt, xlim=None, ylim=None, scale=1):
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
    
    plt.plot(np.linspace(0-timeOffset, t-timeOffset, len(results)), [x * scale for x in results], label=label, alpha=alpha, color=color)

def plotInfo(title, xlabel, ylabel):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    print("----------", title, "----------")

def plotDone(file, legend=True):
    print("##############################################################")
    print()
    if not legend:
        plt.gca().get_legend().remove()
    if hideFit:
        plt.savefig("hists/"+file)
    elif hideHists:
        plt.savefig("fit/"+file)
    else:
        plt.savefig(file)
    plt.show()
    plt.clf()

def flatten(l):
    return [item for sublist in l for item in sublist]
    

def main():
    print("distrib")
    
    if len(sys.argv) < 5 and len(sys.argv) !=2:
        print("Expected atleast 4 arguments or exectly 2")
        print("usage: python distrib.py <folder> <partial expiriment name> <sensor name> <vals/max/min>")
        print("or   : python distrib.py <sensor name: PROX/PIEZO/ACC/MIC>")
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
        
            #plt.title("Proximity Balloon: Present vs Absent")
            plotInfo("Proximity Balloon: Present vs Absent", "proximity sensor value", "probability density")
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "baseline_absent", "PROX", lambda x: x)
            fit_normal(flatten(results_no_balloon), onlyLines=True, label="No Balloon", color='r', bins=list(range(256)), xlim=[-1,256])
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "gray_baseline_present", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Balloon Present", color='g', doFit=False, bins=list(range(256)), xlim=[-1,256])
            
            plotDone('prox_Present_vs_Absent.png')
            
            #-----------------------------------------------------------------------------------------------------------
        
            plotInfo("Proximity Balloon: Absent", "proximity sensor value", "probability density")
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "baseline_absent", "PROX", lambda x: x)
            fit_normal(flatten(results_no_balloon), onlyLines=True, label="No Balloon", color='r', bins=list(range(234, 256)), xlim=[234,256])
            
            plotDone('prox_Absent.png', legend=False)
            
            #-----------------------------------------------------------------------------------------------------------
            
            # IR LED FP
            #plt.title("Proximity Balloon: Absent vs IR LED")
            plotInfo("Proximity Balloon: Absent vs IR LED", "proximity sensor value", "probability density")
            
            xlim=[120,256]
            bins = list(range(xlim[0], xlim[1]))
            
            results_no_balloon, ts, fs = getSignals("../../dataProx", "baseline_absent", "PROX", lambda x: x)
            fit_normal(flatten(results_no_balloon), onlyLines=True, label="No Balloon", color='r', bins=bins, xlim=xlim)
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "gray_IR_LED_direct_full", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Bright IR LED (Balloon Present)", color='b', doFit=False, bins=bins, xlim=xlim)
            
            results_balloon_present, ts, fs = getSignals("../../dataProx", "IR_LED_direct_under_powered", "PROX", lambda x: x)
            fit_normal(flatten(results_balloon_present), onlyLines=True, label="Dim IR LED (Balloon Absent)", color='orange', doFit=False, bins=bins, xlim=xlim)
            
            plotDone('prox_Absent_vs_IR_LED.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX stick
            #plt.title("Proximity Balloon: Present vs Weaving Object (maximal value in 10 runs)")
            plotInfo("Proximity Balloon: Present vs Weaving Object", "maximal value in each repeat", "probability density")
            
            bins = np.linspace(0, 255, num=10)
            xlim=[-1,256]
            
            results1, ts, fs = getSignals("../../dataProx", "gray_stick", "PROX", lambda x: fold(max, 0, x[1:]))
            results2, ts, fs = getSignals("../../fp", "stick", "PROX", lambda x: fold(max, 0, x[1:]))
            results3, ts, fs = getSignals("../../fp", "scissor", "PROX", lambda x: fold(max, 0, x[1:]))
            results4, ts, fs = getSignals("../../fp", "permanent_marker", "PROX", lambda x: fold(max, 0, x[1:]))
            results4, ts, fs = getSignals("../../fp", "black_plastic", "PROX", lambda x: fold(max, 0, x[1:]))
            results = results1+results2+results3+results4
            fit_normal(results, onlyLines=True, label="Balloon Present, weaving object above sensor", color='m', doFit=False, bins=bins, xlim=xlim)
            
            print()
            print("max values:", results)
            print()
            
            results, ts, fs = getSignals("../../dataProx", "gray_baseline_present", "PROX", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Balloon Present", color='g', doFit=False, bins=bins, xlim=xlim)
            
            plotDone('prox_Present_vs_Weaving_Object.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX Examples
            #plt.title("Proximity Balloon: Examples of popping")
            
            
            zero = 0.36
            alpha = 0.7
            
            results_pop1, ts, fs = getSignals("../../pop", "all_(1)", "PROX", lambda x: x)
            results_pop1 = results_pop1[0]
            t1=ts[0]
            results_pop2, ts, fs = getSignals("../../pop", "all_(7)", "PROX", lambda x: x)
            results_pop2 = results_pop2[0]
            t2=ts[0]
            results_pop3, ts, fs = getSignals("../../pop", "all_(8)", "PROX", lambda x: x)
            results_pop3 = results_pop3[0]
            t3=ts[0]
            
            plotInfo("Proximity Balloon: Examples of popping", "time (s)", "proximity sensor value")
            
            plt.plot(np.linspace(0-zero, t1-zero, len(results_pop1)), results_pop1, label="Proximity", alpha=alpha, color='blue')
            plt.plot(np.linspace(-0.285-zero, t2-0.285-zero, len(results_pop2)), results_pop2, label="Proximity", alpha=alpha, color='orange')
            plt.plot(np.linspace(-0.075-zero, t3-0.075-zero, len(results_pop3)), results_pop3, label="Proximity", alpha=alpha, color='green')
            
            plotDone('prox_Examples_pop.png')
            
            plotInfo("Proximity Balloon: Example 1 of popping", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(0-zero, t1-zero, len(results_pop1)), results_pop1, label="Proximity", alpha=alpha, color='blue')
            plotDone('prox_Example_pop_1.png')
            
            plotInfo("Proximity Balloon: Example 2 of popping", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(-0.285-zero, t2-0.285-zero, len(results_pop2)), results_pop2, label="Proximity", alpha=alpha, color='orange')
            plotDone('prox_Example_pop_2.png')
            
            plotInfo("Proximity Balloon: Example 3 of popping", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(-0.075-zero, t3-0.075-zero, len(results_pop3)), results_pop3, label="Proximity", alpha=alpha, color='green')
            plotDone('prox_Example_pop_3.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX Examples : marker
            plotInfo("Proximity Balloon: Example of whiteboard marker interfearing", "time (s)", "proximity sensor value")
            
            zero = 0.36
            alpha = 0.7
            
            results_no_balloon, ts, fs = getSignals("../../fp", "permanent_marker_(2)", "PROX", lambda x: x)
            results_no_balloon = results_no_balloon[0]
            print(fs, ts)
            f = fs[0]
            t = ts[0]
            plt.plot(np.linspace(0-zero, t-zero, len(results_no_balloon)), results_no_balloon, label="Proximity", alpha=alpha, color='blue')
            
            
            plotDone('prox_Examples_marker.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PROX Responce to mirror
            
            #plt.title("Proximity Balloon: Raise and Lower")
            plotInfo("Proximity Balloon: Raise and Lower", "time (s)", "proximity sensor value")
            
            alpha = 0.7
            
            results_red, ts, fs = getSignals("../../fp_tests", "fp_red_(6)", "PROX", lambda x: x)
            results_red = results_red[0]
            t_red = ts[0]
            results_te, ts, fs = getSignals("../../fp_tests", "fp_transparent_edge_(5)", "PROX", lambda x: x)
            results_te = results_te[0]
            t_te = ts[0]
            results_m, ts, fs = getSignals("../../fp_tests", "fp_mirror_angle_(7)", "PROX", lambda x: x)
            results_m = results_m[0]
            t_m = ts[0]
            
            plotInfo("Proximity Balloon: Raise and Lower", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(0, t_red, len(results_red)), results_red, label="Red Balloon", alpha=alpha, color='blue')
            plt.plot(np.linspace(0+0.08, t_te+0.08, len(results_te)), results_te, label="Edge of transparent Balloon", alpha=alpha, color='orange')
            plt.plot(np.linspace(0, t_m, len(results_m)), results_m, label="Mirror at 45 degrees", alpha=alpha, color='green')
            leg = plt.legend(loc='lower center')
            plotDone('prox_Raise_and_lower.png')
            
            plotInfo("Proximity Balloon: Raise and Lower", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(0, t_red, len(results_red)), results_red, label="Red Balloon", alpha=alpha, color='blue')
            leg = plt.legend(loc='lower center')
            plotDone('prox_Raise_and_lower_red.png')
            
            plotInfo("Proximity Balloon: Raise and Lower", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(0+0.08, t_te+0.08, len(results_te)), results_te, label="Edge of transparent Balloon", alpha=alpha, color='orange')
            leg = plt.legend(loc='lower center')
            plotDone('prox_Raise_and_lower_trans.png')
            
            plotInfo("Proximity Balloon: Raise and Lower", "time (s)", "proximity sensor value")
            plt.plot(np.linspace(0, t_m, len(results_m)), results_m, label="Mirror at 45 degrees", alpha=alpha, color='green')
            leg = plt.legend(loc='lower center')
            plotDone('prox_Raise_and_lower_mirror.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
        elif sys.argv[1] == "PIEZO":
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO Effect of Parallel Resistance
            
            fig, (ax1, ax2, ax3) = plt.subplots(3)
            fig.suptitle("Piezo: Effect of Parallel Resistance")
            plt.xlabel("time (s)")
            plt.ylabel("voltage")
            #plt.yscale(3.3/1024)
            fig.tight_layout()
            
            xlim = [-0.2, 0.6]
            ylim = [0, 3.3]
            
            plotValues("../../dataPartyBalloonPiezo/50K-PiozoHard-tapenormal",  "PiezoH_pop_(3)", "PIEZO", plt=ax1, timeOffset=0.57, label="50K Ohm",  xlim=xlim, ylim=ylim, scale=3.3/1024)
            plotValues("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop_(2)", "PIEZO", plt=ax2, timeOffset=0.77, label="100K Ohm", xlim=xlim, ylim=ylim, scale=3.3/1024)
            plotValues("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_1M_pop",  "PIEZO", plt=ax3, timeOffset=0.4,  label="1M Ohm",   xlim=xlim, ylim=ylim, scale=3.3/1024)
            
            plotDone('piezo_Parallel_Resistance.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO still vs vibration
            
            plotInfo("Piezo: Maximal Value From 10 Runs: Still vs Vibrations", "sensor value", "probability density")
            
            xlim = [0, 17]
            bins = list(range(0,18))
            
            results1, ts, fs = getSignals("../../dataPiezo", "still", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results2, ts, fs = getSignals("../../dataPiezo", "vibration_dremel_5t", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results3, ts, fs = getSignals("../../fp_tests", "baseline_motor", "PIEZO", lambda x: fold(max, 0, x[1:]))
            
            fit_normal(results1, onlyLines=True, label="Drone Motors Off",                color='g', doFit=True, xlim=xlim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Drone Motors On",         color='r', doFit=True, xlim=xlim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Rotary Tool 5000 RPM", color='b', doFit=True, xlim=xlim, bins=bins)
            
            plotDone('piezo_vibration.png')
            
            plotInfo("Piezo: Drone Motors Off", "maximal sensor value per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Drone Motors Off",     color='g', doFit=True, xlim=xlim, bins=bins)
            plotDone('piezo_Motors_off.png')
            
            plotInfo("Piezo: Rotary Tool 5000 RPM", "maximal sensor value per run", "probability density")
            fit_normal(results2, onlyLines=True, label="Rotary Tool 5000 RPM", color='b', doFit=True, xlim=xlim, bins=bins)
            plotDone('piezo_5k_rpm.png')
            
            plotInfo("Piezo: Drone Motors On", "maximal sensor value per run", "probability density")
            fit_normal(results3, onlyLines=True, label="Drone Motors On",      color='r', doFit=True, xlim=xlim, bins=bins)
            plotDone('piezo_Motors_on.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO dists scaled
            
            plotInfo("Piezo: Book Hits", "maximal sensor value per run", "probability density")
            
            alpha = 0.6
            xlim = [-20, 120]
            bins = list(range(-20,121, 5))
            
            results1, ts, fs = getSignals("../../dataPiezo", "still", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results2, ts, fs = getSignals("../../fp_tests", "fp_bookface_soft", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results3, ts, fs = getSignals("../../fp_tests", "fp_bookside_non",  "PIEZO", lambda x: fold(max, 0, x[1:]))
            results4, ts, fs = getSignals("../../fp_tests", "fp_bookside_on",   "PIEZO", lambda x: fold(max, 0, x[1:]))
            
            fit_normal(results1, onlyLines=True, label="Drone Motors Off",       color='g',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Bookface Soft",          color='r',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Bookside not on Sensor", color='orange', ylim=[0, 0.15], xlim=xlim, bins=bins)
            fit_normal(results4, onlyLines=True, label="Bookside on Sensor",     color='blue',   ylim=[0, 0.15], xlim=xlim, bins=bins)
            
            plt.legend(loc='upper right')
            
            plotDone('piezo_book.png')
            
            plotInfo("Piezo: Book Hits", "maximal sensor value per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Drone Motors Off",       color='g',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            plt.legend(loc='upper right')
            plotDone('piezo_Motors_off_2.png')
            
            
            plotInfo("Piezo: Book Hits", "maximal sensor value per run", "probability density")
            fit_normal(results2, onlyLines=True, label="Bookface Soft",          color='r',      ylim=[0, 0.15], xlim=xlim, bins=bins)
            plt.legend(loc='upper right')
            plotDone('piezo_bookface_soft.png')
            
            
            plotInfo("Piezo: Book Hits", "maximal sensor value per run", "probability density")
            fit_normal(results3, onlyLines=True, label="Bookside not on Sensor", color='orange', ylim=[0, 0.15], xlim=xlim, bins=bins)
            plt.legend(loc='upper right')
            plotDone('piezo_bookside_not_on.png')
            
            
            plotInfo("Piezo: Book Hits", "maximal sensor value per run", "probability density")
            fit_normal(results4, onlyLines=True, label="Bookside on Sensor",     color='blue',   ylim=[0, 0.15], xlim=xlim, bins=bins)
            plt.legend(loc='upper right')
            plotDone('piezo_bookside_on.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO hit position
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            
            ylim = [0, 0.018]
            xlim = [0,1023]
            bins = np.bins = np.linspace(xlim[0], xlim[1], num=25)
            
            results1, ts, fs = getSignals("../../dataPiezo", "nerf_disk_side", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results2, ts, fs = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results3, ts, fs = getSignals("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop", "PIEZO", lambda x: fold(max, 0, x[1:]))
            
            results4a, ts, fs = getSignals("../../pop", "piezo", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results4b, ts, fs = getSignals("../../pop", "all", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results4b.pop(2) # 14
            #results4b.pop(8) # 8
            #results4b.pop(6) # 6
            results4c, ts, fs = getSignals("../../pop", "fusion", "PIEZO", lambda x: fold(max, 0, x[1:]))
            results4 = results4a+results4b+[results4c[0], results4c[1]]
            
            print()
            print(results4)
            print()
            
            
            fit_normal(results1, onlyLines=True, label="Nerf Vortex Disk Hit, side",            color='orange', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Small Balloon Popping (4 runs)",        color='purple', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            #fit_normal(results4, onlyLines=True, label="Big Balloon Popping (Sensor degradating)", color='blue', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            
            
            plotDone('piezo_nerf.png')
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Nerf Vortex Disk Hit, side",            color='orange', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Small Balloon Popping (4 runs)",        color='purple', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            fit_normal(results4, onlyLines=True, label="Big Balloon Popping (Sensor degradating)", color='blue', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            plotDone('piezo_nerf_plus_big.png')
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Nerf Vortex Disk Hit, side",            color='orange', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            plotDone('piezo_nerf_side.png')
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            fit_normal(results2, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            plotDone('piezo_nerf_on.png')
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            fit_normal(results3, onlyLines=True, label="Small Balloon Popping (4 runs)",        color='purple', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            plotDone('piezo_nerf_small.png')
            
            plotInfo("Piezo: Hitting ballon in diffrent positions", "maximal sensor value per run", "probability density")
            fit_normal(results4, onlyLines=True, label="Big Balloon Popping (Sensor degradating)", color='blue', doFit=True, xlim=xlim, ylim=ylim, bins=bins)
            plotDone('piezo_nerf_big.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # PIEZO dists scaled
            
            plotInfo("Piezo: Distributions Scaled to Same Hieght", "maximal sensor value per run", "")
            
            alpha = 0.6
            xlim = [0,1023]
            bins = np.bins = np.linspace(xlim[0], xlim[1], num=25)
            
            results, ts, fs = getSignals("../../dataPiezo", "still",           "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Drone Motors Off",                      color='g',      doHist=True, doFit=True, scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../fp_tests", "baseline_motor",   "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Drone Motors On",                       color='b',      doHist=True, doFit=True, scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_disk_side",  "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit",                  color='orange', doHist=True, doFit=True, scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPiezo", "nerf_direct_hit", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Nerf Vortex Disk Hit, close to sensor", color='r',      doHist=True, doFit=True, scaleToOne=True, xlim=xlim, bins=bins)
            
            results, ts, fs = getSignals("../../dataPartyBalloonPiezo/100K-PiozoHard-tapenormal", "PiezoH_pop", "PIEZO", lambda x: fold(max, 0, x[1:]))
            fit_normal(results, onlyLines=True, label="Small Balloon Popping",                 color='purple', doHist=True, doFit=True, scaleToOne=True, xlim=xlim, bins=bins)
            
            plotDone('piezo_Scaled.png')
            
            #-----------------------------------------------------------------------------------------------------------
        
        elif sys.argv[1] == "ACC":
            
            #-----------------------------------------------------------------------------------------------------------
            
            # ACC movement
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
           
            xlim=[0.6, 1]
            bins=np.linspace(xlim[0], xlim[1], num=40)
            
            results1, ts, fs = getSignals("../../acc",      "fp_1ms_side",    "ACC", lambda x: fold(min, 2**32, x[1:]))
            results2, ts, fs = getSignals("../../acc",      "fp_1ms_up_down", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results3, ts, fs = getSignals("../../fp_tests", "baseline_motor", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results4, ts, fs = getSignals("../../fp_tests", "fp_bookface",    "ACC", lambda x: fold(min, 2**32, x[1:]))
            results5, ts, fs = getSignals("../../fp_tests", "fp_bookside",    "ACC", lambda x: fold(min, 2**32, x[1:]))
            results6, ts, fs = getSignals("../../fp_tests", "fp_book",        "ACC", lambda x: fold(min, 2**32, x[1:]))
            results7, ts, fs = getSignals("../../fp_tests", "fp_nerf",        "ACC", lambda x: fold(min, 2**32, x[1:]))
            
            fit_normal(results1, onlyLines=True, label="Moving Side to Side (+/- 1 m/s)",  color='orange', doFit=True, xlim=xlim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Drone Motors on, Still",           color='purple', doFit=True, xlim=xlim, bins=bins)
            #fit_normal(results4, onlyLines=True, label="Hit with Face of Book",            color='green', doFit=True, xlim=xlim, bins=bins)
            #fit_normal(results5, onlyLines=True, label="Hit with Side of Book",            color='blue', doFit=True, xlim=xlim, bins=bins)
            fit_normal(results6, onlyLines=True, label="Hit with a Book",            color='green', doFit=True, xlim=xlim, bins=bins)
            #fit_normal(results7, onlyLines=True, label="Hit a Neft Disk",            color='yellow', doFit=True, xlim=xlim, bins=bins)
            
            plt.legend(loc='upper left')
            
            plotDone('acc_move.png')
            
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Moving Side to Side (+/- 1 m/s)",  color='orange', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_ss.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results2, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_ud.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results3, onlyLines=True, label="Drone Motors on, Still",           color='purple', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_mon.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results4, onlyLines=True, label="Hit with Face of Book",            color='green', doFit=True, xlim=[0.3, 1], bins=70)
            plt.legend(loc='upper left')
            plotDone('acc_move_book_face.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results5, onlyLines=True, label="Hit with Side of Book",            color='blue', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_book_side.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results6, onlyLines=True, label="Hit with a Book",            color='green', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_book.png')
            
            plotInfo("Accelerometer: Movement", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results7, onlyLines=True, label="Hit a Neft Disk",            color='yellow', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_move_nerf.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # ACC pop
            
            plotInfo("Accelerometer: Pop", "minimum length of measured acceleration vector per run", "probability density")
           
            xlim=[-0.1, 1.1]
            bins=np.linspace(xlim[0], xlim[1], num=50)
            
            results1, ts, fs = getSignals("../../acc", "fp_1ms_up_down", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results2, ts, fs = getSignals("../../fp_tests", "baseline_motor", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results3, ts, fs = getSignals("../../pop", "all", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results3.pop(2) #14 -> did not fall/stationary on table
            results3b, ts, fs = getSignals("../../pop", "fusion", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results3c, ts, fs = getSignals("../../pop", "acc", "ACC", lambda x: fold(min, 2**32, x[1:]))
            results3 = results3+results3b+results3c
            
            fit_normal(results1, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            fit_normal(results2, onlyLines=True, label="Drone Motors on, stationary",           color='purple', doFit=True, xlim=xlim, bins=bins)
            fit_normal(results3, onlyLines=True, label="Balloon pop",           color='blue', doFit=True, xlim=xlim, bins=bins)
            
            plt.legend(loc='upper left')
            
            plotDone('acc_pop.png')
            
            plotInfo("Accelerometer: Pop", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results1, onlyLines=True, label="Moving Up and Down (+/- 1 m/s)",   color='r',      doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_pop_ud.png')
            
            plotInfo("Accelerometer: Pop", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results2, onlyLines=True, label="Drone Motors on, stationary",           color='purple', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_pop_mon.png')
            
            plotInfo("Accelerometer: Pop", "minimum length of measured acceleration vector per run", "probability density")
            fit_normal(results3, onlyLines=True, label="Balloon pop",           color='blue', doFit=True, xlim=xlim, bins=bins)
            plt.legend(loc='upper left')
            plotDone('acc_pop_pop.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
        elif sys.argv[1] == "MIC":
            
            #-----------------------------------------------------------------------------------------------------------
            
            # MIC pop
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            
            #todo: add new ones
            
            xlim = [-1000, 14000]
            bins=np.linspace(xlim[0], xlim[1], num=30)
            ylim = [0, 0.002]
            
            #results, ts, fs = getSignals("../../fp_tests", "fp_1m", "MIC", lambda x: x)
            #results = list(map(mic_filter, results))
            #results = list(map(lambda x: fold(max, -2**16, x[1:]), results))
            #fit_normal(results, onlyLines=True, label="pop at 1m")
            
            results1, ts, fs = getSignals("../../dataMic", "still_filtered",     "MIC", lambda x: fold(max, -2**16, x[1:]))
            results2, ts, fs = getSignals("../../dataMic", "300hz_filtered",     "MIC", lambda x: fold(max, -2**16, x[1:]))
            results3, ts, fs = getSignals("../../dataMic", "150cm_pop_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            results3b, ts, fs = getSignals("../../fp",     "150cm_pop_filtered", "MIC", lambda x: fold(max, -2**16, x[1:]))
            results3 = results3+results3b
            results4, ts, fs = getSignals("../../dataMic", "30cm_pop_filtered",  "MIC", lambda x: fold(max, -2**16, x[1:]))
            results4b, ts, fs = getSignals("../../fp",     "30cm_pop_filtered",  "MIC", lambda x: fold(max, -2**16, x[1:]))
            results4 = results4+results4b
            
            fit_normal(results1, onlyLines=True, label="stationary (motors off)", color='b', scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            fit_normal(results2, onlyLines=True, label="300Hz tone",         color='g',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            fit_normal(results3, onlyLines=True, label="pop ballon @ 150cm", color='orange', scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            fit_normal(results4, onlyLines=True, label="pop ballon @ 40cm",  color='r',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            
            pop_results = []
            results, ts, fs = getSignals("../../pop", "all", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])#
            results, ts, fs = getSignals("../../pop", "all_(2)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])
            results, ts, fs = getSignals("../../pop", "all_(3)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])#
            results, ts, fs = getSignals("../../pop", "all_(4)", "MIC", lambda x: fold(max, -2**16, x[1:]))
            pop_results.append(results[0])#
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
            fit_normal(pop_results, onlyLines=True, label="pop own ballon (motor on)",  color='purple',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            
            #results, ts, fs = getSignals("../../fp_tests", "baseline_motor", "MIC", lambda x: x)
            #results = list(map(mic_filter, results))
            #results = list(map(lambda x: fold(max, -2**16, x[1:]), results))
            #fit_normal(results, onlyLines=True, label="Drone Motors")
            
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            
            plotDone('mic_dists.png')
            
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            fit_normal(results1, onlyLines=True, label="stationary (motors off)", color='b', scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            plotDone('mic_dists_still.png')
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            fit_normal(results2, onlyLines=True, label="300Hz tone",         color='g',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            plotDone('mic_dists_300hz.png')
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            fit_normal(results3, onlyLines=True, label="pop ballon @ 150cm", color='orange', scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            plotDone('mic_dists_150.png')
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            fit_normal(results4, onlyLines=True, label="pop ballon @ 40cm",  color='r',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            plotDone('mic_dists_40.png')
            
            plotInfo("Microphone: Pop Balloon at Diffrent Distances", "maximal microphone value", "probebility (‰)")
            fit_normal(pop_results, onlyLines=True, label="pop own ballon (motor on)",  color='purple',      scaleToOne=False, xlim=xlim, bins=bins, ylim=ylim)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([str(x*10**3) for x in y_vals])
            plotDone('mic_dists_pop.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # mic noize
            
            plotInfo("Microphone: Value distribution Filtered vs Unfiltered", "maximal microphone value", "probebility (‰)")
            
            xlim = [-14000, 14000]
            bins=np.linspace(xlim[0], xlim[1], num=100)
            
            results1, ts, fs = getSignals("../../fp_tests", "baseline_motor", "MIC", lambda x: x)
            results2 = list(map(mic_filter, results1))
            
            fit_normal(flatten(results1), onlyLines=True, label="Unfiltered motor noise", color='r', xlim=xlim, bins=bins)
            fit_normal(flatten(results2), onlyLines=True, label="Filtered motor noise", color='g', xlim=xlim, bins=bins)
            
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels(['{:3.1f}'.format(x*10**3) for x in y_vals])
            
            plotDone('mic_noize.png')
            
            
            plotInfo("Microphone: Value distribution Filtered vs Unfiltered", "maximal microphone value", "probebility (‰)")
            fit_normal(flatten(results1), onlyLines=True, label="Unfiltered motor noise", color='r', xlim=xlim, bins=bins)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels(['{:3.1f}'.format(x*10**3) for x in y_vals])
            plotDone('mic_noize_unfiltered.png')
            
            plotInfo("Microphone: Value distribution Filtered vs Unfiltered", "maximal microphone value", "probebility (‰)")
            fit_normal(flatten(results2), onlyLines=True, label="Filtered motor noise", color='g', xlim=xlim, bins=bins)
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels(['{:3.1f}'.format(x*10**3) for x in y_vals])
            plotDone('mic_noize_filtered.png')
            
            #-----------------------------------------------------------------------------------------------------------
            
            # Example of effect fillter
            
            plotInfo("Microphone: Effect of Filter When Balloon Pops", "time (s)", "microphone value")
            
            results1, ts, fs = getSignals("../../../Sound detection/", "data_formated", "MIC", lambda x: x)
            results2 = list(map(mic_filter, results1))
            
            t = 2
            
            plt.plot(np.linspace(0, t, len(results1[0][:32000])), results1[0][:32000], label="Un Filtered", color='r')
            plt.plot(np.linspace(0, t, len(results2[0][:32000])), results2[0][:32000], label="Filltered", color='b')
            
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([('{:3.0f}K'.format(x/10**3) if x!=0 else '0') for x in y_vals])
            
            plotDone('mic_filter_example.png')
            
            
            plotInfo("Microphone: Effect of Filter When Balloon Pops", "time (s)", "microphone value")
            plt.plot(np.linspace(0, t, len(results1[0][:32000])), results1[0][:32000], label="Un Filtered", color='r')
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([('{:3.0f}K'.format(x/10**3) if x!=0 else '0') for x in y_vals])
            plotDone('mic_filter_example_unfiltred.png')
            
            plotInfo("Microphone: Effect of Filter When Balloon Pops", "time (s)", "microphone value")
            plt.plot(np.linspace(0, t, len(results2[0][:32000])), results2[0][:32000], label="Filltered", color='b')
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([('{:3.0f}K'.format(x/10**3) if x!=0 else '0') for x in y_vals])
            plotDone('mic_filter_example_filtred.png')
            
            
            #-----------------------------------------------------------------------------------------------------------
            
            plotInfo("Microphone: Pop Spectrogram", "time (s)", "frequency")
            
            results, ts, fs = getSignals("../../../Sound detection/", "data_formated", "MIC", lambda x: x)
            t = 2
            result = results[0][:32000]
            
            plt.specgram(result, NFFT=1024, Fs=16000)
            
            y_vals = plt.gca().get_yticks()
            plt.gca().set_yticklabels([('{:3.0f}KHz'.format(x/10**3) if x!=0 else '0KHz') for x in y_vals])
            
            plotDone('mic_spectrogram.png')
            
            #-----------------------------------------------------------------------------------------------------------
    #mean = statistics.mean(results)
    #standard_deviation = statistics.stdev(results)
    #print(mean, standard_deviation)
    
    
    

if __name__ == "__main__":
    main()