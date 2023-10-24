import sys
import os

os.path.basename(os.path.realpath(__file__))

args = sys.argv
args[0] = os.path.basename(os.path.realpath(args[0]))
args[1] = os.path.basename(os.path.realpath(args[1]))

with open('args.txt', 'w') as f:
    f.write(" ".join(args))