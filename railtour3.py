import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from TempTrasa import TempTrasa
from SpojHrany import SpojHrany
from Trasa import Trasa
import pickle
from timeit import default_timer as timer

MAX_V_ITERACI = 2048
IDPESKY = 9999
IDSPANEK = 9998
starttime = datetime(year=2022, month=8, day=8, hour=9, minute=0)
ciltime = datetime(year=2022, month=8, day=12, hour=16, minute=0)
stred = datetime(year=2022, month=8, day=10, hour=12, minute=30)
norm = ciltime-stred
# CILS = list(range(3000,3297))
CILS = [3334]
# CIL_OD = datetime(year=2022, month=8, day=9, hour=4, minute=0)
# CIL_DO = datetime(year=2022, month=8, day=9, hour=10, minute=0)
CIL_OD = ciltime-timedelta(hours=4)
CIL_DO = ciltime
OLOMOUC = 3333
START = 3333
CIL = 3334
SPANEK_OD = datetime(year=2022, month=8, day=9, hour=20, minute=0)
SPANEK_DO = datetime(year=2022, month=8, day=11, hour=2, minute=0)
TEMP_BLOCK = []
BLOCK_DO = datetime(year=2022, month=8, day=9, hour=0, minute=0)
BLOCK = set()  # set(range(3261,3297))
COUNT_PREMIE = False
TOTAL_KM = 185
PENALE = 0.5
UNAVA = 0
USE_VYKON = 1
HRANA, PRESUN, SPANEK = 0, 1, 2
MAX_VYSLEDKY = 50000
LIMIT_VYKON = 0.5
LIMIT_POCET = 4


def presunHrana(od,do,cas,doba):
    if pd.isnull(doba):
        return None
    return [SpojHrany(od,do,cas.time(),IDPESKY,doba*(1+UNAVA))]

def spanekHrana(od,cas):
    return [SpojHrany(od,od,cas.time(),IDSPANEK,timedelta(hours=6))]

