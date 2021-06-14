"""
----------------------------------------------------------------
----- CoinGecko API Current Price Scraper and MQTT Publisher ---
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This scripts scrapes the current price data from the CoinGecko API, compares it to the price of 
the day before, calculates the percentage change for each given coin and publishes the percentage
change in an MQTT topic.
The data includes the current price of each crypto the user is interested in.

Core features:
    * Scrapes the current price of each crypto in the users table.
    * Compares it to the day before price and calculates the percentage change
    * The percentage change of all coins is sent by a dictionary data structure
    * Publishes the crypto data into a customized MQTT topic called percentagechange
    * The day before prices are saved in a json and updated daily by historicingestion.py
    * Messages are sent in QOS 1


"""

import requests
from database import UsersSQL,PricesSQL
import json
from pprint import pprint
import os 
import paho.mqtt.client as mqtt
import time

class NotifierPublish:
    """
    Scrapes the current price data from the CoinGecko API, compares it to the price of 
    the day before, calculates the percentage change for each given coin and publishes the percentage
    change in an MQTT topic.
    """

    def __init__(self):
        # Reads the prices from the day before by using the dedicated json
        self.pricesql=PricesSQL()
        projectfolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            with open(os.path.join(projectfolder,"data","latestprices.json")) as f:
                self.latestprice=json.load(f)
        # If the json is not present, create it
        except:
            self.pricesql.get_latest_prices()
            with open(os.path.join(projectfolder,"data","latestprices.json"), "w") as f:
                self.latestprice=json.load(f)           

        #MQTT connector
        self.broker = os.environ.get("BROKER_ADDRESS")
        self.client=None
        self.connected=False
        self.currentprices={}

    def __objconnect(self):
        #connects this object to the mqtt broker that is saved in __init__
        #the client id is "Notifier_ingestion"
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
        #This code requests the data to the API and sends them to the dedicated topic in the MQTT
        self.__objconnect()
        self.client.loop_start()

        # Creates a dictionary of all currentprices
        for crypto in self.latestprice['prices']:

            #this try and except is to make sure that the api is working.
            #Various tries are made until the API actually sends the json
            scraped=False
            while scraped==False:
                try:
                    response= requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd')
                    response=response.json()
                    response[crypto]
                    response=dict(response)
                    scraped=True
                except:
                    time.sleep(1)
            
            self.currentprices[crypto]=round(response[crypto]['usd'],6)

        # Compares the prices from the day before (latestprices) to the
        # current prices and calculates the percentage change
        # the percentage change are formatted in a dictionary
        self.percentagechange={}
        for crypto in self.currentprices:
            # details about the formula:
            # https://www.calculatorsoup.com/calculators/algebra/percent-change-calculator.php
            if self.latestprice['prices'][crypto]!=0:
                self.percentagechange[crypto]=round(((self.currentprices[crypto] - self.latestprice['prices'][crypto])/self.latestprice['prices'][crypto])*100,6)
            else:
                self.percentagechange[crypto]=0
        #published the data into the MQTT and disconnects
        self.__mqttpublisher()
        self.client.loop_stop()

    def __mqttpublisher(self):
        #the actual mqtt publisher
        #the used topic is "percentagechange"
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')
        
        #We save the timestamp of latestprices.json. It will be useful for comparing it to today prices for notifications
        self.percentagechange['timestamp of yesterday prices']=self.latestprice['timestamp']

        path='percentagechange'
        self.client.publish(path,str(self.percentagechange), qos=1)

    def update_latest_prices(self):
        #Updates the json file to include the latest prices from the SQL table
        self.pricesql.get_latest_prices()

    def start(self,forever=True):
        # Executes most of the previous scripts:
        # Scrapes the data and publishes it
        # If forever is True, it does so every minute
        if forever==True:
            while True:
                self.__scraper_percentagechange()
                print(self.percentagechange)
                time.sleep(40)
                
        else:
            self.__scraper_percentagechange()
            print(self.percentagechange)

            
            
if __name__ == "__main__": 
    percentagepublisher=NotifierPublish()
    percentagepublisher.start(forever=True)

