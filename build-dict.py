import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from Spoj import Spoj
import pickle

gvd = {}
prij = pd.read_csv('C:\\idos\\prijezdy.csv',names=['idprijezdy','cas','idvlaky','idstanice','druhyden','poradi'])
odj = pd.read_csv('C:\\idos\\odjezdy.csv',names=['idodjezdy','cas','idvlaky','idstanice','druhyden','poradi'])
for j in range(1,2978):
    Breclav = odj[odj['idstanice']==j]
    if not Breclav.empty:
        gvd[j] = {} 
        Breclav.sort_values('cas',inplace=True)
        for i, radek in Breclav.iterrows():
            akt_prij = prij[(prij['idvlaky']==radek['idvlaky']) & (prij['poradi']>radek['poradi'])]
            for index, row in akt_prij.iterrows():
                odjezd = time.fromisoformat(radek['cas'])
                prijezd = time.fromisoformat(row['cas'])
                dt1 = datetime.combine(date(2021,6,1),odjezd) + timedelta(days = int(radek['druhyden']))
                dt2 = datetime.combine(date(2021,6,1),prijezd) + timedelta(days = int(row['druhyden']))
                doba = dt2-dt1
                if not row['idstanice'] in gvd[j]:
                    gvd[j][row['idstanice']] = []
                gvd[j][row['idstanice']].append(Spoj(odjezd,radek['idvlaky'],doba))
with open('C:\\idos\\gvd.pickle', 'wb') as handle:
    pickle.dump(gvd, handle, protocol=pickle.HIGHEST_PROTOCOL)

    