def doIterace(iterace):
    global a1,a2,a3,b,c1,c2,c3,d,e,f,g,h,i,j,k,l
    def count_next_hrany(next_iterace):
        next_iterace['next_hrany'] = [{**x[0], x[2] if x[12]!=SPANEK else IDSPANEK:(x[1], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10], x[11])}
                                      for x in zip(next_iterace.hrany, next_iterace.stanice, next_iterace.next_stanice, next_iterace.x_odjezd,
                                                   next_iterace.next_cas, next_iterace.premie_cas, next_iterace.premie_inday,
                                                   next_iterace.premie_kraje, next_iterace.premie_postupka,next_iterace.next_body,
                                                   next_iterace.next_km, next_iterace.trasa, next_iterace.source)]
        return next_iterace

    def count_vykon(next_iterace):
        doba = np.where(next_iterace.next_stanice == CIL,
                        (ciltime - starttime).total_seconds(),
                        (next_iterace.next_cas - starttime).dt.total_seconds())
        penale = (next_iterace.next_km - kmsec * doba) * PENALE
        penale = np.where(penale > 0, penale, 0)
        pomer = (next_iterace.next_cas - stred)/norm
        docile = next_iterace.next_stanice.map(chp.cas_docile).dt.total_seconds()
        doba = doba + np.where(pomer>0,pomer,0)*docile
        if USE_VYKON == 2:
            vykon = next_iterace.next_body - penale - (doba / 3600)
        else:
            vykon = (next_iterace.next_body - penale) / doba * 3600

        return vykon

    print(x)
    if UNAVA:
        mg_iterace = pd.merge(iterace, presx, left_on='stanice', right_index=True, suffixes=(None,'_staniceod'))
        mg_iterace['u_cas'] = mg_iterace.cas + UNAVA * mg_iterace.cas_staniceod
    else:
        mg_iterace = iterace
        mg_iterace['u_cas'] = mg_iterace.cas
    mg_iterace['n_cas'] = mg_iterace.u_cas - mg_iterace.u_cas.dt.normalize()
    start = timer()
    next_iterace = mg_iterace.join(active_chp, how='cross')
    end = timer()
    a1 += (end-start)
    start = timer()
    next_iterace = next_iterace.sort_values(['n_cas','stanice','next_stanice'])
    end = timer()
    a2 += (end-start)
    start = timer()
    next_iterace = pd.merge_asof(next_iterace, hrany, left_on='n_cas', right_index=True, left_by=['stanice', 'next_stanice'],
                                 right_by=['od', 'do'], direction='forward', suffixes=(None,'_hrana'))
    end = timer()
    a3 += (end-start)
    start = timer()
    next_iterace = next_iterace.dropna(subset=['odjezd'])
    if UNAVA:
        next_iterace['x_odjezd'] = next_iterace.u_cas.dt.normalize()+next_iterace.odjezd-UNAVA * next_iterace.cas_staniceod
    else:
        next_iterace['x_odjezd'] = next_iterace.u_cas.dt.normalize() + next_iterace.odjezd
    next_iterace['next_cas'] = next_iterace.u_cas.dt.normalize()+next_iterace.odjezd+next_iterace.doba+UNAVA*next_iterace.presundo
    next_iterace['next_km'] = next_iterace.km+next_iterace.km_hrana
    # next_iterace['source'] = HRANA
    end = timer()
    b+=(end-start)


    # ------------ Presuny ---------------

    # next_pres = pd.merge(iterace, pres_chp, left_on='stanice', right_index=True,
    #                         suffixes=(None, '_pres'))
    # next_pres = next_pres.rename(columns={'do':'next_stanice'})
    # next_pres['next_cas'] = next_pres.cas+(1+UNAVA)*next_pres.cas_pres
    # next_pres['next_km'] = next_pres.km+next_pres.km_pres
    # next_pres['source'] = PRESUN
    #

    # next_iterace = pd.concat([next_iterace, next_pres])
    next_iterace = pd.merge(next_iterace, aktivni, left_on='next_stanice', right_index=True,
                            suffixes=(None, '_stanicedo'))


    next_iterace['next_body'] = next_iterace.body + next_iterace.body_stanicedo
    next_iterace['app_vykon'] = count_vykon(next_iterace)

    # next_iterace.sort_values(['app_vykon','next_body','next_km'], inplace=True, ascending=[False,False,True])


    is_docile = next_iterace.next_stanice.isin(CILS) & (CIL_OD <= next_iterace.next_cas) & (next_iterace.next_cas <= CIL_DO)

    start = timer()
    # aaa = next_iterace.head(4*MAX_V_ITERACI)
    # bbb = next_iterace.loc[is_docile,next_iterace.columns].head(MAX_V_ITERACI)
    aaa = next_iterace.nlargest(LIMIT_POCET*MAX_V_ITERACI,['app_vykon','next_body'],keep='all')
    end = timer()
    c1 += (end-start)
    start = timer()
    bbb = next_iterace.loc[is_docile,next_iterace.columns].nlargest(MAX_V_ITERACI,['app_vykon','next_body'],keep='all')
    end = timer()
    c2 += (end-start)
    start = timer()
    next_iterace = pd.concat([aaa,bbb])
    end = timer()
    c3 += (end-start)

    start=timer()
    # vyhodime jiz navstivene
    next_iterace = next_iterace.loc[[x[0] not in x[1] for x in zip(next_iterace['next_stanice'], next_iterace['hrany'])],
                                     next_iterace.columns]

    # vyhodime ty, odkud se neda dostat vcas do cile
    next_iterace = next_iterace.loc[next_iterace.next_cas <= next_iterace.docile,next_iterace.columns]

    # vyhodime ty, ktere jsou po cilovem case
    next_iterace = next_iterace.loc[next_iterace.next_cas <= CIL_DO,next_iterace.columns]

    # vyhodime docasne blokovane
    next_iterace = next_iterace.loc[(next_iterace.next_cas > BLOCK_DO) | (~next_iterace.next_stanice.isin(TEMP_BLOCK)),
                                    next_iterace.columns]
    end = timer()
    d += (end-start)

    if len(next_iterace)==0:
        return (pd.DataFrame(),pd.DataFrame())

    start = timer()
    druhyden = next_iterace.next_cas.dt.date > next_iterace.cas.dt.date
    next_iterace['next_inday'] = np.where(druhyden,1,next_iterace.inday+1)
    next_iterace.loc[next_iterace.next_stanice == CIL,'next_inday'] = 0
    next_iterace['next_kraje'] = np.where(druhyden,
                                          ['0' * (x - 2) + '1' + '0' * (14 - x) if 2 <= x <= 14 else '0'*13 for x in next_iterace.kraj],
                                          [x[0][:x[1] - 2] + '1' + x[0][x[1] - 1:] if 2 <= x[1] <= 14 else x[0] for x in
                                           zip(next_iterace['kraje'], next_iterace['kraj'])])
    next_iterace['next_postupka'] = np.where(druhyden,
                                             ['0' * (x - 2) + '1' + '0' * (7 - x) if 2 <= x <= 7 else '0'*6 for x in
                                              next_iterace['body_stanicedo']],
                                             [x[0][:x[1] - 2] + '1' + x[0][x[1] - 1:] if 2 <= x[1] <= 7 else x[0] for x in
                                              zip(next_iterace['postupka'], next_iterace['body_stanicedo'])])
    next_iterace['next_postupka1'] = next_iterace.next_postupka.str.slice(0, 4) == '1111'
    next_iterace['next_postupka2'] = next_iterace.next_postupka.str.slice(1, 5) == '1111'
    next_iterace['premie_cas'] = 0
    if COUNT_PREMIE:
        next_iterace.loc[next_iterace.next_cas < next_iterace.dobapremie1, 'premie_cas'] = 1
        next_iterace.loc[next_iterace.next_cas < next_iterace.dobapremie2, 'premie_cas'] = 2
    next_iterace['premie_inday'] = np.where(next_iterace.next_inday.isin([6, 7, 8]), 1, 0)
    next_iterace['premie_kraje'] = np.where((next_iterace.kraje.str.count('1') == 3) &
                                            (next_iterace.next_kraje.str.count('1') == 4), 2, 0)
    next_iterace['premie_postupka'] = np.select(
        [(next_iterace.postupka1 & ~next_iterace.postupka2 & next_iterace.next_postupka2),
         (~next_iterace.postupka2 & next_iterace.next_postupka2),
         (~next_iterace.postupka1 & next_iterace.next_postupka1)],
        [1, 3, 2], default=0)

    next_iterace['next_body'] = next_iterace.body + next_iterace.body_stanicedo + next_iterace.premie_cas + \
                                next_iterace.premie_inday + next_iterace.premie_kraje + next_iterace.premie_postupka
    end = timer()
    e += (end-start)

    # ------------ Spanek ----------------

    start = timer()
    next_spanek = iterace.loc[~iterace.spanek &
                              (iterace.cas >= SPANEK_OD) & (iterace.cas <= SPANEK_DO) &
                              ((iterace.cas.dt.time >= time(hour=20)) | (iterace.cas.dt.time <= time(hour=2))),
                              iterace.columns]
    next_spanek['next_stanice'] = next_spanek['stanice']
    next_spanek['next_cas'] = next_spanek.cas+pd.Timedelta(6,'h')
    next_spanek['next_km'] = next_spanek.km
    druhyden = next_spanek.next_cas.dt.date > next_spanek.cas.dt.date
    next_spanek['next_inday'] = np.where(druhyden,
                                          1,
                                          next_spanek.inday)
    next_spanek['next_kraje'] = np.where(druhyden,
                                          ['0' * 13],
                                          next_spanek.kraje)
    next_spanek['next_postupka'] = np.where(druhyden,
                                             ['0' * 6],
                                             next_spanek.postupka)
    next_spanek['next_postupka1'] = next_spanek.next_postupka.str.slice(0, 4) == '1111'
    next_spanek['next_postupka2'] = next_spanek.next_postupka.str.slice(1, 5) == '1111'
    next_spanek['premie_cas'] = 0
    next_spanek['premie_inday'] = 0
    next_spanek['premie_kraje'] = 0
    next_spanek['premie_postupka'] = 0
    next_spanek['next_body'] = next_spanek.body + 5
    next_spanek['source'] = SPANEK
    next_spanek['x_odjezd'] = next_spanek['cas']

    next_iterace = pd.concat([next_iterace, next_spanek])
    next_iterace['next_spanek'] = np.where(next_iterace.source == SPANEK,
                                           True,
                                           next_iterace.spanek)
    end = timer()
    f += (end-start)
    start = timer()

    # zbavime se stejnych kombinaci s horsim casem
    next_iterace.sort_values(['next_cas','next_body','next_km'], inplace=True, ascending=[True,False,True])
    next_iterace = next_iterace.drop_duplicates(subset=['visited','next_spanek','next_stanice'],keep='first')
    end = timer()
    g += (end-start)
    start = timer()

    next_iterace['next_visited'] = np.where((next_iterace.source == SPANEK) | (next_iterace.next_stanice == CIL),
                                            next_iterace.visited,
                                            [x[0][:x[1] - 3000] + '1' + x[0][x[1] - 2999:]
                                             for x in zip(next_iterace['visited'], next_iterace['next_stanice'])])
    end = timer()
    h += (end-start)
    start = timer()

    next_iterace['next_vykon'] = count_vykon(next_iterace)
    end = timer()
    i += (end-start)
    start = timer()

    next_vysledky = next_iterace.loc[next_iterace.next_stanice.isin(CILS) &
                                     (CIL_OD <= next_iterace.next_cas) &
                                     (next_iterace.next_cas <= CIL_DO),
                                     next_iterace.columns]

    next_iterace = next_iterace.loc[next_iterace.next_stanice != CIL,next_iterace.columns]
    next_iterace.sort_values(['next_vykon', 'next_km'], ascending=[False, True], inplace=True)
    next_iterace = next_iterace.head(MAX_V_ITERACI)

    next_vysledky.sort_values(['next_vykon', 'next_km'], ascending=[False, True], inplace=True)
    next_vysledky = next_vysledky.head(MAX_VYSLEDKY)
    end = timer()
    j += (end-start)
    start = timer()

    if not next_iterace.empty:
        next_iterace = count_next_hrany(next_iterace)
    if not next_vysledky.empty:
        next_vysledky = count_next_hrany(next_vysledky)
    end = timer()
    k += (end-start)
    start = timer()

    next_iterace = next_iterace.reindex(['next_stanice','next_cas','next_body','next_km','next_kraje','next_visited',
                                         'next_hrany','next_inday','next_postupka','next_postupka1','next_postupka2',
                                         'next_spanek','next_vykon'],axis=1)
    next_iterace.columns = ['stanice','cas','body','km','kraje','visited','hrany','inday','postupka',
                            'postupka1','postupka2','spanek','vykon']
    next_vysledky = next_vysledky.reindex(['next_stanice','next_cas','next_body','next_km','next_kraje','next_visited',
                                         'next_hrany','next_inday','next_postupka','next_postupka1','next_postupka2',
                                         'next_spanek','next_vykon'],axis=1)
    next_vysledky.columns = ['stanice','cas','body','km','kraje','visited','hrany','inday','postupka',
                            'postupka1','postupka2','spanek','vykon']
    end = timer()
    l += (end-start)

    return next_iterace, next_vysledky


