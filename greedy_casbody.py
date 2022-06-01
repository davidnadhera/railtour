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
import heapq
import random
from consts import active

MAX_V_ITERACI = 1000
IDPESKY = 9999
IDSPANEK = 9998
starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)
CILS = [3333]
CIL_OD = datetime(year=2021, month=8, day=6, hour=12, minute=0)
CIL_DO = datetime(year=2021, month=8, day=6, hour=16, minute=0)
OLOMOUC = 3333
SPANEK = 3999
START = 3333
SPANEK_OD = datetime(year=2021, month=8, day=3, hour=20, minute=0)
SPANEK_DO = datetime(year=2021, month=8, day=5, hour=2, minute=0)
TEMP_BLOCK = []
BLOCK_DO = datetime(year=2021, month=8, day=3, hour=0, minute=0)
COUNT_PREMIE = False
TOTAL_KM = 185
PENALE = 0.25
UNAVA = 0

def countVykon1(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    if doba:
        trasa.vykon = (trasa.body-penale)/doba*60.0*60.0 
    else:
        trasa.vykon = 0.0

def countVykon1R(trasa):
    countVykon1(trasa)
    trasa.vykon = round(trasa.vykon,2)

def countVykon2(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    if doba:
        trasa.vykon = trasa.body - penale-doba/60.0/60.0 + trasa.predict_vykon
    else:
        trasa.vykon = 0.0

def countVykon2R(trasa):
    countVykon1(trasa)
    trasa.vykon = round(trasa.vykon,2)

def countVykonF(trasa):
    doba = CIL_DO-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-TOTAL_KM)*PENALE)
    if doba:
        trasa.vykon = (trasa.body-penale)/doba*60.0*60.0 
    else:
        trasa.vykon = 0.0

