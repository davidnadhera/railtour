import pickle
from datetime import time,datetime,timedelta

with open('C:\\Railtour\\hrany\\schema_full.pickle', 'rb') as handle:
    schema = pickle.load(handle)
# with open('C:\\Railtour\\hrany\\schema_full.pickle', 'rb') as handle:
#     schema = pickle.load(handle)
with open('C:\\Railtour\\hrany\\presuny.pickle', 'rb') as handle:
    pres = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)
with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
    graf = pickle.load(handle)
with open('C:\\Railtour\\hrany\\vykony_schema.pickle', 'rb') as handle:
    vykony = pickle.load(handle)

print(vykony[3333,time(9,1)])

# docile = schema[(3333,time(15,57))]

# for idstanice in docile:
#     info = docile[idstanice]
#     (doba,hrana,vykon) = info
#     print(idstanice,str(doba))

# casy = [x[1] for x in schema if x[0]==3286]
# casy = sorted(casy)
# print(casy)

odjezdy = schema[(3333,time(9,0))]
odjezd = odjezdy[3002]
print(odjezd)

# odjezdy = graf[3286][3333]
# for trasa in odjezdy:
#     trasa.vypisSpoje(nazvy,stan,0)
#     print()

