import sys, time, csv
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 2:
    sys.exit('Usage: %s path-to-your-csv-file' % sys.argv[0])

def fit_sin(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = np.std(yy) * 2.**0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * np.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w/(2.*np.pi)
    fitfunc = lambda t: A * np.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": np.max(pcov), "rawres": (guess,popt,pcov)}

adjustmentFile = sys.argv[1]

#data = []
times = []
trackingErrors = []

with open(adjustmentFile, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    next(reader, None)  # skip the headers
    for row in reader:
        t = time.strptime(row[0], "%H:%M:%S")
        seconds = timedelta(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec).total_seconds()
        error = float(row[1])
        #print "{0} {1}".format(time.strftime("%H:%M:%S", timePosition), error)
        #data.append([timePosition, error])
        times.append(seconds)
        trackingErrors.append(error)

slope, intercept, r_value, p_value, std_err = stats.linregress(times, trackingErrors)

print "slope = {0}, intercept = {1}".format(slope, intercept)

def lin(time, error):
    return error - intercept - slope * time
trackingErrorsLinearized = map(lin, times, trackingErrors)

res = fit_sin(times, trackingErrorsLinearized)
print( "Amplitude=%(amp)s, Angular freq.=%(omega)s, phase=%(phase)s, offset=%(offset)s, Max. Cov.=%(maxcov)s" % res )
print "Period {0} seconds".format(2 * np.pi / res["omega"])
print "Phase {0} seconds".format(2 * np.pi / res["phase"])



plt.plot(np.array(times), np.array(trackingErrors), "-k", label="not corrected", linewidth=1)
plt.plot(np.array(times), np.array(trackingErrorsLinearized), "-k", label="linearized")
plt.plot(np.array(times), res["fitfunc"](np.array(times)), "r-", label="y fit curve", linewidth=1)


def linsin(time, error):
    return error - res["fitfunc"](time)

trackingErrorsWithoutSin = np.array(map(linsin, times, trackingErrorsLinearized))
plt.plot(np.array(times), trackingErrorsWithoutSin, "-k", label="without sinus", linewidth=2)

plt.legend(loc="best")
plt.show()