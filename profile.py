import pandas as pd

class Profile:
  def __init__(self, balance=0):
    # Assets is a dictionary of held contacts (key = symbol, value = option object)
    self.assets = {}

    # balance represents the money associated to a given profile
    self.balance = balance;

  def buyOption(self, option):
    ### NEED TO PRINT ORDER CONFIRMATION ###
    if option.costBasis * 100 < self.balance:
      self.assets[option.symbol] = option
      self.balance -= option.costBasis * option.quantity * 100
    else:
      raise Exception("Insufficient funds.")

  def sellOption(self, option):
    pass

  def refreshAssets(self):
    #pulls latest bid, ask, volatility for all contracts in portfolio
    for _, option in self.assets.items():
      option.refresh()

  def viewPortfolio(self):
    self.refreshAssets()
    print()
    print(' Portfolio '.center(90, '='))
    print()
    print("Current Balance: $" + "{:.2f}".format(self.balance))
    print()
    print(''.center(90, '-'))
    print("Assets:")
    print()

    if len(self.assets) > 0:
      frames = []
      for _, option in self.assets.items():
          frames.append(option.row)
      result = pd.concat(frames)
      print(result)
      
    print(''.center(90, '='))
    print()


