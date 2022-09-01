from tda import auth, client
import tda
import json
import config
import pandas as pd
import httpx
import datetime
import pprint


# TDA Ameritrade Token Authentication
try:
    #Authenticate using token if token exists
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    #Use Chromium webdriver to authenticate with TDA login
    from selenium import webdriver
    with webdriver.Chrome(executable_path="/Users/edwarddiller/Python/Opty/chromedriver") as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)
    print('ERROR: Authentication failed.')
    
# Get options chain, return JSON object
def get_opts(ticker, c_type='ALL', s_count=None, f_date=None, t_date=None):
    c.set_enforce_enums(False)
    #options = c.get_option_chain('AAPL',contract_type="CALL",strike_count=10,from_date=datetime.date(2022,9,1),to_date=datetime.date(2022,9,3))
    options = c.get_option_chain(ticker, contract_type=c_type)
    assert options.status_code == httpx.codes.OK, options.raise_for_status()
    query = options.json()
    return query

# Parse options chain, return pandas dataFrame
def parse(query):
    opt_chain = []
    for contr_type in ['callExpDateMap', 'putExpDateMap']:
        contract = dict(query)[contr_type]
        expirations = contract.keys()
        for expiry in list(expirations):
            strikes = contract[expiry].keys()
            for st in list(strikes):
                entry = contract[expiry][st][0]
                opt_chain.append(entry)
    df = pd.DataFrame(opt_chain)
    return df, contract

# Get ticker and Put/Call input from user
def getInput():
    ticker = input("Enter a valid ticker: ")
    putOrCall = input("Specify 'PUT', 'CALL' or leave blank for both: ")
    while putOrCall not in ['', 'PUT', 'CALL']:
        putOrCall = input("Please select ONLY PUT or CALL or nothing: ")
    if putOrCall == '': putOrCall = 'ALL'
    return [ticker, putOrCall]

# Get expiration date input from user
def getInputExpiry(df, contract):
    exp_frame = pd.DataFrame(contract.keys(),columns=["Expiration Date"])
    print(exp_frame)
    rows = exp_frame.size
    exp_i = int(input("Select an expiration date from list above (left column digit): "))
    while exp_i < 0 or exp_i > (rows - 1):
            exp_i = input("Select an expiration date from list above (left column digit): ")

    #Find chosen date:
    date_str = list(contract.keys())[exp_i] #Select date from contract keys in str format
    strike = list(contract[date_str].values())[0] #Choose dummy strike from list of strikes for selected date
    date_unix = strike[0]['expirationDate'] #Open list and return expirationDate in Unix format 

    #Print all strikes for chosen date:
    pd.set_option('display.max_rows', None)
    date_df = df.loc[df['expirationDate'] == date_unix]
    date_df.reset_index(inplace=True) #Resets row indexes
    print(date_df[['strikePrice','putCall','symbol','expirationDate','bid','ask','last','volatility']])

args = getInput()
q = get_opts(args[0], c_type=args[1])
df, contract = parse(q)
getInputExpiry(df, contract)