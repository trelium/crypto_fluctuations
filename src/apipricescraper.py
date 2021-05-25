import requests
import paho.mqtt.client as mqtt
import time
from projecttoolbox import *



class pricescraper:
    """ Scrapes the price from the CoinGecko API and sends them to the scraper/"Name of the coin" topic in our 
    MQTT server.
    """

    def __init__(self,analyzedcryptos,analyzeddays=200,projectbroker='13.73.184.147',confirmdays='y'):

        # list of all cryptos that we are interested in. 
        # the list must contain the correct coin id to work
        # To get a list of all coin IDs, the request url is "https://api.coingecko.com/api/v3/coins/list"
        
        self.cryptos=sanitizecoininput(analyzedcryptos)

        # Warning: due to the automatic granularity of the API, daily data will be used for duration above 90 days.
        # Hourly data will be used for duration between 1 day and 90 days.
        if type(analyzeddays)==int or type(analyzeddays)==float:
            if int(analyzeddays)<=90:

                #This long string is here to inform the user that this software has been designed to work with daily data.
                #While selecting hourly data this code will still work and the data will be published
                #to the correct MQTT topic. That said, the subscriber will refuse the data and will not push it
                #in the SQL.

                #Confirmdays is one of the arguments of the function.
                #It's there to make sure that the user is aware of the subscriber limitation.
                
                confirmdays=confirmdays.lower()
                if 'y' in confirmdays:
                    self.days=int(analyzeddays)
                else:
                    self.days=200
            else:    
                self.days=int(analyzeddays)
        else:
            raise ValueError('Input days should be numeric. "max" is currently not supported.')


        #mqtt connecter
        #oldip:13.73.184.147
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
        #This here is pretty simple: it requests the data to the API and sends them to the MQTT
        
        self.objconnect()
        self.client.loop_start()
        for crypto in self.cryptos:
            response= requests.get("https://api.coingecko.com/api/v3/coins/"+crypto+"/market_chart?vs_currency=usd&days="+str(self.days))
            response=response.json()

            for pricedatapoint in response['prices']:
                self.mqttpublisher(crypto,pricedatapoint)
                #This time.sleep might be the biggest limit to the scalability of the code.
                #I noticed that if we send a lot of messages at the same, the "sub" part of the code
                #Will lose some of the data while it writes on the SQL. 
                #This is because the SQL server that we are using is quite slow and the MQTT is not retaining the messages.
                #This gives more time to the sub code to actually work out everything.
                #I will try to make the sub code more efficient.
                #time.sleep(0.25)

        self.client.loop_stop()

    
    def mqttpublisher(self,crypto,pricedatapoint):
        #quite simple: the mqtt publisher
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')

        path='scraper/'+crypto
        self.client.publish(path,str(pricedatapoint), qos=1)
        
        

if __name__ == "__main__":
    mainscraper=pricescraper(['bitcoin', 'ripple', 'ethereum','binancecoin','dogecoin'])
    mainscraper.scrapepricedata()

# the mqtt topic where things are being published is scraper/nomecrypto.
# nel caso del bitcoin: scraper/bitcoin


#Crontab notes:
# Per impostare il crontab che runna a mezzanotte di questo programma:
# 0 22 * * * python /home/bdtstudent/MainProject/crypto_fluctuations/src/apipricescraper.py >/dev/null 2>&1
# 22^ perché di default crontab usa l'utc

# se non sai usare crontab: premi crontab -e per vedere tutti i vari programmi
# ed i loro orari.

# Per cancellare tutti i crontab:
# crontab -r