"""
--------------------------------------------------------
---- Project Toolbox: useful and reusable functions ----
-------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This module contains utility functions that need to be called by multiple other files.

Functions currently included:
    * sanitizecoinput: Checks if the input list contains only coins that are listed in the CoinGecko API. 

"""

import requests

def sanitizecoininput(analyzedcryptos):
    """
    Checks if the input list contains only coins that are listed in the CoinGecko API.
    If a symbol (es: btc) is used, this function converts the list to the actual id.
    If the coin is present multiple times in the input list, this function will remove the redundancy 
    Arguments:
        :analyzedcryptos: list of strings
    """

    #Checks if the input is a list, otherwise, put it in a list
    if type(analyzedcryptos)!=list:
        cryptos=[analyzedcryptos]
    else:
        cryptos=analyzedcryptos
    

    #this code fills "tempid" with all possible ids and "tempsymbol" with all possible symbols (es:"eth" for ethereum)
    response= requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false")
    response=response.json()
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
    return ret


#If you want to test the sanitizer:
#print(sanitizecoininput(['bitCoin','eTh','LTc']))
#print(sanitizecoininput('parola')) <= Will raise an error
#print(sanitizecoininput(['bitcoin','bitcoin']))

