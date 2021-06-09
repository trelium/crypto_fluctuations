"""
TO DO.
"""


import requests
from database import UsersSQL,PricesSQL
import json

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


