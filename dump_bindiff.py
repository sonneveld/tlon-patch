
import os
import os.path
import sys


import datetime


with open(sys.argv[1], 'rb') as f:
    data0 = f.read()
with open(sys.argv[2], 'rb') as f:
    data1 = f.read()



for i in range(min(len(data0), len(data1))):

    b0 = data0[i]
    b1 = data1[i]

    if b0 != b1:
        print(hex(i), data0[i:i+1], data1[i:i+1] )

