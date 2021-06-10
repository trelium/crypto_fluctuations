"""
TO DO.
"""


import requests
from database import UsersSQL,PricesSQL
import json
from pprint import pprint

class Notifier:


    def __init__(self):
        self.pricesql=PricesSQL()


        try:
            with open("latestprices.json") as f:
                self.latestprice=json.load(f)
        except:
            self.pricesql.get_latest_prices()
            with open("latestprices.json") as f:
                self.latestprice=json.load(f)           


        self.currentprices={}
        for crypto in self.latestprice:
            response= requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd')
            response=response.json()
            response=dict(response)
            self.currentprices[crypto]=round(response[crypto]['usd'],6)

        self.percentagechange={}
        for crypto in self.currentprices:
            # https://www.calculatorsoup.com/calculators/algebra/percent-change-calculator.php
            self.percentagechange[crypto]=round(((self.currentprices[crypto] - self.latestprice[crypto])/self.latestprice[crypto])*100,6)


    def update_latest_prices(self):
        #Updates the json file to include the latest prices from the SQL table
        self.pricesql.get_latest_prices()
            
            

test=Notifier()
pprint(test.percentagechange)