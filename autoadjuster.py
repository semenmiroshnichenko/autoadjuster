import numpy as np
import cv2
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
pixelScaleInArcsecPerPixel = 7.32
# pixelScaleInArcsecPerPixel = 23.4

if len(sys.argv) < 2:
    sys.exit('Usage: %s path-to-your-jpeg-files' % sys.argv[0])

directory = sys.argv[1]
files = sorted(os.listdir(directory))
previousPixelShift = 0
previousYPixelShift = 0

with open(os.path.join(directory,'results.csv'), 'wb') as csvfile:
    resultWriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    resultWriter.writerow(["Time", "Tracking error in arcsec", "Y axis shift in pixel"])
    firstFileDateTime = getImageDate(os.path.join(directory, files[0]))
    referenceImg = cv2.imread(os.path.join(directory, files[0]), cv2.IMREAD_GRAYSCALE | cv2.IMREAD_IGNORE_ORIENTATION)
    
    shape = np.shape(referenceImg)
    imageSize = min(shape[0], shape[1])
    #templateSize = min(shape[0], shape[1]) / 4
    #print "Template size {0} px".format(templateSize)


    
    for i in range(1, len(files)):
        if not files[i].lower().endswith(".jpg"): 
            continue

        fullpath = os.path.join(directory, files[i])
        fileDate = getImageDate(fullpath)
        actualImg = cv2.imread(os.path.join(directory, files[i]), cv2.IMREAD_GRAYSCALE | cv2.IMREAD_IGNORE_ORIENTATION) 

        #y = int(shape[0] / 2) - int(templateSize / 2)
        #x = int(shape[1] / 2) - int(templateSize / 2)
        #template = referenceImg[y:y + templateSize, x: x + templateSize]
        #cv2.imshow("template", cv2.resize(template, (0,0), fx=0.2, fy=0.2))
        #matchTemplateResult = cv2.matchTemplate(actualImg, template, cv2.TM_CCOEFF_NORMED)
        #minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(matchTemplateResult)
        src1np = np.float32(referenceImg)  
        src2np = np.float32(actualImg) 
        ret, response = cv2.phaseCorrelate(src1np,src2np)
        pixelShift = math.sqrt(math.pow(ret[0], 2) + math.pow(ret[1], 2))

        
        #diff = (maxLoc[0] - x, maxLoc[1] - y)
        diff = (ret[0], ret[1])
        print "matchTemplate pixel shift x:{0} y:{1}".format(diff[0], diff[1])
        #src2copy = actualImg.copy()
        #cv2.rectangle(src2copy, maxLoc, (maxLoc[0] + template.shape[0], maxLoc[1] + template.shape[1]) ,(255,255,255), 10)
        #cv2.imshow("result", cv2.resize(src2copy, (0,0), fx=0.1, fy=0.1))
        #cv2.waitKey(20)
        pixelShift = math.sqrt(math.pow(diff[0], 2) + math.pow(diff[1], 2))
        yAxisPixelShift = previousYPixelShift + diff[1]
        angleShiftInDegrees = math.degrees(math.atan(float(diff[1]) / float(diff[0])))

        angleDiff = (previousPixelShift + pixelShift) * pixelScaleInArcsecPerPixel / 3600
        timediff = fileDate - firstFileDateTime
        errorInDegrees = angleDiff - timediff.seconds * anglePerSecInArcDegrees
        print "matchTemplate at {0} tracking error {1} arcsec, Y axis shift {2} pixel".format(timediff, errorInDegrees * 3600, yAxisPixelShift)
        resultWriter.writerow([timediff, errorInDegrees * 3600, yAxisPixelShift])


        #if pixelShift > templateSize / 2:
        if pixelShift > imageSize / 4:
            referenceImg = cv2.imread(os.path.join(directory, files[i]), cv2.IMREAD_GRAYSCALE | cv2.IMREAD_IGNORE_ORIENTATION)
            previousPixelShift = previousPixelShift + pixelShift
            previousYPixelShift = yAxisPixelShift
    print 'Done!'
