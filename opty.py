from tda import auth, client
import tda
import json
import config
import pandas as pd
import httpx
import datetime


# authenticate
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path="/Users/edwarddiller/Python/Opty/chromedriver") as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)
    print('ERROR: must authenticate')
    ASSERT(False)
    
# get options chain, return json object
def get_opts(ticker, c_type='ALL', s_count=None, f_date=None, t_date=None):
    c.set_enforce_enums(False)
    #options = c.get_option_chain('AAPL',contract_type="CALL",strike_count=10,from_date=datetime.date(2022,9,1),to_date=datetime.date(2022,9,3))
    options = c.get_option_chain(ticker, contract_type=c_type)
    assert options.status_code == httpx.codes.OK, options.raise_for_status()
    query = options.json()
    return query

# parse options chain, return panda dataFrame
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
    return df
def getBasicInput():
    ticker = input("enter the ticker: ")
    putOrCall = input("Specify PUT or CALL or nothing for both: ")
    while putOrCall not in ['', 'PUT', 'CALL']:
        putOrCall = input("Please select ONLY PUT or CALL or nothing: ")
    if putOrCall == '': putOrCall = 'ALL'
    return [ticker, putOrCall]

    
args = getBasicInput()
q = get_opts(args[0], c_type=args[1])
df = parse(q)


print(df[['putCall','symbol','daysToExpiration','strikePrice','bid','ask','last','volatility']])
