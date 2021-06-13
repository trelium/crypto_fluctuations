"""
----------------------------------------------------------------
---------    MQTT Subscriber and Notification sender   ---------
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.


---- Description----
This scripts acts as the subscriber of the "percentagechange" MQTT topic.
After that it processes the messages by looking which user should be notified about change of prices
and sends a notification to that user.

Core features:
    * Subscribes to the mqtt topic with a static client id.
    * Sends a notification to the user for each given crytpo if:
        * their desired percentage of change has been met
        * they have "active" in the dbo.users set as TRUE
        * No notification for this crypto has been sent to the user today (used to not overload the user with information)



Other functionalities:
    * The MQTT subscriber is working in QOS 1


"""





from dotenv import load_dotenv
import os
import time
import paho.mqtt.client as mqtt
from queue import SimpleQueue
import ast
import math

import telegram
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
        self.bot = telegram.Bot(token=os.environ.get("KEY"))
    
    def listen_publisher(self,time_activation=30,verboselisten=False):
        """
        this function connects the class to the 'percentagechange' mqtt topic and pushes the messages in a queue.
        Arguments: \\
            :verboselisten: is used for debugging and prints the message that the function is receiving. \\
            :time_activation: is how much time will the subscriber be listening to the mqtt. 
                            Given that we do multiple connections in start(), 
                            it is not necessary for time_activation to be high.
        """

        #connects to the mqtt topic
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("percentagechange",1)
            else:
                print("Bad connection Returned code=",rc)


        #This function specifies what happens every time we receive a message on the mqtt topic 
        def on_message(client, userdata, msg):
            
            
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

        #time_activation is used here. the subscriber will listen for a set amount of time and then stops.
        client.loop_start()
        time.sleep(time_activation)
        client.loop_stop()


    def process_queue(self):
        """
        This method is used for processing the queue.
        Each item of the queue gets extracted and converted to a dictionary.
        After that, we will check for each crypto in the dictionary if any user
        should receive a notification. If that is the case, we send the notification and update latest_notification.
        """

        #formatting of the queue element
        byte_str = self.myqueue.get()
        dict_str = byte_str.decode("UTF-8")
        newprices = ast.literal_eval(dict_str)
        yesterdaytimestamp=newprices.pop('timestamp of yesterday prices')


        for coin in newprices:
            users_to_notify = self.dbusers.get_interested_users(crypto=coin,threshold=newprices[coin],considered_date=yesterdaytimestamp)
            if users_to_notify!=[]: #checks if any user is interested in the given crypto
                for user in users_to_notify: 
                    self.send_notification(chat_id=user[0],crypto=coin,percentage_change=newprices[coin]) #sends a notification to the user
                    ## PER JACOPO: il codice di sotto è commentato perché per debuggare è più utile
                    ## è il codice che aggiorna il timestamp sull'SQL. Se è commentato l'utente continuerà sempre 
                    ## a ricevere notifiche. è utile per debuggare, ma ovviamente non è quello che vogliamo
                    #self.dbusers.latestnotification(chat_id=user[0],crypto=coin) #updates the latest_notification for this crypto/user



    def send_notification(self,chat_id,crypto,percentage_change):
        msg = f'Alert: current {crypto} price is {percentage_change}% with respect to yesterday’s closing. We predict bullish/bearish market conditions, with an expected closing price higher/lower than  yesterday’s. 📈📉'
        self.bot.sendMessage(chat_id=chat_id, text=msg)
        print(chat_id,crypto,percentage_change)
        pass



    def start(self,forever=True,runningtime=None,verbose=False):
        """
        Executes most of the previous scripts:
        If forever is True, it keeps checking for new messages every 40 seconds
        and automatically sends notifications if necessary.
        """
        if forever==True and runningtime==None:
            while True:
                self.listen_publisher(verboselisten=verbose)
                test.process_queue()
        
        else:
            test.listen_publisher(verboselisten=verbose,time_activation=runningtime)
            test.process_queue()


# attiva api_percentage_change per mandare i messaggi, attiva questo per riceverli.
if __name__ == "__main__":
    test=Notifier()
    test.start(verbose=True)