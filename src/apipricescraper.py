import requests
import paho.mqtt.client as mqtt



class pricescraper:

    def __init__(self,analyzedcryptos,analyzeddays=90,projectbroker='51.144.5.107'):

        # list of all cryptos that we are interested in. 
        # the list must contain the correct coin id to work
        # To get a list of all coin IDs, the request url is "https://api.coingecko.com/api/v3/coins/list"
        if type(analyzedcryptos)!=list:
            self.cryptos=[analyzedcryptos]
        else:
            self.cryptos=analyzedcryptos

        # Warning: due to the automatic granularity of the API, daily data will be used for duration above 90 days.
        # Hourly data will be used for duration between 1 day and 90 days.
        if type(analyzeddays)==int or type(analyzeddays)==float:
            if int(analyzeddays)<200:
                confirmdays=input(

"""Are you sure you want to scrape less than 200 days?
Please consider that, while the scraping will work just fine, the SQL has been designed to
work with daily data and as such there might be errors. Are you sure you want to proceed? (Y/N)  """)
                confirmdays=confirmdays.lower()
                if 'y' in confirmdays:
                    print('yes!')
                    self.days=int(analyzeddays)
                else:
                    self.days=200
            else:    
                self.days=int(analyzeddays)
        else:
            raise ValueError('Input days should be numeric.')

        #setup ip address for mqtt
        #self.broker=projectbroker

        #mqtt connecter
        self.broker=projectbroker
        self.client=None
        self.connected=False

    def objconnect(self):
        #connects the object to a mqtt broker
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
        for crypto in self.cryptos:
            response= requests.get("https://api.coingecko.com/api/v3/coins/"+crypto+"/market_chart?vs_currency=usd&days="+str(self.days))
            response=response.json()
            
            self.objconnect()

            for pricedatapoint in response['prices']:
                self.mqttpublisher(crypto,pricedatapoint)

    
    def mqttpublisher(self,crypto,pricedatapoint):
        #mqttpublisher
        if self.connected==False:
            raise Exception('The object is not connected to a mqtt broker.')

        path='scraper/'+crypto
        self.client.publish(path,str(pricedatapoint), qos=0)



mainscraper=pricescraper(['ethereum','bitcoin'],analyzeddays=201)
mainscraper.scrapepricedata()

# the mqtt topic where things are being published is scraper/nomecrypto.
# nel caso del bitcoin: scraper/bitcoin
#mainscraper.scrapepricedata()


# Per impostare il crontab che runna a mezzanotte di questo programma:
# 0 22 * * * python /home/bdtstudent/MainProject/crypto_fluctuations/src/apipricescraper.py >/dev/null 2>&1
# 22^ perché di default crontab usa l'utc

# se non sai usare crontab: premi crontab -e per vedere tutti i vari programmi
# ed i loro orari.


# Per cancellare tutti i crontab:
# crontab -r