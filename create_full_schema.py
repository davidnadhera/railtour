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

FULL = False
IDPESKY = 9999
IDSPANEK = 9998
SPANEK = 3999

aktivni = active

with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)



vysledky = []
zpracovat = []
presuny = {}
spanky = []




for start_p in graf:
    for cil_p in graf[start_p]:
        for hrana in graf[start_p][cil_p]:
            if (cil_p,hrana.prijezd) not in vysledky:
                vysledky.append((cil_p,hrana.prijezd))

if (3333,time(hour=9,minute=0)) not in vysledky:
    vysledky.append((3333,time(hour=9,minute=0)))

if (3000,time(hour=11,minute=55)) not in vysledky:
    vysledky.append((3000,time(hour=11,minute=55)))

if (3000,time(hour=23,minute=55)) not in vysledky:
    vysledky.append((3000,time(hour=23,minute=55)))

print(len(vysledky)) 
print(len(set(vysledky))) 

for (idstanice,cas) in vysledky:
    if idstanice in pres:
        for presun in pres[idstanice]:
            new_stanice = presun['idstanicedo']
            if new_stanice not in aktivni:
                continue
            new_cas = add_time(cas,presun['cas'])
            if ((new_stanice,new_cas) not in vysledky):
                zpracovat.append((new_stanice,new_cas))
                if (new_stanice,new_cas) not in presuny:
                    presuny[(new_stanice,new_cas)] = [idstanice]
                else:
                    presuny[(new_stanice,new_cas)] = []    
   

while len(zpracovat):
    (idstanice,cas) = zpracovat.pop()
    if ((idstanice,cas) not in vysledky):
        vysledky.append((idstanice,cas))
    for presun in pres[idstanice]:
        new_stanice = presun['idstanicedo']
        if new_stanice not in aktivni:
            continue
        curr_presuny = presuny[(idstanice,cas)]
        if new_stanice not in curr_presuny:
            new_cas = add_time(cas,presun['cas'])
            if ((new_stanice,new_cas) not in vysledky) or (((new_stanice,new_cas) in presuny) and (presuny[(new_stanice,new_cas)] != [])):
                zpracovat.append((new_stanice,new_cas))
                if (new_stanice,new_cas) not in presuny:
                    presuny[(new_stanice,new_cas)] = [*curr_presuny, idstanice]
                else:
                    presuny[(new_stanice,new_cas)] = []

print(len(vysledky)) 
print(len(set(vysledky))) 

for (idstanice,cas) in vysledky:
    if (cas>=time(20,0)) or (cas<=time(2,0)):
        new_cas = add_time(cas,timedelta(hours=6))
        if (idstanice,new_cas) not in vysledky:
            spanky.append((idstanice,new_cas))
 

for (idstanice,cas) in spanky:
    vysledky.append((idstanice,cas))
    if idstanice in pres:
        for presun in pres[idstanice]:
            new_stanice = presun['idstanicedo']
            if new_stanice not in aktivni:
                continue
            new_cas = add_time(cas,presun['cas'])
            if ((new_stanice,new_cas) not in vysledky) or (((new_stanice,new_cas) in presuny) and (presuny[(new_stanice,new_cas)] != [])):
                zpracovat.append((new_stanice,new_cas))
                if (new_stanice,new_cas) not in presuny:
                    presuny[(new_stanice,new_cas)] = [idstanice]
                else:
                    presuny[(new_stanice,new_cas)] = []        

print(len(vysledky)) 
print(len(set(vysledky))) 

while len(zpracovat):
    (idstanice,cas) = zpracovat.pop()
    if ((idstanice,cas) not in vysledky):
        vysledky.append((idstanice,cas))
    for presun in pres[idstanice]:
        new_stanice = presun['idstanicedo']
        if new_stanice not in aktivni:
            continue
        curr_presuny = presuny[(idstanice,cas)]
        if new_stanice not in curr_presuny:
            new_cas = add_time(cas,presun['cas'])
            if ((new_stanice,new_cas) not in vysledky) or (((new_stanice,new_cas) in presuny) and (presuny[(new_stanice,new_cas)] != [])):
                zpracovat.append((new_stanice,new_cas))
                if (new_stanice,new_cas) not in presuny:
                    presuny[(new_stanice,new_cas)] = [*curr_presuny, idstanice]
                else:
                    presuny[(new_stanice,new_cas)] = [] 

  
print(len(vysledky)) 
print(len(set(vysledky))) 

with open(f'C:\\Railtour\\hrany\\stops.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)
stops = vysledky

vysledky = {}
x=0
kmsec = 185/103/60/60
PENALE = 0.25

for (idstanice,cas) in stops:
    x+=1
    # print(x)
    sousede = {}
    if idstanice != 3334:       
        for cil,hrany in graf[idstanice].items():
            if len(hrany):
                ind = bisect.bisect_left(hrany,cas,key=lambda x: x.odjezd)
                if ind == len(hrany):
                    hrana = hrany[0]
                    new_cas = datetime.combine(date(2021,8,3),hrana.odjezd) + hrana.doba
                else:
                    hrana = hrany[ind]
                    new_cas = datetime.combine(date(2021,8,2),hrana.odjezd) + hrana.doba
                doba = new_cas-datetime.combine(date(2021,8,2),cas)
                if (doba > timedelta(hours=9)) and (not FULL):
                    continue
                penale = max(0,(hrana.km-kmsec*doba.total_seconds())*PENALE) 
                vykon = (stan[cil]['body']-penale)/doba.total_seconds()*60.0*60.0 
                sousede[cil]=(doba,hrana,vykon)

        if idstanice in pres:
            presuny = pres[idstanice]
            for nextstan in presuny:
                cil = nextstan['idstanicedo']
                if (cil in aktivni):
                    doba = nextstan['cas']

                    new_hrana = TempTrasa(datetime.combine(date(2021,8,2),cas))
                    new_hrana.setDoba(doba)
                    new_hrana.km = nextstan['km']
                    new_hrana.prijezd = new_hrana.prijezd.time()
                    new_hrana.trasa = [SpojHrany(idstanice,cil,cas,IDPESKY,doba)]
                    penale = max(0,(new_hrana.km-kmsec*doba.total_seconds())*PENALE) 
                    vykon = (stan[cil]['body']-penale)/doba.total_seconds()*60.0*60.0
                    if (cil not in sousede) or (sousede[cil][2]<vykon): 
                        sousede[cil] = (doba,new_hrana,vykon)

        if ((cas<=time(hour=2)) or (cas>=time(hour=20))):
            doba = timedelta(hours=6)
            new_hrana = TempTrasa(datetime.combine(date(2021,8,2),cas))
            new_hrana.setDoba(timedelta(hours=6))
            new_hrana.km = 0.0
            new_hrana.prijezd = new_hrana.prijezd.time()
            new_hrana.trasa = []
            sousede[SPANEK] = (doba,new_hrana,5.0/6.0)
        sousede=dict(sorted(sousede.items(), key=lambda item: item[1][2], reverse=True))
    vysledky[(idstanice,cas)] = sousede  

if not FULL:
    with open(f'C:\\Railtour\\hrany\\schema.pickle', 'wb') as handle:
        pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open(f'C:\\Railtour\\hrany\\schema_full.pickle', 'wb') as handle:
        pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)