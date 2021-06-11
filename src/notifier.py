from dotenv import load_dotenv
import os
import time
import paho.mqtt.client as mqtt
from queue import SimpleQueue


load_dotenv()

class Notifier:

    def __init__(self):
        
        #MQTT address
        self.broker = os.environ.get("BROKER_ADDRESS")

        #This class uses a Python queue to operate: note that python queue are optimized
        #for large amount of data and multithreading, as such, they are fairly scalable.
        self.myqueue=SimpleQueue()
    
    def listenpublisher(self, forever=True, time_activation=None):

        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("percentagechange",1)
            else:
                print("Bad connection Returned code=",rc)


        #This function specifies what happens every time we receive a message on the mqtt topic scraper/"name of the crypto"
        def on_message(client, userdata, msg):
            #if save is set to "False", this code will print the message and stop the function.
            
            print(msg.topic+" "+str(msg.payload))

        
        #MQTT connector
        client = mqtt.Client(client_id="Notifier_sub",clean_session=False)
        #client_id="priceSQL_push"
        client.connect(self.broker, 1883, 60)

        #callback_mutex is there to eventually implement multithreading if necessary.
        with client._callback_mutex:
            client._on_message=on_message
        #client.on_message = on_message
        client.on_connect = on_connect

        if forever and time_activation==None:
            client.loop_forever()
        else:
            if time_activation==None:
                time_activation=600

            client.loop_start()
            time.sleep(time_activation)
            client.loop_stop()

test=Notifier()
test.listenpublisher()