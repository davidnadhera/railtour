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

stan = pd.read_csv('C:\\idos\\stanice (3).csv',names=['idstanice','nazev','checkpoint','body','prestup'],
                    index_col='idstanice', quotechar='"')
pres = pd.read_csv('C:\\idos\\presuny.csv',names=['idpresuny','idstaniceod','idstanicedo','cas','km','vnitrni'],
                    quotechar='"')
odj = pd.read_csv('C:\\idos\\odjezdy.csv',names=['idodjezdy','cas','idvlaky','idstanice','druhyden','poradi'],
                    quotechar='"', parse_dates=['cas'])
with open(f'C:\\railtour\\hrany\\hrany3001.pickle', 'rb') as handle:
    seznam = pickle.load(handle)

with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)


for trasa in seznam[3000]:
    trasa.vypisSpoje(nazvy,stan,0)
    print(trasa.prijezd)
    print(trasa.doba)
    print()