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


    def listenscrapers(self,save=True):

        #mqtt connecter

        def on_connect(client, userdata, flags, rc):
            if rc==0:
                print("connected OK Returned code=",rc)
                client.subscribe("scraper/#")
            else:
                print("Bad connection Returned code=",rc)


        #QUI c'è quello che succede ogniqualvolta arriva un nuovo messaggio al topic a cui hai fatto subscribe.
        def on_message(client, userdata, msg):
            
            # Se non si vuole salvare i dati dell'mqtt, basta specificarlo quando si chiama
            # "listenscrapers" mettendo l'argomento "save" come falso.
            if not save:
                print(msg.topic+" "+str(msg.payload))
                return None

            # Formatto il messaggio in arrivo per essere inserito dentro l'SQL
            try:
                templist=str(msg.payload)[3:-2].split(', ')
                temptime=int(templist[0])
                tempprice=float(templist[1])
                coin=msg.topic[msg.topic.rfind('/')+1:]
                deleted=0
            except:
                raise ValueError('There is a problem with the values')

            # aggiungere un if che toglie la data della giornata.
            # Questo perché la nostra API di default considera anche il valore 
            # più recente di oggi, che invece non vogliamo considerare.
            if str(temptime)[-5:]!='00000':
                return None


            #IF the value is already inserted in the SQL, don't add it again, otherwise, add it.
            if len(self.sqlexecute("SELECT * FROM dbo.pricedata WHERE timevalue={} AND coin LIKE '{}';".format(temptime,coin)).fetchall())!=0:
                #return None
                pass            
            else:
                self.sqlexecute("""INSERT INTO dbo.pricedata VALUES('{}',{},{},{});""".format(coin,temptime,tempprice,deleted),
                commit=True)


            #Basically: if the database has more than 200 non-deleted
            #rows for each given coin, delete the oldest record.
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

