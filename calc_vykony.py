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

MAX_V_ITERACI = 1000
IDPESKY = 9999
OLOMOUC = 3333
SPANEK = 3999
#starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)
TOTAL_KM = 185
PENALE = 0.25

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
        trasa.vykon = trasa.body-penale-doba/60.0/60.0 
    else:
        trasa.vykon = 0.0


def presunHrana(idstanice,presun,cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(presun['cas'])
    hrana.km = presun['km']
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = [SpojHrany(idstanice,presun['idstanicedo'],cas.time(),IDPESKY,presun['cas'])]
    return hrana

def spanekHrana(cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(timedelta(hours=6))
    hrana.km = 0.0
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = []
    return hrana  

def doIterace(iterace,x):
    def getNewValues(visited,new_cas,prev_cas,kraje,inday,body,cil):
        druhyden = new_cas.date() > prev_cas.date()
        new_values = {}
        new_visited = visited.copy()
        new_visited.add(cil)
        new_values['visited'] = new_visited               
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
        new_values['body'] = new_body
        new_values['premie'] = 0
        return new_values

    pocet = 0
    new_iterace = heapdict.heapdict()
    print(x)
    while len(iterace) and (pocet<MAX_V_ITERACI):
        pocet += 1
        ((idstanice,frozen_visited),trasa) = iterace.popitem()
        visited = set(frozen_visited)        
        for cil,hrany in graf[idstanice].items():
            if (cil not in visited) and len(hrany):
                alt_cas = trasa.cas
                ind = bisect.bisect_left(hrany,alt_cas.time(),key=lambda x: x.odjezd)
                if ind == len(hrany):
                    hrana = hrany[0]
                    new_cas = datetime.combine(alt_cas.date(),hrana.odjezd) + timedelta(days=1) + hrana.doba
                else:
                    hrana = hrany[ind]
                    new_cas = datetime.combine(alt_cas.date(),hrana.odjezd) + hrana.doba
                if (new_cas-trasa.cas > timedelta(hours=9)) or (new_cas > stan[cil]['docile']):
                    continue
                new_values = getNewValues(visited,new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (hrana,new_values['premie'])
                new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                                new_values['kraje'],new_hrany,countVykon,new_values['inday']) 
                if ((cil,frozenset(new_values['visited'])) not in new_iterace) or (new_iterace[(cil,frozenset(new_values['visited']))].vykon < new_trasa.vykon):     
                    new_iterace[(cil,frozenset(new_values['visited']))] = new_trasa

        if idstanice in pres:
            presuny = pres[idstanice]
            for nextstan in presuny:
                cil = nextstan['idstanicedo']
                if (cil in aktivni) and (cil not in visited):
                    new_cas = trasa.cas+nextstan['cas']
                    if (new_cas > stan[cil]['docile']):
                        continue
                    new_values = getNewValues(visited,new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                    new_hrany = trasa.hrany.copy()
                    new_hrany[cil] = (presunHrana(idstanice,nextstan,trasa.cas),new_values['premie'])
                    new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],\
                                                                    trasa.km + nextstan['km'],new_values['kraje'],\
                                                                        new_hrany,countVykon,new_values['inday']) 
                    if ((cil,frozenset(new_values['visited'])) not in new_iterace) or (new_iterace[(cil,frozenset(new_values['visited']))].vykon < new_trasa.vykon):     
                        new_iterace[(cil,frozenset(new_values['visited']))] = new_trasa
        if (SPANEK not in visited) and ((trasa.cas.time()<=time(hour=2)) or (trasa.cas.time()>=time(hour=20))):
            new_hrany = trasa.hrany.copy()
            new_hrany[SPANEK] = (spanekHrana(trasa.cas),0)
            new_visited = visited.copy()
            new_visited.add(SPANEK)
            new_cas = trasa.cas + timedelta(hours=6)
            if new_cas.date() > trasa.cas.date():
                new_inday = 0
                new_kraje = set()
            else:
                new_inday = trasa.inday
                new_kraje = trasa.kraje
            new_trasa = Trasa(new_cas,trasa.idstart,trasa.body + 5,\
                                                            trasa.km,new_kraje,\
                                                                new_hrany,countVykon,new_inday)
            if ((idstanice,frozenset(new_visited)) not in new_iterace) or (new_iterace[(idstanice,frozenset(new_visited))].vykon < new_trasa.vykon):     
                new_iterace[(idstanice,frozenset(new_visited))] = new_trasa                                                                                            
    return new_iterace

vysledky = {}


with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = active
kmsec = TOTAL_KM/103.0/60.0/60.0
countVykon = countVykon2

for start_p in graf:
    for cil_p in graf[start_p]:
        print(start_p,cil_p)
        hrany = graf[start_p][cil_p]
        for hrana in hrany:
            if (cil_p not in vysledky) or (hrana.prijezd not in vysledky[cil_p]):
                starttime = datetime.combine(datetime(year=2021, month=8, day=2),hrana.prijezd)
                iterace = heapdict.heapdict()
                iterace[(cil_p,frozenset([cil_p]))] = Trasa(starttime,cil_p,0,0.0,set(),{},countVykon,0)
                x = 0

                while x < 3:
                    x += 1
                    if len(iterace):
                        iterace = doIterace(iterace,x)

                if cil_p not in vysledky:
                    vysledky[cil_p] = {}

                if len(iterace):
                    ((idstanice,frozen_visited),trasa) = iterace.popitem()
                    vysledky[cil_p][hrana.prijezd] = trasa.vykon
                else:
                    vysledky[cil_p][hrana.prijezd] = -100

for bod in vysledky:
    vysledky[bod] = dict(sorted(vysledky[bod].items()))


with open(f'C:\\Railtour\\hrany\\vykony3.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)