def presunHrana(idstanice,presun,cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(presun['cas']*(1+koef_unavy))
    hrana.km = presun['km']
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = [SpojHrany(idstanice,presun['idstanicedo'],cas.time(),IDPESKY,presun['cas']*(1+koef_unavy))]
    return hrana

def spanekHrana(cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(timedelta(hours=6))
    hrana.km = 0.0
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = []
    return hrana  

def doIterace():
    def getNewValues(new_cas,prev_cas,kraje,inday,body,cil):
        druhyden = new_cas.date() > prev_cas.date()
        new_values = {}              
        if druhyden:
            new_inday = 1
            new_kraje = set() 
        else:
            new_inday = inday + 1
            new_kraje = kraje.copy()
        idkraj = stan[cil]['idkraj'] 
        if idkraj in range(2,15):
            new_kraje.add(idkraj)
        new_values['kraje'] = new_kraje
        new_values['inday'] = new_inday
        new_body = body + stan[cil]['body']
        if new_inday in [6,7,8] and (cil != OLOMOUC):
            new_body += 1
        if (len(kraje) == 3) and (len(new_kraje) == 4):
            new_body += 2
        if COUNT_PREMIE and (new_cas <= stan[cil]['dobapremie']):
            new_body += 2
            premie = 2
        elif COUNT_PREMIE and (new_cas <= stan[cil]['dobapremie2']):
            new_body += 1
            premie = 1
        else: 
            premie = 0
        new_values['body'] = new_body
        new_values['premie'] = premie
        return new_values

    (cas,body,idstanice) = heapq.heappop(poradi)
    (vykonx,listx) = iterace[(cas,body,idstanice)]
    if vykonx < 1.0:
        return
    trasa = random.choice(listx)
    print(cas)
    visited = set(trasa.hrany.keys())      
    for cil,hrany in graf[idstanice].items():
        if (cil != OLOMOUC) and (cil not in visited) and ((trasa.cas>=BLOCK_DO) or (cil not in TEMP_BLOCK)) and len(hrany):
            alt_cas = trasa.cas + koef_unavy * stan[idstanice]['presunx']
            ind = bisect.bisect_left(hrany,alt_cas.time(),key=lambda x: x.odjezd)
            if ind == len(hrany):
                hrana = hrany[0]
                new_cas = datetime.combine(alt_cas.date(),hrana.odjezd) + timedelta(days=1) + hrana.doba + koef_unavy*hrana.lastPresun
            else:
                hrana = hrany[ind]
                new_cas = datetime.combine(alt_cas.date(),hrana.odjezd) + hrana.doba + koef_unavy*hrana.lastPresun
            if (new_cas-trasa.cas > timedelta(hours=9)) or (new_cas > stan[cil]['docile']):
                continue 
            new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
            new_hrany = trasa.hrany.copy()
            new_hrany[cil] = (hrana,new_values['premie'],koef_unavy) 
            new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                            new_values['kraje'],new_hrany,countVykon,new_values['inday'],0) 
            if ((new_cas,new_values['body'],cil) not in iterace):     
                iterace[(new_cas,new_values['body'],cil)] = (new_trasa.vykon,[new_trasa])
            if ((new_cas,new_values['body'],cil) in iterace):     
                iterace[(new_cas,new_values['body'],cil)][1].append(new_trasa)
            if (new_cas,new_values['body'],cil) not in poradi:
                heapq.heappush(poradi,(new_cas,new_values['body'],cil))
        elif (cil in CILS) and (((cil not in visited)) or (cil == OLOMOUC)) and len(hrany):
            ind = bisect.bisect_left(hrany,trasa.cas.time(),key=lambda x: x.odjezd)
            if ind == len(hrany):
                hrana = hrany[0]
                new_cas = datetime.combine(trasa.cas.date(),hrana.odjezd) + timedelta(days=1) + hrana.doba
            else:
                hrana = hrany[ind]
                new_cas = datetime.combine(trasa.cas.date(),hrana.odjezd) + hrana.doba
            if (new_cas > CIL_DO) or (new_cas < CIL_OD) or (new_cas > stan[cil]['docile']):
                continue
            new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
            new_hrany = trasa.hrany.copy()
            new_hrany[cil] = (hrana,new_values['premie'],koef_unavy)
            vysledky.append(Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                            new_values['kraje'],new_hrany,countVykonF,new_values['inday'],0))

    if idstanice in pres:
        presuny = pres[idstanice]
        for nextstan in presuny:
            cil = nextstan['idstanicedo']
            if (cil != OLOMOUC) and (cil in aktivni) and (cil not in visited)  and ((trasa.cas>=BLOCK_DO) or (cil not in TEMP_BLOCK)):
                new_cas = trasa.cas+nextstan['cas']*(1+koef_unavy)
                if (new_cas > stan[cil]['docile']):
                    continue
                new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (presunHrana(idstanice,nextstan,trasa.cas),new_values['premie'],koef_unavy)
                new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],\
                                                                trasa.km + nextstan['km'],new_values['kraje'],\
                                                                    new_hrany,countVykon,new_values['inday'],0) 
                if ((new_cas,new_values['body'],cil) not in iterace):     
                    iterace[(new_cas,new_values['body'],cil)] = (new_trasa.vykon,[new_trasa])
                if ((new_cas,new_values['body'],cil) in iterace):     
                    iterace[(new_cas,new_values['body'],cil)][1].append(new_trasa)
                if (new_cas,new_values['body'],cil) not in poradi:
                    heapq.heappush(poradi,(new_cas,new_values['body'],cil))
            elif (cil in CILS) and (((cil not in visited)) or (cil == OLOMOUC)):
                new_cas = trasa.cas+nextstan['cas']*(1+koef_unavy)
                if (new_cas > CIL_DO) or (new_cas < CIL_OD) or (new_cas > stan[cil]['docile']):
                    continue
                new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (presunHrana(idstanice,nextstan,trasa.cas),new_values['premie'],koef_unavy)
                vysledky.append(Trasa(new_cas,trasa.idstart,new_values['body'],\
                                                                trasa.km + nextstan['km'],new_values['kraje'],\
                                                                    new_hrany,countVykonF,new_values['inday'],0))  
    if (SPANEK not in visited) and ((trasa.cas.time()<=time(hour=2)) or (trasa.cas.time()>=time(hour=20))) \
    and (trasa.cas<=SPANEK_DO) and (trasa.cas>=SPANEK_OD):
        new_hrany = trasa.hrany.copy()
        new_hrany[SPANEK] = (spanekHrana(trasa.cas),0,koef_unavy)
        new_cas = trasa.cas + timedelta(hours=6)
        if new_cas.date() > trasa.cas.date():
            new_inday = 0
            new_kraje = set()
        else:
            new_inday = trasa.inday
            new_kraje = trasa.kraje
        new_trasa = Trasa(new_cas,trasa.idstart,trasa.body + 5,\
                                                        trasa.km,new_kraje,\
                                                            new_hrany,countVykon,new_inday,0)
        if ((new_cas,trasa.body + 5,idstanice) not in iterace):     
            iterace[(new_cas,trasa.body + 5,idstanice)] = (new_trasa.vykon,[new_trasa])
        if ((new_cas,trasa.body + 5,idstanice) in iterace):     
            iterace[(new_cas,trasa.body + 5,idstanice)][1].append(new_trasa)
        if (new_cas,trasa.body + 5,idstanice) not in poradi:
            heapq.heappush(poradi,(new_cas,trasa.body + 5,idstanice)) 
        if (idstanice in CILS) and (new_cas < CIL_DO) and (new_cas > CIL_OD) and (idstanice not in visited):
            vysledky.append(Trasa(new_cas,trasa.idstart,trasa.body + 5,\
                                                        trasa.km,new_kraje,\
                                                            new_hrany,countVykonF,new_inday,0))                                                                                           

vysledky = []


with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = active
celkdoba = CIL_DO - starttime
kmsec = TOTAL_KM/celkdoba.total_seconds()
countVykon = countVykon1
koef_unavy = UNAVA

iterace = {}
iterace[(starttime,0,START)] = (100,[Trasa(starttime,START,0,0.0,set(),{},countVykon,0,0)])

poradi = [(starttime,0,START)]
heapq.heapify(poradi)


while len(poradi):
    doIterace()

vysledky.sort(reverse=True, key=lambda x:(x.vykon,-x.km))

with open(f'C:\\Railtour\\hrany\\vysledky.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)

for x in range(1):
    trasa = vysledky[x]
    trasa.vypisHlavicku(nazvy)
#    trasa.vypisPointy(nazvy,stan)
