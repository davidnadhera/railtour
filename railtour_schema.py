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
import random

MAX_V_ITERACI = 5000
IDPESKY = 9999
IDSPANEK = 9998
starttime = datetime(year=2022, month=8, day=8, hour=9, minute=0)
ciltime = datetime(year=2022, month=8, day=12, hour=16, minute=0)
CILS = [3334]
CIL_OD = datetime(year=2022, month=8, day=12, hour=12, minute=0)
CIL_DO = datetime(year=2022, month=8, day=12, hour=16, minute=0)
OLOMOUC = 3334
SPANEK = 3999
START = 3333
SPANEK_OD = datetime(year=2022, month=8, day=9, hour=20, minute=0)
SPANEK_DO = datetime(year=2022, month=8, day=11, hour=2, minute=0)
TEMP_BLOCK = []
BLOCK_DO = datetime(year=2022, month=8, day=9, hour=0, minute=0)
COUNT_PREMIE = False
TOTAL_KM = 145
PENALE = 0.0
USE_VYKON = False
LIMIT_VYKON = 0.3
LIMIT_POCET = 40

def countVykon1(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
    # zbyva = CIL_DO - trasa.cas
    # if (zbyva < zlom) and trasa.hrany:
    #     idstanice = list(trasa.hrany)[-1]
    #     if idstanice == SPANEK:
    #         idstanice = list(trasa.hrany)[-2]
    #     penale_cil = (zlom-zbyva)/zlom*(CIL_DO-stan[idstanice]['docile'])
    # else:
    penale_cil = timedelta(days=0)
    # if zbyva < zlom:
    #     penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    # else:
    #     penale = (trasa.km-kmsec*doba)*PENALE
    penale = max(0,(trasa.km-kmsec*doba)*PENALE)   
    if doba:
        trasa.vykon = (trasa.body-penale+trasa.predict_vykon)/(doba+penale_cil.total_seconds())*60.0*60.0 
    else:
        trasa.vykon = 0.0
    # trasa.vykon = trasa.vykon * (1+random.random()/5)

def countVykon2(trasa):
    doba = trasa.cas-starttime
    doba = doba.total_seconds()
#    penale = max(0,(trasa.km-kmsec*doba)*PENALE)
    penale = (trasa.km-kmsec*doba)*PENALE
    if doba:
        trasa.vykon = trasa.body - penale-doba/60.0/60.0 + trasa.predict_vykon
    else:
        trasa.vykon = 0.0

def countVykonF(trasa):
    if trasa.cas>ciltime-timedelta(hours=4): 
        doba = CIL_DO-starttime
    else:
        doba = trasa.cas-starttime
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

def doIterace(iterace,x):
    def getNewValues(new_cas,prev_cas,kraje,inday,body,cil,postupka):
        postupka1 = {2,3,4,5}
        postupka2 = {3,4,5,6}
        postupka3 = {4,5,6,7}

        druhyden = new_cas.date() > prev_cas.date()
        new_values = {}              
        if druhyden:
            new_inday = 1
            new_kraje = set()
            new_postupka = set() 
        else:
            new_inday = inday + 1
            new_kraje = kraje.copy()
            new_postupka = postupka.copy()
        idkraj = stan[cil]['idkraj'] 
        if idkraj in range(2,15):
            new_kraje.add(idkraj)
        new_values['kraje'] = new_kraje
        new_values['inday'] = new_inday        
        new_body = body + stan[cil]['body']
        if new_inday in [6,7,8,9] and (cil != OLOMOUC):
            new_body += 1
        if (len(kraje) == 3) and (len(new_kraje) == 4):
            new_body += 2
        if (100 not in new_postupka) and \
            (postupka1.issubset(new_postupka) or postupka2.issubset(new_postupka) or postupka3.issubset(new_postupka)):
            new_postupka.add(100)
            new_body += 2
        new_postupka.add(stan[cil]['body'])
        new_values['postupka'] = new_postupka
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
        in_it = 0
        ((idstanice,frozen_visited),trasa) = iterace.popitem()
        visited = set(frozen_visited)
        if (idstanice,trasa.cas.time()) not in schema:
            trasa.vypisHlavicku(nazvy)      
        for cil,info in schema[(idstanice,trasa.cas.time())].items():
            if (cil not in visited) and ((trasa.cas>=BLOCK_DO) or (cil not in TEMP_BLOCK)) \
            and ((cil != SPANEK) or ((trasa.cas>=SPANEK_OD) and (trasa.cas<=SPANEK_DO))) \
            and (trasa.cas<=CIL_DO):
                (doba,hrana,vykon) = info
                if (vykon<LIMIT_VYKON) and (cil != OLOMOUC):
                    continue
                new_cas = trasa.cas + doba
                if (cil != SPANEK) and (cil != OLOMOUC) and (new_cas > stan[cil]['docile']):
                    continue
                in_it += 1
                if (in_it>LIMIT_POCET) and (x>1):
                    break
                new_visited = visited.copy()
                new_visited.add(cil)
                if (idstanice,trasa.cas.time()) in vykony:
                    pv = vykony[(idstanice,trasa.cas.time())]
                else:
                    pv = 0 
                if (cil != SPANEK):  
                    new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil,trasa.postupka)
                else:                    
                    if new_cas.date() > trasa.cas.date():
                        new_inday = 0
                        new_kraje = set()
                        new_postupka = set()
                    else:
                        new_inday = trasa.inday
                        new_kraje = trasa.kraje
                        new_postupka = trasa.postupka
                    new_values = {}
                    new_values['kraje'] = new_kraje
                    new_values['inday'] = new_inday
                    new_values['postupka'] = new_postupka
                    new_values['body'] = trasa.body + 5
                    new_values['premie'] = 0
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (hrana,new_values['premie'],round(trasa.vykon,2)) 
                new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                  new_values['kraje'],new_hrany,countVykon,new_values['inday'],pv,\
                                  new_values['postupka'])
                if cil == SPANEK:
                    cil_stanice = idstanice
                else:
                    cil_stanice = cil 
                if (cil_stanice != OLOMOUC) and \
                (((cil_stanice,frozenset(new_visited)) not in new_iterace) \
                or (new_iterace[(cil_stanice,frozenset(new_visited))].vykon < new_trasa.vykon)):     
                    new_iterace[(cil_stanice,frozenset(new_visited))] = new_trasa
                if (new_cas <= CIL_DO) and (new_cas >= CIL_OD) and (cil_stanice in CILS):
                    vysledky.append(Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                  new_values['kraje'],new_hrany,countVykonF,new_values['inday'],pv,\
                                  new_values['postupka']))
            # elif (cil in CILS) and (((cil not in visited)) or (cil == OLOMOUC)):
            #     (doba,hrana,vykon) = info
            #     new_cas = trasa.cas + doba
            #     if ((new_cas > CIL_DO) or (new_cas < CIL_OD)) or ((cil != OLOMOUC)  and (new_cas > stan[cil]['docile'])):
            #         continue
            #     new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil,trasa.postupka)
            #     new_hrany = trasa.hrany.copy()
            #     new_hrany[cil] = (hrana,new_values['premie'],0)
            #     vysledky.append(Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
            #                       new_values['kraje'],new_hrany,countVykonF,new_values['inday'],0,\
            #                       new_values['postupka']))                                                                                         
    return new_iterace

vysledky = []


with open('C:\\Railtour\\hrany\\schema.pickle', 'rb') as handle:
    schema = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
if not USE_VYKON:
    vykony = {}
else:
    with open('C:\\Railtour\\hrany\\vykony_schema.pickle', 'rb') as handle:
        vykony = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = active
if CILS == []:
    CILS = aktivni
celkdoba = CIL_DO - starttime
zlom = celkdoba*0.5

kmsec = TOTAL_KM/celkdoba.total_seconds()
countVykon = countVykon1

iterace = heapdict.heapdict()
iterace[(START,frozenset([START]))] = Trasa(starttime,START,0,0.0,set(),{},countVykon,0,0,set())
x = 0


while len(iterace):
    x += 1
    iterace = doIterace(iterace,x)

vysledky.sort(reverse=True, key=lambda x:(x.vykon,-x.km))

with open(f'C:\\Railtour\\hrany\\vysledky.pickle', 'wb') as handle:
    pickle.dump(vysledky, handle, protocol=pickle.HIGHEST_PROTOCOL)

if len(vysledky):
    trasa = vysledky[0]
    trasa.vypisHlavicku(nazvy)
    print([x[2] for x in list(trasa.hrany.values())])
#    trasa.vypisPointy(nazvy,stan)
