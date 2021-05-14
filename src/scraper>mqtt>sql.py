import pyodbc
import paho.mqtt.client as mqtt
import time

class mqtttosql:
    """
    This object fulfills the "sub" related role in our scraper.
    It listens to the mqtt publisher of the apipricescraper and it can load the data it receives in the
    specified SQL.
    """

    def __init__(self):

        #Our Server information
        self.server = 'bdtproject-sqlserver.database.windows.net'
        self.database = 'BDT-SQL1'
        self.username = 'jacoccardo'
        self.password = 'Riccarcopo1'
        self.driver= '{ODBC Driver 17 for SQL Server}'

        #SQL connector
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cnxn.setencoding('utf-8')
        self.cursor=self.cnxn.cursor()

        #MQTT address
        self.broker='51.144.5.107'


    def listenscrapers(self,save=True,forever=True):
        """
        Select "save" if you want the data to be saved on the SQL database, otherwise this code
        will only print the messages it receives.

        Select "forever" if you want the "listen" function to run forever - it might be useful if you
        expect a lot of messages, but it does consume some RAM (and we only have 1gb on this machine :P )
        """

        #mqtt connecter
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("scraper/#")
            else:
                print("Bad connection Returned code=",rc)

        #This function specifies what happens every time we receive a message on the mqtt topic scraper/"name of the crypto"
        def on_message(client, userdata, msg):
            
            #if save is set to "False", this code will print the message and stop the function.
            if not save:
                print(msg.topic+" "+str(msg.payload))
                return None

            # Here we format the message we are receiving to prepare it to be sent to the SQL.
            try:
                templist=str(msg.payload)[3:-2].split(', ')
                temptime=int(templist[0])
                tempprice=float(templist[1])
                coin=msg.topic[msg.topic.rfind('/')+1:]
                deleted=0
            except:
                print('There is a problem with the formatting of the values of this message')
                return None

            # Our API, by default, sends us their most recent price data.
            # This checks that our data actually comes from midnight.
            if str(temptime)[-5:]!='00000':
                return None


            #IF the value is already inserted in the SQL, don't add it again, otherwise, add it.
            if len(self.sqlexecute("SELECT * FROM dbo.pricedata WHERE timevalue={} AND coin LIKE '{}';".format(temptime,coin)).fetchall())!=0:
                return None        
            else:
                self.sqlexecute("""INSERT INTO dbo.pricedata VALUES('{}',{},{},{});""".format(coin,temptime,tempprice,deleted),
                commit=True)


            #Basically: if the database has more than 200 non-deleted
            #rows for this given coin, delete the oldest record by marking its deleted column.
            updated=False
            while not updated:
                if len(self.sqlexecute("SELECT * FROM dbo.pricedata WHERE coin LIKE '{}' AND deleted=0;".format(coin)).fetchall())>200:
                    self.sqlexecute("""
                    UPDATE dbo.pricedata SET deleted=1 WHERE id=(
                    SELECT id FROM dbo.pricedata WHERE 
                    timevalue=(SELECT MIN(timevalue) FROM dbo.pricedata WHERE coin LIKE '{}' AND deleted=0)
                    AND coin LIKE '{}'
                    );""".format(coin,coin),True)
                else:
                    updated=True

        #MQTT connector
        client = mqtt.Client()
        client.connect(self.broker, 1883, 60)
        client.on_message = on_message
        client.on_connect = on_connect

        #Checks if the Forever argument is true or false
        if forever==False:
            client.loop_start()
            time.sleep(1200)
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


mqttsubber=mqtttosql()
mqttsubber.listenscrapers(forever=False)

