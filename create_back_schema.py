import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
from Trasa import Trasa
import pickle
import heapdict
import bisect
from timeit import default_timer as timer
from collections import Counter
from consts import active

def add_time(cas,doba):
    den = datetime.combine(date(2021,6,1),cas)
    posun_den = den + doba
    return posun_den.time()

FULL = True
IDPESKY = 9999
IDSPANEK = 9998
SPANEK = 3999


with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open(f'C:\\Railtour\\hrany\\stops.pickle', 'rb') as handle:
    stops = pickle.load(handle)

vysledky = {}
casy = {}
x=0
aktivni = active

for (idstanice,cas) in stops:
    if idstanice not in casy:
        casy[idstanice] = []
    casy[idstanice].append(cas)

for idstanice in casy:
    casy[idstanice] = sorted(casy[idstanice])

for start in graf:
    for cil in graf[start]:
        graf[start][cil] = sorted(graf[start][cil],key=lambda x: x.prijezd) 

for (idstanice,cas) in stops:
    sousede = {}
    for start in graf:
        if idstanice in graf[start]:
            hrany = graf[start][idstanice]
            if len(hrany):
                ind = bisect.bisect_right(hrany,cas,key=lambda x: x.prijezd)
                if ind == 0:
                    hrana = hrany[-1]
                    new_cas = datetime.combine(date(2021,8,2),hrana.prijezd) - hrana.doba
                else:
                    hrana = hrany[ind-1]
                    new_cas = datetime.combine(date(2021,8,3),hrana.prijezd) - hrana.doba
                ind2 = bisect.bisect_right(casy[start],new_cas.time())
                if ind2 == 0:
                    pos_new_cas = datetime.combine(new_cas.date(),casy[start][-1]) - timedelta(days = 1)
                else:
                    pos_new_cas = datetime.combine(new_cas.date(),casy[start][ind2-1])
                doba = datetime.combine(date(2021,8,3),cas)-pos_new_cas
                if (doba > timedelta(hours=9)) and (not FULL):
                    continue
                sousede[start]=(doba,hrana,stan[cil]['body']/doba.total_seconds()*60.0*60.0)

    if idstanice in pres:
        presuny = pres[idstanice]
        for nextstan in presuny:
            start = nextstan['idstanicedo']
            if (start in aktivni):
                pres_start = [x for x in pres[start] if x['idstanicedo']==idstanice]
                pres_doba = pres_start[0]['cas']
                new_cas = datetime.combine(date(2021,8,2),cas) - pres_doba
                ind2 = bisect.bisect_right(casy[start],new_cas.time())
                if ind2 == 0:
                    pos_new_cas = datetime.combine(new_cas.date(),casy[start][-1]) - timedelta(days=1)
                else:
                    pos_new_cas = datetime.combine(new_cas.date(),casy[start][ind2-1])
                doba = datetime.combine(date(2021,8,2),cas)-pos_new_cas
                if doba.total_seconds() == 0:
                    print(start,idstanice,cas,new_cas,pos_new_cas)
                if (start not in sousede) or (sousede[start][0]>doba):
                    new_hrana = TempTrasa(datetime.combine(date(2021,8,2),pos_new_cas.time()))
                    new_hrana.setDoba(doba)
                    new_hrana.km = nextstan['km']
                    new_hrana.prijezd = new_hrana.prijezd.time()
                    new_hrana.trasa = [SpojHrany(start,idstanice,pos_new_cas.time(),IDPESKY,doba)]
                    sousede[cil] = (doba,new_hrana,stan[cil]['body']/doba.total_seconds()*60.0*60.0)

    if ((cas<=time(hour=8)) and (cas>=time(hour=2))):
        new_cas = datetime.combine(date(2021,8,2),cas)-timedelta(hours=6)
        ind2 = bisect.bisect_left(casy[idstanice],new_cas.time())
        if ind2 == 0:
            pos_new_cas = datetime.combine(new_cas.date(),casy[idstanice][-1]) - timedelta(days=1)
        else:
            pos_new_cas = datetime.combine(new_cas.date(),casy[idstanice][ind2-1])
        doba = datetime.combine(date(2021,8,2),cas)-pos_new_cas
        new_hrana = TempTrasa(datetime.combine(date(2021,8,2),pos_new_cas.time()))
        new_hrana.setDoba(timedelta(hours=6))
        new_hrana.km = 0.0
        new_hrana.prijezd = new_hrana.prijezd.time()
        new_hrana.trasa = []
        sousede[SPANEK] = (doba,new_hrana,5.0/6.0)
    sousede=dict(sorted(sousede.items(), key=lambda item: item[1][2], reverse=True))
    vysledky[(idstanice,cas)] = sousede  

if not FULL:
    with open(f'C:\\Railtour\\hrany\\backschema.pickle', 'wb') as handle:
        pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open(f'C:\\Railtour\\hrany\\backschema_full.pickle', 'wb') as handle:
        pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)