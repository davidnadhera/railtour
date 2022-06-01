import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from Spoj import Spoj
import pickle
from consts import active


graf = {}

for i in set(active)-set([3334]):
    podgraf = {}
    with open(f'C:\\Railtour\\hrany\\hrany{i}.pickle', 'rb') as handle:
        seznam = pickle.load(handle)
    for j in active:
        podgraf[j] = seznam[j]
    graf[i] = podgraf


with open(f'C:\\Railtour\\hrany\\graf.pickle', 'wb') as handle:
    pickle.dump(graf, handle, protocol=pickle.HIGHEST_PROTOCOL)