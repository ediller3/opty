from datetime import datetime
import pandas as pd

class Option:
  def __init__(self, row, quantity):
    self.symbol = row['symbol'].iloc[0]
    self.putOrCall = row['putCall'].iloc[0]
    self.costBasis = row['ask'].iloc[0]
    self.lastBid = row['bid'].iloc[0]
    self.lastAsk = row['ask'].iloc[0]
    self.lastVolatility = row['volatility'].iloc[0]
    self.dateExp = row['expirationDate'].iloc[0]
    self.quantity = quantity
    self.datePurchase = datetime.now()
    self.row = row
  def getOption(self):
    pRow = self.row
    pRow = pRow.drop(['ask','bid'], axis = 1)
    pRow.insert(0,'quantity',[self.quantity])
    pRow.insert(0, 'purchase date', [self.datePurchase.strftime("%m/%d/%Y, %H:%M")])
    print(pRow)
