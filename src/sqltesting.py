# import requests
# import time

# for i in range(10):
#     response= requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=200")
#     response=response.json()
#     for pricedatapoint in response['prices']:
#         mqttpublisher('bitcoin',pricedatapoint)

# def mqttpublisher(self,crypto,pricedatapoint):
        
#     #mqtt connecter
#     client = mqtt.Client('scraperclient')
#     def on_connect(client, userdata, flags, rc):
#         if rc==0:
#             print("connected OK Returned code=",rc)
#         else:
#             print("Bad connection Returned code=",rc)
#     client.on_connect = on_connect
#     client.connect(self.broker, 1883, 60)

#     #mqttpublisher
#     path='scraper/'+crypto
#     client.publish(path,str(pricedatapoint), qos=0)