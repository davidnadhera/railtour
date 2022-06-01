
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
from Trasa import Trasa
import pickle
import heapdict
from timeit import default_timer as timer
from consts import active

MAX_V_ITERACI = 20000
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
USE_VYKON = True
LIMIT_VYKON = 0.3
LIMIT_POCET = 40

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
        in_it = 0
        ((idstanice,frozen_visited),trasa) = iterace.popitem()
        visited = set(frozen_visited)
        if (idstanice,trasa.cas.time()) not in schema:
            trasa.vypisHlavicku(nazvy)      
        for cil,info in schema[(idstanice,trasa.cas.time())].items():
            if (cil != OLOMOUC) and (cil not in visited) and ((trasa.cas>=BLOCK_DO) or (cil not in TEMP_BLOCK)) \
            and ((cil != SPANEK) or ((trasa.cas>=SPANEK_OD) and (trasa.cas<=SPANEK_DO))):
                (doba,hrana,vykon) = info
                if vykon<LIMIT_VYKON:
                    continue
                in_it += 1
                if in_it>LIMIT_POCET:
                    break
                new_cas = trasa.cas + doba
                new_visited = visited.copy()
                new_visited.add(cil)
                if (cil != SPANEK) and (new_cas > stan[cil]['docile']):
                    continue
                pv = vykony[(idstanice,trasa.cas.time())] 
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
                new_hrany[cil] = (hrana,new_values['premie'],in_it) 
                new_trasa = Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                                new_values['kraje'],new_hrany,countVykon,new_values['inday'],pv)
                if cil == SPANEK:
                    cil_stanice = idstanice
                else:
                    cil_stanice = cil 
                if ((cil_stanice,frozenset(new_visited)) not in new_iterace) or (new_iterace[(cil_stanice,frozenset(new_visited))].vykon < new_trasa.vykon):     
                    new_iterace[(cil_stanice,frozenset(new_visited))] = new_trasa
            elif (cil in CILS) and (((cil not in visited)) or (cil == OLOMOUC)):
                (doba,hrana,vykon) = info
                new_cas = trasa.cas + doba
                if (new_cas > CIL_DO) or (new_cas < CIL_OD) or (new_cas > stan[cil]['docile']):
                    continue
                new_values = getNewValues(new_cas,trasa.cas,trasa.kraje,trasa.inday,trasa.body,cil)
                new_hrany = trasa.hrany.copy()
                new_hrany[cil] = (hrana,new_values['premie'],0)
                vysledky.append(Trasa(new_cas,trasa.idstart,new_values['body'],trasa.km + hrana.km,\
                                                                new_values['kraje'],new_hrany,countVykonF,new_values['inday'],0))                                                                                         
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
celkdoba = CIL_DO - starttime
kmsec = TOTAL_KM/celkdoba.total_seconds()
countVykon = countVykon1

iterace = heapdict.heapdict()
iterace[(START,frozenset([START]))] = Trasa(starttime+timedelta(minutes=1),START,0,0.0,set(),{},countVykon,0,0)
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
