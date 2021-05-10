import requests
import json
import paho.mqtt.client as mqtt


# list of all cryptos that we are interested in. 
# the list must contain the correct coin id to work
# To get a list of all coin IDs, the request url is "https://api.coingecko.com/api/v3/coins/list"
analyzedcryptos=['bitcoin']


def scrapepricedata(analyzedcryptos):
    for crypto in analyzedcryptos:
        
        #richiedo i dati
        response= requests.get("https://api.coingecko.com/api/v3/coins/"+crypto+"/market_chart?vs_currency=usd&days=90")
        response=response.json()
        
        for i in response['prices']:
            print(i)


#scrapepricedata(analyzedcryptos)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

client = mqtt.Client()
client.on_connect = on_connect
client.connect('51.144.5.107', 1883, 60)
client.publish('test', 'message', qos=0)
