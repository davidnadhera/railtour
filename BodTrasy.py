from datetime import timedelta


class BodTrasy:
    def __init__(self, idstanice, cas, km, body, kraje, inday, hrana, premie):
        self.cas = cas
        self.idstanice = idstanice
        self.kraje = kraje
        self.km = km
        self.body = body
        self.inday = inday
        self.docile = timedelta(hours=0)
        self.hrana = hrana
        self.premie = premie
