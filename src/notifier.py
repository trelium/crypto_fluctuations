"""
----------------------------------------------------------------
----- CoinGecko API current price Scraper and MQTT Publisher ---
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
    * The day before prices are saved in a json and updated daily by mqttsub.py
    * Messages are sent in QOS 1


"""





from dotenv import load_dotenv
import os
import time
import paho.mqtt.client as mqtt
from queue import SimpleQueue
import ast
import math
from database import UsersSQL

load_dotenv()

class Notifier:

    def __init__(self):
        
        #MQTT address
        self.broker = os.environ.get("BROKER_ADDRESS")

        self.dbusers=UsersSQL()

        #This class uses a Python queue to operate: note that python queue are optimized
        #for large amount of data and multithreading, as such, they are fairly scalable.
        self.myqueue=SimpleQueue()
    
    def listenpublisher(self,time_activation=30,verboselisten=False):

        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("percentagechange",1)
            else:
                print("Bad connection Returned code=",rc)


        #This function specifies what happens every time we receive a message on the mqtt topic scraper/"name of the crypto"
        def on_message(client, userdata, msg):
            #if save is set to "False", this code will print the message and stop the function.

            if verboselisten:
                print(msg.topic+" "+str(msg.payload))

            self.myqueue.put(msg.payload)
        
        #MQTT connector
        client = mqtt.Client(client_id="Notifier_sub",clean_session=False)
        #client_id="priceSQL_push"
        client.connect(self.broker, 1883, 60)

        #callback_mutex is there to eventually implement multithreading if necessary.
        with client._callback_mutex:
            client._on_message=on_message
        #client.on_message = on_message
        client.on_connect = on_connect

        client.loop_start()
        time.sleep(time_activation)
        client.loop_stop()

    def processqueue(self):

        byte_str = self.myqueue.get()
        dict_str = byte_str.decode("UTF-8")
        newprices = ast.literal_eval(dict_str)
        yesterdaytimestamp=newprices.pop('timestamp of yesterday prices')
        for coin in newprices:
            #print(coin,newprices[coin],yesterdaytimestamp)
            users_to_notify=self.dbusers.get_interested_users(crypto=coin,threesold=newprices[coin],considered_date=yesterdaytimestamp)
            if users_to_notify!=[]:
                for user in users_to_notify:
                    self.SendNotification(chat_id=user[0],crypto=coin,percentage_change=newprices[coin])
                    self.dbusers.update_preferences(chat_id=user[0],crypto=coin)

    def SendNotification(self,chat_id,crypto,percentage_change):
        print(chat_id,crypto,percentage_change)
        pass



    def start(self,forever=True,runningtime=None,verbose=False):

        if forever==True and runningtime==None:
            while True:
                self.listenpublisher(verboselisten=verbose)
                test.processqueue()
        
        else:
            test.listenpublisher(verboselisten=verbose,time_activation=runningtime)
            test.processqueue()


# attiva api_percentage_change, attiva questo e dovrebbe arrivare un messaggio al minuto.

test=Notifier()
test.start()