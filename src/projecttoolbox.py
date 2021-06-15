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

"""

import requests

from database import UsersSQL

def sanitizecoininput(analyzedcryptos, dbinstance:UsersSQL):
    """
    First, converts input names to those reuired by the ConGeckoAPI.
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
    

    #this code fills "tempid" with all possible ids and "tempsymbol" with all possible symbols (es:"eth" for ethereum)
    
    # Useful if the API doesn't work properly
    #Various tries are made until the API actually sends the json
    scraped=False
    while scraped==False:
        try:
            response = requests.get("https://api.coingecko.com/api/v3/coins/list")
            response = response.json()
            if response!=[]:
                scraped=True
        except:
            time.sleep(2)

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


#If you want to test the sanitizer:
#test=UsersSQL()
#print(sanitizecoininput(['bitCoin','eTh','LTc'],test))
#print(sanitizecoininput('parola')) <= Will raise an error
