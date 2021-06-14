"""
----------------------------------------------------------------
----- CoinGecko API price history Scraper and MQTT Publisher ---
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This script scrapes the data of the CoinGecko API and publishes that data to the correct
MQTT topic. The data includes the price history of each selected crypto.

Core features:
    * Scrapes the price history for any number of cryptos and any number of days
    * Publishes the crypto data into a customized MQTT topic called scraper/<name of the crypto>
    * Messages are sent in QOS 1

"""

import requests
import paho.mqtt.client as mqtt
from datetime import datetime
from projecttoolbox import *
from database import UsersSQL
from dotenv import load_dotenv
import os
import time

load_dotenv()

class PriceScraper:
    """ 
    Scrapes the price from the CoinGecko API and sends them to the scraper/"Name of the coin" topic in our 
    MQTT server.
    """
    def __init__(self,analyzedcryptos = None,analyzeddays=200):

        # list of all cryptos that we are interested in. 
        # the list must contain the correct coin id to work
        # To get a list of all coin IDs, the request url is "https://api.coingecko.com/api/v3/coins/list"
        if analyzedcryptos == None:
            db = UsersSQL()
            self.cryptos = list(db.get_coins_in_table())
        else:
             self.cryptos = analyzedcryptos

        # Warning: due to the automatic granularity of the API, daily data will be used for duration above 90 days.
        # Hourly data will be used for duration between 1 day and 90 days.
        if type(analyzeddays)==int or type(analyzeddays)==float:
            if int(analyzeddays)<=90:
                
                confirmdays=input("""
                This software has been designed to work with daily data.
                By selecting less than 90 days, you WILL be selecting hourly data due to the automatic granularity of the API.
                By selecting hourly data this code will still work and the data will be published
                to the correct MQTT topic. That said, the subscriber will refuse the data and will not push it in the SQL.
                Are you sure you want to proceed in selecting less than 90 days? (Y/N)
                """)
                confirmdays=confirmdays.lower()
                if 'y' in confirmdays:
                    print('ok')
                    self.days=int(analyzeddays)
                else:
                    self.days=200
            else:    
                self.days=int(analyzeddays)
        else:
            raise ValueError('Input days should be numeric. "max" is currently not supported.')

        #mqtt connecter
        self.broker = os.environ.get("BROKER_ADDRESS")
        self.client=None
        self.connected=False


    def objconnect(self):
        """
        Connects this object to the mqtt broker that is saved in __init__
        """
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
            else:
                print("Bad connection Returned code=",rc)

        self.client = mqtt.Client('scraperclient')
        self.client.on_connect = on_connect
        self.client.connect(self.broker, 1883, 60)
        self.connected=True


    def scrapepricedata(self):
        """
        Requests the data to the API and sends them to the MQTT
        """
        self.objconnect()
        self.client.loop_start()

        ncoin=0 #useful for debugging
        for crypto in self.cryptos:
            
            ncoin+=1
            print(ncoin,' ',crypto)


            # Useful if the API doesn't work properly
            #Various tries are made until the API actually sends the json
            scraped=False
            while scraped==False:
                try:
                    response= requests.get("https://api.coingecko.com/api/v3/coins/"+crypto+"/market_chart?vs_currency=usd&days="+str(self.days))
                    response=response.json()
                    response['prices']
                    scraped=True
                except:
                    time.sleep(2)
            
            # Sending tens of thousands of MQTT messages has proven to be fairly inefficient, as such we will send
            # less messages but bigger: each message contains the price history of the crypto.
            list_to_publish=[]
            for pricedatapoint in response['prices']:
                list_to_publish.append(list([crypto]+pricedatapoint))

            #time.sleep(0.7)
            self.mqttpublisher(crypto,list_to_publish)

        self.client.loop_stop()

    
    def mqttpublisher(self,crypto,list_to_publish):
        """
        The actual mqtt publisher
        """
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')

        path='scraper/'+crypto
        self.client.publish(path,str(list_to_publish), qos=1)
        
        

if __name__ == "__main__":
    print('Daily prices ingestion started: ', datetime.now()) # <- used for debugging

    # Connects to the SQL utentibot to get a list of every coin the users are interested in.
    mainscraper=PriceScraper(analyzeddays=200)
    mainscraper.scrapepricedata()

# the mqtt topic where things are being published is scraper/nomecrypto.
# for example, by publishing bitcoin data the topic will be: scraper/bitcoin


