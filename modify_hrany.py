import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from Spoj import Spoj
import pickle


#for i in list(range(3000,3297))+[3333]:
for i in list(range(3002,3297)):
    with open(f'C:\\railtour\\hrany\\hrany{i}.pickle', 'rb') as handle:
        seznam = pickle.load(handle)
    Brno = seznam[3000]
    for hrana in Brno:
        if hrana.prijezd.time()<=time(hour=8, minute=22):
            hrana.setPrijezd(time(hour=8, minute=22))
        elif hrana.prijezd.time()<=time(hour=20, minute=22):
            hrana.setPrijezd(time(hour=20, minute=22))
        else:
            diff = datetime.combine(hrana.prijezd.date()+timedelta(days=1),time(hour=8, minute=22))-hrana.prijezd
            hrana.setDoba(hrana.doba+diff)
    for cil,hrany in seznam.items():
        to_delete = []
        for hrana in hrany:
            if hrana.doba>timedelta(days=5):
                to_delete.append(hrana)
            hrana.prijezd = hrana.prijezd.time()
        for hrana in to_delete:
            hrany.remove(hrana)


    with open(f'C:\\Railtour\\hrany\\hrany{i}.pickle', 'wb') as handle:
        pickle.dump(seznam, handle, protocol=pickle.HIGHEST_PROTOCOL)