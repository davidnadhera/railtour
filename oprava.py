import pickle
from consts import active

with open('C:\\Railtour\\hrany\\stops.pickle', 'rb') as handle:
    stops = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)
with open(f'C:\\Railtour\\hrany\\stops_zaloha.pickle', 'wb') as handle:
    pickle.dump(stops, handle, protocol=pickle.HIGHEST_PROTOCOL)

aktivni = active
print(len(stops))


stops2 = [x for x in stops if x[0] in aktivni]
print(len(stops2))


with open(f'C:\\Railtour\\hrany\\stops.pickle', 'wb') as handle:
    pickle.dump(stops2, handle, protocol=pickle.HIGHEST_PROTOCOL)