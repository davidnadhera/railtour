import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
import pickle
import heapdict

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

def make_time(x):
    return x.time()

def dijkstra(start,curr_cas):
    h = heapdict.heapdict()
    for i in stan.index.tolist():
        h[i] = TempTrasa(curr_cas)

    init_value = h[start]
    init_value.setDoba(timedelta(days = 0))
    h[start] = init_value
    curr_doba = timedelta(days = 0)

    while len(h) and (curr_doba <= timedelta(hours = 48)):
        (idstanice,temptrasa) = h.popitem()
        if (stan.at[idstanice,'checkpoint'] == 1) & (idstanice != start):
            if hrany[idstanice]:
                last_hrana = hrany[idstanice][-1]
                first_hrana = hrany[idstanice][0]
                if last_hrana.prijezd < temptrasa.prijezd:
                    hrany[idstanice].append(temptrasa)
                elif (first_hrana.prijezd.date() == temptrasa.prijezd.date()) or (first_hrana.prijezd.time() > temptrasa.prijezd.time()):
                    last_hrana.odjezd = temptrasa.odjezd
                    last_hrana.setDoba(temptrasa.doba)
                    last_hrana.km = temptrasa.km
                    last_hrana.trasa = list(temptrasa.trasa)
                    last_hrana.lastPresun = temptrasa.lastPresun
            else: 
                hrany[idstanice].append(temptrasa)
        curr_doba = temptrasa.doba
        curr_cas = base_cas+curr_doba
        curr_presuny = pres[(pres['idstaniceod']==idstanice) & (pres['vnitrni']==0)]
        for i, next_stan in curr_presuny.iterrows():
            new_doba = curr_doba + next_stan['cas']
            if (next_stan['idstanicedo'] in h) and (new_doba < h[next_stan['idstanicedo']].doba):
                curr_value = h[next_stan['idstanicedo']]
                curr_value.setDoba(new_doba)
                curr_value.trasa = list(temptrasa.trasa)
                curr_value.trasa.append(SpojHrany(idstanice,next_stan['idstanicedo'],
                                                                                    curr_cas.time(),
                                                                                    0,next_stan['cas']))
                curr_value.km = temptrasa.km + next_stan['km']
                curr_value.presun = True
                curr_value.lastPresun = next_stan['cas']
                h[next_stan['idstanicedo']] = curr_value
        if not temptrasa.presun:
            curr_doba += stan.at[idstanice,'prestup']
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
                new_doba = new_cas - base_cas + curr_spoj.doba
                if (next_stan in h) and (new_doba < h[next_stan].doba):
                    curr_value = h[next_stan]
                    curr_value.setDoba(new_doba)
                    curr_value.trasa = list(temptrasa.trasa)
                    curr_value.trasa.append(SpojHrany(idstanice,next_stan,new_cas.time(),curr_spoj.idvlaky,curr_spoj.doba))
                    curr_value.km = temptrasa.km
                    curr_value.presun = False
                    curr_value.lastPresun = 0.0
                    h[next_stan] = curr_value

hrany = {}

with open('C:\\users\\david\\downloads\\gvd_modified.pickle', 'rb') as handle:
    gvd = pickle.load(handle)


stan = pd.read_csv('C:\\users\\david\\downloads\\stanice (3).csv',names=['idstanice','nazev','checkpoint','body','prestup'],
                    index_col='idstanice', quotechar='"')
pres = pd.read_csv('C:\\users\\david\\downloads\\presuny.csv',names=['idpresuny','idstaniceod','idstanicedo','cas','km','vnitrni'],
                    quotechar='"')
odj = pd.read_csv('C:\\users\\david\\downloads\\odjezdy.csv',names=['idodjezdy','cas','idvlaky','idstanice','druhyden','poradi'],
                    quotechar='"', parse_dates=['cas'])
pres['cas'] = pd.to_timedelta(pres['cas'])
stan['prestup'] = pd.to_timedelta(stan['prestup'])
for start in range(3038,3297):
    print(start)
    for i in stan.index.tolist():
        if stan.at[i,'checkpoint'] == 1:
            hrany[i] = []
    Jested_pres = pres[(pres['idstaniceod']==start) & (pres['vnitrni']==0)]
    pres_odj = pd.merge(Jested_pres,odj,how="inner",
        left_on='idstanicedo',
        right_on='idstanice',
        sort=False)
    casy_presunu = pres_odj['cas_x']
    casy_odjezdu = pres_odj['cas_y']
    casy_odchodu = (casy_odjezdu - pres_odj['cas_x']).map(make_time)
    casy_odchodu.sort_values(inplace=True)
    casy_odchodu.drop_duplicates(inplace=True)



    for cas in casy_odchodu.iteritems():
        base_cas = make_date(cas[1])
        curr_cas = base_cas
        print(curr_cas)
        dijkstra(start,curr_cas)
        

    with open(f'C:\\users\\david\\downloads\\hrany{start}.pickle', 'wb') as handle:
        pickle.dump(hrany, handle, protocol=pickle.HIGHEST_PROTOCOL)


