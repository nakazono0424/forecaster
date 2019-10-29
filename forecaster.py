import numpy as np
import sqlite3 as sql
import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import jpholiday
import pandas as pd
import acf


def closestEventIndex(events, date):
    last = len(events)
    for i in range(last):
        if events[i] <= date and date <= events[i+1]:
            if date-events[i] < events[i+1]- date:
                return i
            else:
                return i+1
            
    if events[-1] < date:
        return -1
    elif date<events[0]:
        return 0



def closestEvent(events, date):
    return events[closestEventIndex(events, date)]


def getCandidates(events, rang, period):
    latest = events[-1]
    criterion = latest-datetime.timedelta(days=int(period))
    
    i=closestEventIndex(events, criterion)
    d=int((events[i+1]-events[i]).days)
    if d>365: d=365
    pivot = latest + datetime.timedelta(days=d)
    candidates=[pivot+datetime.timedelta(days=j) for j in rang]

    #candidates=[i for i in candidates if i>latest]

    return candidates

def genLM(cdv):
    nrow = len(cdv)
    col_uniq = ["月","火","水","木","金","土","日","祝"]
    ncol = len(col_uniq)
    m = np.zeros((nrow, ncol))

    for i in range(nrow):
        index = col_uniq.index(cdv.iat[i,0])
        m[i, index] = 1

    return m

def getLMAll(plist, first, last):
    days_num=(last-first).days+1
    dates = [first+datetime.timedelta(days=x) for x in range(days_num)]
    plist_alldate=getParamList(dates)
    #cols =
    LM = genLM(plist_alldate.iloc[:, [0]])
#    if len(plist_alldate) > 1:
#        for col in range(2, len(plist_alldate)):
 #           print(plist_alldate.info())
  #          LM = np.concatenate([LM, genLM(plist_alldate.iloc[:, [col]])], 1)

    return LM

def getTS(recurrence, first, last):
    days_num = (last-first).days+1
    dates=[first+datetime.timedelta(days=x) for x in range(days_num)]

    ts=np.zeros(len(dates))
    nrow=len(recurrence)
    for i in range(nrow):
        if recurrence[i] in dates:
            index = dates.index(recurrence[i])
            ts[index]=1

    return ts


def weekdays(dates):
    weekdays=["月","火","水","木","金","土","日","祝"]
    if jpholiday.is_holiday(dates.date()):
        return weekdays[7]
    else:
        return weekdays[dates.weekday()]

def monthweeks(dates):
    return (int(dates.day)-1)//7+1

def getParamList(dates):
    wdays=[weekdays(i) for i in dates]
    weeks=[monthweeks(i) for i in dates]
    months=[i.month for i in dates]
    monthdays=[i.strftime("%m-%d") for i in dates]
    #holidays=holidays(dates)
    plist=pd.DataFrame({'wdays':wdays, 'weeks':weeks, 'months':months, 'monthdays':monthdays})

    return plist

def getW(ts, LM):
    x = np.block([ts.reshape(709, 1), LM])
    a,b =np.polyfit(ts, x, 1)
    return a

def getF(candidates_plist, LM, W, candidates_date):
    cn_LM=["月","火","水","木","金","土","日","祝"]
    m = np.zeros((len(candidates_plist.index), len(cn_LM)))
    for col in candidates_plist.columns:
        for i in range(len(m)):
            if candidates_plist.at[i, col] in cn_LM:
                index= cn_LM.index(candidates_plist.at[i,col])
                m[i, index] = 1


    f = np.kron(m, W[1: -1]) + W[1]
    F = np.sum(f, axis=1)

    return F

def forecast(recurrence_range, candidates_range, events):
    #繰返し作業履歴
    first=recurrence_range[0]
    last=recurrence_range[1]
    recurrence=events
    recurrence_plist=getParamList(recurrence)

    #次の作業の候補日
    period = acf.getBigWaveCycle(recurrence, recurrence_range)
    if period==0: period=365
    
    candidates=getCandidates(recurrence, candidates_range, period)
    candidates_plist=getParamList(candidates)

    #ts = LM * W からWを求める
    # F = X  * W からFを求める
    LM = getLMAll(recurrence_plist, first, last)

    #ts = smmthingTS(ts)
    ts = getTS(recurrence, first, last)
    
    W = getW(ts, LM)

    f= getF(candidates_plist, LM, W, candidates)

    index = np.max(f)
    forecasted=candidates[int(index)]
    
    return(forecasted)


    
