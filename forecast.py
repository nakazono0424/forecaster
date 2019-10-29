#import acf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sqlite3 as sql
import datetime
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import jpholiday
import sys
import forecaster
args = sys.argv

conn = sql.connect("../db/gn.db")
c=conn.cursor()
c.execute("select distinct rec_id from event_table order by rec_id desc")
rec_id = c.fetchone()[0]
candidates_range=list(range(-3,4))

for i in range(1, rec_id+1):
    c.execute("select start_time from event_table where rec_id = {0} and date(start_time) <='{1}-03-31'".format(i, int(args[1])-1))
    events = c.fetchall()
    events=[dt.strptime(events[i][0], "%Y-%m-%d %H:%M:%S") for i in range(len(events))]
    if len(events)<=1:continue
    #print(events)
    first=events[0]
    last=events[-1]
    print("rec_id =",i)
    rec_range=(first, last)
    while True:
        forecasted=forecaster.forecast(rec_range, candidates_range, events)
        events.append(forecasted)
        if forecasted<dt(int(args[1]), 4, 1, 0, 0, 0):continue
        if forecasted>=dt(int(args[1])+1, 4, 1, 0, 0, 0):break
        print(forecasted)
#print(events[0][0])

conn.close()

