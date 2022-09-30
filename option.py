from datetime import datetime
import pandas as pd
from opty import getSpecificOpt

class Option:
  def __init__(self, row, quantity):
    self.symbol = row['symbol'].iloc[0]
    self.putCall = row['putCall'].iloc[0]
    self.costBasis = row['ask'].iloc[0]
    self.strike = row['strikePrice'].iloc[0]
    self.lastVolatility = row['volatility'].iloc[0]
    self.dateExp = row['expirationDate'].iloc[0]
    self.bid = row['bid'].iloc[0]
    self.ask = row['ask'].iloc[0]
    self.quantity = quantity
    self.datePurchase = datetime.now()

    self.profit = self.bid - self.costBasis


    ### NEED TO CHANGE HOW ASSETS ARE DISPLAYED BASED ON E*TRADE STYLE ###
    #Clean up row
    self.row = row
    #self.row.drop(['ask','bid'], axis = 1)
    self.row.insert(0,'profit',[self.profit])
    self.row.insert(0,'costBasis',[self.costBasis])
    self.row.insert(0,'quantity',[self.quantity])
    self.row.insert(0, 'purchaseDate', [self.datePurchase.strftime("%m/%d/%Y, %H:%M")])

  def refresh(self):
    contract = getSpecificOpt(self,self)
    self.bid = contract['bid']
    self.ask = contract['ask']
    self.lastVolatility = contract['volatility']
    self.profit = self.bid - self.costBasis