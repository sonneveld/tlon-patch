import csv
import datetime
import os
import os.path
import sys
import time

from blake3 import blake3

'''
This was just used to dump last modified dates and checksums for future
documentation of all the game files.
'''

def hashit(fpath):
    hasher = blake3()
    with open(fpath, 'rb') as f:
        d = f.read()
    hasher.update(d)
    return hasher.hexdigest()

with open('filemeta.csv', 'wt', newline='',) as csvfile:

    fieldnames = ['path', 'modified', 'b3sum']
    csvwriter = csv.writer(csvfile, dialect='excel')
    csvwriter.writerow(fieldnames)

    # VERSIONS2 is a directory with a whole bunch of different versions of TLON I found
    os.chdir("VERSIONS2")

    for d in os.listdir():
        # print(d)
        os.chdir(d)
        for dirpath, dirnames, filenames in os.walk('.'):
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                mtime = os.path.getmtime(fpath)
                dt_utc = datetime.datetime.fromtimestamp(mtime, datetime.UTC)
                # print (mtime)
                # print (time.ctime(mtime))
                # print( datetime.datetime.fromtimestamp(mtime) )
                csvwriter.writerow( [fpath, dt_utc.astimezone(), hashit(fpath)] )

        os.chdir("..")