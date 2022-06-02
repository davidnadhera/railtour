import pickle

with open('C:\\railtour\\hrany\\hrany3041.pickle', 'rb') as handle:
    gvd = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice_nazvy.pickle', 'rb') as handle:
    nazvy = pickle.load(handle)
with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)

for trasa in gvd[3184]:
    trasa.vypisSpoje(nazvy,stan,0)
    print()