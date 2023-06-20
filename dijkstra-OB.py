import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
import pickle
import heapdict
from copy import copy

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

def make_time(x):
    return x.time()

def dijkstra(start,casy):
    h = heapdict.heapdict()
    hotovo = {}
    prvni = {}
    for cas in casy:
        for s in stanice:
            my_trasa = TempTrasa(cas)
            if s == start:
                my_trasa.setDoba(timedelta(days=0))
            else:
                my_trasa.setDoba(timedelta(days=10))
            my_trasa.idstanice = start
            h[(s,cas.time())] = my_trasa
    for s in stanice:
        hotovo[s] = time(0,0)
        prvni[s] = time(23,59)
    x=0
    ((idstanice,curr_odjezd),temptrasa) = h.popitem()
    while len(h) and ((x==0) or (temptrasa.doba <= timedelta(hours = 48))):       
        x+=1
        if (hotovo[idstanice]>curr_odjezd) or \
           (temptrasa.doba >= timedelta(days=1)) or \
           ((curr_odjezd>temptrasa.prijezd.time()) and (temptrasa.prijezd.time()>=prvni[idstanice])):
            ((idstanice,curr_odjezd),temptrasa) = h.popitem()            
            continue
        hotovo[idstanice] = curr_odjezd
        if prvni[idstanice] == time(23,59):
            prvni[idstanice] = temptrasa.prijezd.time() 
        curr_cas = make_date(temptrasa.odjezd)+temptrasa.doba
        if (stan.at[idstanice,'checkpoint'] == 1):
            if (idstanice != start):
                hrany[idstanice].append(temptrasa)
            if temptrasa.doba:
                ((idstanice,curr_odjezd),temptrasa) = h.popitem()
                continue
        curr_presuny = pres[(pres['idstaniceod']==idstanice) & (pres['vnitrni']==0)]
        for _, next_stan in curr_presuny.iterrows():
            new_doba = temptrasa.doba + next_stan['cas']
            new_key = (next_stan['idstanicedo'],temptrasa.odjezd)
            # new_prijezd = make_date(temptrasa.odjezd)+new_doba
            # new_key2 = (next_stan['idstanicedo'],new_prijezd.time())
            if ((new_key in h) and (new_doba<h[new_key].doba)):
                newtrasa = copy(temptrasa)
                newtrasa.setDoba(new_doba)
                newtrasa.trasa = list(temptrasa.trasa)
                newtrasa.trasa.append(SpojHrany(idstanice,next_stan['idstanicedo'],
                                                                                    curr_cas.time(),
                                                                                    0,next_stan['cas']))
                newtrasa.km = temptrasa.km + next_stan['km']
                newtrasa.presun = True
                newtrasa.idstanice = next_stan['idstanicedo']
                newtrasa.lastPresun = next_stan['cas']
                h[new_key] = newtrasa

        if not temptrasa.presun:
            curr_cas += stan.at[idstanice,'prestup']
        if idstanice in gvd:
            curr_gvd_idstanice = gvd[idstanice]
            for next_stan in curr_gvd_idstanice:
                if curr_gvd_idstanice[next_stan][-1].odjezd < curr_cas.time():
                    curr_spoj = curr_gvd_idstanice[next_stan][0]
                    new_cas = datetime.combine(curr_cas.date(),curr_spoj.odjezd) + timedelta(days = 1)
                else:
                    for spoj in curr_gvd_idstanice[next_stan]:
                        if spoj.odjezd >= curr_cas.time():
                            curr_spoj = spoj
                            new_cas = datetime.combine(curr_cas.date(),curr_spoj.odjezd)
                            break
                new_doba = new_cas - make_date(temptrasa.odjezd) + curr_spoj.doba
                new_key = (next_stan,temptrasa.odjezd)
                # new_prijezd = make_date(temptrasa.odjezd)+new_doba 
                # new_key2 = (next_stan,new_prijezd.time())
                if (new_key in h) and (new_doba<h[new_key].doba):
                    newtrasa = copy(temptrasa)
                    newtrasa.setDoba(new_doba)
                    newtrasa.trasa = list(temptrasa.trasa)
                    newtrasa.trasa.append(SpojHrany(idstanice,next_stan,new_cas.time(),curr_spoj.idvlaky,curr_spoj.doba))
                    newtrasa.km = temptrasa.km
                    newtrasa.presun = False
                    newtrasa.idstanice = next_stan
                    newtrasa.lastPresun = 0.0
                    h[new_key] = newtrasa
        ((idstanice,curr_odjezd),temptrasa) = h.popitem()

hrany = {}

with open('C:\\idos\\gvd_modified.pickle', 'rb') as handle:
    gvd = pickle.load(handle)


stan = pd.read_csv('C:\\idos\\stanice (3).csv',names=['idstanice','nazev','checkpoint','body','prestup'],
                    index_col='idstanice', quotechar='"')
pres = pd.read_csv('C:\\idos\\presuny.csv',names=['idpresuny','idstaniceod','idstanicedo','cas','km','vnitrni'],
                    quotechar='"')
odj = pd.read_csv('C:\\idos\\odjezdy.csv',names=['idodjezdy','cas','idvlaky','idstanice','druhyden','poradi'],
                    parse_dates=['cas'])
pres['cas'] = pd.to_timedelta(pres['cas'])
stan['prestup'] = pd.to_timedelta(stan['prestup'])
stanice = stan.index.tolist()
for start in [3000,3333]:
    print(start)
    for i in stan.index.tolist():
        if stan.at[i,'checkpoint'] == 1:
            hrany[i] = []
    if start == 3000:
        casy_odchodu=[time(hour=8,minute=22),time(hour=20,minute=22)]    
    if start == 3333:
        casy_odchodu=[time(hour=9,minute=0)]
    casy = list(map(make_date,casy_odchodu))
    dijkstra(start,casy)
        

    with open(f'C:\\railtour\\hrany\\hrany{start}.pickle', 'wb') as handle:
        pickle.dump(hrany, handle, protocol=pickle.HIGHEST_PROTOCOL)
