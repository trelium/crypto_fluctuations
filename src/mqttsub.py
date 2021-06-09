import pyodbc
import paho.mqtt.client as mqtt
import time
import datetime
from queue import SimpleQueue
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

        #Our Server information
        self.server = os.environ.get("SQL_SERVER")  #collation: SQL_Latin1_General_CP1_CI_AS
        self.database = os.environ.get("SQL_DATABASE")
        self.username = os.environ.get("SQL_USERNAME")
        self.password = os.environ.get("SQL_PASSWORD")
        self.driver= os.environ.get("SQL_DRIVER")

        #SQL connector
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cnxn.setencoding('utf-8')
        self.cursor=self.cnxn.cursor()

        #MQTT address
        self.broker='13.73.184.147'
        

        #Only used by listenscrapers if verbose is on. Useful for debugging, because it checks
        #how many (and which) message the sub has received
        self.i=0


        #This program uses a Python queue to operate: note that python queue are optimized
        #for large amount of data and multithreading, as such, they are fairly scalable.
        self.myqueue=SimpleQueue()


    def listenscrapers(self,save=True,forever=True,verbose=False):
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

        #Checks if the Forever argument is true or false
        if forever==False:
            client.loop_start()
            time.sleep(300)
            client.loop_stop()
        else:
            client.loop_start()
            client.loop_forever()


    def sqlexecute(self,query,commit=False):
        """
        A very simple function to work with SQL
        it allows to do simple queries and commit them without having to write the whole thing.
        Also returns self.cursor to make sure that you can use it for fetchall() functions whenever
        you do a SELECT query.
        """

        self.cursor.execute(query)
        if commit:
            self.cursor.commit()

        return self.cursor

    def sqlinserter(self):
        """
        This is the part of the code that takes messages from the queue and pushes them to the SQL.
        It requires no argument, given that the queue is already present in our class.
        """

        print('Starting the data insertion from the queue')

        #We're using a list to make appends because append in python has complexity O(1)
        index=0
        valuelst=[]
        while self.myqueue.empty()==False:
            tempvalue=self.myqueue.get()
            print(tempvalue)
            #IF the value is already inserted in the SQL, don't add it again, otherwise, add it.
            if len(self.sqlexecute(f"SELECT * FROM dbo.pricedata WHERE timevalue={tempvalue[1]} AND coin LIKE '{tempvalue[0]}';").fetchall())!=0:
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
                finalquery='INSERT INTO dbo.pricedata VALUES '+(','.join(valuelst))+';'
                self.sqlexecute(finalquery,commit=True)
                valuelst=[]

        # Given that our queue rarely has multiple of 980 elements, we'll do a final push by 
        # selecting the remaining messages.
        if len(valuelst)>0:
            finalquery='INSERT INTO dbo.pricedata VALUES '+(','.join(valuelst))+';'
            self.sqlexecute(finalquery,commit=True)
            valuelst=[]


    def sqlupdater(self):
        """
        Basically: if the database has more than 200 non-deleted
        rows for each given coin, delete the oldest record by marking its deleted column as deleted.
        """  

        print('Starting to Update the SQL File')
        #We select all coins in the database
        cryptosquery=self.sqlexecute("SELECT DISTINCT coin FROM dbo.pricedata")
        cryptos=[i[0] for i in cryptosquery.fetchall()]

        #Actual updater, it's mostly SQL.
        for coin in cryptos:
            print(coin)
            updated=False
            while not updated:
                if len(self.sqlexecute("SELECT * FROM dbo.pricedata WHERE coin LIKE '{}' AND deleted=0;".format(coin)).fetchall())>200:
                    self.sqlexecute(f"""
                    UPDATE dbo.pricedata SET deleted=1 WHERE id=(
SELECT id
FROM dbo.pricedata 
WHERE timevalue=(
    SELECT MIN(timevalue)
    FROM dbo.pricedata
    WHERE coin
    LIKE '{coin}' AND deleted=0
)
AND coin LIKE '{coin}'
);
""",True)
                else:
                    updated=True


    
if __name__ == "__main__":

    mqttsubber=MqttSQL()
    mqttsubber.listenscrapers(forever=False,verbose=True,save=True)
    mqttsubber.sqlinserter()
    mqttsubber.sqlupdater()
    

