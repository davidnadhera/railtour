from datetime import datetime,date

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

class Trasa:
    def __init__(self,cas,idstart,body,km,kraje,hrany,countVykon,inday,predict_vykon=0,postupka=set()):
        self.cas = cas
        self.body = body
        self.km = km
        self.kraje = kraje
        self.hrany = hrany
        self.idstart = idstart
        self.countVykon = countVykon
        self.predict_vykon = predict_vykon
        self.postupka = postupka
        self.countVykon(self) 
        self.inday = inday

    def setBody(self, x):
        self.body = x
        self.countVykon(self)

    def setCas(self, x):
        self.cas = x
        self.countVykon(self)

    def __lt__(self, other):
        return self.vykon > other.vykon

    def vypisSpoje(self,nazvy,stan):
        for (hrana,_,koef_unavy) in self.hrany.values():
            hrana.vypisSpoje(nazvy,stan,koef_unavy)

    def vypisHlavicku(self,nazvy):
        premie = [x[1] for x in self.hrany.values() if x[1]>0]
        print(f'Stanice: {nazvy[list(self.hrany.keys())[-1]]}, Cas: {self.cas}, '
              f'Visited: {list(map(lambda x:nazvy[x],list(self.hrany.keys())))}, '
              f'Body: {self.body}, Km: {round(self.km,1)}, Vykon: {round(self.vykon,2)}, '
              f'Premie: {sum(premie)}')

    def vypisPointy(self,nazvy,stan):
        od = self.idstart
        for cil,(hrana,premie,koef_unavy) in self.hrany.items():
            koef_unavy = 0
            if cil == 3999:
                cil = od
                body = 5
                odjezd = hrana.odjezd
                prijezd = hrana.prijezd
            elif len(hrana.trasa) <= 1:
                body = stan[cil]["body"]
                odjezd = hrana.odjezd
                prijezd = hrana.prijezd
            else:
                body = stan[cil]["body"]
                odjezd = make_date(hrana.odjezd) - koef_unavy * stan[od]['presunx']
                odjezd = odjezd.time()
                prijezd = make_date(hrana.prijezd) + koef_unavy * hrana.lastPresun
                prijezd = prijezd.time()               
            print(f'Od: {nazvy[od]}, Do: {nazvy[cil]}, Odjezd: {odjezd}, Prijezd: {prijezd}, '
                  f'Km: {round(hrana.km,1)}, Body: {body}, Premie: {premie}')
            od = cil






      