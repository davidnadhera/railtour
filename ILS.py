import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
from BodTrasy import BodTrasy
from Trasa2 import Trasa2
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
starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)
ciltime = datetime(year=2021, month=8, day=6, hour=16, minute=0)
TOTAL_KM = 185
PENALE = 0.25
COUNT_PREMIE = False
CIL_DO = datetime(year=2021, month=8, day=6, hour=16, minute=0)

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

def countVykonF(trasa):
    doba = ciltime-starttime
    doba = doba.total_seconds()
    penale = max(0,(trasa.km-TOTAL_KM)*PENALE)
    if doba:
        trasa.vykon = (trasa.body-penale)/doba*60.0*60.0 
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

def getnewtrasa(trasa,hrana,doba,cil):
    new_cas = trasa.cas + doba
    if (cil != SPANEK):  
        new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
    else:                    
        if new_cas.date() > trasa.cas.date():
            new_inday = 0
            new_kraje = set()
        else:
            new_inday = trasa.inday
            new_kraje = trasa.kraje
        new_values = {}
        new_values['kraje'] = new_kraje
        new_values['inday'] = new_inday
        new_values['body'] = trasa.body + 5
        new_values['premie'] = 0
    new_hrany = trasa.hrany.copy()
    new_hrany[cil] = (hrana,new_values['premie'],round(trasa.vykon,2)) 
    new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                    new_values['kraje'],new_hrany,countVykon,new_values['inday'],0)
    return new_trasa
    
with open('C:\\Railtour\\hrany\\schema_full.pickle', 'rb') as handle:
    schema = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = active
dobazavodu = ciltime-starttime
kmsec = TOTAL_KM/dobazavodu.total_seconds()
countVykon = countVykon1

curr_trasa = Trasa(starttime,OLOMOUC,0,0.0,set(),{OLOMOUC:(None,0,OLOMOUC)},countVykon,0,0)
newtrasy = [curr_trasa]

while len(newtrasy):
    base_trasa = Trasa(starttime,OLOMOUC,0,0.0,set(),{},countVykon,0,0)
    trasy = {}
    odkud = OLOMOUC
    for kam,bod in curr_trasa.hrany.items():
        newtrasy = {}
        for _cas,trasa in trasy.items():
            if kam in schema[((odkud,_cas.time()))]:
                (doba,hrana,vykon) = schema[((odkud,_cas.time()))][kam]
                new_cas = _cas + doba
                if new_cas > CIL_DO:
                    continue
                newtrasa = getnewtrasa(trasa,hrana,doba,kam)
                if (new_cas not in newtrasy) or (newtrasy[new_cas] < newtrasa):
                    newtrasy[new_cas] = newtrasa
        visited = list(curr_trasa.hrany.keys())
        visited.append(OLOMOUC)
        for cil,info in schema[(odkud,base_trasa.cas.time())].items():
            if (cil not in visited):
                (doba,hrana,vykon) = info
                new_cas = base_trasa.cas + doba
                if (cil != SPANEK) and (new_cas > stan[cil]['docile']):
                    continue
                newtrasa = getnewtrasa(base_trasa,hrana,doba,cil)
                if cil == SPANEK:
                    cil = odkud
    #            newtrasa.vypisHlavicku(nazvy)
                if kam in schema[((cil,new_cas.time()))]: 
                    (doba,hrana,vykon) = schema[((cil,new_cas.time()))][kam]
                    new_cas = newtrasa.cas + doba
                    if new_cas > CIL_DO:
                        continue
                    newtrasa = getnewtrasa(newtrasa,hrana,doba,kam)
        #            newtrasa.vypisHlavicku(nazvy) 
                    if (new_cas not in newtrasy) or (newtrasy[new_cas] < newtrasa):
                        newtrasy[new_cas] = newtrasa
        if newtrasy:                
            trasy = newtrasy
            if kam != OLOMOUC:
                (doba,hrana,vykon) = schema[((odkud,base_trasa.cas.time()))][kam]
                new_cas = base_trasa.cas + doba
                base_trasa = getnewtrasa(base_trasa,hrana,doba,kam)
                if kam != SPANEK:               
                    odkud = kam

    trasy = sorted(trasy.values())
    curr_trasa = trasy[0]

curr_trasa.vypisHlavicku(nazvy)        


# with open(f'C:\\Railtour\\hrany\\ILS.pickle', 'wb') as handle:
#     pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)
