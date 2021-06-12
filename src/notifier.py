from dotenv import load_dotenv
import os
import time
import paho.mqtt.client as mqtt
from queue import SimpleQueue
import ast
import math


load_dotenv()

class Notifier:

    def __init__(self):
        
        #MQTT address
        self.broker = os.environ.get("BROKER_ADDRESS")

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

        print(yesterdaytimestamp)
        print(newprices)
        for coin in newprices:
            pass
            #TODO

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