from datetime import datetime,date

def make_date(x):
    return datetime.combine(date(2021,6,1),x)

class Trasa2:
    def __init__(self,cas,idstart,body,km,kraje,hrany,countVykon,inday,cil,ciltime):
        self.cas = cas
        self.body = body
        self.km = km
        self.kraje = kraje
        self.hrany = hrany
        self.idstart = idstart
        self.countVykon = countVykon
        self.countVykon(self) 
        self.inday = inday
        self.cil = cil
        self.ciltime = ciltime

    def setBody(self, x):
        self.body = x
        self.countVykon(self)

    def setCas(self, x):
        self.cas = x
        self.countVykon(self)

    def __lt__(self, other):
        return self.vykon > other.vykon

    def vypisSpoje(self,nazvy,stan):
        for bod in self.hrany.values():
            bod.hrana.vypisSpoje(nazvy,stan,0)

    def vypisHlavicku(self,nazvy):
        premie = [x.premie for x in self.hrany.values() if x.premie>0]
        print(f'Visited: {list(map(lambda x:nazvy[x],list(self.hrany.keys())))}, '
              f'Body: {self.body}, Km: {round(self.km,1)}, Vykon: {round(self.vykon,2)}, '
              f'Premie: {sum(premie)}')

    def vypisPointy(self,nazvy,stan):
        od = self.idstart
        for cil,bod in self.hrany.items():
            if cil == 3999:
                cil = od
                body = 5
                odjezd = bod.hrana.odjezd
                prijezd = bod.hrana.prijezd
            else:
                body = stan[cil]["body"]
                odjezd = bod.hrana.odjezd
                prijezd = bod.hrana.prijezd            
            print(f'Od: {nazvy[od]}, Do: {nazvy[cil]}, Odjezd: {odjezd}, Prijezd: {prijezd}, '
                  f'Km: {round(bod.hrana.km,1)}, Body: {body}, Premie: {bod.premie}')
            od = cil
