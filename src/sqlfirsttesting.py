import pyodbc
import paho.mqtt.client as mqtt

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
                client.subscribe("#")
            else:
                print("Bad connection Returned code=",rc)

        def on_message(client, userdata, msg):
            #print(msg.topic+" "+str(msg.payload))

            print(msg.payload)
            print(msg.state)
            print(msg.dup)
            print(msg.info)



        client = mqtt.Client()
        client.connect(self.broker, 1883, 60)
        client.on_message = on_message
        client.on_connect = on_connect



        client.loop_start()
        client.loop_forever()

    def sqlexecute(self,query):
        self.cursor.execute(query)
        self.cursor.commit()

        return self.cursor


test=mqtttosql()
#test.listenscrapers()
test.sqlexecute()

#print(test.cursor)