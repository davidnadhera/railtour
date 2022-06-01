import pandas as pd
import pickle
from datetime import datetime

starttime = datetime(year=2022, month=8, day=8, hour=9, minute=0)

stan = pd.read_csv('C:\\users\\david\\downloads\\stanice (7).csv', names=['idstanice','body','dobapremie','dobapremie2',
                    'idkraj','presunx'], index_col='idstanice')
stan['presunx'] = pd.to_timedelta(stan['presunx'],unit='s')
stan['dobapremie'] = pd.to_timedelta(stan['dobapremie'],unit='h') + starttime
stan['dobapremie2'] = pd.to_timedelta(stan['dobapremie2'],unit='h') + starttime

stanice = {}


for i,nextstan in stan.iterrows():
    s = {}
    s['body'] = nextstan['body']
    s['dobapremie'] = nextstan['dobapremie']
    s['dobapremie2'] = nextstan['dobapremie2']
    s['idkraj'] = nextstan['idkraj']
    s['presunx'] = nextstan['presunx']
    stanice[i] = s

print(stanice)

with open(f'C:\\Railtour\\hrany\\stanice.pickle', 'wb') as handle:
    pickle.dump(stanice, handle, protocol=pickle.HIGHEST_PROTOCOL)