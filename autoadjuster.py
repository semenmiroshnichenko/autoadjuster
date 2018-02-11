import numpy as np
import cv2
import cv
import math, os
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import csv
import sys

anglePerSecInArcDegrees = 360/86164.090530833

def getImageDate(filename):
    img = Image.open(filename)
    info = img._getexif()
    exifs = {}

    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exifs[decoded] = value
    return datetime.datetime.strptime(exifs['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")

# set this paratemer according to your objective lens and sensor you're using
pixelScaleInArcsecPerPixel = 7.29

if len(sys.argv) < 2:
    sys.exit('Usage: %s path-to-your-jpeg-files' % sys.argv[0])

directory = sys.argv[1]

files = sorted(os.listdir(directory))
firstFileDateTime = getImageDate(os.path.join(directory, files[0]))
with open(os.path.join(directory,'results.csv'), 'wb') as csvfile:
    resultWriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(1, len(files)):
        if not files[i].lower().endswith(".jpg"): 
            continue

        fullpath = os.path.join(directory, files[i])
        fileDate = getImageDate(fullpath)
        src1 = cv2.imread(os.path.join(directory, files[0]),0)
        src2 = cv2.imread(os.path.join(directory, files[i]),0) 
        src1np = np.float32(src1)  
        src2np = np.float32(src2) 
        ret = cv2.phaseCorrelate(src1np,src2np)
        
        pixelShift = math.sqrt(math.pow(ret[0], 2) + math.pow(ret[1], 2))
        angleShiftInDegrees = math.degrees(math.atan(ret[1] / ret[0]))

        angleDiff = pixelShift * pixelScaleInArcsecPerPixel / 3600
        #print angleDiff
        timediff = fileDate - firstFileDateTime
        errorInDegrees = angleDiff - timediff.seconds * anglePerSecInArcDegrees
        print "at {0} tracking error {1} arcsec, shift {2} deg".format(timediff, errorInDegrees * 3600, angleShiftInDegrees)
        resultWriter.writerow([timediff, errorInDegrees * 3600, angleShiftInDegrees])
    print 'Done!'
