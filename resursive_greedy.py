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

MAX_V_ITERACI = 20000
IDPESKY = 9999
IDSPANEK = 9998
starttime = datetime(year=2021, month=8, day=2, hour=9, minute=1)
CILS = [3333]
CIL_OD = datetime(year=2021, month=8, day=6, hour=12, minute=0)
CIL_DO = datetime(year=2021, month=8, day=6, hour=16, minute=0)
OLOMOUC = 3333
SPANEK = 3999
START = 3333
BRNO = 3000
SPANEK_OD = datetime(year=2021, month=8, day=3, hour=20, minute=0)
SPANEK_DO = datetime(year=2021, month=8, day=5, hour=2, minute=0)
TEMP_BLOCK = []
BLOCK_DO = datetime(year=2021, month=8, day=3, hour=0, minute=0)
COUNT_PREMIE = False
TOTAL_KM = 185
PENALE = 0.25
USE_VYKON = False
LIMIT_VYKON = 0
LIMIT_POCET = 15

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
        trasa.vykon = trasa.body - penale-doba/60.0/60.0
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

def generate_casy(start_cas,cil_cas,idstanice):
    cas = start_cas.date()
    casy = [(idstanice,datetime.combine(cas,x[1])) for x in schema if (x[0]==idstanice) and (x[1]>start_cas.time())]
    cas = cas + timedelta(days = 1)
    while cas<cil_cas.date():
        casy = casy + [(idstanice,datetime.combine(cas,x[1])) for x in schema if x[0]==idstanice]
        cas = cas + timedelta(days = 1)
    casy = casy + [(idstanice,datetime.combine(cas,x[1])) for x in schema if (x[0]==idstanice) and (x[1]<cil_cas.time())]
    return casy

def RG(s,t,X,i,kraje,inday):
    (start,start_cas) = s
    (cil,cil_cas) = t
    rozdil_casu = cil_cas-start_cas
    if (start != START) or (cil != START):
        if cil not in schema[(start,start_cas.time())]:
            return None
        info = schema[(start,start_cas.time())][cil]
        (doba,hrana,vykon) = info
        if doba > rozdil_casu:
            return None
        new_cas = start_cas + doba
        if new_cas.date() > start_cas.date():
            new_inday = 1
            new_kraje = set() 
        else:
            new_inday = inday + 1
            new_kraje = kraje.copy()
        idkraj = stan[cil]['idkraj'] 
        if idkraj in range(2,15):
            new_kraje.add(idkraj)
        new_body = stan[cil]['body']
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
        trasa = Trasa(start_cas,start,new_body,hrana.km,new_kraje,{cil:(hrana,premie,0)},countVykon,new_inday,0)
    else:
        trasa = Trasa(starttime+timedelta(minutes=1),START,0,0.0,set(),{},countVykon,0,0)
    if i==0:
        return trasa
    max_vykon = 0
    not_visited = [x for x in aktivni if (x not in X) and (x not in {start,cil})]
    for idstanice in not_visited: 
        polovina = start_cas + rozdil_casu/2
        kandidati = [x[1] for x in schema if (x[0]==idstanice) and (x[1]>=polovina.time())]
        if kandidati == []:
            kandidati = [x[1] for x in schema if (x[0]==idstanice)]
            kandidati = sorted(kandidati)
            half_cas = datetime.combine(polovina.date()+timedelta(days=1),kandidati[0])
        else:
            kandidati = sorted(kandidati)
            half_cas = datetime.combine(polovina.date(),kandidati[0])
        cas = (idstanice,half_cas)
        leva_trasa = RG(s,cas,X,i-1,kraje,inday)
        if leva_trasa:
            new_X = X.copy()
            new_X.append(list(leva_trasa.hrany.keys()))
            prava_trasa = RG(cas,t,new_X,i-1,leva_trasa.kraje,leva_trasa.inday)
            if prava_trasa:
                new_trasa = Trasa(prava_trasa.cas,leva_trasa.idstart,leva_trasa.body+prava_trasa.body,leva_trasa.km+prava_trasa.km,\
                                prava_trasa.kraje,{**leva_trasa.hrany,**prava_trasa.hrany},countVykon,prava_trasa.inday,0)
                if new_trasa.vykon > max_vykon:
                    trasa = new_trasa
                    max_vykon = new_trasa.vykon
    return trasa  



with open('C:\\Railtour\\hrany\\schema_full.pickle', 'rb') as handle:
    schema = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = set(stan.keys())
celkdoba = CIL_DO - starttime
kmsec = TOTAL_KM/celkdoba.total_seconds()
countVykon = countVykon1

vysledky = RG((START,starttime),(START,CIL_DO),[],3,set(),0)

with open(f'C:\\Railtour\\hrany\\vysledky.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)

if vysledky:
    print(vysledky.body,vysledky.km,list(vysledky.hrany.keys()))
#    trasa.vypisPointy(nazvy,stan)
