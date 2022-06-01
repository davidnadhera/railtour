from Spoj import Spoj

class SpojHrany(Spoj):
  def __init__(self,od,do,cas,idvlaky,doba):
      super().__init__(cas,idvlaky,doba)
      self.od = od
      self.do = do
