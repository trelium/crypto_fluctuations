"""
-------------------------------------------------------------------
---- Database Management Utilities for Cryptocurrency Predictor----
------------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
Tis module contains the utility class used in order to interact with 
the SQL database instance. This stores: 
    * Table priceshistory: historic price data for set of cryptos.
        Interface for this table is provided by UsersSQL class.
    * Table users: user's chat states and preferences 
        Interface for this table is provided by PricesSQL class.


"""

import pyodbc
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv
import os

load_dotenv()

class UsersSQL():
    """
    Class to instantiate a connection and interact with the SQL database table 
    containing the preferences expressed by the users via the Telegram interface. 

    Functionalities include:
        * Setting states relative to different chat_ids
        * Checking information related to different chat_ids

    """
    def __init__(self):
        self.server = os.environ.get("SQL_SERVER")  #collation: SQL_Latin1_General_CP1_CI_AS
        self.database = os.environ.get("SQL_DATABASE")
        self.username = os.environ.get("SQL_USERNAME")
        self.password = os.environ.get("SQL_PASSWORD")
        self.driver= os.environ.get("SQL_DRIVER")
        
        #establish connection 
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cnxn.setencoding('utf-8')
        self.cursor = self.cnxn.cursor()

        #check if data is already present, otherwise create table 
        self.cursor.execute("""SELECT  table_name name FROM INFORMATION_SCHEMA.TABLES """)
        present_tables = self.cursor.fetchall()
        if not 'users' in [elem for sublist in present_tables for elem in sublist]: #True if table is present
            self.cursor.execute("""CREATE TABLE users 
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
            


class PricesSQL():
    """
    Class to instantiate a connection and interact with the SQL database table 
    containing the historic price data for the currently available cryptocurrencies.
    """
    def __init__(self):
        self.server = os.environ.get("SQL_SERVER")  #collation: SQL_Latin1_General_CP1_CI_AS
        self.database = os.environ.get("SQL_DATABASE")
        self.username = os.environ.get("SQL_USERNAME")
        self.password = os.environ.get("SQL_PASSWORD")
        self.driver= os.environ.get("SQL_DRIVER")
        
        #establish connection 
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cnxn.setencoding('utf-8')
        self.cursor = self.cnxn.cursor()

        #check if data is already present, otherwise create table 
        self.cursor.execute("""SELECT  table_name name FROM INFORMATION_SCHEMA.TABLES """)
        present_tables = self.cursor.fetchall()
        if not 'priceshistory' in [elem for sublist in present_tables for elem in sublist]: #True if table is present
            self.cursor.execute("""CREATE TABLE priceshistory 
            (id VARCHAR(300), 
            coin VARCHAR(255), 
            timevalue BIGINT, 
            price FLOAT, 
            deleted BIT);""") #TODO correct datatypes

    def execute_query(self,query:str(),commit=False):
        """
        Wrapper method to execute SQL queries on the connected DB instance.
        Returns:
            :self.cursor: to make sure that you can use it for fetchall() functions whenever
                            you do a SELECT query.
        """

        self.cursor.execute(query)
        if commit:
            self.cursor.commit()

        return self.cursor 

    def value_already_present(self,timevalue,coinname):
        """
        Checks whether the price value for a given timestam and a given coin is already present in the DB.
        Returns:
            :Bool: True/False 
        """
        return len(self.execute_query(f"SELECT * FROM dbo.pricedata WHERE timevalue={timevalue} AND coin LIKE '{coinname}';").fetchall())!=0

    def insert_price_values(self,prices:list()):
        self.execute_query('INSERT INTO dbo.pricedata VALUES '+(','.join(prices))+';', commit=True)
        return
    
    def update_time_window(self):
        """
        If the database has more than 200 non-deleted
        rows for each given coin, delete the oldest record by marking its deleted column as deleted.
        This makes sure that at any point in time only 200 observations for each coin are marked as
        not deleted in the respective column.
        """  

        #We select all coins in the database
        cryptosquery=self.execute_query("SELECT DISTINCT coin FROM dbo.pricedata")
        cryptos=[i[0] for i in cryptosquery.fetchall()]

        #Actual updater
        for coin in cryptos:
            updated=False
            while not updated:
                if len(self.execute_query("SELECT * FROM dbo.pricedata WHERE coin LIKE '{}' AND deleted=0;".format(coin)).fetchall())>200:
                    self.execute_query("""
                    UPDATE dbo.pricedata SET deleted=1 WHERE id=(
                    SELECT id FROM dbo.pricedata WHERE 
                    timevalue=(SELECT MIN(timevalue) FROM dbo.pricedata WHERE coin LIKE '{}' AND deleted=0)
                    AND coin LIKE '{}'
                    );""".format(coin,coin),True)
                else:
                    updated=True
 