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

load_dotenv()


class MqttSQL:
    """
    This object fulfills the "sub" related role in our scraper.
    It listens to the mqtt publisher of the apipricescraper and it can load the data it receives in the
    specified SQL.
    """

    def __init__(self):

        #MQTT address
        self.broker = os.environ.get("BROKER_ADDRESS")
        
        #Instantiate connection to database
        self.db = PricesSQL()

        #Only used by listenscrapers if verbose is on. Useful for debugging, because it checks
        #how many (and which) message the sub has received
        self.i=0


        #This program uses a Python queue to operate: note that python queue are optimized
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

            # Here we format the message we are receiving to prepare it to be sent to the SQL.
            # The formatting is fairly efficient, allowing for fast processing
            try:
                templist=str(msg.payload)[3:-2].split(', ')
                temptime=int(templist[0])
                tempprice=float(templist[1])
                coin=msg.topic[8:]
                deleted=0
            except:
                print('There is a problem with the formatting of the values of this message')
                return None

            
            if verbose:
                print('id: ',self.i,msg.topic[8:],datetime.datetime.now())
                self.i+=1

            # Our API, by default, sends us their most recent price data.
            # This checks that our data actually comes from midnight.
            if str(temptime)[-5:]!='00000':
                return None

            #This is the end of the "on message" sequence: we push our formatted tuple in a FIFO queue
            self.myqueue.put(tuple([coin,temptime,tempprice,deleted]))


        #MQTT connector
        client = mqtt.Client(client_id="priceSQL_push")
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
            tempvalue=self.myqueue.get()
            print(tempvalue)
            #IF the value is already inserted in the SQL, don't add it again, otherwise, add it.
            #print(alreadypresent)
            if tuple([tempvalue[0],tempvalue[1]]) in alreadypresent:
                continue       
            #IF the value is already present in valuelst, don't add it to the query.
            if str(tempvalue) in valuelst:
                continue
            
            # We noticed our SQL INSERT query has some problems after 1000 values, as such we're splitting
            # the task and doing multiple inserts of 950 values.
            if index<950: 
                index+=1
                valuelst.append(str(tempvalue))
            else:
                index=0
                self.db.insert_price_values(valuelst)
                valuelst=[]

        # Given that our queue rarely has multiple of 980 elements, we'll do a final push by 
        # selecting the remaining messages.
        if len(valuelst)>0:
            self.db.insert_price_values(valuelst)
            valuelst=[]

    def update_latest_prices(self):
        #Updates the json file to include the latest prices from the SQL table
        self.db.get_latest_prices()



    
if __name__ == "__main__":

    mqttsubber=MqttSQL()
    mqttsubber.listenscrapers(timescraping=600,verbose=True,save=True)
    mqttsubber.sqlinserter()
    mqttsubber.db.update_time_window()
    mqttsubber.update_latest_prices()
    

