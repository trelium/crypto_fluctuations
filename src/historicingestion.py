"""
----------------------------------------------------------------
----   Data Ingestion: MQTT Subscriber and SQL inserter     ----
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This scripts takes care of the actual ingestion of data and inserts the data into the SQL table "priceshistory".
For more details about the actual SQL queries, consult the class PricesSQL of database.py 

Core features:
    * Subscribes to the specific topic of each crypto
    * Loads data into the SQL efficiently

Other functionalities:
    * Can read the MQTT messages without inserting data into the SQL. Can be useful if you are planning to use
      the API data for other purposes.
    * Filters input data: data that is not properly formatted or that is already present in the pricehistory table
      will not be considered.
    * The MQTT subscriber is working in QOS 1
    * The MQTT subscriber is able to read different topics, this is because a customized topic is made
    by the publisher for each crypto.

"""

import pyodbc
import paho.mqtt.client as mqtt
import time
import datetime
from queue import SimpleQueue
from database import PricesSQL
from dotenv import load_dotenv
import os
from ast import literal_eval

load_dotenv()

class MqttSQL:
    """
    This object fulfills the "sub" related role in our scraper.
    It listens to the mqtt publisher of the apihistoricprices and it can load the data it receives in the
    specified SQL.
    """
    def __init__(self):
        #MQTT address
        self.broker = os.environ.get("BROKER_ADDRESS")
        
        #Instantiate connection to database
        self.db = PricesSQL()

        #Only used by listenscrapers if verbose is on. Useful for debugging, because it checks
        #how many (and which) message the sub has received
        self.i=1

        #This class uses a Python queue to operate: note that python queue are optimized
        #for large amount of data and multithreading, as such, they are fairly scalable.
        self.myqueue=SimpleQueue()


    def listenscrapers(self,save=True,timescraping=600,verbose=False):
        """
        Select "save" if you want the data to be saved on the SQL database, otherwise this code
        will only print the messages it receives.

        Select "forever" if you want the "listen" function to run forever)

        Verbose will just notify you when you receive a message on the MQTT
        """

        #mqtt connecter
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("scraper/#",1)
            else:
                print("Bad connection Returned code=",rc)

        #This function specifies what happens every time we receive a message on the mqtt topic scraper/"name of the crypto"
        def on_message(client, userdata, msg):
            #if save is set to "False", this code will print the message and stop the function.
            if not save:
                print(msg.topic+" "+str(msg.payload))
                return None

            if verbose:
                print('id: ',self.i,msg.topic[8:],datetime.datetime.now())
                self.i+=1

            #This is the end of the "on message" sequence: we push our formatted tuple in a FIFO queue
            self.myqueue.put(msg.payload)


        #MQTT connector
        client = mqtt.Client(client_id="priceSQL_push",clean_session=False)
        #client_id="priceSQL_push"
        client.connect(self.broker, 1883, 60)

        #callback_mutex is there to eventually implement multithreading if necessary.
        with client._callback_mutex:
            client._on_message=on_message
        #client.on_message = on_message
        client.on_connect = on_connect


        # With the time argument, you can decide how much will the subber work for.
        # Useful if you are expecting lots of data or not much of it.
        client.loop_start()
        time.sleep(timescraping)
        client.loop_stop()



    def sqlinserter(self):
        """
        This is the part of the code that takes messages from the queue and pushes them to the SQL.
        It requires no argument, given that the queue is already present in our class.
        """

        print('Starting the data insertion from the queue')

        #We're using a list to make appends because append in python has complexity O(1)
        index=0
        valuelst=[]
        alreadypresent=self.db.get_coins_and_timevalues()
        while self.myqueue.empty()==False:
            
            #converts the string in the queue to a list for each crypto
            cryptohistory=str(self.myqueue.get())
            cryptohistory=literal_eval(cryptohistory[3:-2])
            cryptohistory=list(cryptohistory)

            for i in cryptohistory:

                # Here we format the list element
                coin=i[0]
                timevalue=i[1]
                price=i[2]
                deleted=0
                formattedtuple=tuple([coin,timevalue,price,deleted])
                #print(formattedtuple)
            
                # Our API, by default, sends us their most recent price data.
                # This checks that our data actually comes from midnight.
                # Works in GMT +01:00
                if str(timevalue)[-5:]!='00000':
                    continue

                dt_object = datetime.datetime.fromtimestamp(timevalue//1000)
                if not((dt_object.hour==1 or dt_object.hour==0 or dt_object.hour==2) and dt_object.minute==0 and dt_object.second==00):
                    continue

                #IF the value is already inserted in the SQL, don't add it again, otherwise, add it.
                #print(alreadypresent)
                if tuple([coin,timevalue]) in alreadypresent:
                    continue       

                #IF the value is already present in valuelst, don't add it to the query.
                if str(formattedtuple) in valuelst:
                    continue
            
                # We noticed our SQL INSERT query has some problems after 1000 values, as such we're splitting
                # the task and doing multiple inserts of 950 values.
                if index<950: 
                    index+=1
                    valuelst.append(str(formattedtuple))
                else:
                    index=0
                    print('Inserted 950 data points')
                    self.db.insert_price_values(valuelst)
                    valuelst=[]
                    alreadypresent=self.db.get_coins_and_timevalues()

            # Given that our queue rarely has multiple of 980 elements, we'll do a final push by 
            # selecting the remaining messages.
            if len(valuelst)>0:
                print('Inserted data in the SQL')
                self.db.insert_price_values(valuelst)
                valuelst=[]

    def update_latest_prices(self):
        #Updates the json file to include the latest prices from the SQL table
        self.db.get_latest_prices()



    
if __name__ == "__main__":

    mqttsubber=MqttSQL()
    mqttsubber.listenscrapers(timescraping=15,verbose=True,save=True)
    mqttsubber.sqlinserter()
    mqttsubber.db.update_time_window()
    mqttsubber.update_latest_prices()
    

