import sys
import matplotlib.pyplot as plt

file1 = open(sys.argv[1], 'r')
Lines = file1.readlines()

print("lines:")
print(Lines)

x = [int(l) for l in Lines]

print("x:")
print(x)

plt.plot(x)

#plt.show()
plt.savefig('foo.png')
