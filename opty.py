from tda import auth, client
import json
import config
import pandas as pd

# authenticate
try:
    c = auth.client_from_token_file(config.token_path, config.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome(executable_path="/Users/edwarddiller/Python/Opty/chromedriver") as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path)
 
c.get_option_chain('AAPL')
