import pyodbc
import paho.mqtt.client as mqtt
import time

class mqtttosql:

    def __init__(self):
        self.server = 'bdtproject-sqlserver.database.windows.net'
        self.database = 'BDT-SQL1'
        self.username = 'jacoccardo'
        self.password = 'Riccarcopo1'
        self.driver= '{ODBC Driver 17 for SQL Server}'

        #sql
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cnxn.setencoding('utf-8')
        self.cursor=self.cnxn.cursor()

        #mqtt
        self.broker='51.144.5.107'


    def listenscrapers(self):

        #mqtt connecter

        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("scraper/#")
            else:
                print("Bad connection Returned code=",rc)


        #QUI c'è quello che succede ogniqualvolta arriva un nuovo messaggio al topic a cui hai fatto subscribe.
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))

            # qui è tutto un to be continued
            # if len(self.cursor.execute('SELECT * FROM dbo.pricedata').fetchall())<=200:
            #     pass


            coin=msg.topic[str(msg.topic).rfind('/')+1:]
            
            deleted=0
            print(coin)

        client = mqtt.Client()
        client.connect(self.broker, 1883, 60)
        client.on_message = on_message
        client.on_connect = on_connect

        client.loop_start()
        time.sleep(600)
        #client.loop_forever()

    def sqlexecute(self,query,commit=False):
        self.cursor.execute(query)

        if commit:
            self.cursor.commit()

        return self.cursor


test=mqtttosql()
test.listenscrapers()

#print(test.cursor)
