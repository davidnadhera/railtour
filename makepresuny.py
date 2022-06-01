import pandas as pd
import pickle

pres = pd.read_csv('C:\\users\\david\\downloads\\presuny.csv',names=['idpresuny','idstaniceod','idstanicedo','cas','km','vnitrni'])
pres['cas'] = pd.to_timedelta(pres['cas'])

stanice = pres.idstaniceod.unique()
presuny = {}

for s in stanice:
    pres_s = pres[(pres['idstaniceod']==s) & (pres['vnitrni']==1)]
    presuny_s_list = []
    for i,nextstan in pres_s.iterrows():
        presuny_s = {}
        presuny_s['idstanicedo'] = nextstan['idstanicedo']
        presuny_s['cas'] = nextstan['cas']
        presuny_s['km'] = nextstan['km']
        presuny_s_list.append(presuny_s)
    if presuny_s_list:
        presuny[s] = presuny_s_list

print(presuny)

with open(f'C:\\Railtour\\hrany\\presuny.pickle', 'wb') as handle:
    pickle.dump(presuny, handle, protocol=pickle.HIGHEST_PROTOCOL)



