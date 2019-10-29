import datetime
from datetime import datetime as dt
import numpy as np

def datesToOcurreds(dates, rang):
    length=int((rang[1]-rang[0]+datetime.timedelta(days=1)).days)
    occurreds = np.zeros(length, dtype=int)
    days_num=(rang[1]-rang[0]).days + 1
    
    seq_dates=[rang[0]+datetime.timedelta(days=x) for x in range(days_num)]

    for i in range(len(dates)):
        for j in range(len(seq_dates)):
            if dates[i]==seq_dates[j]:
                occurreds[j]=1

    return occurreds

def getAC(f, rang):
    start = 0
    end = int((rang[1]-rang[0]).days)

    ac = [0]*(end+1)

    for lag in range(end):
        p=f[lag:len(f)]*f[0:len(f)-lag]
        ac[lag]=np.mean(p)

    return ac

def getBigWaveCycle(dates, rang):
    upper=400
    lower=50
    series = datesToOcurreds(dates, rang)
    ac = getAC(series, rang)

    ac_order=sorted(ac, reverse=True)
    #print(ac, ac_order)
    #x = ac_order

    #ac_order=[i for i in x if x/np.max(x) > 0.1]
    ac_order=[i for i in ac_order if i < upper]
    ac_order=[i for i in ac_order if i > lower]

    if len(ac_order)==0:cycle_bigwave=0
    else:cycle_bigwave=ac_order[0]

    return cycle_bigwave

