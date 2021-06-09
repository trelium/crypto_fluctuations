import pyodbc

server = 'bdtproject.database.windows.net'
database = 'bdt-sql2'
username = 'jacoccardo'
password = 'Riccarcopo1'   
driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#drop table utenti_bot
#header : user_id, chat_id, state, active, binance, bitcoin... 

#cursor.execute("CREATE TABLE utenti_bot (user_id VARCHAR(300), chat_id VARCHAR(300), state VARCHAR(300), active BINARY(1), binancecoin FLOAT, bitcoin FLOAT, ethereum FLOAT, ripple FLOAT, dogecoin FLOAT);") #submits the quey 
#cursor.execute("INSERT INTO utenti_bot(user_id,state,binancecoin,active) VALUES ('fhrigni56','in attesa',-23.45,0)" )
#cnxn.commit() #mandatory in order to save permanently 
#cursor.execute("select * from utenti_bot where active = 0 ")
cursor.execute("SELECT chat_id FROM dbo.utenti_bot WHERE chat_id = '4yyuy44610376' ")
rows = cursor.fetchall()
print(rows)

#cursor.execute("CREATE TABLE notifiche_utenti (user_id VARCHAR(300), chat_id VARCHAR(300), last_notified TIMESTAMP, binancecoin FLOAT, bitcoin FLOAT, ethereum FLOAT, ripple FLOAT, dogecoin FLOAT);")  
#cnxn.commit()
"""
rows = cursor.fetchall() #gets the query results 
print(rows[0][3])
print(bool(rows[0][3]))
print(rows[0][3] == b'\x00')
print(bool(rows[0][3]) == True)

print(bool( b'\x01')==False)
"""

#delete table 
#cursor.execute("""DROP TABLE utenti_bot;""")
#cnxn.commit()

"""
with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT TOP 3 name, collation_name FROM sys.databases")
        row = cursor.fetchone()
        while row:
            print (str(row[0]) + " " + str(row[1]))
            row = cursor.fetchone()
"""

diction  = {'update_id': 136492356, 'message': {'message_id': 272, 'date': 1621530681, 
'chat': {'id': 444610376, 'type': 'private', 'username': 'trelium', 'first_name': 'Jacopo'}, 
'text': '/start', 
'entities': [{'type': 'bot_command', 'offset': 0, 'length': 6}], 
'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
'from': {'id': 444610376, 'first_name': 'Jacopo', 'is_bot': False, 'username': 'trelium', 'language_code': 'en'}}} 

print(diction['message']['from']['username'])
print (u'\U0001f604')


"""
cg = CoinGeckoAPI()
db = UtentiSQL()

rows = db.cursor.fetchall()
print(rows)

                                 
currentvalues = cg.get_price(ids=['bitcoin', 'ripple', 'ethereum','Binance Coin','dogecoin' ], vs_currencies='usd')
print(currentvalues)
print(db.get_chats(currentvalues))
print(db.set_state(chat='chatdiprova', user='utenteprova', state= 'ready'))
db.cursor.execute(" SELECT* from  dbo.utenti_bot ")
rows = db.cursor.fetchall()
print(rows)
#db.cnxn.commit()

"""
