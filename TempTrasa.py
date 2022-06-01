from datetime import timedelta, datetime, date

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

class TempTrasa:
    def __init__(self, odjezd):
        self.odjezd = odjezd.time()
        self.doba = timedelta(days=10)
        self.trasa = []
        self.km = 0.0
        self.presun = True
        self.lastPresun = timedelta(seconds=0)
        self.prijezd = (odjezd + timedelta(days=10))

    def __lt__(self, other):
        # return self.doba < other.doba
        if self.prijezd != other.prijezd:
            return self.prijezd < other.prijezd
        elif self.idstanice == other.idstanice:
            return self.odjezd > other.odjezd
        else:
            return self.idstanice < other.idstanice

    def setDoba(self, doba):
        self.doba = doba
        dt = datetime.combine(date(2021,6,1),self.odjezd) + doba
        self.prijezd = dt

    def setPrijezd(self, cas):
        self.prijezd = datetime.combine(self.prijezd.date(),cas)
        self.doba = self.prijezd-datetime.combine(date(2021,6,1),self.odjezd)

    def vypisSpoje(self,nazvy,stan,koef_unavy):
        for i,spoj in enumerate(self.trasa):
            odjezd = spoj.odjezd
            prijezd = spoj.prijezd
            if (i == 0) and (len(self.trasa) > 1):
                odjezd = make_date(odjezd) - koef_unavy * stan[spoj.od]['presunx']
                odjezd = odjezd.time()
            if (i == len(self.trasa)-1) and (len(self.trasa) > 1):
                prijezd = make_date(prijezd) + koef_unavy * self.lastPresun
                prijezd = prijezd.time()
            print(f'Od: {nazvy[spoj.od]}, Do: {nazvy[spoj.do]}, Odjezd: {odjezd}, Prijezd: {prijezd}')

    def to_dict(self):
        result = {'odjezd': str(self.odjezd),
                  'doba': str(self.doba),
                  'km': self.km,
                  'presundo': str(self.lastPresun),
                  'trasa': []}
        for i,spoj in enumerate(self.trasa):
            dict_spoj = {'odjezd': str(spoj.odjezd),
                         'prijezd': str(spoj.prijezd),
                         'vlak': spoj.idvlaky,
                         'od': spoj.od,
                         'do': spoj.do}
            result['trasa'].append(dict_spoj)
        return result


        