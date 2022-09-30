from multiprocessing.sharedctypes import Value
from sre_constants import CALL
from wsgiref import validate
from tda import auth, client
import tda
import json
import config
import pandas as pd
import httpx
import datetime
import pprint
import re
import inquirer

# TDA Ameritrade Token Authentication
def tdaAuth():
    try:
        #Authenticate using token if token exists
        c = auth.client_from_token_file(config.token_path, config.api_key)
    except FileNotFoundError:
        #Use Chromium webdriver to authenticate with TDA login
        from selenium import webdriver
        with webdriver.Chrome(executable_path="/Users/edwarddiller/Python/Opty/chromedriver") as driver:
            c = auth.client_from_login_flow(driver, config.api_key, config.redirect_uri, config.token_path)
        print('ERROR: Authentication failed.')

    return c
    
# Get options chain, return JSON object
def getOpts(ticker, s_count=None, f_date=None, t_date=None):
    c = tdaAuth()
    c.set_enforce_enums(False)
    #options = c.get_option_chain('AAPL',contract_type='PUT',strike_count=10,from_date=datetime.date(2022,9,1),to_date=datetime.date(2022,10,20))
    options = c.get_option_chain(ticker, contract_type='ALL')
    assert options.status_code == httpx.codes.OK, options.raise_for_status()
    query = options.json()

    if query['status'] ==  'FAILED':
        raise ValueError("Query failed. Invalid ticker possible.")

    return query

#Pulls new data from TDA-API and returns dictionary with latest data for given option object
def getSpecificOpt(c, option):
    c = tdaAuth()
    c.set_enforce_enums(False)
    ticker = option.symbol.split('_')[0]
    options = c.get_option_chain(ticker, contract_type=option.putCall, strike=option.strike, from_date=option.dateExp, to_date=option.dateExp)
    assert options.status_code == httpx.codes.OK, options.raise_for_status()
    query = options.json()
    
    dict = {}
    if option.putCall == "CALL":
        dict = query['callExpDateMap']
    elif option.putCall == "PUT":
        dict = query['putExpDateMap']

    #Goes through dictionary to get to sub dictionary for our target contract
    contract = list(list(dict.values())[0].values())[0][0]

    return contract

# Parse options chain, return pandas dataFrame
def parse(query, putCall):
    opt_chain = []

    map = []
    match putCall:
        case 'CALL':
            map = ['callExpDateMap']
        case 'PUT':
            map = ['putExpDateMap']
        case 'ALL':
            map = ['callExpDateMap', 'putExpDateMap']

    for contr_type in map:
        contract = dict(query)[contr_type]
        expirations = contract.keys()
        for expiry in list(expirations):
            strikes = contract[expiry].keys()
            for st in list(strikes):
                entry = contract[expiry][st][0]
                opt_chain.append(entry)

    df = pd.DataFrame(opt_chain)
    return df, contract

# Get ticker and Put/Call input from user and return args for tda-api client request
def getTickerInput():

    tickerQuestion = [
    inquirer.Text('ticker',
                message="Enter a valid ticker",
                ),
    inquirer.List('putCall',
                  message="Select an order type",
                  choices=["Put","Call","Put & Call"]
                ),
    ]

    tickerAnswers = inquirer.prompt(tickerQuestion)

    ticker = tickerAnswers['ticker']
    putCall = tickerAnswers['putCall']

    match putCall:
        case "Put":
            putCall = "PUT"
        case "Call":
            putCall = "CALL"
        case "Put & Call":
            putCall = "ALL"
        
    return [ticker, putCall]

# Get expiration date input from user and return Unix date
def getExpiryInput(df, contract):
    expiryList = list(contract.keys())
    expiryList.insert(0, "Back")

    expiryQuestion = [
    inquirer.List('date',
                  message="Please select an expiration date (yyyy-mm-dd:DTE)",
                  choices=expiryList,
              ),
    ]

    expiryAnswer = inquirer.prompt(expiryQuestion)
    if expiryAnswer['date'] == "Back":
        raise Exception

    #Find chosen date:
    strike = list(contract[expiryAnswer['date']].values())[0] #Choose dummy strike from list of strikes for selected date
    date_unix = strike[0]['expirationDate'] #Open list and return expirationDate in Unix format 

    return date_unix

#Get strike selection input from user
def getStrikeInput(df,date_unix):

    #Print all strikes for chosen date:
    pd.set_option('display.max_rows', None)
    date_df = df.loc[df['expirationDate'] == date_unix]
    date_df.reset_index(inplace=True) #Resets row indexes

    #Convert display of Unix timestamps to Datetime Dates for readability
    for i in date_df.index:
        date = datetime.datetime.fromtimestamp((date_df.loc[i,'expirationDate'])/1000.0).date()
        date_df.loc[i,'expirationDate'] = date

    date_df = date_df[['strikePrice','putCall','symbol','expirationDate','bid','ask','last','volatility']]
    print(date_df)

    strike_list = date_df['strikePrice'].values.tolist()

    def strike_validation(strikeAnswer, current):
        if not float(current) in strike_list:
            raise inquirer.errors.ValidationError("", reason="Invalid strike")

        return True

    strikeQuestion = [
        inquirer.Text(
            "strike",
            message="Enter a valid strike from the list above",
            validate=strike_validation,
        ),
    ]

    strikeAnswer = inquirer.prompt(strikeQuestion)
    return date_df, strikeAnswer

#Take in input on purchase order and return pandas df row for selected options contract
def getOrderInput(df, strikeAnswer):
    df_row = df.loc[df['strikePrice'] == float(strikeAnswer['strike'])]
    #df_row = df_row.set_index('strikePrice')
    print()
    print(' Selected Contract '.center(90, '='))
    print()
    print(df_row)
    print()
    print(''.center(90, '='))
    print()

    def qty_validation(orderAnswers, current):
        if int(current) < 1:
            raise inquirer.errors.ValidationError("", reason="Invalid order quantity.")

        return True
    
    orderQuestion = [
    inquirer.List('order',
                  message="Select an order type",
                  choices=["Buy","Sell"]
              ),
    inquirer.Text(
        "qty",
        message="Enter the quantity",
        validate=qty_validation
    ),
    ]

    orderAnswers = inquirer.prompt(orderQuestion)

    return df_row, orderAnswers['order'], int(orderAnswers['qty'])
    
