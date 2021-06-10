"""
TO DO.
"""


import requests
from database import UsersSQL,PricesSQL
import json
from pprint import pprint
import os 
import paho.mqtt.client as mqtt
import time

class Notifier:

    def __init__(self):
        self.pricesql=PricesSQL()


        try:
            with open(os.path.join("data","latestprices.json")) as f: 
                self.latestprice=json.load(f)
        except:
            self.pricesql.get_latest_prices()
            with open(os.path.join("data","latestprices.json")) as f:
                self.latestprice=json.load(f)           


        
        self.broker = os.environ.get("BROKER_ADDRESS")
        self.client=None
        self.connected=False
        self.currentprices={}

    def __objconnect(self):
        #connects this object to the mqtt broker that is saved in __init__
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
            else:
                print("Bad connection Returned code=",rc)

        self.client = mqtt.Client('Notifier_ingestion')
        self.client.on_connect = on_connect
        self.client.connect(self.broker, 1883, 60)
        self.connected=True


    def __scraper_percentagechange(self):
        #This code requests the data to the API and sends them to the MQTT
        self.__objconnect()
        self.client.loop_start()

        for crypto in self.latestprice:
            response= requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd')
            response=response.json()
            response=dict(response)
            self.currentprices[crypto]=round(response[crypto]['usd'],6)

        self.percentagechange={}
        for crypto in self.currentprices:
            # https://www.calculatorsoup.com/calculators/algebra/percent-change-calculator.php
            self.percentagechange[crypto]=round(((self.currentprices[crypto] - self.latestprice[crypto])/self.latestprice[crypto])*100,6)


        self.__mqttpublisher()
        self.client.loop_stop()


    def __mqttpublisher(self):
        #the actual mqtt publisher
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')

        path='percentagechange'
        self.client.publish(path,str(self.percentagechange), qos=1)



    def update_latest_prices(self):
        #Updates the json file to include the latest prices from the SQL table
        self.pricesql.get_latest_prices()

    def start(self,forever=True):
        
        if forever==False:
            while True:
                self.__scraper_percentagechange()
                time.sleep(60)
                
        else:
            self.__scraper_percentagechange()

            
            

test=Notifier()
test.start()

