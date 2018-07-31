import sys, time, csv
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 2:
    sys.exit('Usage: %s path-to-your-csv-file' % sys.argv[0])

adjustmentFile = sys.argv[1]

data = []

with open(adjustmentFile, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        timePosition = time.strptime(row[0], "%H:%M:%S")
        error = float(row[1])
        #print "{0} {1}".format(time.strftime("%H:%M:%S", timePosition), error)
        data.append([timePosition, error])
a = np.array(data)
# x = np.float32(data)
# y = np.sin(x)
plt.plot(a[0])
plt.show()

print "done"