vysledky = pd.DataFrame(columns=['stanice','cas','body','km','kraje','visited','hrany','inday','postupka',
                                 'postupka1','postupka2','spanek','vykon'])
vysledky = vysledky.astype({"postupka1":bool,"postupka2":bool,"spanek":bool})

with open('data2\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('data2\\bhrany.pickle', 'rb') as handle:
    hrany = pickle.load(handle)
with open('data2\\checkpointy.pickle', 'rb') as handle:
    chp = pickle.load(handle)
with open('data2\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

aktivni = chp[chp.active]
active_chp = pd.Series(list(set(aktivni.index)-BLOCK), name='next_stanice')
if not CILS:
    CILS = list(aktivni.index)
presx = pres[(pres.index>=3000) & (pres.do<3000)].groupby('od').cas.min()
presx[[3000,3333]] = pd.Timedelta(0)
presx = presx.reindex(np.append(np.arange(3000,3297,1),3333))
presx = presx.fillna(pd.Timedelta(0))
pres_chp = pres[(pres.index.isin(aktivni.index)) & (pres.do.isin(aktivni.index))]
nazvy[IDSPANEK] = 'Spánek'
hrany = hrany.sort_values(['odjezd','od','do']).set_index('odjezd',drop=False)
chp['cas_docile'] = ciltime-chp.docile

celkdoba = CIL_DO - starttime
kmsec = TOTAL_KM/celkdoba.total_seconds()

iterace = pd.DataFrame({'stanice': [START],
                        'cas': [pd.to_datetime(starttime)],
                        'body': [0],
                        'km': [0.0],
                        'kraje': ['0'*13],
                        'visited': ['0'*297],
                        'hrany': [{}],
                        'inday': [0],
                        'postupka': ['0'*6],
                        'postupka1': [False],
                        'postupka2': [False],
                        'spanek': [False],
                        'vykon': [0]})
x = 0
a1 = a2 = a3 = b = c1 = c2 = c3 = d = e = f = g = h = i = j = k = l = 0

while len(iterace):
    x += 1
    iterace, new_vysledky = doIterace(iterace)
    vysledky = pd.concat([vysledky, new_vysledky])
    vysledky.sort_values(['vykon', 'km'], ascending=[False, True], inplace=True)
    vysledky = vysledky.head(MAX_VYSLEDKY)
    print(len(iterace))

print(a1)
print(a2)
print(a3)
print(b)
print(c1)
print(c2)
print(c3)
print(d)
print(e)
print(f)
print(g)
print(h)
print(i)
print(j)
print(k)
print(l)

vysledky.to_pickle('data2\\vysledky.pickle')

best_result = vysledky.iloc[0]
for stanice,(prev_stanice, cas, next_cas, premie_cas, premie_inday, premie_kraje, premie_postupka, body, km, trasa) in best_result.hrany.items():
    print(nazvy[stanice], cas, next_cas, premie_cas, premie_inday, premie_kraje, premie_postupka, body, round(km,1))