"""
---------------------------------------------------------
---- Project Toolbox: project-wide utility functions ----
---------------------------------------------------------
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This module contains utility functions that need to be called by multiple other files.

Functions currently included:
    * sanitizecoinput: Checks if the input list contains only coins that are listed in the CoinGecko API. 
    * savesupportedcoins: saves the supportedcoins in a json for fast lookup - we noticed that the API is not as fast as just loading the json, so that is why we're using this system.

"""

import requests
from database import UsersSQL
import time
import os
import json

def sanitizecoininput(analyzedcryptos, dbinstance:UsersSQL):
    """
    First, converts input names to those required by the ConGeckoAPI.
    If a symbol (es: btc) is used, this function converts the name to the actual crypto id.
    Then, it returns a list containing only those input names that are also among the currently 
    accepted ones (as returned by get_coins_in_table) - an instanced database is necessary for the function to operate.
    If the coin is present multiple times in the input list, this function will remove the redundancy 
    Arguments:
        :analyzedcryptos: list of strings
    """
    trackedcoins = dbinstance.get_coins_in_table()

    #Checks if the input is a list, otherwise, put it in a list
    if type(analyzedcryptos)!=list:
        cryptos=[analyzedcryptos]
    else:
        cryptos=analyzedcryptos
      
    
    #Loads the data from supported coins, if supportedcoins.json is not present, create it. If everything fails, load the data from the API
    try:
        try:
            projectfolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(projectfolder,"data","supportedcoins.json")) as f:
                response=json.load(f)
                # If the json is not present, create it
        except:
            createtable=UsersSQL()
            savesupportedcoins(createtable)
            projectfolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(projectfolder,"data","supportecoins.json")) as f:
                response=json.load(f)           
    except:
        scraped=False
        while scraped==False:
            # Useful if the API doesn't work properly
            #Various tries are made until the API actually sends the json
            try:
                response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")
                response = response.json()
                if response!=[]:
                    scraped=True
            except:
                time.sleep(1)

    
    #this code fills "tempid" with all possible ids and "tempsymbol" with all possible symbols (es:"eth" for ethereum)
    tempid=set()
    tempsymbol={}
    for i in response:
        tempid.add(i['id'])
        tempsymbol[i['symbol']]=i['id']


    # Checks if the cryptos in the input list are present in either tempid OR tempsymbol.
    # IF this condition is not satisfied, raise an error.
    ret=[]
    for crypto in cryptos:
        crypto=crypto.lower().replace(' ','-')
        if crypto in tempid:
            if crypto not in ret:
                ret.append(crypto)
        elif crypto in tempsymbol:
            ret.append(tempsymbol[crypto])
        else:
            raise ValueError(f"\nThe '{crypto}' cryptocurrency is not listed in the coin list of CoinGecko.\nPlease refer to https://api.coingecko.com/api/v3/coins/list for a complete list of supported coins.")

    #returns a sanitized list (each crypto in lowercase, each symbol translated to the corresponding crypto)
    #containing only those names currently part of get_coins_in_table
    sanitized = [coin for coin in ret if coin in trackedcoins]
    
    return sanitized


def savesupportedcoins(dbinstance:UsersSQL):
    """
    saves the supportedcoins in a json for fast lookup - we noticed that the API is not as fast as just loading the json, so that is why we're using this system.
    """

    # Useful if the API doesn't work properly
    #Various tries are made until the API actually sends the json
    trackedcoins = dbinstance.get_coins_in_table()

    scraped=False
    while scraped==False:
        try:
            response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")
            response = response.json()
            if response!=[]:
                scraped=True
        except:
            time.sleep(1)

    supportedcoins=[]

    for i in response:
        if i['id'] in trackedcoins:
            tempdict={}
            tempdict['id']=i['id']
            tempdict['symbol']=i['symbol']
            supportedcoins.append(tempdict)

    projectfolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(projectfolder,"data","supportedcoins.json"), "w") as out_file:
        json.dump(supportedcoins,out_file,indent=0)



#If you want to test the sanitizer:
#test=UsersSQL()
#print(savesupportedcoins(test))
#print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
# print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
#print(sanitizecoininput('parola')) <= Will raise an error
