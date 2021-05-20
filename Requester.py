"""
-------------------------------------------------------------------
---- Database Management Utilities for Cryptocurrency Predictor----
------------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - May 2021.

---- Description----
Tis module contains the utility class used in order to interact with 
the SQL database instance storing user's chat states and preferences 
via suitable queries.  

Functionalities include:
    * Setting states relative to different chat_ids
    * Checking information related to different chat_ids

"""

# ! pip install pycoingecko
import pyodbc
from pycoingecko import CoinGeckoAPI


class UtentiSQL():
    """
    Class to instantiate a connection to the SQL database containing the preferences expressed
    by the users via the Telegram interface. 
    """
    def __init__(self):
        self.server = 'bdtproject.database.windows.net'  #collation: SQL_Latin1_General_CP1_CI_AS
        self.database = 'BDT-sql2'
        self.username = 'jacoccardo'
        self.password = 'Riccarcopo1'   
        self.driver= '{ODBC Driver 17 for SQL Server}'
        
        #establish connection 
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cursor = self.cnxn.cursor()

        #check if data is already present, otherwise create table 
        self.cursor.execute("""SELECT  table_name name FROM INFORMATION_SCHEMA.TABLES """)
        present_tables = self.cursor.fetchall()
        if not 'utenti_bot' in [elem for sublist in present_tables for elem in sublist]: #True if table is present
            self.cursor.execute("""CREATE TABLE utenti_bot 
            (user_id VARCHAR(300), 
            chat_id VARCHAR(300), 
            state VARCHAR(300), 
            active BINARY(1), 
            coin_1 VARCHAR(300),
            pct_1 FLOAT, 
            coin_2 VARCHAR(300),
            pct_2 FLOAT,
            coin_3 VARCHAR(300),
            pct_3 FLOAT,
            coin_4 VARCHAR(300),
            pct_4 FLOAT,
            coin_5 VARCHAR(300),
            pct_5 FLOAT);""")

    
    def get_chats(self, currentvalues): 
        """
        Retrieves the chat_ids relative to the users that need to be notified of a change, given in input the current market values. 
        """
        for currency in currentvalues:
            if currentvalues[currency]['usd'] > 0:
                self.cursor.execute("""SELECT chat_id FROM dbo.utenti_bot WHERE active = 1 AND {} > {} """.format(currency, currentvalues[currency]['usd']))
            else:
                self.cursor.execute("""SELECT chat_id FROM dbo.utenti_bot 
                                        WHERE active = 1 
                                        AND {} < {} """.format(currency, currentvalues[currency]['usd']))

        return self.cursor.fetchall() #list of tuples

    def set_state(self, user:str(), chat:str(), state:str()):  
        try:
            self.cursor.execute("""UPDATE dbo.utenti_bot SET state='{state}' WHERE chat_id='{chat}'
                                IF @@ROWCOUNT=0
                                INSERT INTO dbo.utenti_bot(user_id, chat_id, state) VALUES ('{user}','{chat}','{state}');""".format(user = user, chat = chat, state = state))

            self.cnxn.commit()
            return True
        except: 
            return False 
    
    def get_state(self, chat:str()):
        try:
            self.cursor.execute("""SELECT state FROM dbo.utenti_bot
                                    WHERE chat_id = '{}' """.format(chat))
            found = self.cursor.fetchall()
            if len(found) != 0:
                return str(found[0][0])
            else:
                return ('no state')
        except:
            return False

    def set_active(self,chat:str(), value:int()):
        """
        Marks the user as active (that is: waiting for updates) by setting the respective attribute.
        :Params:
        value: 0 = inactive; 1 = active
        """
        try:
            self.cursor.execute("""UPDATE dbo.utenti_bot SET active = {} 
                                    WHERE chat_id = '{}' """.format(value, chat))
            self.cnxn.commit()
            return True
        except: 
            return False 

    def is_already_present(self,chat:str()):
        """
        Returns true if a chat is already in the database, false otherwise 
        """
        self.cursor.execute("""SELECT chat_id FROM dbo.utenti_bot
                                    WHERE chat_id = '{}' """.format(chat))
        found = self.cursor.fetchall()
        if len(found) != 0:
            return True 
        else:
            return False

    
    def get_active(self,chat:str()):
        """
        Returns the current value of the 'active' attribute of a user.
        Exits with value False in case of errors raised
        """
        try:
            self.cursor.execute("""SELECT active FROM dbo.utenti_bot
                                    WHERE chat_id = '{}' """.format(chat))
            found = self.cursor.fetchall()
            if len(found) != 0 and str(found[0][0]) ==  b'\x01':
                return 1
            elif len(found) != 0 and str(found[0][0]) ==  b'\x00':
                return 0
            else: 
                return False
        except:
            return False
        

    def set_preferences(self, chat:str(), preferences: dict()):
        try:
            if not self.is_already_present(chat): #actually it is always going to be present
                    self.cursor.execute("""INSERT INTO dbo.utenti_bot(chat_id) 
                                    #VALUES '{}' """.format(chat))
                    self.cnxn.commit()                        
            i=0
            for coin in preferences: #valid only since we have 5 preferences to loop
                i+=1
                self.cursor.execute("""UPDATE dbo.utenti_bot 
                                    SET coin_{i} = '{name}', pct_{i} = {pct}                                    
                                    WHERE chat_id = '{chat}' """.format(i = i, name = coin, pct = preferences[coin], chat=chat))
                self.cnxn.commit()
                
        except:
            raise ValueError()
            


