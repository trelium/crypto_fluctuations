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
import json

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
                self.cursor.execute("""SELECT chat_id FROM dbo.users WHERE active = 1 AND {} > {} """.format(currency, currentvalues[currency]['usd']))
            else:
                self.cursor.execute("""SELECT chat_id FROM dbo.users 
                                        WHERE active = 1 
                                        AND {} < {} """.format(currency, currentvalues[currency]['usd']))

        return self.cursor.fetchall() #list of tuples

    def set_state(self, user:str(), chat:str(), state:str()):  
        try:
            self.cursor.execute("""UPDATE dbo.users SET state='{state}' WHERE chat_id='{chat}'
                                IF @@ROWCOUNT=0
                                INSERT INTO dbo.users(user_id, chat_id, state) VALUES ('{user}','{chat}','{state}');""".format(user = user, chat = chat, state = state))

            self.cnxn.commit()
            return True
        except: 
            return False 
    
    def get_state(self, chat:str()):
        try:
            self.cursor.execute("""SELECT state FROM dbo.users
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
            self.cursor.execute("""UPDATE dbo.users SET active = {} 
                                    WHERE chat_id = '{}' """.format(value, chat))
            self.cnxn.commit()
            return True
        except: 
            return False 

    def is_already_present(self,chat:str()):
        """
        Returns true if a chat is already in the database, false otherwise 
        """
        self.cursor.execute("""SELECT chat_id FROM dbo.users
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
            self.cursor.execute("""SELECT active FROM dbo.users
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
                    self.cursor.execute("""INSERT INTO dbo.users(chat_id) 
                                    #VALUES '{}' """.format(chat))
                    self.cnxn.commit()                        
            i=0
            for coin in preferences: #valid only since we have 5 preferences to loop
                i+=1
                self.cursor.execute("""UPDATE dbo.users 
                                    SET coin_{i} = '{name}', pct_{i} = {pct}                                    
                                    WHERE chat_id = '{chat}' """.format(i = i, name = coin, pct = preferences[coin], chat=chat))
                self.cnxn.commit()
                
        except:
            raise ValueError()

    def get_preferences(self):
        """
        This function returns a set of all the coins that the users want to be updated about.
        Each coin is listed only once, without information about price threesolds or users. 
        """
        self.cursor.execute("""SELECT coin_1 FROM dbo.users WHERE coin_1 IS NOT NULL
                                UNION
                                SELECT coin_2 FROM dbo.users WHERE coin_2 IS NOT NULL
                                UNION
                                SELECT coin_3 FROM dbo.users WHERE coin_3 IS NOT NULL
                                UNION
                                SELECT coin_4 FROM dbo.users WHERE coin_4 IS NOT NULL
                                UNION
                                SELECT coin_5 FROM dbo.users WHERE coin_5 IS NOT NULL""")

        #a set is used for efficiency
        ret=set()
        
        #adds each preferred crypto to the set
        for i in self.cursor.fetchall():
            ret.add(i[0])
        
        #converts the set in a list and returns it.
        return list(ret)

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
            self.cursor.execute("""CREATE TABLE priceshistory(
                                    id int IDENTITY(1,1) PRIMARY KEY,
                                    coin VARCHAR(255) NOT NULL,
                                    timevalue BIGINT NOT NULL,   
                                    price FLOAT NOT NULL,
                                    deleted BIT NOT NULL);""") #TODO correct datatypes

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

    def value_already_present(self,timevalue,coin):
        """
        Checks whether the price value for a given timestam and a given coin is already present in the DB.
        Returns:
            :Bool: True/False 
        """
        return len(self.execute_query(f"SELECT * FROM dbo.priceshistory WHERE timevalue={timevalue} AND coin LIKE '{coin}';").fetchall())!=0

    def insert_price_values(self,prices:list()):
        self.execute_query('INSERT INTO dbo.priceshistory VALUES '+(','.join(prices))+';', commit=True)
        return
    
    def get_coins(self):
        """
        Returns a list of all unique coins currently present in the priceshistory table 
        """
        cryptosquery=self.execute_query("SELECT DISTINCT coin FROM dbo.priceshistory")
        cryptos=[i[0] for i in cryptosquery.fetchall()]
        return cryptos

    def update_time_window(self):
        """
        If the database has more than 200 non-deleted
        rows for each given coin, delete the oldest record by marking its deleted column as deleted.
        This makes sure that at any point in time only 200 observations for each coin are marked as
        not deleted in the respective column.
        """  

        #We select all coins in the database
        cryptos = self.get_coins()

        #Actual updater
        for coin in cryptos:
            updated=False
            while not updated:
                if len(self.execute_query(f"SELECT * FROM dbo.priceshistory WHERE coin LIKE '{coin}' AND deleted=0;").fetchall())>200:
                    self.execute_query(f"""
                    UPDATE dbo.priceshistory SET deleted=1 WHERE id=(
                    SELECT id FROM dbo.priceshistory WHERE 
                    timevalue=(SELECT MIN(timevalue) FROM dbo.priceshistory WHERE coin LIKE '{coin}' AND deleted=0)
                    AND coin LIKE '{coin}'
                    );""", True)
                else:
                    updated=True
 
    def get_prices(self, coin:str()):
        """
        Returns a list containing the closing prices marked as not deleted for a specified coin name
        Arguments:
            :coin: name of the coin. Must be a sanitized (as returned by projecttoolbox.sanitizecoininput()) 
        """
        prices = self.execute_query(f"SELECT price FROM dbo.priceshistory WHERE coin LIKE '{coin}' AND deleted=0;").fetchall()
        return prices

    def get_latest_prices(self,save=True):
        """
        Update the "latestprices.json" with the latest prices of the coins.
        It does so by selecting the most recent timestamp from dbo.priceshistory and the coin prices for that date.
        By default, it saves the data into a json.
        """

        latestprices=self.execute_query("SELECT coin,price FROM dbo.priceshistory WHERE timevalue=(SELECT MAX(timevalue) FROM dbo.priceshistory)").fetchall()
        dictret={}

        for i in latestprices:
            dictret[i[0]]=round(i[1],6)

        if save:
            with open(os.path.join("data","latestprices.json"), "w") as out_file:
                json.dump(dictret, out_file, indent = 0)

        return dictret