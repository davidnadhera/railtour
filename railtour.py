import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
from Trasa import Trasa
import pickle
import heapdict

MAX_V_ITERACI = 10000
IDPESKY = 9999
IDSPANEK = 9998
starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)

def countVykon1(trasa):
    doba = trasa.cas-starttime
    if doba:
        trasa.vykon = trasa.body/doba.total_seconds()*60.0*60.0 
    else:
        trasa.vykon = 0.0

def presunHrana(presun,cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(presun['cas'])
    hrana.km = presun['km']
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = [SpojHrany(presun['idstaniceod'],presun['idstanicedo'],cas.time(),IDPESKY,presun['cas'])]
    return hrana

def spanekHrana(cas):
    hrana = TempTrasa(cas)
    hrana.setDoba(timedelta(hours=6))
    hrana.km = 0.0
    hrana.prijezd = hrana.prijezd.time()
    hrana.trasa = []
    return hrana  

def doIterace(iterace,x):
    def getNewValues(visited,druhyden,kraje,inday,body,cil):
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
        idkraj = stan.at[cil,'idkraj'] 
        if idkraj in range(2,15):
            new_kraje.add(idkraj)
        new_values['kraje'] = new_kraje
        new_values['inday'] = new_inday
        new_body = body + stan.at[cil,'body']
        if new_inday in [6,7,8]:
            new_body += 1
        if (len(kraje) == 3) and (len(new_kraje) == 4):
            new_body += 2
        new_values['body'] = new_body
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
                if hrany[-1].odjezd < trasa.cas.time():
                    hrana = hrany[0]
                    new_cas = datetime.combine(trasa.cas.date(),hrana.odjezd) + timedelta(days=1) + hrana.doba
                else:
                    for hrana in hrany:
                        if hrana.odjezd >= trasa.cas.time():
                            new_cas = datetime.combine(trasa.cas.date(),hrana.odjezd) + hrana.doba
                            break
                if new_cas-trasa.cas > timedelta(hours=9):
                    continue
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = hrana
                new_values = getNewValues(visited,new_cas.date() > trasa.cas.date(),trasa.kraje,trasa.inday,trasa.body,cil)
                to_include = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                                new_values['kraje'],new_hrany,countVykon1,new_values['inday'])
                if (x<=6) or (to_include.vykon > 1.0):
                    new_iterace[(cil,frozenset(new_values['visited']))] = to_include
        presuny = pres[(pres['idstaniceod']==idstanice) & (pres['vnitrni']==1) & (pres['idstanicedo'].isin(list(stan.index)))\
                         & (~pres['idstanicedo'].isin(visited))]
        for i,nextstan in presuny.iterrows():
            cil = nextstan['idstanicedo']
            new_cas = trasa.cas+nextstan['cas']
            new_values = getNewValues(visited,new_cas.date() > trasa.cas.date(),trasa.kraje,trasa.inday,trasa.body,cil)
            new_hrany = trasa.hrany.copy()
            new_hrany[cil] = presunHrana(nextstan,trasa.cas)
            new_iterace[(cil,frozenset(new_values['visited']))] = Trasa(new_cas,trasa.idstart,new_values['body'],\
                                                              trasa.km + nextstan['km'],new_values['kraje'],\
                                                              new_hrany,countVykon1,new_values['inday'])            
    return new_iterace

vysledky = heapdict.heapdict()


with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)


stan = pd.read_csv('C:\\users\\david\\downloads\\stanice (5).csv', names=['idstanice','body','dobapremie','dobapremie2',
                    'docile','idkraj','presunx'], index_col='idstanice', quotechar='"', parse_dates=['docile'])
pres = pd.read_csv('C:\\users\\david\\downloads\\presuny.csv',names=['idpresuny','idstaniceod','idstanicedo','cas','km','vnitrni'],
                    quotechar='"')
pres['cas'] = pd.to_timedelta(pres['cas'])
stan['presunx'] = pd.to_timedelta(stan['presunx'],unit='s')
stan['dobapremie'] = pd.to_timedelta(stan['dobapremie'],unit='h') + starttime
stan['dobapremie2'] = pd.to_timedelta(stan['dobapremie2'],unit='h') + starttime

iterace = heapdict.heapdict()
iterace[(3333,frozenset([3333]))] = Trasa(starttime,3333,0,0.0,set(),{},countVykon1,0)

for x in range(30):
    iterace = doIterace(iterace,x+1)

for _ in range(1):
    ((idstanice,frozen_visited),trasa) = iterace.popitem()
    print(f'Stanice: {idstanice}, Cas: {trasa.cas}, Visited: {frozen_visited}, Body: {trasa.body}\
    Km: {round(trasa.km,1)}, Kraje: {trasa.kraje}, Hrany: {trasa.hrany}, Vykon: {round(trasa.vykon,2)}\
    Ve dni: {trasa.inday}')
    # trasa.vypisSpoje()