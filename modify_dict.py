import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from Spoj import Spoj
import pickle

def myFun(e):
    return datetime.combine(date(2021,6,1),e.prijezd) + timedelta(days = e.druhyden)

with open('C:\\idos\\gvd.pickle', 'rb') as handle:
    gvd = pickle.load(handle)
for i in gvd:
    for j in gvd[i]:
        gvd[i][j].sort(key=myFun)
        prev_odjezd = datetime(year=2021,month=6,day=1)
        to_remove = []
        for spoj in gvd[i][j]:
            curr_odjezd = datetime.combine(date(2021,6,1),spoj.odjezd)
            if curr_odjezd <= prev_odjezd:
                to_remove.append(spoj)
            else:
                prev_odjezd = curr_odjezd
        for spoj in to_remove:
            gvd[i][j].remove(spoj) 

for spoj in gvd[3][102]:
    print(f"Odjezd: {spoj.odjezd}, Prijezd: {spoj.prijezd}")
for spoj in gvd[98][21]:
    print(f"Odjezd: {spoj.odjezd}, Prijezd: {spoj.prijezd}")

with open('C:\\idos\\gvd_modified.pickle', 'wb') as handle:
    pickle.dump(gvd, handle, protocol=pickle.HIGHEST_PROTOCOL)