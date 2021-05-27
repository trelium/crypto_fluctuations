import requests

def sanitizecoininput(analyzedcryptos):
    """
    Checks if the input list contains only coins that are listed in the CoinGecko API.
    If a symbol (es: btc) is used, this function converts the list to the actual id.
    """

    if type(analyzedcryptos)!=list:
        cryptos=[analyzedcryptos]
    else:
        cryptos=analyzedcryptos

    
    response= requests.get("https://api.coingecko.com/api/v3/coins/list")
    response=response.json()
    
    tempid=set()
    tempsymbol={}



    for i in response:
        tempid.add(i['id'])
        tempsymbol[i['symbol']]=i['id']
    
    ret=[]

    for crypto in cryptos:
        crypto=crypto.lower()
        if crypto in tempid:
            ret.append(crypto)
        elif crypto in tempsymbol:
            ret.append(tempsymbol[crypto])
        else:
            raise ValueError("The '{}' cryptocurrency is not listed in the coin list of CoinGecko.\nPlease refer to https://api.coingecko.com/api/v3/coins/list for a complete list of supported coins.".format(crypto))

    
    return ret
