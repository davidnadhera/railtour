# import numpy as np
# import pandas as pd
# from datetime import date, time, datetime, timedelta
# from Spoj import Spoj
# import pickle

# def myFun(e):
#     return datetime.combine(date(2021,6,1),e.prijezd) + timedelta(days = e.druhyden)

# with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
#     stanice = pickle.load(handle)
# with open('C:\\Railtour\\hrany\\graf.pickle', 'rb') as handle:
#     graf = pickle.load(handle)
# for i in list(graf.keys()):
#     hrany = sorted(graf[i][3334],key=lambda x: x.prijezd)
#     if not len(hrany):
#         stanice[i]['docile'] = datetime(2022,8,12,16,0)
#         continue
#     if hrany[0].prijezd > time(16,0):
#         hrana = hrany[-1]
#         stanice[i]['docile'] = datetime.combine(date(2022,8,11),hrana.prijezd) - hrana.doba
#         continue
#     else:
#         for hrana in hrany:
#             if hrana.prijezd <= time(16,0):
#                 stanice[i]['docile'] = datetime.combine(date(2022,8,12),hrana.prijezd) - hrana.doba
#             else:
#                 break

# print(stanice[3022]['docile'])

# with open('C:\\Railtour\\hrany\\stanice.pickle', 'wb') as handle:
#     pickle.dump(stanice, handle, protocol=pickle.HIGHEST_PROTOCOL)

import numpy as np
import pandas as pd
from datetime import date, time, datetime, timedelta
from Spoj import Spoj
import pickle

def myFun(e):
    return datetime.combine(date(2021,6,1),e.prijezd) + timedelta(days = e.druhyden)

with open('C:\\Railtour\\hrany\\stanice.pickle', 'rb') as handle:
    stanice = pickle.load(handle)
print(stanice)
# for i in stanice:
#     stanice[i]['dobapremie'] = stanice[i]['dobapremie']+timedelta(days=371)
#     stanice[i]['dobapremie2'] = stanice[i]['dobapremie2']+timedelta(days=371)


# with open('C:\\Railtour\\hrany\\stanice.pickle', 'wb') as handle:
#     pickle.dump(stanice, handle, protocol=pickle.HIGHEST_PROTOCOL)