"""
----------------------------------------------------------------
----- CoinGecko API price history Scraper and MQTT Publisher ---
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This scripts scrapes the data of the CoinGecko API and publishes that data to the correct
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
from dotenv import load_dotenv
import os

load_dotenv()



class PriceScraper:
    """ 
    Scrapes the price from the CoinGecko API and sends them to the scraper/"Name of the coin" topic in our 
    MQTT server.
    """

    def __init__(self,analyzedcryptos,analyzeddays=200,projectbroker='13.73.184.147'):

        # list of all cryptos that we are interested in. 
        # the list must contain the correct coin id to work
        # To get a list of all coin IDs, the request url is "https://api.coingecko.com/api/v3/coins/list"
        self.cryptos=sanitizecoininput(analyzedcryptos)

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
        self.broker=projectbroker
        self.client=None
        self.connected=False

    def objconnect(self):
        #connects this object to the mqtt broker that is saved in __init__
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
        #This code requests the data to the API and sends them to the MQTT
        self.objconnect()
        self.client.loop_start()
        for crypto in self.cryptos:
            response= requests.get("https://api.coingecko.com/api/v3/coins/"+crypto+"/market_chart?vs_currency=usd&days="+str(self.days))
            response=response.json()
            for pricedatapoint in response['prices']:
                self.mqttpublisher(crypto,pricedatapoint)

        self.client.loop_stop()

    
    def mqttpublisher(self,crypto,pricedatapoint):
        #the actual mqtt publisher
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')

        path='scraper/'+crypto
        self.client.publish(path,str(pricedatapoint), qos=1)
        
        

if __name__ == "__main__":
    print(datetime.now())
    mainscraper=PriceScraper(['bitcoin','XRP','Tether','dogecoin','eth','LTC','ADA','DOT','BCH','BNB','XLM','Chainlink'],analyzeddays=210)
    #mainscraper=PriceScraper(['bitcoin','eth','chainlink','XLM','dogecoin','LTC'],analyzeddays=200)
    #mainscraper=PriceScraper('bitcoin')
    mainscraper.scrapepricedata()

# the mqtt topic where things are being published is scraper/nomecrypto.
# for example, by publishing bitcoin data the topic will be: scraper/bitcoin


