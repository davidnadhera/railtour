from datetime import datetime
import pickle

starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)
CIL_DO = datetime(year=2021, month=8, day=6, hour=16, minute=0)

def countVykon1(trasa):
    doba = trasa.cas-starttime
    if doba:
        trasa.vykon = trasa.body/doba.total_seconds()*60.0*60.0 
    else:
        trasa.vykon = 0.0

def countVykonF(trasa):
    doba = CIL_DO-starttime
    if doba:
        trasa.vykon = trasa.body/doba.total_seconds()*60.0*60.0 
    else:
        trasa.vykon = 0.0

with open('C:\\Railtour\\hrany\\vysledky.pickle', 'rb') as handle:
    vysledky = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)

vysledky.sort(reverse=True, key=lambda x:(x.body,-x.km))

for x in range(1):
    trasa = vysledky[x]
    trasa.vypisHlavicku(nazvy)
    trasa.vypisPointy(nazvy,stan)
 #   trasa.vypisSpoje(nazvy,stan)