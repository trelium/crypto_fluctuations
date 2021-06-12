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
            print(users_to_notify)
            if users_to_notify!=[]:
                print(newprices[coin])
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