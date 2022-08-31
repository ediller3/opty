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
 
c.set_enforce_enums(False)

opt_chain = []
options = c.get_option_chain('AAPL',contract_type="CALL",strike_count=10,from_date=datetime.date(2022,9,1),to_date=datetime.date(2022,9,3))
assert options.status_code == httpx.codes.OK, options.raise_for_status()
query = options.json()

for contr_type in ['callExpDateMap', 'putExpDateMap']:
    contract = dict(query)[contr_type]
    expirations = contract.keys()
    for expiry in list(expirations):
        strikes = contract[expiry].keys()
        for st in list(strikes):
            entry = contract[expiry][st][0]
            opt_chain.append(entry)
df = pd.DataFrame(opt_chain)
print(df.columns)
print(df[['putCall','symbol','daysToExpiration','strikePrice','bid','ask','last','volatility']])
