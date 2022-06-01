import pandas as pd
import pickle
from datetime import datetime

starttime = datetime(year=2021, month=8, day=2, hour=9, minute=0)

stan = pd.read_csv('C:\\users\\david\\downloads\\stanice (6).csv', names=['idstanice','nazev'], index_col='idstanice', quotechar='"')

stanice = {}


for i,nextstan in stan.iterrows():
    stanice[i] = nextstan['nazev']
stanice[3999] = 'Spánek'

print(stanice)

with open(f'C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'wb') as handle:
    pickle.dump(stanice, handle, protocol=pickle.HIGHEST_PROTOCOL)