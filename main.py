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
from option import Option
from opty import *
from profile import Profile
import pickle

try:
    print("Profile loaded.")
    infile = open('profile','rb')
    profile = pickle.load(infile)
    infile.close()
except:
    print("No profile found. Creating new profile.")
    profile = Profile(5000)

def optionsChain():
    # Loop until valid ticker is received
    args = []
    while True:
        args = getTickerInput()
        try:
            q = getOpts(args[0])
            break
        except ValueError:
            print("Query failed. Invalid ticker likely.")
            pass

    try:  
        # Parse JSON query and return pandas df and dateMap dictionary
        df, contract = parse(q, args[1])

        # Get expiry input from user
        exp_unix = getExpiryInput(df, contract)

        #Get strike selection input from user
        order_df, strikeAnswer = getStrikeInput(df, exp_unix)

        #Get order input from user
        df_row, orderType, qty = getOrderInput(order_df, strikeAnswer)

        o = Option(df_row, qty)
        profile.buyOption(o)
    except Exception as e:
        print(e)
        return

#Main Menu input
def mainMenu():
    menuQuestion = [
    inquirer.List('menu',
                  message="Welcome to Opty",
                  choices=["Portfolio","Options Chain","Exit"]
                ),
    ]

    menuAnswer = inquirer.prompt(menuQuestion)
    match menuAnswer['menu']:
        case "Portfolio":
            profile.viewPortfolio()
        case "Options Chain":
            optionsChain()
        case "Exit":
            raise Exception("User has quit from the main menu.")

def main():
    while True:
        try:
            mainMenu()
        except Exception as e:
            outfile = open('profile', 'wb')
            pickle.dump(profile,outfile)
            outfile.close()
            print(e)
            break

if __name__ == '__main__':
    main()