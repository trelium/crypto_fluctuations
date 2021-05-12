import pyodbc

server = 'bdtproject-sqlserver.database.windows.net'
database = 'bdt-SQL1'
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
cursor.execute("select * from utenti_bot where active = 0 ")

#cursor.execute("CREATE TABLE notifiche_utenti (user_id VARCHAR(300), chat_id VARCHAR(300), last_notified TIMESTAMP, binancecoin FLOAT, bitcoin FLOAT, ethereum FLOAT, ripple FLOAT, dogecoin FLOAT);")  
#cnxn.commit()

rows = cursor.fetchall() #gets the query results 
print(rows[0][3])
print(bool(rows[0][3]))
print(rows[0][3] == b'\x00')
print(bool(rows[0][3]) == True)

print(bool( b'\x01')==False)
"""
with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT TOP 3 name, collation_name FROM sys.databases")
        row = cursor.fetchone()
        while row:
            print (str(row[0]) + " " + str(row[1]))
            row = cursor.fetchone()
"""