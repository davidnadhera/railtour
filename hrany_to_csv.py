from datetime import date, time, datetime, timedelta
import pickle
import json
import csv

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

def add_time(t,i):
    return (make_date(t)+i).time()

fieldnames = ['id', 'od', 'do', 'km', 'prijezd', 'casod', 'casdo', 'trasa', 'body', 'presunx', 'doba', 'druhyden']
rows = []
id=1

with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stan = pickle.load(handle)

rows = {}
for start in list(range(3000,3297))+[3333,3334]:
    rows[start] = []

for start in list(range(3000,3297))+[3333]:
    with open(f'C:\\Railtour\\hrany\\hrany{start}.pickle', 'rb') as handle:
        seznam = pickle.load(handle)
    for cil,hrany in seznam.items():
        prev_time = time(0,0)
        for hrana in hrany:
            if hrana.doba<=timedelta(hours=9):
                if make_date(prev_time)<make_date(hrana.odjezd)-timedelta(hours=9):
                    prev_time = (make_date(hrana.odjezd)-timedelta(hours=9)).time()
                if hrana.prijezd.time() < hrana.odjezd:
                    druhyden = 1
                else:
                    druhyden = 0
                trasa = []
                for spoj in hrana.trasa:
                    trasa.append(str(spoj.od))
                str_trasa = '{'+','.join(trasa)+'}'
                row = {
                    'id' : id,
                    'od': start,
                    'do': cil,
                    'km': round(hrana.km,1),
                    'prijezd': hrana.prijezd.time(),
                    'casod': prev_time,
                    'casdo': hrana.odjezd,
                    'trasa': str_trasa,
                    'body': stan[cil]['body'],
                    'presunx': hrana.lastPresun.total_seconds(),
                    'doba': str(hrana.doba)[-8:],
                    'druhyden': druhyden,
                }
                rows[start].append(row)
                rows[cil].append(row)
                id += 1
                prev_time = (make_date(hrana.odjezd) + timedelta(seconds=1)).time()
        if hrany:
            hrana = hrany[0]
            if hrana.doba<=timedelta(hours=9):
                if make_date(prev_time)<make_date(hrana.odjezd)-timedelta(hours=9)+timedelta(days=1):
                    prev_time2 = (make_date(hrana.odjezd)-timedelta(hours=9)).time()
                else:
                    prev_time2 = prev_time
                if prev_time2 >= prev_time:
                    druhyden = 1
                    trasa = []
                    for spoj in hrana.trasa:
                        trasa.append(str(spoj.od))
                    str_trasa = '{'+','.join(trasa)+'}'
                    doba = make_date(hrana.prijezd.time())+timedelta(days=1)-make_date(time(23,59,59))
                    row = {
                        'id' : id,
                        'od': start,
                        'do': cil,
                        'km': round(hrana.km,1),
                        'prijezd': hrana.prijezd.time(),
                        'casod': prev_time2,
                        'casdo': time(23,59,59),
                        'trasa': str_trasa,
                        'body': stan[cil]['body'],
                        'presunx': hrana.lastPresun.total_seconds(),
                        'doba': str(doba)[-8:],
                        'druhyden': druhyden,
                    }
                    rows[start].append(row)
                    rows[cil].append(row)
                    id += 1

for start in list(range(3000,3297)):
    with open(f'C:\\Railtour\\csv_hrany\\hrany{start}.csv', 'w+', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
        writer.writerows(rows[start])
