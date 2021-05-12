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
        client = mqtt.Client('scraperclient')
        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("#")
            else:
                print("Bad connection Returned code=",rc)
        client.on_connect = on_connect



        def on_message(client, userdata, msg):
            print('barbapapà')
            print(msg.topic+" "+str(msg.payload))
            print(msg)

        client.on_message = on_message


        client.connect(self.broker, 1883, 60)

        client.loop_start()
        client.loop_forever()
        time.sleep(100)




test=mqtttosql()
test.listenscrapers()
