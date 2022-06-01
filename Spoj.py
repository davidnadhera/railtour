from datetime import datetime


class Spoj:
    def __init__(self, cas, idvlaky, doba):
        self.odjezd = cas
        self.idvlaky = idvlaky
        dt = datetime.combine(datetime.today(),cas) + doba
        self.prijezd = dt.time()
        self.doba = doba
        if self.prijezd < self.odjezd:
            self.druhyden = 1
        else:
            self.druhyden = 0