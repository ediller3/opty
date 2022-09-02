class Profile:
  def __init__(self, balance=0):
    # assets is a symbol to list of Option objects dictionary
    self.assets = {}
    # # balance represents the money associated to a given profile
    # self.balance = balance

  def buyOption(self, option):
    symbol = option.symbol
    print(symbol)
    if symbol in self.assets:
      self.assets[symbol].append(option)
    else:
      self.assets[symbol] = [option]

  def sellOption(self, option):
    pass

  def viewPortfolio(self):
    for _, options in self.assets.items():
      for o in options:
        o.getOption()

