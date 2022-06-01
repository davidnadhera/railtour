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
from consts import active

MAX_V_ITERACI = 10000
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
USE_VYKON = True

def countVykon1(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    if doba:
        trasa.vykon = (trasa.body-penale)/doba*60.0*60.0 
    else:
        trasa.vykon = 0.0

def countVykon2(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    if doba:
        trasa.vykon = trasa.body - penale-doba/60.0/60.0 + trasa.predict_vykon
    else:
        trasa.vykon = 0.0

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

def doIterace(iterace,x):
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

    pocet = 0
    new_iterace = heapdict.heapdict()
    print(x)
    while len(iterace) and (pocet<MAX_V_ITERACI):
        pocet += 1
        ((idstanice,frozen_visited),trasa) = iterace.popitem()
        visited = set(frozen_visited)      
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
                new_visited = visited.copy()
                new_visited.add(cil)
                if (new_cas-trasa.cas > timedelta(hours=9)) or (new_cas > stan[cil]['docile']):
                    continue
                pv = 0 
                if cil in vykony:
                    klice = list(vykony[cil].keys())
                    ind = bisect.bisect_left(klice,new_cas.time())
                    if ind == len(klice):
                        klic = klice[0]
                    else:
                        klic = klice[ind]
                    pv = vykony[cil][klic]  
                new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (hrana,new_values['premie'],koef_unavy) 
                new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                                new_values['kraje'],new_hrany,countVykon,new_values['inday'],pv) 
                if ((cil,frozenset(new_visited)) not in new_iterace) or (new_iterace[(cil,frozenset(new_visited))].vykon < new_trasa.vykon):     
                    new_iterace[(cil,frozenset(new_visited))] = new_trasa
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
                    new_visited = visited.copy()
                    new_visited.add(cil)
                    if (new_cas > stan[cil]['docile']):
                        continue
                    new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                    new_hrany = trasa.hrany.copy()
                    new_hrany[cil] = (presunHrana(idstanice,nextstan,trasa.cas),new_values['premie'],koef_unavy)
                    pv = 0
                    if cil in vykony:
                        klice = list(vykony[cil].keys())
                        ind = bisect.bisect_left(klice,new_cas.time())
                        if ind == len(klice):
                            klic = klice[0]
                        else:
                            klic = klice[ind]
                        pv = vykony[cil][klic]
                    new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],\
                                                                    trasa.km + nextstan['km'],new_values['kraje'],\
                                                                        new_hrany,countVykon,new_values['inday'],pv) 
                    if ((cil,frozenset(new_visited)) not in new_iterace) or (new_iterace[(cil,frozenset(new_visited))].vykon < new_trasa.vykon):     
                        new_iterace[(cil,frozenset(new_visited))] = new_trasa
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
            new_visited = visited.copy()
            new_visited.add(SPANEK)
            new_cas = trasa.cas + timedelta(hours=6)
            if new_cas.date() > trasa.cas.date():
                new_inday = 0
                new_kraje = set()
            else:
                new_inday = trasa.inday
                new_kraje = trasa.kraje
            pv = 0
            if cil in vykony:
                klice = list(vykony[cil].keys())
                ind = bisect.bisect_left(klice,new_cas.time())
                if ind == len(klice):
                    klic = klice[0]
                else:
                    klic = klice[ind]
                pv = vykony[cil][klic]
            new_trasa = Trasa(new_cas,trasa.idstart,trasa.body + 5,\
                                                            trasa.km,new_kraje,\
                                                                new_hrany,countVykon,new_inday,pv)
            if ((idstanice,frozenset(new_visited)) not in new_iterace) or (new_iterace[(idstanice,frozenset(new_visited))].vykon < new_trasa.vykon):     
                new_iterace[(idstanice,frozenset(new_visited))] = new_trasa 
            if (idstanice in CILS) and (new_cas < CIL_DO) and (new_cas > CIL_OD) and (idstanice not in visited):
                vysledky.append(Trasa(new_cas,trasa.idstart,trasa.body + 5,\
                                                            trasa.km,new_kraje,\
                                                                new_hrany,countVykonF,new_inday,0))                                                                                           
    return new_iterace

vysledky = []


with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
if not USE_VYKON:
    vykony = {}
else:
    with open('C:\\Railtour\\hrany\\vykony3.pickle', 'rb') as handle:
        vykony = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = active
celkdoba = CIL_DO - starttime
kmsec = TOTAL_KM/celkdoba.total_seconds()
countVykon = countVykon2
koef_unavy = UNAVA

iterace = heapdict.heapdict()
iterace[(START,frozenset([START]))] = Trasa(starttime,START,0,0.0,set(),{},countVykon,0,0)
x = 0


while len(iterace):
    x += 1
    iterace = doIterace(iterace,x)

vysledky.sort(reverse=True, key=lambda x:(x.vykon,-x.km))

with open(f'C:\\Railtour\\hrany\\vysledky.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)

for x in range(1):
    trasa = vysledky[x]
    trasa.vypisHlavicku(nazvy)
#    trasa.vypisPointy(nazvy,stan)
